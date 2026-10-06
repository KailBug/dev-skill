#!/usr/bin/env python3
"""Validate this repository's skill catalog, metadata, and local Markdown links.

Requires PyYAML. This validator reads files only: it neither imports skill code nor
fetches linked URLs. Run ``python scripts/validate_skills.py --root PATH``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml


NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}


class UniqueSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that also rejects accidentally repeated mapping keys."""


def _unique_mapping(loader: UniqueSafeLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            if key in result:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"duplicate key {key!r}", key_node.start_mark,
                )
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                "mapping keys must be scalar values", key_node.start_mark,
            ) from exc
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping,
)


@dataclass(frozen=True)
class Issue:
    path: str
    code: str
    message: str
    line: int | None = None

    def __str__(self) -> str:
        location = f"{self.path}:{self.line}" if self.line else self.path
        return f"{location}: [{self.code}] {self.message}"


def valid_name(value: Any) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= 64 and bool(NAME_PATTERN.fullmatch(value))


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.issues: list[Issue] = []

    def add(self, path: Path, code: str, message: str, line: int | None = None) -> None:
        try:
            display = path.relative_to(self.root).as_posix()
        except ValueError:
            display = str(path)
        self.issues.append(Issue(display, code, message, line))

    def read(self, path: Path) -> str | None:
        if not within(path, self.root):
            self.add(path, "path-escape", "File resolves outside the repository.")
            return None
        try:
            return path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            self.add(path, "read-error", f"Cannot read UTF-8 file: {exc}")
            return None

    def yaml_mapping(self, path: Path, source: str, offset: int = 0) -> dict | None:
        try:
            data = yaml.load(source, Loader=UniqueSafeLoader)
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            line = mark.line + 1 + offset if mark is not None else None
            self.add(path, "yaml-invalid", str(exc).splitlines()[0], line)
            return None
        if not isinstance(data, dict):
            self.add(path, "yaml-type", "YAML content must be a mapping.", offset + 1)
            return None
        return data

    def catalog(self, actual: set[str]) -> None:
        path = self.root / "skills.json"
        source = self.read(path)
        if source is None:
            return
        try:
            data = json.loads(source)
        except json.JSONDecodeError as exc:
            self.add(path, "catalog-json", exc.msg, exc.lineno)
            return
        if not isinstance(data, dict):
            self.add(path, "catalog-type", "Catalog must be a JSON object.")
            return
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            self.add(path, "catalog-version", "schema_version must be the integer 1.")
        entries = data.get("skills")
        if not isinstance(entries, list):
            self.add(path, "catalog-type", "skills must be an array.")
            return
        names: set[str] = set()
        paths: set[str] = set()
        for index, entry in enumerate(entries):
            label = f"skills[{index}]"
            if not isinstance(entry, dict):
                self.add(path, "catalog-entry", f"{label} must be an object.")
                continue
            name, category, relative = (entry.get(key) for key in ("name", "category", "path"))
            if not valid_name(name):
                self.add(path, "catalog-name", f"{label}.name must be a 1–64 character lowercase hyphenated name.")
            elif name in names:
                self.add(path, "duplicate-name", f"{label}.name repeats {name!r}.")
            else:
                names.add(name)
            if not valid_name(category):
                self.add(path, "catalog-category", f"{label}.category must be a lowercase hyphenated name.")
            if not isinstance(relative, str):
                self.add(path, "catalog-path", f"{label}.path must be a relative POSIX path.")
                continue
            parts = PurePosixPath(relative).parts
            expected = f"skills/{category}/{name}"
            if relative != expected or len(parts) != 3 or "\\" in relative:
                self.add(path, "catalog-path", f"{label}.path must equal {expected!r}.")
                continue
            if not valid_name(name) or not valid_name(category):
                continue
            if relative in paths:
                self.add(path, "duplicate-path", f"{label}.path repeats {relative!r}.")
            paths.add(relative)
            if not within(self.root / relative, self.root):
                self.add(path, "path-escape", f"{label}.path resolves outside the repository.")
        for missing in sorted(actual - paths):
            self.add(path, "catalog-missing", f"Skill {missing!r} is absent from the catalog.")
        for stale in sorted(paths - actual):
            self.add(path, "catalog-stale", f"Catalog path {stale!r} has no SKILL.md.")

    def skill(self, path: Path) -> str | None:
        source = self.read(path)
        if source is None:
            return None
        lines = source.splitlines()
        if not lines or lines[0].strip() != "---":
            self.add(path, "frontmatter-missing", "SKILL.md must begin with YAML frontmatter.", 1)
            return None
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            self.add(path, "frontmatter-unclosed", "YAML frontmatter has no closing ---.", 1)
            return None
        data = self.yaml_mapping(path, "\n".join(lines[1:end]), offset=1)
        if data is None:
            return None
        for key in data:
            if key not in FRONTMATTER_KEYS:
                self.add(path, "frontmatter-key", f"Unsupported frontmatter key {key!r}.", 2)
        name = data.get("name")
        if not valid_name(name):
            self.add(path, "skill-name", "name must be 1–64 lowercase letters/digits with single internal hyphens.", 2)
        elif name != path.parent.name:
            self.add(path, "skill-directory", f"name {name!r} differs from directory {path.parent.name!r}.", 2)
        description = data.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            self.add(path, "skill-description", "description must be nonempty text of at most 1024 characters.", 2)
        if "license" in data and (not isinstance(data["license"], str) or not data["license"].strip()):
            self.add(path, "skill-license", "license must be nonempty text.", 2)
        if "metadata" in data:
            metadata = data["metadata"]
            if not isinstance(metadata, dict) or any(
                not isinstance(k, str) or not k.strip() or not isinstance(v, str)
                for k, v in metadata.items()
            ):
                self.add(path, "skill-metadata", "metadata must be a mapping with nonempty string keys and string values.", 2)
        if "allowed-tools" in data:
            allowed = data["allowed-tools"]
            if not (isinstance(allowed, str) and bool(allowed.strip())) and not (
                isinstance(allowed, list) and bool(allowed)
                and all(isinstance(item, str) and bool(item.strip()) for item in allowed)
            ):
                self.add(path, "skill-tools", "allowed-tools must be nonempty text or an array of nonempty strings.", 2)
        self.agent_metadata(path.parent, name if isinstance(name, str) else path.parent.name)
        return name if valid_name(name) else None

    def agent_metadata(self, directory: Path, name: str) -> None:
        path = directory / "agents" / "openai.yaml"
        if not path.exists():
            return
        source = self.read(path)
        if source is None:
            return
        data = self.yaml_mapping(path, source)
        if data is None:
            return
        if "interface" in data:
            interface = data["interface"]
            if not isinstance(interface, dict) or not interface:
                self.add(path, "agent-interface", "interface must be a nonempty mapping.")
            else:
                short = interface.get("short_description")
                if not isinstance(short, str) or not short.strip() or not 25 <= len(short) <= 64:
                    self.add(path, "agent-description", "interface.short_description must contain 25–64 characters.")
                prompt = interface.get("default_prompt")
                if not isinstance(prompt, str) or f"${name}" not in prompt:
                    self.add(path, "agent-prompt", f"interface.default_prompt must mention ${name}.")
        if "policy" in data:
            policy = data["policy"]
            if not isinstance(policy, dict):
                self.add(path, "agent-policy", "policy must be a mapping.")
            elif "allow_implicit_invocation" in policy and type(policy["allow_implicit_invocation"]) is not bool:
                self.add(path, "agent-policy", "policy.allow_implicit_invocation must be a YAML boolean.")

    def check_target(self, path: Path, target: str, line: int) -> None:
        target = target.strip()
        if not target or target.startswith("#"):
            return
        decoded = unquote(target)
        if re.match(r"^[a-zA-Z]:[/\\]", decoded) or decoded.startswith("\\") or decoded.lower().startswith("file:"):
            self.add(path, "link-absolute", f"Link uses a local absolute path: {target!r}.", line)
            return
        if decoded.startswith("//"):
            return  # Protocol-relative remote URL.
        if decoded.startswith("/"):
            self.add(path, "link-absolute", f"Link uses a local absolute path: {target!r}.", line)
            return
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", decoded):
            return  # External URI; never fetch or execute it.
        try:
            local = unquote(urlsplit(target).path)
        except ValueError:
            self.add(path, "link-invalid", f"Cannot parse link target {target!r}.", line)
            return
        if not local:
            return
        destination = path.parent / local.replace("\\", "/")
        if not within(destination, self.root):
            self.add(path, "link-escape", f"Link escapes the repository: {target!r}.", line)
        elif not destination.exists():
            self.add(path, "link-missing", f"Link target does not exist: {target!r}.", line)

    def markdown(self, path: Path) -> None:
        source = self.read(path)
        if source is None:
            return
        source = _without_code(source)
        definitions: dict[str, tuple[str, int]] = {}
        definition_spans: list[tuple[int, int]] = []
        for match in re.finditer(r"^ {0,3}\[([^\]\n]+)\]:\s*(<[^>\n]+>|\S+)", source, re.MULTILINE):
            label = _reference_label(match.group(1))
            target = match.group(2).strip("<>")
            line = source.count("\n", 0, match.start()) + 1
            definitions[label] = (target, line)
            definition_spans.append(match.span())
            self.check_target(path, target, line)
        for match in re.finditer(r"(?<!\\)\[([^\]\n]+)\]", source):
            if any(start <= match.start() < end for start, end in definition_spans):
                continue
            pos = match.end()
            line = source.count("\n", 0, match.start()) + 1
            if pos < len(source) and source[pos] == "(":
                target = _inline_destination(source, pos)
                if target is not None:
                    self.check_target(path, target, line)
            elif pos < len(source) and source[pos] == "[":
                end = source.find("]", pos + 1)
                if end != -1 and "\n" not in source[pos:end]:
                    label = _reference_label(source[pos + 1:end] or match.group(1))
                    if label not in definitions:
                        self.add(path, "link-reference", f"Reference link {label!r} has no definition.", line)
            else:
                label = _reference_label(match.group(1))
                if label in definitions:
                    target, _ = definitions[label]
                    self.check_target(path, target, line)

    def run(self) -> list[Issue]:
        if not self.root.is_dir():
            self.add(self.root, "root-missing", "Repository root is not a directory.")
            return self.issues
        skill_paths = sorted(self.root.glob("skills/*/*/SKILL.md"))
        actual = {path.parent.relative_to(self.root).as_posix() for path in skill_paths}
        self.catalog(actual)
        names: dict[str, Path] = {}
        markdown_files: set[Path] = set()
        for path in skill_paths:
            name = self.skill(path)
            if name is not None:
                if name in names:
                    self.add(path, "duplicate-name", f"Skill name {name!r} also occurs in {names[name].relative_to(self.root).as_posix()}.")
                else:
                    names[name] = path
            markdown_files.update(path.parent.rglob("*.md"))
        markdown_files.update(self.root.glob("*.md"))
        markdown_files.update((self.root / "docs").rglob("*.md"))
        markdown_files.update(self.root.glob("skills/*/README.md"))
        for path in sorted(markdown_files):
            self.markdown(path)
        return self.issues


def _reference_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def _without_code(source: str) -> str:
    """Blank fenced/inline code while preserving line numbers and offsets."""
    output = []
    fence: str | None = None
    fence_length = 0
    for line in source.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is None and match:
            fence, fence_length = match.group(1)[0], len(match.group(1))
            output.append(re.sub(r"[^\r\n]", " ", line))
        elif fence is not None:
            output.append(re.sub(r"[^\r\n]", " ", line))
            if re.match(rf"^ {{0,3}}{re.escape(fence)}{{{fence_length},}}\s*$", line):
                fence = None
        else:
            output.append(line)
    cleaned = "".join(output)
    return re.sub(r"(`+)([^`\n]*?)\1", lambda match: " " * len(match.group(0)), cleaned)


def _inline_destination(source: str, start: int) -> str | None:
    """Read a Markdown destination, including angle brackets and nested ()."""
    pos = start + 1
    while pos < len(source) and source[pos].isspace():
        pos += 1
    if pos == len(source):
        return None
    if source[pos] == "<":
        end = source.find(">", pos + 1)
        return source[pos + 1:end] if end != -1 else None
    begin, depth = pos, 0
    while pos < len(source):
        char = source[pos]
        if char == "\\" and pos + 1 < len(source) and source[pos + 1] in "() ":
            pos += 2
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                return source[begin:pos].replace(r"\(", "(").replace(r"\)", ")")
            depth -= 1
        elif char.isspace() and depth == 0:
            return source[begin:pos]
        pos += 1
    return None


def validate_repository(root: Path | str) -> list[Issue]:
    return Validator(Path(root)).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Repository root (defaults to this script's parent repository).")
    args = parser.parse_args(argv)
    issues = validate_repository(args.root)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        print(f"Validation failed: {len(issues)} issue(s).", file=sys.stderr)
        return 1
    print("Validation passed: skill catalog, metadata, and local Markdown links are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Behavioral tests for the repository validator; no installed skills required."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills" / "website" / "example-skill"
        self.skill.mkdir(parents=True)
        self.write("README.md", "# Skills\n[Catalog](skills/website/README.md)\n")
        self.write("skills/website/README.md", "[Skill](example-skill/SKILL.md)\n")
        self.write("skills/website/example-skill/references/design.md", "# Design\n")
        self.write_skill()
        self.write_catalog([self.entry()])

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def write_skill(self, extra: str = "", body: str = "[Design](references/design.md)\n") -> None:
        (self.skill / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Build useful example websites.\n"
            + extra + "---\n# Example\n" + body, encoding="utf-8",
        )

    def entry(self, category: str = "website", name: str = "example-skill") -> dict:
        return {"name": name, "category": category, "path": f"skills/{category}/{name}"}

    def write_catalog(self, entries: list[dict]) -> None:
        self.write("skills.json", json.dumps({"schema_version": 1, "skills": entries}))

    def codes(self) -> set[str]:
        return {issue.code for issue in validator.validate_repository(self.root)}

    def test_minimal_skill_without_ui_metadata_is_valid(self) -> None:
        self.assertEqual([], validator.validate_repository(self.root))

    def test_valid_optional_metadata_and_ui(self) -> None:
        self.write_skill("license: MIT\nallowed-tools: [Read, Write]\nmetadata:\n  author: example\n")
        self.write("skills/website/example-skill/agents/openai.yaml", (
            "interface:\n  display_name: Example\n"
            "  short_description: Build clean product websites with reusable design guidance\n"
            "  default_prompt: Use $example-skill to build a product page.\n"
            "policy:\n  allow_implicit_invocation: false\n"
        ))
        self.assertEqual(set(), self.codes())

    def test_missing_link_target_reports_file_and_line(self) -> None:
        self.write_skill(body="[Missing](references/missing.md)\n")
        issues = validator.validate_repository(self.root)
        missing = [issue for issue in issues if issue.code == "link-missing"]
        self.assertEqual(1, len(missing))
        self.assertEqual("skills/website/example-skill/SKILL.md", missing[0].path)
        self.assertEqual(6, missing[0].line)

    def test_catalog_missing_and_stale_entries(self) -> None:
        self.write_catalog([self.entry(name="missing-skill")])
        self.assertTrue({"catalog-missing", "catalog-stale"} <= self.codes())

    def test_missing_or_malformed_catalog_is_rejected(self) -> None:
        (self.root / "skills.json").unlink()
        self.assertIn("read-error", self.codes())
        self.write("skills.json", '{"schema_version": 1, "skills": null}')
        self.assertIn("catalog-type", self.codes())
        self.write("skills.json", '{"schema_version": true, "skills": []}')
        self.assertIn("catalog-version", self.codes())

    def test_duplicate_names_across_categories(self) -> None:
        self.write("skills/other/example-skill/SKILL.md", (self.skill / "SKILL.md").read_text())
        self.write("skills/other/example-skill/references/design.md", "# Design")
        self.write_catalog([self.entry(), self.entry(category="other")])
        duplicates = [issue for issue in validator.validate_repository(self.root) if issue.code == "duplicate-name"]
        self.assertEqual(2, len(duplicates))

    def test_duplicate_catalog_path(self) -> None:
        self.write_catalog([self.entry(), self.entry()])
        self.assertIn("duplicate-path", self.codes())

    def test_metadata_requires_string_mapping(self) -> None:
        for extra in ("metadata: [a, b]\n", "metadata:\n  author: 42\n"):
            with self.subTest(extra=extra):
                self.write_skill(extra)
                self.assertIn("skill-metadata", self.codes())

    def test_safe_yaml_rejects_python_object_tags_and_duplicate_keys(self) -> None:
        self.write_skill("metadata: !!python/object/apply:os.system ['echo unsafe']\n")
        self.assertIn("yaml-invalid", self.codes())
        self.write_skill("description: Another description.\n")
        self.assertIn("yaml-invalid", self.codes())

    def test_invalid_names_and_directory_mismatch(self) -> None:
        for name in ("bad--name", "-bad", "bad-", "Uppercase", "a" * 65):
            with self.subTest(name=name):
                text = (self.skill / "SKILL.md").read_text().replace("name: example-skill", f"name: {name}")
                (self.skill / "SKILL.md").write_text(text)
                self.assertIn("skill-name", self.codes())
                self.write_skill()
        text = (self.skill / "SKILL.md").read_text().replace("name: example-skill", "name: different-name")
        (self.skill / "SKILL.md").write_text(text)
        self.assertIn("skill-directory", self.codes())

    def test_description_bounds(self) -> None:
        for value in ('""', '"' + "x" * 1025 + '"'):
            with self.subTest(value=value[:20]):
                self.write_skill()
                text = (self.skill / "SKILL.md").read_text().replace(
                    "description: Build useful example websites.", f"description: {value}",
                )
                (self.skill / "SKILL.md").write_text(text)
                self.assertIn("skill-description", self.codes())

    def test_ui_description_prompt_and_policy_types(self) -> None:
        self.write("skills/website/example-skill/agents/openai.yaml", (
            "interface:\n  short_description: Too short\n  default_prompt: Build a website\n"
            "policy:\n  allow_implicit_invocation: 'true'\n"
        ))
        self.assertTrue({"agent-description", "agent-prompt", "agent-policy"} <= self.codes())

    def test_absolute_links_and_path_escape_are_rejected(self) -> None:
        self.write_skill(body=(
            "[Windows](C:/Users/example/file.md)\n[Unix](/tmp/file.md)\n"
            "[URI](file:///C:/example.md)\n[Outside](../../../../outside.md)\n"
        ))
        issues = validator.validate_repository(self.root)
        self.assertEqual(3, sum(issue.code == "link-absolute" for issue in issues))
        self.assertEqual(1, sum(issue.code == "link-escape" for issue in issues))

    def test_internal_cross_directory_links_remote_urls_and_anchors_are_valid(self) -> None:
        self.write_skill(body=(
            "[Repo](../../../README.md#skills)\n[Design](references/design.md?mode=1#design)\n"
            "[Web](https://example.com/unavailable)\n[Mail](mailto:example@example.com)\n"
            "[Remote](//example.com/path)\n[Anchor](#example)\n"
        ))
        self.assertEqual(set(), self.codes())

    def test_reference_links_and_definitions(self) -> None:
        self.write_skill(body=(
            "[Design][guide]\n[guide]: references/design.md\n[Missing][no-such-reference]\n"
        ))
        self.assertEqual({"link-reference"}, self.codes())
        self.write_skill(body="[Design][guide]\n[guide]: references/missing.md\n")
        self.assertIn("link-missing", self.codes())

    def test_fenced_and_inline_code_examples_are_ignored(self) -> None:
        self.write_skill(body=(
            "```markdown\n[Example](missing.md)\n```\n"
            "~~~~markdown\n[Example](another-missing.md)\n~~~~\n"
            "`[Inline](also-missing.md)`\n[Actual](references/design.md)\n"
        ))
        self.assertEqual(set(), self.codes())

    def test_nested_parentheses_and_angle_bracket_destinations(self) -> None:
        self.write("skills/website/example-skill/references/design (v2).md", "# Version 2")
        self.write_skill(body='[Design](<references/design (v2).md> "title")\n')
        self.assertEqual(set(), self.codes())
        self.write("skills/website/example-skill/references/design(v2).md", "# Version 2")
        self.write_skill(body="[Design](references/design(v2).md)\n")
        self.assertEqual(set(), self.codes())

    def test_encoded_filename_characters_and_traversal(self) -> None:
        self.write("skills/website/example-skill/references/design#v2.md", "# Version 2")
        self.write_skill(body="[Design](references/design%23v2.md)\n")
        self.assertEqual(set(), self.codes())
        self.write_skill(body="[Outside](%2e%2e/%2e%2e/%2e%2e/%2e%2e/outside.md)\n")
        self.assertIn("link-escape", self.codes())

    def test_repository_documentation_links_are_checked(self) -> None:
        self.write("docs/maintenance.md", "[Missing](missing.md)\n")
        self.write("CONTRIBUTING.md", "[Missing](no-such-file.md)\n")
        issues = validator.validate_repository(self.root)
        self.assertEqual({"docs/maintenance.md", "CONTRIBUTING.md"},
                         {issue.path for issue in issues if issue.code == "link-missing"})

    def test_cli_exit_status_for_valid_and_invalid_repository(self) -> None:
        valid = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)],
                               capture_output=True, text=True, check=False)
        self.assertEqual(0, valid.returncode, valid.stderr)
        self.write_skill(body="[Missing](missing.md)\n")
        invalid = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(1, invalid.returncode)
        self.assertIn("SKILL.md:6", invalid.stderr)


if __name__ == "__main__":
    unittest.main()

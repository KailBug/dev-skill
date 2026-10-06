# 安装、更新与卸载

## 安装单位

安装 `skills/website/minimal-product-website/` 的完整目录。`SKILL.md`、`LICENSE`、相对引用的 `references/`、可选 `assets/` 和 `agents/` 一起保留。`website/` 是分类，仓库根目录不是一个 Skill。

Codex 默认使用 `~/.codex/skills/`；有 `CODEX_HOME` 时使用 `<CODEX_HOME>/skills/`。其他支持此格式的工具请使用其 Skill 目录。不要因为使用 Skill 而安装仓库维护依赖。

## Windows / PowerShell

以下命令用于首次安装，遇到同名目录会停止，不覆盖本地定制：

```powershell
git clone https://github.com/KailBug/dev-skill.git
Set-Location dev-skill
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }
$skillDestination = Join-Path $skillRoot 'minimal-product-website'
if (Test-Path -LiteralPath $skillDestination) { throw '同名 Skill 已存在；请按更新说明备份后处理。' }
New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
Copy-Item -LiteralPath '.\skills\website\minimal-product-website' -Destination $skillDestination -Recurse
```

## macOS / Linux

```sh
git clone https://github.com/KailBug/dev-skill.git
cd dev-skill
skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
skill_destination="$skill_root/minimal-product-website"
if [ -e "$skill_destination" ]; then
  echo "同名 Skill 已存在；请先按更新说明备份。" >&2
else
  mkdir -p "$skill_root"
  cp -R skills/website/minimal-product-website "$skill_destination"
fi
```

## 调用与资源使用

刷新工具的 Skill 列表，或按工具要求重新打开会话。使用 `$minimal-product-website` 并说明品牌、受众、主要行动和已有项目约束。入口文件说明需要读取的设计参考；不必默认加载全部参考资料。

如果手动使用 CSS/JS：页面外层添加 `.mpw-site`，复制或映射 CSS 变量；`reveal.js` 是 ES module，需要本地 HTTP 服务或项目开发服务器预览。直接双击 `file://` HTML 可能拦截模块导入。框架组件在卸载时调用 `initReveals()` 返回的清理函数。

## 更新

1. 查看 [CHANGELOG.md](../CHANGELOG.md)，检查是否有迁移或名称变化。
2. 在仓库目录运行 `git pull --ff-only`；需要稳定快照时检出已发布 tag。
3. 将已安装的完整 Skill 目录备份到 Skill 搜索目录之外，避免旧副本被重复发现。
4. 比较并保留自己的定制改动，再将新目录整体复制到原安装位置；不要仅替换 `SKILL.md` 而遗漏资源。
5. 刷新发现列表，用一个代表性请求验证。

若更新失败，从备份恢复完整目录；不要覆盖有本地改动的仓库 checkout。GitHub 下载 ZIP 的使用者同样复制整个 Skill 目录。

## 卸载与常见问题

卸载只移除安装目录中的 `minimal-product-website/`。先确认实际绝对路径和需要保留的定制内容，不删除整个 `skills/` 或 `.codex/`。

无法发现 Skill 时检查安装目录层级、UTF-8入口、frontmatter以及工具发现规则。页面缺少样式时检查 CSS 路径与 `.mpw-site`；模块不运行时检查是否通过 HTTP 预览。减少动画或关闭 JavaScript 时，核心内容应保持可见。

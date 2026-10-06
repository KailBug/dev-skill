# dev-skill

按领域组织的开发 Skill 集合。每个 Skill 都包含明确的适用范围、可复用指导和必要资源，可以独立安装、修改和维护。

首个分类是 **website**，首个 Skill 是 **minimal-product-website**：以支付宝 AI 付官网的设计语言为参考，生成白底黑字、大留白、圆角卡片、胶囊按钮与克制动效的响应式网站。品牌、内容和页面结构按业务适配。

## Skill 目录

| 分类 | Skill | 用途 | 状态 |
| --- | --- | --- | --- |
| [website](skills/website/README.md) | [minimal-product-website](skills/website/minimal-product-website/README.md) | 极简科技风的品牌官网、产品网站、服务页与活动落地页 | 初始版本；结构与资源行为已验证 |

机器可读索引位于 [skills.json](skills.json)。分类只负责组织文件；实际安装单位是包含 `SKILL.md` 的具体 Skill 目录。

## 快速使用

1. 按 [安装说明](docs/installation.md) 将具体 Skill 目录安装到支持此格式的工具中。Codex 默认路径为 `~/.codex/skills/`，设置了 `CODEX_HOME` 时使用其 `skills/` 子目录。
2. 在请求中调用 `$minimal-product-website`，说明你的品牌、受众、主要行动和已有技术栈。

```text
使用 $minimal-product-website，为中文笔记工具生成官网。
面向大学生，品牌色用绿色，主要行动是免费试用。
不需要终端卡、合作伙伴 logo 或业务指标。
```

只使用 Skill 时，无需安装此仓库的 Python、Node.js 或浏览器测试依赖。已有项目可以仅引用指导并将 CSS 变量映射到自己的设计系统；基础 CSS/JS 是可选资源。

## 仓库结构

```text
skills/website/minimal-product-website/  # 可独立安装的 Skill
skills.json                             # Skill 索引
docs/installation.md                    # 安装、更新、卸载
docs/skill-spec.md                      # 分类与 Skill 结构规范
docs/maintenance.md                     # 来源维护、验证、版本和回滚
scripts/validate_skills.py               # 结构、元信息及内部链接校验
tests/                                  # 校验器与浏览器资源测试
.github/                                # CI、Issue 和 PR 模板
```

## 本地维护与检查

维护环境：Python 3.10+、Node.js 22+、npm；首次运行浏览器测试需安装 Chromium。

```sh
python -m pip install -r requirements-dev.txt
npm ci
npx playwright install chromium
python scripts/validate_skills.py
python -m unittest discover -s tests -p "test_*.py"
npm run check:assets
git diff --check
```

GitHub Actions 在推送到 `main` 和指向 `main` 的 Pull Request 时运行结构校验、校验器测试及 Chromium 资源测试。检查涵盖桌面/手机溢出、触摸目标、键盘焦点、滚动入场、减少动画、关闭 JavaScript 和资源清理；它不能保证每个生成的网站都满足业务目标。生成结果仍需针对真实内容检查。

## 文档与贡献

- [安装、更新与卸载](docs/installation.md)
- [贡献指南](CONTRIBUTING.md)
- [Skill 结构规范](docs/skill-spec.md)
- [维护手册](docs/maintenance.md)
- [版本记录](CHANGELOG.md)
- [安全反馈](SECURITY.md)

新增 Skill 时更新目录、索引与版本记录，再提交带用途和验证结果的 PR。维护流程和测试依赖不应成为普通使用 Skill 的额外要求。

## 许可证与来源

本仓库原创代码与说明文档采用 [MIT License](LICENSE)。参考网站的商标、原始文案、第三方 logo、专有字体和插画不随本仓库分发，MIT 不授予这些外部资产的使用权。

参考页面的观察日期、资源链接和实测值见 [来源记录](skills/website/minimal-product-website/references/source-observations.md)。它们是设计快照；通用化参数与改进建议另行标明。仓库与支付宝无隶属或背书关系。

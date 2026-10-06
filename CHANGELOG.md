# 版本记录

仓库使用语义版本；条目注明受影响 Skill。版本号由 [VERSION](VERSION) 保存，发布规则见 [维护手册](docs/maintenance.md)。

## Unreleased

暂无待发布变更。

## 0.1.1 — 2026-10-06

### 修复

- 仓库 CI：为 Python pip 缓存指定 `requirements-dev.txt`，修复默认依赖文件匹配失败而提前停止的问题；平台检查各自完成，不互相取消。
- `website/minimal-product-website` 的生成指导与资源行为保持兼容。

## 0.1.0 — 2026-10-06

### 新增

- `website/minimal-product-website`：首个网站生成 Skill，包含字体、配色、布局、圆角、组件、动效、响应式规则、来源记录和可改造 CSS/JS。
- 分类索引、安装说明、贡献指南、维护手册、结构规范与安全反馈说明。
- MIT 许可证、Git/编辑器基础配置、Issue 与 PR 模板。
- 独立结构校验器及其单元测试，Chromium 资源行为测试和 GitHub Actions 工作流。

### 验证范围

- 设计资源在1440、1024、390和320px视口的布局检查。
- 入场、键盘焦点、减少动画、无 JavaScript、隐藏控件与清理行为。
- 一个摄影工作室场景的独立试用，验证非支付业务适配。试用素材与临时文件不作为 Skill 资产发布。

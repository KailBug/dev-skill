# minimal-product-website

生成或重设计极简科技风的品牌官网、产品网站、服务页与活动落地页。设计语言参考支付宝 AI 付官网，业务内容、品牌和布局按需求调整。

入口是 [SKILL.md](SKILL.md)。主要设计参数见 [设计规范](references/design-system.md)；参考网页的观察日期和实测值见 [来源记录](references/source-observations.md)。

## 能力与边界

- 系统中文字体、字号层级、黑白灰配色与可替换的强调色。
- 页面宽度、留白、分级圆角、卡片、胶囊 CTA 与响应式组合。
- 克制的滚动入场及可选展示动效，键盘与减少动画适配。
- 可改造的 [CSS 起点](assets/design-system.css) 与 [入场模块](assets/reveal.js)。

Skill 提供生成指导和可选资源，具体网站仍由代理结合业务实现。它不包含完整业务后台、支付接口、复制/轮播控制器，也不要求复制原站整页结构。来源品牌、字体文件、logo、插画和业务数据不随 Skill 分发。

## 使用示例

```text
使用 $minimal-product-website，为自然光摄影工作室生成官网。
保留真实作品照片，品牌色用绿色，主要行动是预约拍摄。
包含作品、服务与 FAQ，不需要终端、合作品牌带或业务指标。
```

安装时复制本目录本身，方法见 [安装说明](../../../docs/installation.md)。无需安装仓库维护工具。使用 CSS/JS 时保留其作用域与清理接口，通过 HTTP 预览模块脚本。

修改或新增内容遵循 [贡献指南](../../../CONTRIBUTING.md)；版本由仓库 [CHANGELOG.md](../../../CHANGELOG.md) 统一记录。

本目录携带 [MIT License](LICENSE)，独立安装时一并保留。复制 CSS/JS 到生成项目时保留文件版权标识，并携带许可全文，例如放到项目第三方声明文件中。

# Skill 结构规范

分类用于仓库组织，Skill 目录是可独立复制、安装和维护的单元。

```text
skills/
  website/
    minimal-product-website/
      SKILL.md
      agents/openai.yaml       # 可选：界面信息与调用策略
      references/              # 可选：按任务读取的细节
      assets/                  # 可选：复制或改造到产物的资源
      scripts/                 # 可选：确有用途的执行脚本
```

安装时复制 `minimal-product-website/` 本身，不把 `website/` 整个分类作为一个 Skill。新增分类无需建立空模板或改变现有 Skill 的安装方式。

## 名称与入口

分类名和 Skill 名使用小写字母、数字与连字符；Skill 名不超过 64 个字符，在仓库内唯一。目录名、frontmatter 的 `name` 和 `$skill-name` 调用名称一致。

`SKILL.md` 使用 UTF-8 编码，并以 YAML frontmatter 开始：

```yaml
---
name: minimal-product-website
description: "生成或重设计极简科技风的品牌官网、产品网站与落地页；适用于用户要求这一视觉风格或调用本 Skill 的任务。"
---
```

`name`、`description` 是必需字段。描述负责发现与触发，应准确说明做什么以及何时使用，避免“适用于所有开发任务”等泛化表述。保留有实际用途且被目标环境支持的可选字段；不要添加用于替代仓库版本管理的必需自定义字段。

## 内容与资源

入口正文保留目标、关键决策和真实约束。复杂参数、特定模式和来源记录放到 `references/`，并在相关步骤说明何时阅读。不要默认要求读取全部参考资料。可复用输出素材放到 `assets/`；重复且适合确定性处理的逻辑才放到 `scripts/`。

内部链接以当前文档为基准使用相对路径，例如 `[设计参数](references/design-system.md)`。资源名称应稳定，移动或删除文件前搜索调用方并同步修正。不得引用个人机器的绝对路径、未提交的文件或密钥。外部来源使用完整 URL，并记录观察日期和来源所支持的结论。

Skill 应在其目录内自包含。仅当任务确实需要且目标环境可用时，才引用另一个 Skill 或指定工具。提供现有技术栈的适配或替代方式，不因为偏好而强制所有项目安装相同框架、动画库或全部维护依赖。

## 调用策略与边界

`agents/openai.yaml` 可提供简明的 `display_name`、`short_description` 和 `default_prompt`。默认保留自动发现和隐式调用；只有用户明确要求时才设置显式调用策略。更新已有文件时保留无关的策略和依赖字段。

Skill 不扩大用户的任务范围或授权。发布、付费、发送信息等行为遵循当前会话的授权与工具规则；不要在普通生成流程里加入假设性的审批清单。用户明确选择的内容、品牌、技术栈和交付位置优先于 Skill 默认值。

## 检查要求

在仓库根目录执行：

```sh
python scripts/validate_skills.py
npm run check:assets
git diff --check
```

根据改动再运行对应的脚本、构建或代表性行为检查。验证应覆盖可观察的效果，不用固定措辞或标题匹配代替行为。没有运行的验证不能写成通过。

所有版本变更记录在仓库 [CHANGELOG.md](../CHANGELOG.md)，条目注明相关分类和 Skill；不要在每个 Skill 内复制安装指南或仓库维护文档。

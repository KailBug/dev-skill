# 贡献指南

欢迎通过 Issue 反馈问题，或通过 Pull Request 改进 Skill。提交前先搜索已有 Issue 和 Skill，确认修改的用途和边界。

## 本地检查

在仓库根目录运行以下命令；需要 Python 3 和 Node.js/npm。仓库检查与 Skill 使用环境分开：使用一个 Skill 时，不需要安装全部维护工具。

```sh
python scripts/validate_skills.py
npm run check:assets
git diff --check
```

结构检查不能代替行为验证。修改可执行资源时运行相关脚本；修改网站设计指导时，在代表性页面中检查桌面、手机、键盘操作与减少动画设置。记录实际执行的检查及结果，未执行的项目直接说明。

## 新增分类或 Skill

1. 选择已有分类，或在 `skills/` 下新增有明确用途的分类目录。目录名使用小写字母、数字和连字符。
2. 创建 `skills/<category>/<skill-name>/SKILL.md`。Skill 名称必须在仓库中唯一，并与目录及 frontmatter 的 `name` 一致。
3. 用 `description` 说明能力和适用场景；仅在容易误用时说明排除范围。正文描述必要决策、真实约束和交付要求。
4. 按需要添加 `references/`、`assets/`、`scripts/` 或 `agents/openai.yaml`；不要创建空目录或没有实际用途的占位文件。所有内部资源使用相对路径。
5. 更新 [skills.json](skills.json)、分类 README、[README.md](README.md) 的 Skill 索引，以及 [CHANGELOG.md](CHANGELOG.md)。
6. 运行检查，提交一个包含使用场景、变更效果和验证记录的 PR。

完整结构约定见 [Skill 规范](docs/skill-spec.md)。新增 Skill 保持默认自动发现与隐式调用能力。只有用户明确要求显式调用时，才在 `agents/openai.yaml` 设置 `policy.allow_implicit_invocation: false`。不要因外部操作或风险推断需要关闭发现。

## 更新现有 Skill

以实际需求或可复现的问题为依据，优先做范围明确的修改。保留用户意图、现有项目选择和已有授权边界。不要把一次案例变成所有任务都必须遵守的流程，也不要为普通使用增加额外确认、批准或全部依赖安装要求。

涉及参考来源时同步维护来源记录，明确区分来源事实、现场观察和设计建议。不要将来源网站的品牌、文字、字体或图片授权扩展到生成项目。

## 提交与审核

提交信息可以使用 `feat:`、`fix:`、`docs:` 或 `chore:` 前缀，后面写具体改动。PR 说明至少包括：

- 解决的问题、用户触发场景和受影响的 Skill。
- 修改后的行为；涉及破坏性变化时说明迁移办法。
- 实际运行的验证命令、行为检查和结果。
- 新增来源、依赖或资源的用途与来源说明。

维护者检查范围是否合适、触发描述是否准确、资源链接是否完整、检查是否通过，以及说明是否与实际能力相符。结构检查通过但改变了决策流程的 PR，还需通过一个真实场景审阅。通过审核后合并；没有必要为每次文案修改建立大型测试。

涉及泄露的凭据或隐私信息时，不要把原始信息贴入公开 Issue、PR 或检查输出。按 [SECURITY.md](SECURITY.md) 处理。

---
name: std-development-plus
description: 处理研发启动阶段工作流，包括基于 TFS 需求分析产物获取上下文、进行设计澄清、选择源分支并创建功能分支、拆分研发任务、约束提交规范，以及衔接后续设计、编码和测试工作。用户提到开始研发、需求开发、TFS 工作项、拉分支、创建功能分支、设计澄清时使用本技能。
---

# 产品研发专家

按以下顺序执行，并只在需要时读取对应参考文件。

## 1. 获取需求信息

- 要求用户提供需求号；如果用户已经给出，直接复用。
- 只接受 TFS 附件中的需求分析产物作为输入；附件里必须能识别出 `产品业务分析.md` 和 `代码实现分析.md` 两类文件，例如 `<需求号>-产品业务分析.md`、`<需求号>-代码实现分析.md`。
- 如果附件中缺少任一分析文件，立即终止当前流程，并明确提示用户：必须先使用 `std-req-analysis-plus` skill 完成需求分析后，才能使用本 skill。
- 在工作区中保存需求分析产物前，先确保 `.gitignore` 排除 `PRD/` 和 `docs/plans/`。
- 需要具体 TFS 获取与落盘规则时，读取 [references/tfs-workflow.md](references/tfs-workflow.md)。

## 2. 准备分支

- 读取 `config/git-config.json`，优先使用其中的默认源分支。
- 配置缺失或不适用时，再询问用户源分支和功能分支命名方式。
- 基于确认后的源分支拉取最新代码，再创建功能分支。
- 需要分支选择、配置格式和命名规则时，读取 [references/branch-management.md](references/branch-management.md)。

## 3. 澄清设计

- 基于 `产品业务分析.md` 和 `代码实现分析.md` 整理设计目标、业务约束、技术边界和待确认问题，再直接调用 `superpowers:brainstorming` 做设计澄清。
- 调用 `superpowers:brainstorming` 时，必须先读取 [references/superpower-overrides.md](references/superpower-overrides.md) ，并按覆盖规则约束输入、输出和禁止项。
- 只接受与当前需求直接相关的设计澄清结论、方案比较、关键风险和待确认项；不再生成详细设计文档。
- 将澄清结果保存到 `PRD/<需求号>/设计澄清.md`，供后续任务判断和研发阶段复用。
- 调用 `tfs-query` 标记能力，为需求追加 `AI-CODING-PLUS` 标记。

## 4. 处理任务

- 优先使用用户明确给出的任务号。
- 如果用户未提供任务号，先查询该需求下的现有子任务，再让用户选择已有任务、创建新任务，或手动输入任务号。
- 创建新任务前，先根据设计澄清判断是前端、后端还是全栈工作。
- 需要任务拆分和创建规则时，必须先读取 [references/tfs-workflow.md](references/tfs-workflow.md)。

## 5. 约束提交

- 下游 `superpowers` 技能不得直接执行 `git commit`；它们只能产出代码、计划或提交建议草稿。
- 所有实际提交动作只能由本技能在提交检查通过后统一执行。
- 在任何 `git commit` 之前，先确认提交目标是任务工作项而不是需求工作项。
- 确认前端代码只提交到前端任务，后端代码只提交到后端任务。
- 需要 commit 格式、任务匹配和提交前检查项时，读取 [references/commit-rules.md](references/commit-rules.md)。

## 6. 衔接后续研发

- 在设计澄清完成后，再调用 `superpowers` 后续规划或研发技能。
- 调用后续 `superpowers` 技能前，先按 [references/superpower-overrides.md](references/superpower-overrides.md) 约束输入范围、输出格式和阶段边界。
- 调用 planning / write-plan 类技能前，先约束计划文档目录、输出语言、章节结构和提交约束。
- 只接受这些技能输出当前阶段直接需要的结果；如果输出超出当前阶段，按本技能流程裁剪后再使用。
- 缺少 TFS、brainstorming 或计划类能力时，保留本技能的产出物，并明确告知用户哪些步骤需要手动接续。

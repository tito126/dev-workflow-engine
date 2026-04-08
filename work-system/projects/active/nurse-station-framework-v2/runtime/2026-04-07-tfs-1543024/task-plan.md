# TFS 1543024 - task-plan

## Goal
在 `E:\winning-code\frontend\webui-next` 的 `winning-webui-inpatient-bedcard` 模块内，为住院护士站床位卡“已出院查询方案”增加日期筛选能力：日期类型下拉（出区日期 / 出院结算日期）+ 日期范围控件，并接入正确查询参数。

## Current phase
execution dispatch

## Stage breakdown
1. narrow locate
2. scoped implementation
3. requirement-fit review
4. verification
5. controller synthesis

## Decisions
- 本次作为“护士站框架 v2 的中任务验证样本”正式重跑
- 不重复 wrapper 排障
- 不重复历史分析
- 仅聚焦 `winning-webui-inpatient-bedcard` 及其直接相关调用链
- 若 requirement-fit 与代码现实不一致，先停下汇报，不自行漂移
- 执行 carrier: wrapper opencode
- 模型: glm-5

## Hard constraints
- 先做窄范围 locate，再实现
- 不扩展到其他查询方案
- 不顺手重构搜索区
- 输出必须包含：
  - locate findings
  - likely files
  - modified files
  - parameter mapping / query integration notes
  - acceptance checklist result
  - remaining risks

## Done definition
- 已完成窄范围 locate
- 已在目标模块完成最小实现
- 已输出结构化结果并覆盖 acceptance checkpoints
- 已明确剩余风险与未验证点

## Error log
- none

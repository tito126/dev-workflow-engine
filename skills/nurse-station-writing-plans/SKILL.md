---
name: nurse-station-writing-plans
description: 当一个护士站任务已经完成 intake，需要被转成可执行计划，并明确文件、agent 角色、验证步骤和交接边界时使用。触发场景包括 MVP 执行准备、真实需求拆解、缺陷修复实现规划，以及护士站研发中的可复用工作流资产建设。
---

# 护士站执行计划编写

把一个已澄清的护士站事项，转成无需执行者反复猜题、也无需 controller 多次转述的可执行计划。

## 目标

本阶段的目标不是“列一个 checklist”，而是把前序 requirement summary 压缩成后续阶段可以反复复用的执行底稿。

一份好的计划应同时解决：
- 后续执行器不需要再从聊天里回捞大量上下文
- controller 不需要在 locator / implementer / verifier 之间反复口头转述
- 同一个中任务跨多轮推进时，计划仍能充当稳定锚点
- skill 顺序能够自然串起来，而不是每一段都像重新开题

## 计划要求

每份计划都必须包含：
1. 目标与预期行为
2. 范围内与范围外边界
3. 仓库 / 模块 / 可能文件目标
4. Agent 分工
   - controller
   - locator / analyst
   - implementer
   - verifier / reviewer
5. 执行顺序
6. 验证步骤
7. 风险 / 回滚顾虑
8. 编码前必须确认的事项
9. 应使用哪种执行载体（`direct edit` / `ACP opencode` / `exec opencode` / other）
10. 后续阶段共享输入摘要
11. 哪些内容要沉淀为 findings / progress / verification evidence
12. 对于 SQL / 性能优化任务，代码分析后必须回问用户确认的业务 / 语义 / 性能问题
13. 本轮允许改动层级 / 禁止改动层级
14. 验收方式与证据预期（代码完成 / 需求完成 / 效果已验证分别靠什么判定）

## 规则

- 把本技能视为护士站默认流程中的第二阶段，位于 `nurse-station-brainstorming` 之后。
- 除非用户明确说明该任务已过 intake，或前序 brainstorming checkpoint 已确认就绪，否则不要把本技能作为入口阶段。
- 优先拆成小而可独立评审的任务。
- 如果任务是 `light` 或 `medium`，优先用最小计划，不要强行套重型多角色结构。
- 已知时要明确写出文件和模块名。
- 如果文件目标未知，就在计划里加入专门的定位任务，再进入实现。
- 如果任务属于 SQL / 性能优化，计划中必须显式写出“分析后向用户确认”的阻断点；没有用户确认，不进入 implementer。
- 不要把不确定性藏在计划里，要显式标出来。
- 当 controller 可以给出更尖锐上下文时，不要让 implementer 自己“去代码库里摸索”。
- 默认把本计划视为后续阶段共享底稿，而不是一次性聊天输出。
- 如果已经存在 runtime task，就把计划绑定到该 runtime path，而不是只留作聊天输出。
- 如果外部执行会使用 `opencode`，就要显式决定是 `ACP opencode` 还是裸 `exec opencode`。
- 一旦需求边界、结果语义、是否分页、是否允许改系统策略、是否涉及第三方规则等关键口径发生变化，必须重写 success anchors 及受影响的计划段落，不要只在聊天里补一嘴。
- 默认路径：`ACP opencode`。
- 当前 Windows 环境下，只有在 `2026-04-08` 记录的本地 ACP 手动补丁仍然存在时，才把 `ACP opencode` 视为正式可用。
- 如果 ACP 不可用、不健康，或升级后补丁被覆盖，则降级为裸 `exec opencode`。
- 不要把基于 wrapper 的 `start-opencode-task.ps1` 当成标准路径或降级路径，除非当前是在明确排查它本身。

## 推荐计划结构

### 计划头
- Item:
- Task level:
- Execution carrier:
- Goal:
- Repo:
- Module:
- In scope:
- Out of scope:
- Allowed change layers:
- Shared context summary:
- Success anchors:
- Acceptance method:
- Evidence expectations:
- Runtime path:
- Phases to mirror in later artifacts:
- Expected findings capture:
- Expected progress updates:
- Pre-code confirmation items:
- User confirmation gate after analysis:
- If scope changes later, rewrite these sections first:

### Agent 分工
- Controller:
- Locator / Analyst:
- Implementer:
- Verifier / Reviewer:

### 任务
- Task 1:
  - Purpose:
  - Inputs:
  - Likely files:
  - Output:
  - Should persist as:
  - Verification:
- Task 2:
  - Purpose:
  - Inputs:
  - Likely files:
  - Output:
  - Should persist as:
  - Verification:

### 风险
-

### 执行就绪度
- Can enter coding now: yes/no
- Missing prerequisite:

## SQL / 性能优化任务补充要求

如果任务属于 SQL / 性能优化，计划里至少要写明：
- 本轮允许不允许改系统策略
- 本轮允许不允许改变查询语义
- 结果一致性、性能收益、实现侵入性三者的优先级
- 验收方式是代码证据、真实样本、SQL plan、压测、日志对比中的哪些
- 如果只能拿到代码证据，后续谁来补效果验证、在什么环境补

## 对 ACP 的特殊用法

当任务走 `ACP opencode` 时，计划不应只写“让 opencode 做这个”，而应尽量把以下内容一次性给全：
- 任务目标
- 仓库路径
- 范围边界
- 可能文件或模块
- 当前阶段
- 结构化输出要求
- 停止条件
- 后续结果要如何被主控吸收

目标是把“主控重复转述”降到最低。

## 集成关系

完成计划后：
- 默认把计划视为后续 `subagent-execution`、`implementer`、`verification` 的共享输入。
- 如果任务有 runtime path，就把计划视为该任务的执行底稿，而不是只留在聊天里。
- 如果任务会使用 `opencode`，优先走 `ACP opencode`。
- 如果 ACP 被阻塞，或 Windows 本地补丁失效 / 被覆盖，则降级为裸 `exec opencode`。
- 不要把标准护士站执行路由到基于 wrapper 的启动方式（`start-opencode-task.ps1`）。
- 当需要专门执行角色时，使用 `nurse-station-subagent-execution`。
- 在宣称完成前，用 `nurse-station-verification` 先定义并执行验收检查。
- 完整的阶段顺序和产物落地约定，见 `nurse-station-orchestrator`。

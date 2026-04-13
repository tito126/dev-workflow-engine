---
name: nurse-station-subagent-execution
description: 当一个已澄清且已完成计划的护士站任务，需要从主控会话派发给 locator、implementer、verifier 等专门执行角色时使用。触发场景包括让 executor / opencode / codex 在特定仓库内做分析或实现，同时保持主会话只承担 controller 职责。
---

# 护士站子执行器派发

本技能定义主控会话如何派发专门化执行工作，同时避免主控自己吞掉实现工作，或在多个阶段之间反复做人肉转发器。

## 核心原则

主会话是 controller，不是全能执行者。

当 ACP 已可用时，应把它当成减少上下文重复灌输、减少转述折损、提升中任务连续性的主要执行底座，而不是只把它当成“另一个能跑命令的通道”。

## 顺序规则

把本技能视为护士站流程里的下游执行阶段，而不是入口阶段。

默认顺序：
`nurse-station-brainstorming -> nurse-station-writing-plans -> nurse-station-subagent-execution`

在没有经过显式 brainstorming checkpoint 和 planning step 确认就绪前，不要派发子执行任务。

只有当用户明确说明该任务已经过了 intake 或 planning 时，才允许绕过这条顺序。

## 角色

### Controller
负责：
- 需求 intake
- 就绪度判断
- 任务拆解
- 派发措辞
- 收集输出
- 决定下一跳
- 最终综合收口

### Locator / Analyst
负责：
- 查找代码入口点
- 追踪配置 / schema / API 映射
- 识别可能文件和风险点
- 在未被明确要求前不修改代码
- 尽量输出可直接供 implementer 复用的 findings，而不是聊天散点

### Implementer
负责：
- 做有边界的代码修改
- 运行本地定向检查
- 报告已改内容和仍然不确定的部分
- 尽量输出可直接供 verification / review 使用的结构化结果

### Verifier / Reviewer
负责：
- 检查行为是否符合需求
- 检查重复条件 / 回归 / 缺口
- 不轻信 implementer 的自报完成

## 派发规则

- 直接传递任务文本，不要指望执行器自己重新发现全部上下文。
- 尽量一次性传足可稳定复用的上下文，不要依赖后续补锅式追加说明。
- 显式传递仓库路径。
- 在派发前先确认 `work-system/config/nurse-station-repo-routing.yaml` 已存在且 `status=ready`；如果仍是 `draft`，不得派发新的多仓分析 / 实现任务。
- 在需要时显式传递模型选择。
- 若已知模块和可能文件提示，也一并传入。
- 如果输入里已经包含产品 / 需求给出的正式文案，要显式告诉子执行器：该文案是否受保护、是否允许改写；默认按“不允许改写”处理。
- 若任务属于复杂且受持续跟踪的流，显式传递 shared context summary / success anchors / current stage。
- 若已知当前阶段，也显式传递当前阶段。
- 说明应沉淀哪些输出，例如 findings、implementation result、verification evidence。
- 要求结构化输出。
- 保持每个执行器聚焦于单一角色。
- 如果使用 `opencode`，**必须优先以 `ACP opencode` 作为标准路径**。
- 当前 Windows 环境下，只有在 `2026-04-08` 记录的本地 ACP 手动补丁仍然存在时，才把 `ACP opencode` 视为正式可用。
- 如果 ACP 不可用、不健康，或升级后补丁被覆盖，才降级到裸 `exec opencode`。
- 不要把基于 wrapper 的 `start-opencode-task.ps1` 当成护士站执行的默认或降级路径。

## 推荐派发载荷

每个子任务都应说明：
- 角色
- 目标
- 仓库路径
- 任务级别
- 执行载体（`direct edit` / `ACP opencode` / `exec opencode` / other）
- Shared context summary
- Success anchors
- 模块 / 范围
- runtime path 或持续跟踪标识
- 当前阶段
- 应沉淀的输出类型
- 硬约束
- 预期输出结构
- 停止条件

## ACP 优先时的特别要求

当选择 `ACP opencode` 时，优先利用它的持续会话能力减少重复喂上下文：
- 同一个中任务的后续轮次，优先在同一执行上下文上追加，而不是每次从零重讲
- controller 的价值应更多体现在阶段判断和任务切分，而不是反复复述全部需求
- 若已有 planning 产物，优先把计划摘要直接作为派发输入
- 若已有 findings，优先把 findings 当成 implementer 和 verifier 的共享输入

## 评审顺序

对于实现类工作，使用以下顺序：
1. 如有需要，先 locator / analyst
2. implementer
3. verifier / reviewer
4. controller 综合收口

## 反模式

不要：
- 默认让 controller 自己做完所有代码分析和实现
- 发送“分析整个仓库”这类过宽 prompt
- 在范围仍模糊时，把定位和编码合成一个任务
- 仅凭 implementer 输出就宣告完成
- 把基于 wrapper 的启动方式当成护士站 `opencode` 的标准路径
- 把 ACP 只当成一次性远程命令通道，而不利用其减少上下文重复输入的价值

## 集成关系

在 `nurse-station-writing-plans` 之后使用。
对于复杂任务，优先派发带显式共享输入的工作，而不是只依赖聊天上下文。
当选择 `opencode` 时，**必须优先用 `ACP opencode`**。
若 ACP 不可用、不健康、或本地补丁被覆盖，才降级到裸 `exec opencode`。
完整的阶段顺序、派发规则和产物落地约定，见 `nurse-station-orchestrator`。
在最终完成前，应自然与 `nurse-station-verification` 配合。
完整的阶段顺序、派发规则和产物落地约定，见 `nurse-station-orchestrator`。

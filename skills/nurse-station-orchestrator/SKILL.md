---
name: nurse-station-orchestrator
description: 护士站任务统一入口。当收到任何护士站相关需求、缺陷、优化项或治理项时，优先读取本文件确定走哪条流程线、经过哪些阶段、产物落到哪里。不要跳过本文件直接进入某个具体 skill。
---

# 护士站任务入口

当收到护士站相关任务时，先读本文件。它负责：
1. 判断任务级别
2. 选定执行路径
3. 明确经过哪些阶段
4. 约定中间产物落到哪里

## 全局流程图

```
需求进入
  │
  ▼
┌─────────────────────┐
│ brainstorming       │  ← 所有任务必经
│ 需求澄清 + 任务分级  │
└────────┬────────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
  light     medium     heavy
    │         │          │
    ▼         ▼          ▼
 direct    writing-    writing-
 edit      plans       plans
    │         │          │
    ▼         ▼          ▼
 quick    locator?     locator
 verify    (按需)        │
    │         │          ▼
    ▼         ▼       implementer
  done    implementer     │
              │          ▼
              ▼       verification
          verification     │
              │          ▼
              ▼       review-gate
          review-gate     │
              │          ▼
              ▼       retrospective
             done        │
                        ▼
                       done
```

## 三条路径

### light 路径
适用：小范围、本地化、目标清晰、不需要外部执行器

```
brainstorming（简短检查点，确认足够清楚）
  → direct edit
  → 简短验证
  → done
```

不需要 runtime，不需要 plan，不需要外部执行器。
重点是 brainstorming 确认"这确实够轻"，而不是直接跳过。

### medium 路径
适用：边界可控，需要定位 / 窄范围实现 / 明确验证，大概率用 ACP opencode

```
brainstorming
  → writing-plans
  → locator（按需插入）
  → implementer（优先 ACP opencode）
  → verification
  → review-gate
  → done
```

### heavy 路径
适用：多阶段、高不确定性、跨仓库、需要 runtime 跟踪

```
brainstorming
  → writing-plans
  → locator
  → implementer（可分多轮）
  → verification
  → review-gate
  → retrospective
  → done
```

## 阶段说明

### brainstorming（必经）
- 产出：requirement summary + success anchors + 任务级别 + 推荐路径
- 不允许跳过，除非用户显式说"已过 intake"
- 必须显式检查方案是否依赖第三方 / 外部团队 / 外部系统配合，以及该依赖是否已明确到可执行
- 如果依赖方一旦配合就能直接规避本需求，则要先重判“该需求是否仍成立”，不能直接流入 planning / implementer
- 如果任务不够清楚，在这里停下追问

### writing-plans
- 产出：共享底稿（plan），含 agent 分工、执行载体、验证步骤
- medium / heavy 必经
- plan 是后续所有阶段的共享输入

### locator（按需插入）
- **何时需要**：planning 阶段无法确定具体文件，需要先做代码定位
- **何时跳过**：planning 阶段已经知道改哪些文件
- 插入位置：writing-plans 之后、implementer 之前
- 产出：findings（供 implementer 直接复用）
- 对于 medium 任务，locator 和 implementer 可以合并成一个 ACP session 里连续推进

### implementer
- 执行载体选择：
  - 优先 `ACP opencode`（当前环境依赖 2026-04-08 Windows 手动补丁）
  - ACP 不可用时降级 `exec opencode`
  - 禁止 wrapper 作为标准路径
- 产出：结构化实现报告（供 verification 和 review-gate 直接引用）

### verification
- 对照 planning 阶段的 success anchors 逐条核对
- 产出：验证结论 + 验证证据摘要
- 如果验收锚点缺失，退回 brainstorming 或 planning

### review-gate
- 三道闸门按顺序执行：编码前需求匹配 → 实现后需求匹配 → 代码质量
- 产出：评审结论 + 可沉淀经验
- 前序闸门不通过时，不启动后续闸门

### retrospective（heavy 任务收尾）
- 评估上下文流转效率：每段衔接是否做到了少重复喂、少转述
- 产出：框架改进建议 + 资产决策

## 产物落地约定

### 目录结构
护士站任务的持久化产物统一落到：
```
work-system/deliverables/nurse-station/{task-id}/
```

其中 `{task-id}` 在 brainstorming 阶段确定，格式建议：`{tfs-id 或简短标识}-{日期}`

### 标准文件

| 阶段 | 文件 | 内容 | 是否必须 |
|------|------|------|---------|
| brainstorming | `requirement-summary.md` | 需求澄清结果、success anchors、任务级别 | medium/heavy 必须 |
| writing-plans | `plan.md` | 执行计划、agent 分工、验证步骤 | medium/heavy 必须 |
| locator | `findings.md` | 代码定位结果、入口文件、风险 | 有 locator 阶段时必须 |
| implementer | `implementation-result.md` | 实现报告、已改文件、不确定性 | medium/heavy 必须 |
| verification | `verification-evidence.md` | 验证结论、未验证点 | medium/heavy 必须 |
| review-gate | `review-conclusion.md` | 评审结论、可沉淀经验 | medium/heavy 建议 |

### 产物流转规则
- 每个阶段的输入优先从前序阶段的落地文件中读取，而不是从聊天里回捞
- brainstorming 的 `requirement-summary.md` → planning 的输入
- planning 的 `plan.md` → implementer 的输入
- locator 的 `findings.md` → implementer 的输入（若存在）
- implementer 的 `implementation-result.md` → verification 的输入
- verification 的 `verification-evidence.md` → review-gate 的输入
- 若后续阶段发现关键外部依赖在 intake 中未被识别，或需求成立前提发生变化，必须回退到 brainstorming / planning 重写，不允许带着旧前提继续收口

### light 任务例外
light 任务不需要创建 deliverables 目录，产物直接在聊天中流转即可。

## subagent-execution 的定位

`nurse-station-subagent-execution` 不是流程中的一个"阶段"，而是 **派发层**：
- 它定义了 controller 如何把工作派给外部执行器（ACP opencode / exec opencode）
- 它不与 implementer 竞争，而是 complement：implementer 定义"做什么"，subagent-execution 定义"怎么派出去"
- 对于 medium 任务：controller 用 subagent-execution 的派发规则，把 implementer 角色的工作交给 ACP opencode
- 对于 light 任务：controller 自己做 direct edit，不需要 subagent-execution

## 执行载体选择规则

| 条件 | 载体 |
|------|------|
| 任务简单、改动量小、不需要外部工具 | direct edit |
| 需要代码定位 / 分析 / 实现，ACP 可用 | ACP opencode |
| 需要代码定位 / 分析 / 实现，ACP 不可用 | exec opencode |
| 用户明确指定用某个执行器 | 用户指定 |

ACP 可用性检查：
- 当前 Windows 环境依赖 2026-04-08 的本地手动补丁
- 若 OpenClaw 升级后 ACP 再次报 `backend unavailable`，先检查补丁是否被覆盖

## 反模式

不要：
- 收到护士站任务就直接跳到 implementer，跳过 brainstorming
- 每个阶段都从零重讲需求，而不复用前序阶段的产物
- controller 在 locator / implementer / verifier 之间做人肉转发器
- 把 ACP 只当一次性命令通道，而不利用其减少上下文重复的价值
- 把 light 任务强行套进 medium/heavy 流程
- 把 medium 任务升级成 heavy 流程
- 让 implementer 同时承担 locator 的职责
- 在关键外部依赖未明确时，把“依赖方会配合”当成默认成立前提直接推进实现

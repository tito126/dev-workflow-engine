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

## YAML 前置配置（强制）

在任何护士站任务进入仓库分析、定位、实现前，先检查并读取工作区文件：
`work-system/config/nurse-station-repo-routing.yaml`

如果该文件不存在：
1. 由 `orchestrator` 自动创建一个 `draft` 模板
2. 模板来源固定为：`skills/nurse-station-orchestrator/references/nurse-station-repo-routing.template.yaml`
3. 创建完成后，**立即停止后续阶段**
4. 明确要求用户先维护 YAML，再继续

强制规则：
1. 任何护士站代码任务在进入 planning / locator / implementer 前，都必须先检查上面的 YAML。
2. 如果用户已经明确给了仓库路径，可以把用户路径作为候选首扫根参考，但这不等于可以绕过 YAML。
3. 如果 YAML 不存在、`status` 不是 `ready`、必填项为空、仍保留占位值、或当前任务无法映射到明确扫描根，则**禁止继续后续阶段**。
4. 此时必须明确要求用户先维护 YAML，而不是依赖记忆、历史经验或临时猜目录继续推进。
5. `status=draft` 只表示“模板已创建”，**不表示可继续执行**；draft 状态下只能停，不能侥幸扩扫、定位、实现或收口。

换句话说：
- **允许**由 orchestrator 自动创建 `draft` 模板
- **允许**把用户给的路径当成 YAML 校验时的候选输入
- **禁止**在 YAML 未配置完成时继续 planning / locator / implementer
- **禁止**把“我记得前端大概在哪”当成正式规则
- **禁止**把 `draft` 错当成“先跑起来再说”

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
  → 定位确认（确认改动目标已从 API 入口或代码调用链独立验证）
  → direct edit
  → 简短验证
  → done
```

不需要运行时跟踪，不需要计划文档，不需要外部执行器。
重点是 brainstorming 确认"这确实够轻"，而不是直接跳过。

**light 路径的定位确认步骤（不可跳过）：**
- 确认改动目标已从 API 入口或代码调用链独立验证
- 如果改动目标仅来自需求分析文档建议，light 路径不适用，应升级到 medium
- 如果任务涉及"给打印/输出 BO 增加字段"，必须确认该 BO 在目标 API 的实际响应链中

### medium 路径
适用：边界可控，需要定位 / 窄范围实现 / 明确验证，大概率用 ACP opencode

```
brainstorming
  → writing-plans
  → locator（按需插入，SQL / 性能优化任务默认必经）
  → 用户确认闸门（SQL / 性能优化任务）
  → implementer（优先 ACP opencode）
  → verification
  → review-gate
  → done
```

### heavy 路径
适用：多阶段、高不确定性、跨仓库、需要运行时跟踪

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
- 产出：需求摘要 + 成功锚点 + 任务级别 + 推荐路径
- 不允许跳过，除非用户显式说"已过前置澄清"
- 必须显式检查方案是否依赖第三方 / 外部团队 / 外部系统配合，以及该依赖是否已明确到可执行
- 如果依赖方一旦配合就能直接规避本需求，则要先重判“该需求是否仍成立”，不能直接流入计划或实现阶段
- 如果任务不够清楚，在这里停下追问
- 只要后续阶段可能涉及代码扫描 / 仓库定位，就必须同时检查 repo-routing YAML 是否已配置完成；未完成时，本阶段就应阻断，而不是把问题留到 locator 才暴露

### writing-plans
- 产出：共享底稿（plan），含角色分工、执行载体、验证步骤
- medium / heavy 必经
- plan 是后续所有阶段的共享输入
- 若关键口径发生变化（如是否分页、是否允许改系统策略、是否展开第三方规则、结果语义优先级变化），必须先回写并重写成功锚点，再继续后续阶段

### locator（按需插入）
- **何时需要**：计划阶段无法确定具体文件，需要先做代码定位
- **SQL / 性能优化例外**：即使计划阶段已大致知道文件，也默认先做 `locator`，补代码证据与待确认问题
- **何时跳过**：计划阶段已经知道改哪些文件
- 插入位置：`writing-plans` 之后、实现阶段之前
- 产出：`findings`（供实现阶段直接复用）
- 对于 medium 任务，`locator` 和实现阶段可以合并成一个 ACP 会话里连续推进

### user-confirmation gate（SQL / 性能优化任务）
- `locator` / 分析 必须先把代码证据、候选问题和待确认语义整理出来
- 主控必须基于这些结果向用户追问现场业务场景、结果语义和性能目标
- 未完成这一闸门前，不进入 implementer

### implementer
- 执行载体选择：
  - 优先 `ACP opencode`（当前环境依赖 2026-04-08 Windows 手动补丁）
  - ACP 不可用时降级 `exec opencode`
  - 禁止 wrapper 作为标准路径
- 产出：结构化实现报告（供 verification 和 review-gate 直接引用）

### verification
- 对照计划阶段的成功锚点逐条核对
- 产出：验证结论 + 验证证据摘要
- 如果验收锚点缺失，退回 `brainstorming` 或计划阶段
- 必须显式区分“代码完成”“需求完成”“效果已验证”三种状态

### review-gate
- 三道闸门按顺序执行：编码前需求匹配 → 实现后需求匹配 → 代码质量
- 产出：评审结论 + 可沉淀经验
- 前序闸门不通过时，不启动后续闸门
- 若当前只有代码证据或业务确认，而没有真实环境 / 真实样本证据，不得把结论写成“效果已验证”

### retrospective（heavy 任务收尾）
- 评估上下文流转效率：每段衔接是否做到了少重复喂、少转述
- 产出：框架改进建议 + 资产决策

## 产物落地约定

### 目录结构
护士站任务的持久化产物统一落到：
```
work-system/deliverables/nurse-station/{task-id}/
```

其中 `{task-id}` 在 `brainstorming` 阶段确定，格式建议：`{tfs-id 或简短标识}-{日期}`

### 标准文件

| 阶段 | 文件 | 内容 | 是否必须 |
|------|------|------|---------|
| brainstorming | `requirement-summary.md` | 需求澄清结果、成功锚点、任务级别 | medium/heavy 必须 |
| writing-plans | `plan.md` | 执行计划、角色分工、验证步骤 | medium/heavy 必须 |
| locator | `findings.md` | 代码定位结果、入口文件、风险 | 有 locator 阶段时必须 |
| implementer | `implementation-result.md` | 实现报告、已改文件、不确定性 | `medium/heavy` 必须 |
| verification | `verification-evidence.md` | 验证结论、未验证点 | medium/heavy 必须 |
| review-gate | `review-conclusion.md` | 评审结论、可沉淀经验 | medium/heavy 建议 |

### 产物流转规则
- 每个阶段的输入优先从前序阶段的落地文件中读取，而不是从聊天里回捞
- `brainstorming` 的 `requirement-summary.md` → 计划阶段输入
- `planning` 的 `plan.md` → 实现阶段输入
- `locator` 的 `findings.md` → 实现阶段输入（若存在）
- `implementer` 的 `implementation-result.md` → `verification` 的输入
- verification 的 `verification-evidence.md` → review-gate 的输入
- 若后续阶段发现关键外部依赖在前置澄清中未被识别，或需求成立前提发生变化，必须回退到 `brainstorming` / 计划阶段重写，不允许带着旧前提继续收口
- 若后续阶段发现 SQL / 性能优化任务缺少现场业务口径或用户确认，也必须回退到 `locator` / 计划阶段补齐，不允许直接带着技术猜测改码
- 若后续阶段发现关键口径变化已使原成功锚点失效，也必须回退到计划阶段重写，不允许只靠聊天补口径继续推进
- 若后续阶段发现 repo-routing YAML 缺失、过期、未配置完成，或本轮实际扩扫根超出了 YAML 白名单，也必须回退，停止继续推进，并要求先维护 YAML

### light 任务例外
light 任务不需要创建完整的 deliverables 目录结构，但必须在聊天中显式产出：
1. 修改文件清单（含完整路径和行号）
2. 修改理由（为什么改这个文件而不是别的）
3. API 调用链确认（如果涉及接口/打印类任务，简述从哪个 API 端点追踪到该文件）

这三项产出用于：
- 后续发现问题时快速定位偏差来源
- 为 review-gate 提供最小可审查证据
- 避免类似"改了但不生效"的问题在 light 任务中反复出现

## subagent-execution 的定位

`nurse-station-subagent-execution` 不是流程中的一个"阶段"，而是 **派发层**：
- 它定义了主控如何把工作派给外部执行器（ACP opencode / exec opencode）
- 它不与实现阶段竞争，而是互补：`implementer` 定义"做什么"，`subagent-execution` 定义"怎么派出去"
- 对于 `medium` 任务：主控用 `subagent-execution` 的派发规则，把 `implementer` 角色的工作交给 ACP opencode
- 对于 light 任务：主控自己做 direct edit，不需要 subagent-execution

## 执行载体选择规则

| 条件 | 载体 |
|------|------|
| 任务简单、改动量小、不需要外部工具 | direct edit |
| 需要代码定位 / 分析 / 实现，ACP 可用 | ACP opencode |
| 需要代码定位 / 分析 / 实现，经用户确认后允许降级 | exec opencode |
| 用户明确指定用某个执行器 | 用户指定 |

ACP 可用性检查：
- 当前 Windows 环境依赖 2026-04-08 的本地手动补丁
- 若 OpenClaw 升级后 ACP 再次报 `backend unavailable`，先检查补丁是否被覆盖
- 若出现 `backend unavailable`、timeout、empty output、result relay 异常、child 有落盘但主会话无有效回传等情况，默认视为 **ACP 阻塞**
- 一旦判定为 ACP 阻塞，主控必须先向用户报告阻塞，再等待用户确认是否降级 `exec opencode`
- 未获用户确认前，不得主会话直接接管代码分析或改码

## 反模式

不要：
- 收到护士站任务就直接跳到 implementer，跳过 brainstorming
- 每个阶段都从零重讲需求，而不复用前序阶段的产物
- 主控在 `locator` / `implementer` / `verifier` 之间做人肉转发器
- 把 ACP 只当一次性命令通道，而不利用其减少上下文重复的价值
- 把 `light` 任务强行套进 `medium/heavy` 流程
- 把 `medium` 任务升级成 `heavy` 流程
- 让 `implementer` 同时承担 `locator` 的职责
- 在关键外部依赖未明确时，把“依赖方会配合”当成默认成立前提直接推进实现
- 在 SQL / 性能优化任务里，跳过代码分析后的用户确认环节，直接把候选优化方向落成代码

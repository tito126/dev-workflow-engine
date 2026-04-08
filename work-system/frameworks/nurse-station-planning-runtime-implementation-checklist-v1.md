# `nurse-station-* × planning-runtime` 实施改造清单 v1

## 1. 文档定位

本文档是《`nurse-station-* × planning-runtime` 协同设计 v1》的执行版清单，用于把方案层内容压缩成可逐项推进的改造任务。

目标不是再次解释理念，而是回答：

1. 先改哪些
2. 每个 skill 具体补什么
3. 哪些内容现在就能做
4. 哪些内容要等 `planning-runtime` 骨架落地后再做

---

## 2. 实施总原则

1. **先补 integration，后补实现细节**
2. **先让 skill 会“引用 runtime”，再让 runtime 真正自动运转**
3. **先保证边界清晰，再追求自动化**
4. **先拿真实任务试跑，再扩展到更多项目**

---

## 3. 两阶段实施策略

## 阶段 A：先改 `nurse-station-*`

目标：

- 让现有护士站 skill 具备 runtime 协同意识
- 明确哪些输出应该回写 runtime 文件
- 明确何时需要启动 `planning-runtime`

## 阶段 B：再建 `planning-runtime`

目标：

- 建立 runtime skill 骨架
- 提供模板、脚本、运行规则
- 支撑护士站 skill 的 runtime 写入和闭环检查

---

## 4. 阶段 A：`nurse-station-*` 改造清单

## A1. `nurse-station-brainstorming`

### 目标

让它不仅判断 ready for planning / ready for execution，还能判断：

- 是否建议创建 runtime task

### 必改项

1. 在输出模板中增加：
   - `Runtime recommended: yes/no`
   - `Suggested task-id:`
2. 在 Integration 中增加：
   - 若任务为复杂任务且准备进入 planning，提示调用 `planning-runtime`
3. 在 readiness 判断中补充：
   - 是否需要跨轮执行
   - 是否需要大量定位/实现/验证

### 改造完成标准

- 该 skill 能自然把复杂事项引导到 runtime 模式

---

## A2. `nurse-station-writing-plans`

### 目标

让计划可以直接映射到 runtime 的 `task-plan.md`

### 必改项

1. 在输出模板中增加：
   - `Runtime path:`
   - `Phases to mirror in task-plan.md:`
   - `Expected findings capture:`
2. 在 Integration 中补充：
   - 若 runtime task 已存在，计划输出要绑定该路径
3. 明确：
   - 当前计划是供 implementer 执行，也是供 runtime 追踪阶段状态使用

### 改造完成标准

- 输出的 plan 可以直接翻译为 runtime phase 结构

---

## A3. `nurse-station-locator`

### 目标

让代码定位结果优先进入 `findings.md`

### 必改项

1. 输出模板中增加：
   - `Runtime path:`
   - `Findings sections to update:`
2. Integration 中补充：
   - 复杂任务下，定位结果默认回写 runtime findings
3. 增加一条明确规则：
   - 不要只给聊天结论，要说明哪些内容应写入 findings

### 改造完成标准

- locator 的结果天然可沉淀成 implementer 的输入材料

---

## A4. `nurse-station-implementer`

### 目标

让实现输出不止停在“Implementation report”，而是进入 runtime 过程文件。

### 必改项

1. 输出模板中增加：
   - `Runtime path:`
   - `Progress updates required:`
   - `Errors to persist:`
2. Integration 中补充：
   - 复杂任务下，实现结果应同步到 `progress.md`
3. 明确：
   - 发现新的失败尝试，必须落到 runtime 文件，而不是只口头说明

### 改造完成标准

- implementer 输出可以直接支撑 review / verification / retrospective

---

## A5. `nurse-station-review-gate`

### 目标

让 review 明确基于 runtime 证据，而不只看聊天摘要。

### 必改项

1. 输出模板中增加：
   - `Runtime evidence reviewed:`
   - `Missing evidence:`
2. Integration 中补充：
   - review 时优先读取 runtime 的 plan/findings/progress
3. 明确：
   - 如果 evidence 不足，要指出缺什么，而不是直接给通过/不通过

### 改造完成标准

- review 成为“基于运行证据的 gate”，而不是印象式 gate

---

## A6. `nurse-station-verification`

### 目标

让 verification 输出可直接进入 `outcome.md`

### 必改项

1. 输出模板中增加：
   - `Runtime path:`
   - `Outcome update:`
   - `Return stage if failed:`
2. Integration 中补充：
   - 复杂任务验收结果需写回 outcome
3. 明确：
   - verification fail 时要指出回到哪一阶段，不只说“未完成”

### 改造完成标准

- verification 的结果可以直接作为 runtime 闭环输入

---

## A7. `nurse-station-subagent-execution`

### 目标

让所有 sub-task 都显式绑定 runtime 路径。

### 必改项

1. 在 Dispatch rules 增加：
   - `Pass runtime path explicitly`
   - `Require runtime file updates or references`
2. 在 Recommended dispatch payload 中增加：
   - `runtime path`
   - `current phase`
   - `which runtime file to update`
3. 明确：
   - 复杂任务不应在没有 runtime task 的情况下直接下发 implementer

### 改造完成标准

- subagent 输出能自然回流到 runtime 容器

---

## A8. `nurse-station-mvp-retrospective`

### 目标

让 retrospective 默认基于 runtime 证据做复盘。

### 必改项

1. 输出模板中增加：
   - `Runtime task reviewed:`
   - `Missing runtime evidence:`
2. Integration 中补充：
   - 默认读取 runtime 的 4 个文件
3. 明确：
   - 复盘结果需指向 skill / template / handoff 的更新建议

### 改造完成标准

- 复盘不再依赖印象，而是基于完整执行轨迹

---

## 5. 阶段 A 执行顺序（推荐）

推荐顺序如下：

1. `nurse-station-brainstorming`
2. `nurse-station-writing-plans`
3. `nurse-station-subagent-execution`
4. `nurse-station-locator`
5. `nurse-station-implementer`
6. `nurse-station-review-gate`
7. `nurse-station-verification`
8. `nurse-station-mvp-retrospective`

原因：

- 先改前置路由与 planning，确保后续所有 skill 都知道 runtime 是什么
- 再改执行、审查、验证、复盘阶段

---

## 6. 阶段 B：`planning-runtime` 骨架建设清单

## B1. 新建 skill 目录

建立：

```text
skills/planning-runtime/
```

## B2. 新建基础文件

建立：

1. `SKILL.md`
2. `reference.md`
3. `examples.md`

## B3. 新建模板目录

建立：

```text
skills/planning-runtime/templates/
```

模板文件：

1. `task-plan.md`
2. `findings.md`
3. `progress.md`
4. `outcome.md`

## B4. 新建脚本目录

建立：

```text
skills/planning-runtime/scripts/
```

脚本建议：

1. `init-runtime-task.ps1`
2. `check-runtime-complete.ps1`
3. `session-catchup.py`

---

## 7. `planning-runtime` 核心规则清单

在 `SKILL.md` 中至少需要写清：

1. 什么时候启用
2. 什么时候不启用
3. runtime 目录创建规则
4. 4 个文件分别记录什么
5. 哪类输出必须落盘
6. 阶段完成时如何更新状态
7. 结束前如何检查是否闭环
8. 如何桥接到项目档案 / daily / memory

---

## 8. 推荐的真实试跑任务

在阶段 A 和阶段 B 初步完成后，建议拿一个真实任务试跑。

优先级推荐：

1. **病区护士高危问题分类治理**
   - 适合验证：brainstorming → planning → findings → retrospective
2. **护士站专项开发框架真实需求 MVP**
   - 适合验证：full chain
3. **某个真实 bug / 稳定性修复任务**
   - 适合验证：locator → implementer → review → verification

---

## 9. 试跑时重点观察什么

试跑时不要只看“能不能跑通”，要重点观察：

1. runtime 文件是否真的在帮助续接，而不是增加负担
2. 哪个阶段最容易忘记回写 runtime
3. review / verification 是否真的用到了 runtime 证据
4. retrospective 是否能从 runtime 里抽出真实摩擦点
5. 是否出现重复记录或边界冲突

---

## 10. 当前最小可执行动作

如果现在就开始推进，建议按这个顺序做：

1. 在主会话里先改 `nurse-station-brainstorming`
2. 再改 `nurse-station-writing-plans`
3. 再改 `nurse-station-subagent-execution`
4. 然后继续补 locator / implementer / verification / review / retrospective
5. 等这组 skill 在主会话里调顺后，再正式建 `skills/planning-runtime/`

---

## 11. 最终结论

当前最正确的推进顺序不是：

- 先把 `planning-runtime` 做得很完整，再让护士站 skill 去适配

而是：

- 先把 `nurse-station-*` 调成“知道 runtime 是什么、知道何时写回 runtime”
- 再让 `planning-runtime` 作为统一执行态容器落地

这样可以最大限度降低空转设计风险。

也就是说：

**先让阶段技能长出 runtime 协同意识，再让 runtime skill 真正接管执行态。**

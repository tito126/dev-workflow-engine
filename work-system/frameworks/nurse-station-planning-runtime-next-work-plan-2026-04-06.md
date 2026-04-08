# `nurse-station-* × planning-runtime` 下一步工作计划（2026-04-06）

## 1. 文档目的

本文档不是泛泛总结，而是把后续要做的工作压成一份可执行清单，明确回答：

1. 现在先做什么，后做什么
2. 是否需要 add 新 agent
3. `nurse-station-*` 每个 skill 要改什么
4. 哪些 runtime 协同点现在就改
5. 哪些内容要等 `planning-runtime` 本体落地后再补
6. 修改时如何保持现有 skill 风格，不做无谓重写

---

## 2. 当前阶段判断

## 2.1 一句话判断

当前最合理的推进方式不是：

- 先把 `planning-runtime` 单独做成一个很完整的大 skill

而是：

- 先让 `nurse-station-*` 具备 runtime 协同意识
- 再建设 `planning-runtime` 本体
- 再拿真实任务（如 `1543024`）试跑闭环

## 2.2 当前工作重心

当前工作重心应当是：

**进入逐项修改 skill 设计的状态。**

也就是：

- 不再停留在“建议层”
- 不再只讨论理念
- 直接明确每个 `SKILL.md` 要新增哪些 runtime 协同点
- 并区分“现在就改”和“等 planning-runtime 落地后再改”

---

## 3. 是否需要 add agent

## 3.1 结论

**当前不把“先 add agent”作为前置阻塞项。**

## 3.2 原因

现阶段要做的是：

- 技能职责收紧
- handoff 更窄
- review gate 更硬
- runtime 协同点进入 skill 设计

这些事情就算还没有 add 新 agent，也照样能推进。

## 3.3 当前不 add 的影响

现在不 add 新 agent，影响的是：

- 后续调度自动化程度
- 主控卸责的彻底程度
- 长期复用时的执行稳定性

但**不影响当前把 skill 设计改到位**。

## 3.4 什么时候再考虑 add agent

建议在以下条件满足后再 add：

1. `nurse-station-*` skill 结构稳定
2. `planning-runtime` 骨架落地
3. 至少跑完 1 次真实任务闭环（如 `1543024`）
4. 已经确认哪些角色真的需要实体化

## 3.5 后续建议 add 的 agent 顺序

后续若进入 agent 实体层，建议顺序如下：

1. `locator`
2. `implementer`
3. `reviewer`
4. `verifier`
5. `runtime-keeper`（可选，后续再看）

说明：

- `reviewer` 与 `verifier` 一开始可以先合并，不必过早拆细
- `runtime-keeper` 不建议现在创建，先用 skill + 文档规则兜住

---

## 4. 总体实施顺序

建议按以下顺序推进。

### Phase 1：先改 `nurse-station-*`

目标：
- 让现有技能都知道 runtime 是什么
- 让输出知道该落到哪个 runtime 文件
- 不改深层逻辑，只补 integration 设计点

### Phase 2：落 `planning-runtime` 骨架

目标：
- 建本地 skill
- 建模板
- 建 runtime 目录规则
- 建最小脚本骨架

### Phase 3：拿真实任务试跑

推荐任务：
- `1543024`

目标：
- 验证从 brainstorming 到 retrospective 是否能串起来
- 看 runtime 文件是否真的有用

### Phase 4：再决定是否 add agent

目标：
- 在真实运行证据基础上决定 agent 实体层，而不是预先拍脑袋建编制

---

## 5. `nurse-station-*` 改造总原则

## 5.1 保持现有 skill 风格

修改时遵循：

- 不大改已有结构
- 不重写整份 `SKILL.md`
- 以“补 integration 规则 / 输出字段 / runtime 协同点”为主
- 保持现有 skill 的语气、结构、职责边界

## 5.2 改造目标

每个 skill 改造后，至少要回答：

1. 是否建议启用 runtime
2. 如果已有 runtime task，输出应回写哪里
3. 当前阶段最应更新哪个 runtime 文件
4. 若失败或阻塞，应把什么写进 runtime 证据链

## 5.3 改造边界

当前阶段**不要求**每个 skill 真的自动写文件。

当前阶段只要求：

- 在设计上显式知道 runtime path
- 明确说明哪些输出应该映射到哪个 runtime 文件
- 为后续 `planning-runtime` 接管执行态打基础

---

## 6. 逐项 skill 改造清单

以下为当前已存在的 `nurse-station-*` skill 的逐项修改计划。

---

## 6.1 `nurse-station-brainstorming`

### 当前角色
- 需求准入
- 边界澄清
- 成功标准判断
- readiness 判断

### 本轮改造目标
让它不仅判断是否 ready for planning / execution，还能判断：

- 是否建议进入 runtime 模式

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **输出模板增加字段**
   - `Runtime recommended: yes/no`
   - `Suggested task-id:`
2. **Mandatory checks 增加判断**
   - 是否预计跨轮执行
   - 是否需要大量定位 / 实现 / 验证
3. **Integration 补充**
   - 若任务复杂且 ready for planning，建议创建 runtime task

### 暂时不改的点
- 不在本 skill 内直接创建 runtime 文件
- 不强行要求自动落盘

### 未来等 `planning-runtime` 落地后再补
- 与 `planning-runtime` 的直接触发衔接语句
- 更明确的 runtime task 初始化指令模板

---

## 6.2 `nurse-station-writing-plans`

### 当前角色
- 生成 execution-ready plan
- 明确 files / roles / validation

### 本轮改造目标
让 plan 可以自然映射到 runtime 的 `task-plan.md`

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Output template 增加字段**
   - `Runtime path:`
   - `Phases to mirror in task-plan.md:`
   - `Expected findings capture:`
2. **Rules 补充一句**
   - 若 runtime task 已存在，计划应显式绑定该路径
3. **Integration 补充**
   - 复杂任务下，plan 不只是给 implementer，也用于 runtime phase 跟踪

### 暂时不改的点
- 不重写现有 plan 模板整体结构
- 不新增大量 runtime 专用文案块

### 未来等 `planning-runtime` 落地后再补
- phase 与 `task-plan.md` 模板字段的精确对齐
- runtime completion bridge 字段

---

## 6.3 `nurse-station-subagent-execution`

### 当前角色
- 主控到 specialized worker 的分发规则

### 本轮改造目标
让 sub-task 天然绑定 runtime task，而不是只靠聊天上下文传递

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Dispatch rules 增加**
   - `Pass runtime path explicitly`
   - `Pass current phase explicitly`
   - `State which runtime file should be updated or referenced`
2. **Recommended dispatch payload 增加字段**
   - `runtime path`
   - `current phase`
   - `runtime update target`
3. **Integration 补充**
   - 复杂任务下，不建议在没有 runtime task 的情况下直接发 implementer 任务

### 暂时不改的点
- 不引入新的复杂派发 DSL
- 不要求当前就自动更新 runtime 文件

### 未来等 `planning-runtime` 落地后再补
- dispatch 与 runtime task 初始化脚本联动
- session catchup / completion check 接入点

---

## 6.4 `nurse-station-locator`

### 当前角色
- 定位入口文件
- 识别参数链路和改动面
- 不改代码

### 本轮改造目标
让定位结果优先沉淀为 `findings.md` 的内容来源

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Output template 增加字段**
   - `Runtime path:`
   - `Findings sections to update:`
2. **Responsibilities 下补一句**
   - 复杂任务下，定位结果默认应能沉淀到 runtime findings
3. **Integration 补充**
   - 若 runtime task 存在，定位结果不应只停在聊天中

### 暂时不改的点
- 不要求 locator 自己直接写 findings 文件
- 不改动其“只定位不实现”的核心边界

### 未来等 `planning-runtime` 落地后再补
- findings 模板字段对齐
- 引导 locator 将 evidence 映射到固定 findings section

---

## 6.5 `nurse-station-implementer`

### 当前角色
- 按明确范围改代码
- 做局部验证
- 输出实现报告

### 本轮改造目标
让实现结果进入 `progress.md` 的逻辑已经显式存在

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Required report 增加字段**
   - `Runtime path:`
   - `Progress updates required:`
   - `Errors to persist:`
2. **Rules 补充一句**
   - 新的失败尝试与结构冲突应作为 runtime 证据保留，而不只口头汇报
3. **Integration 补充**
   - 复杂任务下，实现输出默认对应 `progress.md`

### 暂时不改的点
- 不在 implementer skill 中引入自动写 runtime 文件脚本
- 不改变其“只在 scope clear 后进入实现”的核心门槛

### 未来等 `planning-runtime` 落地后再补
- progress 模板字段映射
- 与 runtime error persistence 的固定格式

---

## 6.6 `nurse-station-review-gate`

### 当前角色
- Gate 1：Requirement fit
- Gate 2：Code quality

### 本轮改造目标
让 review 明确基于 runtime 证据，而不是只看 implementer 摘要

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Output template 增加字段**
   - `Runtime evidence reviewed:`
   - `Missing evidence:`
2. **Reviewer mindset 补一句**
   - 若 runtime 证据链存在，应优先读取而不是只看聊天摘要
3. **Integration 补充**
   - review 时优先参考 `task-plan.md / findings.md / progress.md`

### 暂时不改的点
- 不把 review 逻辑重写成 planning-runtime 的子技能
- 不新增复杂证据分类体系

### 未来等 `planning-runtime` 落地后再补
- completion check 的直接挂接点
- review 对 runtime 缺失字段的固定报错格式

---

## 6.7 `nurse-station-verification`

### 当前角色
- 验证 requirement fit / scene fit / technical fit
- 判断 accept as complete

### 本轮改造目标
让 verification 结果可自然映射到 `outcome.md`

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Output template 增加字段**
   - `Runtime path:`
   - `Outcome update:`
   - `Return stage if failed:`
2. **Integration 补充**
   - 复杂任务下，verification 输出应能同步到 runtime outcome
3. **Rules / checklist 补一句**
   - fail 时要明确回退到哪一阶段，不只说未完成

### 暂时不改的点
- 不重写整个 verification checklist
- 不引入过多 runtime 术语，避免破坏现有可读性

### 未来等 `planning-runtime` 落地后再补
- `outcome.md` 精确字段映射
- verification 与 completion check 脚本协同

---

## 6.8 `nurse-station-mvp-retrospective`

### 当前角色
- 真实 run 后抽经验
- 转化为 framework 改进项

### 本轮改造目标
让 retrospective 默认意识到“应该基于 runtime 证据做复盘”

### 现在就要修改的点
在现有 `SKILL.md` 中补：

1. **Mandatory output 增加字段**
   - `Runtime task reviewed:`
   - `Missing runtime evidence:`
2. **Integration 补充**
   - 若 runtime task 存在，复盘应优先读取其 4 个文件
3. **Framework update 部分补一句**
   - 新增建议要指向 skill / template / handoff / runtime rule

### 暂时不改的点
- 不要求 retrospective 现在就自动抓取 runtime 文件
- 不重写其现有复盘维度结构

### 未来等 `planning-runtime` 落地后再补
- 默认读取 runtime 四文件
- retrospective 与 outcome / project dossier 回写桥接

---

## 7. 当前不建议大改的 skill

以下 skill 当前阶段不建议大改，只需在后续真实试跑中观察。

### 7.1 `nurse-station-review-gate` 与 `nurse-station-verification` 的进一步拆分

当前先保持：
- review gate
- verification

两个 skill 的边界不动。

等真实试跑后再判断是否还需要再细分。

### 7.2 `nurse-station-subagent-execution` 的复杂编排细节

当前不引入更多编排语法。

先把：
- runtime path
- current phase
- runtime update target

这三个字段补进 dispatch 规则即可。

---

## 8. `planning-runtime` 本体何时开始建

建议在以下条件达成后启动：

1. 上述 `nurse-station-*` 的 integration 改造完成
2. 已形成统一 runtime 文件映射规则
3. 已确认复杂任务中哪些输出必须落盘

也就是说：

**先让阶段 skill 们知道 runtime 是什么，再让 planning-runtime 真正落地。**

---

## 9. 下一步明确动作

建议按以下顺序逐项修改：

1. 修改 `nurse-station-brainstorming`
2. 修改 `nurse-station-writing-plans`
3. 修改 `nurse-station-subagent-execution`
4. 修改 `nurse-station-locator`
5. 修改 `nurse-station-implementer`
6. 修改 `nurse-station-review-gate`
7. 修改 `nurse-station-verification`
8. 修改 `nurse-station-mvp-retrospective`

完成后，再开始建设：

9. `skills/planning-runtime/`

---

## 10. 最终结论

当前阶段最关键的不是先建更多 agent，也不是先把 `planning-runtime` 做成一个很大的完整体系。

当前阶段最关键的是：

**把 `nurse-station-*` 从“有阶段技能”推进到“知道如何与 runtime 执行容器协同的阶段技能”。**

这是后续所有自动化、agent 实体层、复杂任务闭环的前提。

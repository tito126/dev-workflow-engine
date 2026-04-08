# `nurse-station-* × planning-runtime` 协同设计 v1

## 1. 文档定位

本文档用于定义当前 `nurse-station-*` 系列 skill 与拟建设的 `planning-runtime` skill 之间的协同关系、职责边界、运行顺序和改造清单。

目标不是再造一套并行框架，而是让两组能力形成稳定分工：

- `nurse-station-*` 负责护士站领域流程与阶段动作
- `planning-runtime` 负责复杂任务执行态的上下文控制与运行容器

---

## 2. 协同总判断

## 2.1 一句话结论

`nurse-station-*` 和 `planning-runtime` 不是替代关系，而是：

**领域流程层 × 运行态控制层**

的互补关系。

## 2.2 两组 skill 的本质差异

### `nurse-station-*`

解决的是：

- 护士站任务如何准入
- 如何澄清需求
- 如何拆计划
- 如何定位代码
- 如何实现
- 如何审查
- 如何验证
- 如何复盘

它强在：

**阶段职责清晰、领域语义明确、流程链完整。**

### `planning-runtime`

解决的是：

- 复杂任务启动后，如何建立 runtime 工作区
- 如何把目标、发现、进展、错误持续落盘
- 如何让多轮续接时不需要重新拼装上下文
- 如何在结束前进行阶段闭环检查
- 如何桥接正式项目档案与交付结果

它强在：

**执行态控制、上下文续接、错误持久化、运行文件容器。**

---

## 3. 当前问题：为什么两组 skill 必须协同

如果只有 `nurse-station-*`，会出现的问题：

1. 阶段定义清楚，但缺少统一 runtime 文件落点
2. 各阶段产出可能只停留在聊天或零散文档里
3. 多轮执行时，上下文续接成本高
4. 错误与尝试没有强制沉淀进运行态文件
5. 任务完成与否容易靠主观感觉判断

如果只有 `planning-runtime`，会出现的问题：

1. 不具备护士站领域的业务准入能力
2. 不知道如何做护士站特有的需求澄清
3. 不知道如何做领域化 locator / implementer / verifier 分工
4. 容易变成通用 planning 包，而不是护士站专项能力底座

因此两者必须组合使用：

- `nurse-station-*` 决定每个阶段该做什么
- `planning-runtime` 保证这些阶段在一个稳定的执行容器里持续运行

---

## 4. 协同架构

推荐采用以下分层：

```text
主控层
  OpenClaw main session

领域流程层
  nurse-station-brainstorming
  nurse-station-writing-plans
  nurse-station-locator
  nurse-station-implementer
  nurse-station-review-gate
  nurse-station-verification
  nurse-station-mvp-retrospective
  nurse-station-subagent-execution

运行态控制层
  planning-runtime

正式记录层
  work-system/projects/
  work-system/daily/
  work-system/deliverables/
  memory/
  MEMORY.md
```

---

## 5. 运行总原则

## 5.1 原则一：领域判断和运行控制分离

- `nurse-station-*` 做领域判断
- `planning-runtime` 做运行控制

不要让 `planning-runtime` 负责业务决策；
也不要让 `nurse-station-*` 各自维护独立的 runtime 文件体系。

## 5.2 原则二：一条复杂任务只绑定一个 runtime task 工作区

推荐统一写到：

`work-system/projects/active/<project>/runtime/<task-id>/`

所有相关 skill 在该任务周期内共用：

- `task-plan.md`
- `findings.md`
- `progress.md`
- `outcome.md`

## 5.3 原则三：阶段技能产出必须可回写到 runtime 文件

任何一个 `nurse-station-*` skill 的输出，如果属于该复杂任务，就应该能够明确写入 runtime task 对应文件，而不是只停留在聊天里。

## 5.4 原则四：复盘必须基于 runtime 证据，不只基于印象

`nurse-station-mvp-retrospective` 应优先读取 runtime 文件，而不是仅基于最终摘要做复盘。

---

## 6. 角色分工图

## 6.1 OpenClaw main session（主控）

负责：

- 收用户输入
- 判断是否进入护士站正式流程
- 判断是否启用 `planning-runtime`
- 决定调用哪个 `nurse-station-*` 阶段 skill
- 汇总结果并回写正式记录

## 6.2 `planning-runtime`

负责：

- 初始化 runtime task
- 维护运行文件结构
- 约束关键内容落盘
- 提醒阶段状态更新
- 进行闭环检查
- 桥接 outcome 与正式记录层

## 6.3 `nurse-station-*`

负责：

- 在各自阶段完成业务语义上的分析、计划、实现、审查、验证、复盘
- 将高价值输出写入 runtime 文件或引用 runtime 证据

---

## 7. 每个护士站 skill 与 `planning-runtime` 的协同关系

以下逐个说明。

## 7.1 `nurse-station-brainstorming`

### 当前定位

负责需求准入、边界澄清、成功标准、执行 readiness 判断。

### 与 `planning-runtime` 的关系

它是最适合作为 runtime 启动前置门的 skill。

### 推荐协同方式

1. 先由 `nurse-station-brainstorming` 产出 requirement intake
2. 如果判断为：
   - 复杂任务
   - 需要跨轮推进
   - 需要代码执行或大量分析
   则建议启用 `planning-runtime`
3. requirement intake 摘要写入对应 task 的 `task-plan.md`

### 推荐新增 integration 规则

在该 skill 中补充：

- 若任务 ready for planning 且预计进入多阶段执行，提示主控创建 runtime task
- 输出中增加：
  - Runtime recommended: yes/no
  - Suggested task-id:

---

## 7.2 `nurse-station-writing-plans`

### 当前定位

负责把已澄清事项变成 execution-ready 的计划。

### 与 `planning-runtime` 的关系

它产出的计划，应该成为 `task-plan.md` 的核心内容来源。

### 推荐协同方式

1. `planning-runtime` 建立 runtime task
2. `nurse-station-writing-plans` 输出正式计划
3. 将计划固化进 `task-plan.md`
4. 后续每个阶段状态更新，都围绕该文件进行

### 推荐新增 integration 规则

- 若 runtime task 已存在，计划输出需引用该路径
- 输出结构中增加：
  - Runtime path:
  - Phases to mirror in `task-plan.md`:
  - Findings capture expected: yes/no

---

## 7.3 `nurse-station-locator`

### 当前定位

负责找实现入口、参数流、配置、改动文件，不负责实现。

### 与 `planning-runtime` 的关系

它是 `findings.md` 的重要内容生产者。

### 推荐协同方式

locator 运行时：

- 文件定位结果写入 `findings.md`
- 关键文件、入口路径、风险点同步到 `task-plan.md` 或 `progress.md`

### 推荐新增 integration 规则

- 输出需增加：
  - Runtime path:
  - Findings sections to update:
  - Likely files for implementer:

### 特别提醒

不要让 locator 把所有定位结果只留在聊天回复里；应明确要求“写入 runtime findings”。

---

## 7.4 `nurse-station-implementer`

### 当前定位

负责 scoped code changes 和局部验证。

### 与 `planning-runtime` 的关系

它是 `progress.md` 与 `task-plan.md` 的核心更新者之一。

### 推荐协同方式

implementer 执行后应至少回写：

- 改了哪些文件 → `progress.md`
- 做了什么改动 → `progress.md`
- 哪些没改 → `progress.md`
- 遇到的错误 / 调整 → `task-plan.md` + `progress.md`
- 是否 ready for review → `outcome.md` 或 `progress.md`

### 推荐新增 integration 规则

- 输出结构中增加：
  - Runtime path:
  - Progress updates required:
  - Errors to persist:

### 特别提醒

不要让 implementer 只交一个聊天版“Implementation report”就结束；应落入 runtime 文件。

---

## 7.5 `nurse-station-review-gate`

### 当前定位

负责 requirement fit 与 code quality 两道 gate。

### 与 `planning-runtime` 的关系

它应读取 runtime 中已有证据，而不是只信 implementer 总结。

### 推荐协同方式

review-gate 在做 gate 审查时，优先参考：

- `task-plan.md`：原始目标与范围
- `findings.md`：定位依据与风险
- `progress.md`：实际动作、改动、验证情况

### 推荐新增 integration 规则

- 输出结构中增加：
  - Runtime evidence reviewed:
  - Missing evidence:
  - Return to implementer / locator with which runtime corrections:

---

## 7.6 `nurse-station-verification`

### 当前定位

负责对 requirement intent、scene constraints、execution claims 做最终校验。

### 与 `planning-runtime` 的关系

它是 runtime 闭环前的最后业务验真层。

### 推荐协同方式

verification 产出需同步到：

- `outcome.md`：是否 accept as complete
- `progress.md`：验证结果摘要

如果 verification fail，则需明确写回：

- 哪个阶段需要回退
- 哪些点要重新进入 implement / locator / review

### 推荐新增 integration 规则

- 输出结构中增加：
  - Runtime path:
  - Outcome update:
  - Accept as complete:
  - Return stage if failed:

---

## 7.7 `nurse-station-subagent-execution`

### 当前定位

负责 controller 到 specialized worker 的分发。

### 与 `planning-runtime` 的关系

它是把 runtime task 贯穿到执行者手里的关键桥梁。

### 推荐协同方式

每个 dispatch payload 都必须显式携带：

- runtime path
- 当前 phase
- 需要回写哪个文件
- stop condition

### 推荐新增 integration 规则

在 Dispatch rules 中新增：

1. Pass runtime path explicitly
2. Require worker to update or reference runtime files
3. Do not dispatch implementation work without runtime task when task is complex

---

## 7.8 `nurse-station-mvp-retrospective`

### 当前定位

负责真实 run 后抽经验，转化为 framework 改进。

### 与 `planning-runtime` 的关系

它是 runtime 产物向长期资产沉淀的关键转换层。

### 推荐协同方式

retrospective 默认读取：

- `task-plan.md`
- `findings.md`
- `progress.md`
- `outcome.md`

以此回答：

- 哪些阶段顺畅
- 哪些阶段信息不够
- 哪些失败模式重复出现
- 哪些模板、skill、handoff rule 需要补

### 推荐新增 integration 规则

- 输出结构中增加：
  - Runtime task reviewed:
  - Missing runtime evidence:
  - Template / skill / handoff updates suggested:

---

## 8. 推荐的统一 runtime 文件映射规则

为避免不同 skill 各写各的，建议统一映射如下：

## 8.1 `task-plan.md`

由以下 skill 重点更新：

- `nurse-station-brainstorming`
- `nurse-station-writing-plans`
- `planning-runtime`

主要内容：

- 目标
- 当前阶段
- 阶段拆解
- readiness 判断
- 错误表

## 8.2 `findings.md`

由以下 skill 重点更新：

- `nurse-station-locator`
- `nurse-station-brainstorming`
- 必要时 `implementer`

主要内容：

- 代码定位发现
- 文档阅读发现
- 风险点
- 资源链接

## 8.3 `progress.md`

由以下 skill 重点更新：

- `nurse-station-implementer`
- `nurse-station-review-gate`
- `nurse-station-verification`

主要内容：

- 做了什么
- 改了哪些文件
- 验证做了什么
- 错误和修正

## 8.4 `outcome.md`

由以下 skill 重点更新：

- `nurse-station-verification`
- `nurse-station-review-gate`
- `nurse-station-mvp-retrospective`
- `planning-runtime`

主要内容：

- 最终结果
- 是否接受完成
- 残留风险
- 需要回写的正式记录
- 已同步状态

---

## 9. 一条推荐运行链路

推荐按以下顺序运行：

```text
1. nurse-station-brainstorming
   ↓
2. planning-runtime (init runtime task)
   ↓
3. nurse-station-writing-plans
   ↓
4. nurse-station-subagent-execution
   ↓
5. nurse-station-locator / implementer / review / verification
   ↓
6. planning-runtime (completion check + outcome bridge)
   ↓
7. nurse-station-mvp-retrospective
   ↓
8. work-control / project dossier / daily summary / memory 回写
```

---

## 10. 推荐改造清单

建议分两批改造。

## 10.1 第一批：先改 integration 说明，不改深层逻辑

优先在以下 skill 中增加 integration 文案：

1. `nurse-station-brainstorming`
2. `nurse-station-writing-plans`
3. `nurse-station-locator`
4. `nurse-station-implementer`
5. `nurse-station-subagent-execution`
6. `nurse-station-verification`
7. `nurse-station-review-gate`
8. `nurse-station-mvp-retrospective`

改造目标：

- 明确 runtime path
- 明确输出回写哪个文件
- 明确何时触发 `planning-runtime`

## 10.2 第二批：再补模板与实际使用规则

在 `planning-runtime` 落地后，再补：

- runtime 模板字段
- session catchup 规则
- completion check 脚本
- retrospective 对 runtime 的默认读取规则

---

## 11. 最容易犯的错误

以下错误需要提前避免：

1. **让 `planning-runtime` 替代业务 skill**
   - 错，`planning-runtime` 不做护士站业务判断

2. **让每个 `nurse-station-*` skill 各自创建自己的中间文件**
   - 错，应统一写入 runtime task

3. **只在聊天中输出 skill 结果，不回写 runtime 文件**
   - 错，这会让 runtime 失去意义

4. **把所有任务都强制走 runtime**
   - 错，应只在复杂任务中使用

5. **复盘只看最终摘要，不看 runtime 证据**
   - 错，这样无法抽取真正的执行摩擦点

---

## 12. 最终结论

`nurse-station-*` 已经回答了：

**护士站任务该如何按阶段做。**

`planning-runtime` 需要补上的是：

**这些阶段如何在同一个复杂任务中被稳定串起来，并留下可续接、可验证、可复盘的运行轨迹。**

因此，最合理的组合方式是：

- `nurse-station-*` 作为领域流程层
- `planning-runtime` 作为运行态控制层

并统一以：

`work-system/projects/active/<project>/runtime/<task-id>/`

作为复杂任务的执行态容器。

这套协同设计如果跑顺，后续护士站专项开发框架就不只是“有很多 skill”，而会真正形成：

- 可阶段化分工
- 可跨轮续接
- 可错误持久化
- 可正式回写
- 可复盘优化

的稳定机制。

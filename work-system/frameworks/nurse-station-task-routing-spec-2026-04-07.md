# 护士站任务分级与路由规则（2026-04-07）

## 1. 目标

这份规则用于把护士站框架从“固定顺序流程”升级为“按任务特征自适应分流的执行系统”。

核心原则不是让所有任务都走同一条最完整链，而是：

> 先判断任务级别与信息完备度，再决定进入哪条执行路径。

---

## 2. 路由总原则

在护士站框架中，任何任务进入正式执行前，都必须先回答两类问题：

### 2.1 任务复杂度
- 是 light / medium / heavy 哪一类？
- 是否需要跨轮推进？
- 是否需要多角色协作？
- 是否需要 runtime 证据链？

### 2.2 需求完备度
- 场景是否明确？
- 模块 / 页面 / 代码范围是否明确？
- 验收标准是否明确？
- 是否已经具备 coding 所需的 requirement-fit artifact？

只有同时判断这两类问题，路由才稳定。

---

## 3. 一级分流：Light / Medium / Heavy

## 3.1 Light

### 判定条件
同时满足大部分以下条件：
- 单页面或单模块小改动
- 目标行为清楚
- 插入 / 修改位置清楚
- 场景限制清楚
- 通常 1 个文件，或 2 个高度耦合但边界清楚的文件
- 验收标准可以写成 1-3 条直接检查项
- 不需要跨多轮探索

### 默认路由
`brainstorming(light intake) -> requirement-fit mini check -> locator(optional) -> implementer -> verification`

### 默认不启用
- 不默认 runtime
- 不默认 `subagent-execution`
- 不默认完整 `review-gate`

### 升级条件
满足任一即升为 Medium：
- UI / 参数 / 场景仍有关键不确定点
- 涉及跨文件联动且边界不稳
- 验收项写不清
- implementer 需要自己判断较多结构问题

---

## 3.2 Medium

### 判定条件
满足以下若干特征：
- 需求本身不算大，但存在跨文件、跨条件、跨角色确认
- 需要先定位再实现
- 需要至少一轮中间 review 或 requirement-fit gate
- 影响仍可控，但不能直接开改
- 验收标准可形成，但需要先补 requirement-fit artifact

### 默认路由
`brainstorming -> requirement-fit checkpoint -> writing-plans(minimal) -> locator -> implementer(narrow handoff) -> requirement-fit review -> verification`

### runtime 规则
默认不强制；仅在以下任一情况启用：
- 任务要跨轮推进
- 任务本身要作为流程样板 / 复盘样本
- 需要显式保留 findings / progress / outcome 证据链

### 子代理规则
默认不强制；只有主控判断本轮执行面已超出自己直接承接范围时，才进入 `subagent-execution`。

### 升级条件
满足任一即升为 Heavy：
- 需要多阶段持续跟踪
- 需要明确 runtime 才能控制上下文
- 需要 formal review / verification / retrospective
- 涉及复杂定位、复杂改动或高不确定性

---

## 3.3 Heavy

### 判定条件
满足以下若干特征：
- 多阶段、多轮推进
- 高不确定性
- 跨模块 / 跨 repo / 跨角色
- 必须保留证据链
- 需要 runtime 持续承载目标、发现、进展、错误、结果
- 需要正式 review / verification / retrospective

### 默认路由
`brainstorming -> task-level routing -> planning-runtime(init) -> requirement-fit checkpoint -> writing-plans(full) -> subagent-execution -> locator/implementer/review/verification -> retrospective`

### 默认启用
- runtime
- 结构化 findings / progress / outcome
- 明确 phase contract

---

## 4. 二级分流：需求完备度闸门

任务级别确定后，仍不能直接进入 coding。

还必须判断是否已达到 **Ready for coding**。

### 4.1 必须明确的最小项
- 业务目标
- 目标场景
- 模块 / 页面 / 代码范围
- 成功标准
- 至少一个可验证观察点

### 4.2 对 UI / 前端类任务额外要求
- 控件 / 交互对象是什么
- 新增 / 移动 / 替换的位置
- 与相邻元素的顺序关系
- 场景显隐规则
- 是否去重旧入口
- 验收时应观察什么页面结果

### 4.3 如果不满足
- 不进入 implementer
- 回到 `brainstorming` 或 requirement-fit checkpoint 补齐

---

## 5. 各 Skill 在路由中的职责

## 5.1 `nurse-station-brainstorming`
负责：
- 需求准入
- 输出任务级别建议
- 输出 route recommendation
- 判断 requirement-fit artifact 是否已具备

## 5.2 `nurse-station-writing-plans`
负责：
- 按任务级别输出 full plan 或 minimal plan
- 把 coding 前必须确认项写清楚

## 5.3 `nurse-station-subagent-execution`
负责：
- 仅承接 Medium / Heavy 中确有必要分发的任务
- 不是默认总线

## 5.4 `planning-runtime`
负责：
- 仅在 Heavy 或部分 Medium 样板任务中启用
- 作为执行态容器，而不是所有任务的默认负担

## 5.5 `nurse-station-review-gate`
负责：
- 中重任务中的阶段门禁
- 不再作为所有任务的默认中间动作

## 5.6 `nurse-station-verification`
负责：
- 最终确认 requirement fit / scene fit / technical fit
- 若无前置验收物，则不得判定完成

---

## 6. 回退规则

### 回到 `brainstorming`
当业务目标、场景、边界重新变得不清楚时。

### 回到 requirement-fit checkpoint
当前置信息不够做稳定 coding / verification 时。

### 回到 `locator`
当前实现失败可能由入口定位不稳导致时。

### 回到 `implementer`
方向对，但改动不稳、越界、结构有问题时。

### 回到 `review-gate`
实现完成但还需阶段门禁确认时。

---

## 7. 一句话执行纪律

护士站框架后续默认执行纪律应改为：

> 先分级，再补齐 requirement-fit，再决定是否启用 runtime / planning / subagent / review-heavy 链，而不是把完整重链作为默认流程。 

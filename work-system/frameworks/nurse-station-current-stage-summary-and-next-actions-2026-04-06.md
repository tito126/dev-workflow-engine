# 护士站框架当前阶段总结与下一步可执行事项（2026-04-06）

## 1. 文档目的

本文档用于对当前阶段已经完成的工作做一次正式收口，并明确列出下一步可直接落地执行的事项，避免当前进展只停留在聊天中。

本文档重点回答：

1. 到目前为止到底做成了什么
2. 当前阶段还没做完的是什么
3. 下一步最值得立刻推进的具体事项有哪些
4. 这些事项执行顺序应该如何安排

---

## 2. 当前阶段已完成的工作

## 2.1 `1543024` 真实链路已完成的部分

围绕 TFS 需求 `1543024`，当前已经完成：

1. **需求准入**
   - 确认这是护士站床位卡场景中的真实需求
   - 明确核心目标：将时间区间条件从“更多搜索”前移到主搜索区
   - 明确边界：
     - 保留“类型切换 + 日期范围”交互
     - 仅在“已出院”场景显示
     - 不处理“默认勾选且不可编辑”

2. **实现计划样板**
   - 已形成正式的实现计划框架
   - 已明确仓库、模块、关键文件、Agent 分工与验证点

3. **代码定位**
   - 已定位关键文件：
     - `homeHeader.vue`
     - `searchComp.vue`
   - 已识别当前实现是组合条件，而不是两个完全独立控件

4. **实现失败复盘**
   - 已形成正式失败复盘文档
   - 已总结出这次跑偏的根因
   - 已明确提出需要补：
     - 超窄实现 handoff 规范
     - review gate 回环规则

## 2.2 护士站 Skill 体系已完成的部分

当前 `nurse-station-*` 已完成：

1. Skill 骨架搭建
2. prompts 与 anti-patterns 增补
3. 样板模板补齐
4. 第一轮 runtime 协同改造

已完成 runtime 协同改造的 skill：

- `nurse-station-brainstorming`
- `nurse-station-writing-plans`
- `nurse-station-subagent-execution`
- `nurse-station-locator`
- `nurse-station-implementer`
- `nurse-station-review-gate`
- `nurse-station-verification`
- `nurse-station-mvp-retrospective`

这些 skill 现在已经开始显式知道：

- 是否推荐 runtime
- runtime path 是什么
- 输出应该映射到哪个 runtime 文件
- review / retrospective 应优先读取 runtime 证据

## 2.3 `planning-runtime` 已完成的部分

当前已完成最小骨架：

- `skills/planning-runtime/SKILL.md`
- `reference.md`
- `examples.md`
- `templates/task-plan.md`
- `templates/findings.md`
- `templates/progress.md`
- `templates/outcome.md`
- 脚本占位：
  - `init-runtime-task.ps1`
  - `check-runtime-complete.ps1`
  - `session-catchup.py`

这意味着：

- `planning-runtime` 已经从概念进入“可继续施工”的状态
- 但目前仍是最小骨架，不是完整可运行成品

---

## 3. 当前阶段还没完成的部分

## 3.1 `1543024` 还没完成的部分

当前仍未完成：

1. **稳定实现**
   - 上一轮 implementer 试跑已确认会跑偏
   - 代码改动已撤销
   - 尚未进入更窄粒度的重新实现

2. **正式 review**
   - 还未真正按双 gate 规则执行一轮完整 review

3. **正式 verification**
   - 还未完成对场景限制、参数链路、去重逻辑的正式验证

4. **runtime 真实试跑闭环**
   - 还未用 `1543024` 建立真实 runtime task 目录并跑完整闭环

## 3.2 框架还没完成的部分

当前仍未完成：

1. `planning-runtime` 脚本仍是占位版
2. runtime 文件尚未在真实任务中使用
3. 还缺：
   - 超窄实现 handoff 正式文档
   - review gate 回环规则正式文档
4. 还未验证：
   - runtime 文件是否真的降低上下文漂移
   - retrospective 是否能基于 runtime 证据更稳地提炼框架资产

---

## 4. 当前阶段的判断

## 4.1 一句话判断

当前阶段不是“还在讨论框架”，而是：

**已经完成框架第一轮搭建，正在进入从概念框架到真实执行系统的过渡期。**

## 4.2 当前最关键的风险

当前最关键的风险不是“没想清楚”，而是：

**如果继续直接推进 `1543024`，而不先补执行护栏与 runtime 实际落地，仍可能重复上一轮实现跑偏的问题。**

所以当前最值得做的，不是盲目继续改代码，而是：

- 把执行护栏补完整
- 让 runtime 真跑起来
- 然后再重启 `1543024` 的实现链

---

## 5. 下一步可落地执行的具体事项

以下列出当前阶段之后，最值得立即推进的事项。

## 5.1 事项 1：产出超窄实现 handoff 规范文档

### 目标
把“implementer 一次只能接窄任务”的约束正式写成框架规则。

### 要做什么
形成一份正式文档，至少写清：

1. 什么叫超窄任务
2. 什么情况下必须拆任务
3. 一次 implementer 允许改几个文件
4. 什么情况下必须把实现拆成 `Task A / Review A / Task B / Review B`
5. 哪些任务绝不能打包给一个 implementer 一次完成

### 直接价值
解决 `1543024` 这类任务在实现阶段容易发散的问题。

---

## 5.2 事项 2：产出 review gate 回环规则文档

### 目标
把 review 从“最后看看”升级成过程中的强门禁。

### 要做什么
形成一份正式文档，至少写清：

1. implementer 何时必须停下来进入 review
2. Gate 1 / Gate 2 分别检查什么
3. 不通过时如何回退
4. 什么时候允许进入下一步实现
5. review 与 verification 的边界如何分开

### 直接价值
避免错误实现一路扩散，直到污染多个文件后才发现。

---

## 5.3 事项 3：建立第一条真实 runtime task

### 目标
不再只搭骨架，真正让 `planning-runtime` 在真实任务上跑起来。

### 推荐任务
优先推荐直接用：

- `1543024`

### 要做什么
在合适项目路径下创建：

`work-system/projects/active/<project>/runtime/<task-id>/`

并初始化：

- `task-plan.md`
- `findings.md`
- `progress.md`
- `outcome.md`

### 直接价值
验证 runtime 文件是不是在真实链路中真的有用，而不是纸面设计。

---

## 5.4 事项 4：用更窄粒度重新启动 `1543024`

### 目标
不再“一口气实现”，而是按新的框架纪律重新推进。

### 推荐拆法

#### Task A
只处理 `homeHeader.vue`
- 前移时间区间组合条件
- 不碰 `searchComp.vue`

#### Review A
检查：
- 插入位置是否正确
- 是否只在“已出院”显示
- 是否没有破坏原结构

#### Task B
只处理 `searchComp.vue`
- 去掉重复展示
- 不再改主搜索区逻辑

#### Review B
检查：
- 是否真正去重
- 是否没有误伤其他筛选项

#### Task C
统一 verification
- 验证交互、场景、参数链路

### 直接价值
这是对“超窄实现 handoff + review gate 回环规则”的第一次真实验证。

---

## 5.5 事项 5：把 runtime 使用结果反哺到 Skill 与模板

### 目标
让 runtime 真正成为框架资产，而不是一次性试验。

### 要做什么
在完成一次 runtime 真实试跑后，回头检查：

1. 哪些字段根本没用
2. 哪些信息仍然漏记
3. 哪些 skill 的 runtime 协同点还不够具体
4. 哪些模板需要删减或补充

### 直接价值
保证 `planning-runtime` 不是越做越重，而是越跑越贴合真实工作。

---

## 6. 推荐执行顺序

建议按以下顺序推进：

1. **先出文档**
   - 超窄实现 handoff 规范
   - review gate 回环规则

2. **再跑 runtime**
   - 建立 `1543024` 的真实 runtime task

3. **再回到需求执行**
   - 用更窄粒度重启 `1543024`

4. **最后做反哺**
   - 用真实运行结果修正 skill / template / runtime 结构

这个顺序的好处是：

- 不会再直接裸跑实现
- 先把最关键护栏立起来
- 再让真实任务验证护栏是不是有效

---

## 7. 当前是否需要 add agent

当前阶段：

**不需要把 add agent 作为下一步前置动作。**

原因：

- 现在更需要的是规则收紧与 runtime 真跑
- agent 实体层可以等至少一条 runtime 真实链路跑顺后再定

后续若进入 agent 实体化阶段，建议顺序：

1. `locator`
2. `implementer`
3. `reviewer`
4. `verifier`

但这属于下一阶段，不是当前阶段最优先事项。

---

## 8. 最终结论

当前阶段已经不再是“要不要做框架”的阶段，而是：

**框架第一版已经搭起来，接下来要让它真正跑一次、摔一次、收一次，并把结果变成稳定规则。**

因此，下一步最值得马上推进的事项，不是继续扩展文档范围，而是：

1. 出两份关键执行护栏文档
2. 建第一条真实 runtime task
3. 用 `1543024` 按新纪律重新启动实现

这三步一旦完成，这套护士站框架就会从“已经有框架感”进入“已经有执行系统感”。

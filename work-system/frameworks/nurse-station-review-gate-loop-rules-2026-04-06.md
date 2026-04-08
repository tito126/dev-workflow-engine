# 护士站 review gate 回环规则（2026-04-06）

## 1. 文档目的

本文档用于定义护士站专项开发框架中，review 不再只是“最后看一眼”，而是作为实现过程中的强门禁与回环机制存在。

目标是解决当前已暴露的问题：

- implementer 改完一大坨后才发现方向不对
- 错误改动在多个文件中扩散
- 主控只能事后救火
- verification 被迫在错误实现基础上工作

---

## 2. 一句话定义

**review gate 回环规则** 指的是：

> 每当实现任务完成一个足够独立的子阶段后，必须进入 review；review 不通过，则工作返回上一个合适阶段修正；review 通过，才允许进入下一子阶段。

换句话说：

- review 不是总结动作
- review 是中间门禁
- review 的结果必须影响执行流向

---

## 3. 为什么必须回环

如果 review 只是最后统一做，会出现：

1. implementer 连续改多个文件
2. 中间错误无人拦截
3. 直到结构已经被污染时才发现
4. 修复成本、判断成本、上下文成本都显著上升

`1543024` 这次已经真实证明了这一点。

所以 review 不能再停留在“最后检查”，而必须成为：

- 阶段结束后的强制动作
- 继续执行前的放行门

---

## 4. 基本回环流程

推荐固定为：

```text
Task A -> Review A -> Task B -> Review B -> Verification -> Retrospective
```

而不是：

```text
Task A + Task B + Task C 一起做完 -> 最后统一 review
```

---

## 5. Review 的两道 Gate

## Gate 1：Requirement / Spec Fit

目的：
先确认这一步做的事，业务方向和边界是对的。

必须检查：

1. 是否解决了当前子任务目标
2. 是否保持了约定交互
3. 是否符合场景限制
4. 是否越界做了别的事
5. 是否已经影响到本不该动的部分

如果 Gate 1 不通过：
- **禁止进入 Gate 2**
- 直接回退给 Implementer 修正

## Gate 2：Code Quality / Change Risk

目的：
在业务方向正确的前提下，再确认代码结构是否足够稳。

必须检查：

1. 改动是否局部、是否过度扩张
2. 是否有明显结构错误或逻辑重复
3. 是否有明显回归风险
4. 是否与计划中的文件边界一致
5. 是否为下一阶段留下了稳定基线

如果 Gate 2 不通过：
- 返回 Implementer 做代码层修正
- 不允许继续下一子阶段

---

## 6. 何时必须进入 review

以下场景必须进入 review：

1. 一个超窄 implementer task 完成后
2. 关键插入点已经改完后
3. 一个文件的主要改动完成后
4. 进入下一个文件前
5. 参数链路或场景控制被触及之后

也就是说：

- review 的触发点是“阶段完成”
- 不是“全部都做完了再说”

---

## 7. Review 不通过时回到哪一阶段

不是所有失败都回 implementer 同一层直接改。

推荐规则如下：

### 情况 A：实现偏题，但定位本身没错
- 回到：Implementer
- 说明：任务边界执行错了，但入口判断没问题

### 情况 B：实现方向偏题，怀疑入口定位本身就不稳
- 回到：Locator / Analyst
- 说明：需要重新确认文件、参数链路或入口点

### 情况 C：实现内容大体正确，但代码结构不稳
- 回到：Implementer
- 说明：做局部修整，不必重新定位

### 情况 D：业务边界本身又不清楚了
- 回到：Brainstorming / Writing Plans
- 说明：不是实现错，而是上游澄清不够

也就是说，review 不只是说“不过”，还必须指出：

- 回退到哪一层
- 为什么回退到那一层

---

## 8. Review 与 Verification 的边界

## Review

负责：
- 阶段门禁
- 判断当前子阶段能不能继续
- 防止错误继续扩散

## Verification

负责：
- 最终交付前的完整验真
- 场景、交互、参数、完成度的全局检查

因此：

- review 是过程门禁
- verification 是最终验收

不能把 verification 当成“最后补救 review”的地方。

---

## 9. `1543024` 的推荐回环示例

### Task A
只改 `homeHeader.vue`

### Review A
Gate 1：
- 是否真的把组合条件前移到主搜索区
- 是否只在已出院显示

Gate 2：
- 是否破坏了主搜索区结构
- 是否产生重复节点 / 错误方法结构

若不通过：
- 返回 Implementer 修 `homeHeader.vue`
- 不允许继续碰 `searchComp.vue`

### Task B
只改 `searchComp.vue`

### Review B
Gate 1：
- 是否只处理了重复展示问题
- 是否没有扩大到其他过滤项逻辑

Gate 2：
- 是否没有误伤现有筛选结构
- 是否没有引入无关代码片段

若不通过：
- 返回 Implementer 或 Locator
- 不允许直接进入 verification

### Verification
在前面两轮 review 都通过后，再做完整验证。

---

## 10. 与 runtime 的关系

review gate 回环规则一旦建立，runtime 文件的作用会更清楚：

- `task-plan.md`：记录当前处于哪个阶段
- `findings.md`：支撑 review 判断入口与依据是否正确
- `progress.md`：记录 implementer 到底做了什么
- `outcome.md`：记录本阶段是否放行到下一步

也就是说：

**runtime 让 review 有证据，review 让 runtime 有阶段边界。**

---

## 11. 最终结论

从现在开始，护士站框架中的 review 不应再被当成“最后看看”。

默认规则应改为：

1. 一个实现子任务结束
2. 必须进入 review
3. review 不过就回环
4. review 通过才继续
5. 所有子阶段完成后，才进入 verification

这会让流程看起来多了一道门，但实际上是在显著降低：

- 错误扩散成本
- 主控救火成本
- 多轮续接混乱成本

它不是让流程更重，而是让执行真正可控。

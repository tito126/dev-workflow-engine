# acceptance — 默认验收收口

把实现结果、需求匹配、效果验证、复盘信号收成一个默认收口节点。

## 目标

默认情况下，不再把 `verification` 和 `review-gate` 拆成两个必经文件。

`acceptance.md` 要一次回答清楚：

1. 代码是否完成
2. 需求是否完成
3. 效果是否已验证
4. 还有哪些未验证点
5. 是否需要进入 retrospective 或 deep review
6. 是否产出了应沉淀到中央 `pattern-ledger.md` 的模式

## 适用方式

- light 任务：实现后直接进入 `acceptance.md`
- medium 任务：`planning / locator / implementer` 后统一进入 `acceptance.md`
- heavy 任务：先用 `acceptance.md` 做默认收口；只有满足触发条件时，再进入 `retrospective.md` 或 `review-gate.md`

## 核心规则

### 1. 必须拆开三件事

绝不把下面三件事混写成一个笼统的“已完成”：

- 代码完成
- 需求完成
- 效果已验证

### 2. 文案类任务必须双拆

当任务包含说明文案、提示文案、帮助文本、配置说明或产品给定原文时，至少拆开判断：

- 位置 / 承载方式是否通过
- 文案内容是否按原文或约定口径落地

### 3. 证据等级必须显式写

- A：真实环境 / 真实样本 / 实测结果
- B：代码证据 / 静态分析 / 结构化 diff
- C：业务口头确认 / 聊天确认

若当前只有 B / C 级证据，不要宣称“效果已验证”。

### 4. retro 信号要在这里收集

收口时顺手判断：

- 是否发生返工
- 是否发生阶段回退
- 是否新增可复用规则
- 是否暴露 skill 流程缺口
- 是否需要 controller 手工补锅
- 是否需要 deep review / retrospective

### 5. pattern 候选优先记中央台账

如果本次任务长出了跨任务可复用的规则，优先把候选条目补到：

`work-system/frameworks/nurse-station/pattern-ledger.md`

而不是只留在当前任务目录里。

## 进入 deep review / retrospective 的触发条件

### 进入 `review-gate.md`

满足任意一条即可：
- 高风险改动，需要多闸门评审
- 需求是否完成存在争议
- 多仓 / 多角色协作后需要正式结论
- 当前 acceptance 结论不足以支撑上线或交付

### 进入 `retrospective.md`

满足任意一条即可：
- 发生返工或阶段回退
- 出现新的可复用规则
- skill 流程被绕开或失效
- 路由 / 基线 / 验收机制被真实任务打脸
- controller 多次手工补锅才能继续

## 输出模板

```text
# acceptance - {taskId}

## 收口结论
- 运行时路径：
- 已审阅输入：
- 代码完成：是 / 否
- 需求完成：是 / 否
- 效果已验证：是 / 否
- 证据等级：A / B / C
- 是否接受为完成：是 / 否
- 若不接受，回退阶段：

## 需求与实现匹配
- 已满足的成功锚点：
- 未满足的成功锚点：
- 范围是否越界：
- 文案类任务的“位置验收”结论：
- 文案类任务的“内容验收”结论：

## 风险与未验证点
- 风险：
- 未验证点：
- 是否需要补真实环境验证：

## retro signals
- 是否返工：是 / 否
- 是否回退阶段：是 / 否
- 是否发现新规则：是 / 否
- 是否发现流程缺口：是 / 否
- 是否需要 controller 手工补锅：是 / 否
- 是否进入 review-gate：是 / 否
- 是否进入 retrospective：是 / 否

## pattern candidates
- 是否应追加到中央 pattern-ledger：是 / 否
- 候选模式标题：
- 候选规则：
- 影响阶段：
- 来源证据：

## 备注
- 
```

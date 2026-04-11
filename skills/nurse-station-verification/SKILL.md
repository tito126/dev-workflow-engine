---
name: nurse-station-verification
description: 当护士站实现结果或代码定位结论需要在验收前，对照需求意图、展示规则、场景约束和执行声明做核对时使用。触发场景包括实现完成后、locator 产出结论后，或最终向用户交付前。
---

# 护士站结果验证

验证结果要对照需求本身，而不是只对照 implementer 的总结。验证产出的核心价值不仅是"通过/不通过"，还在于为后续 review-gate 和用户交付提供可直接复用的验证证据。

## 目标

通过核对真实被请求的行为是否被满足，防止"假完成"。同时把验证结论结构化，避免后续 review-gate 重新从聊天里回捞上下文。

## 核心规则

验证阶段不允许猜测验收依据。

验证阶段必须显式区分三件事：
- 代码是否完成
- 需求是否满足
- 效果是否已验证

这三件事可以同时为真，也可以只成立其中一部分，不能混写成一个笼统的“已完成”。

如果任务没有清晰的编码前验收锚点，就不要把它标记为完成，而应把它退回到更前面的合适阶段。

默认退回顺序应遵循护士站流程：
`nurse-station-brainstorming -> nurse-station-writing-plans -> execution -> nurse-station-verification`

如果验收锚点缺失，是因为之前没有显式经过 brainstorming checkpoint，那么应先退回 `nurse-station-brainstorming`，而不是假装这只是实现质量问题。

## 验证通过前必须具备的内容

至少应能指向：
- 已澄清的业务目标
- 场景约束
- 范围内 / 范围外边界
- 一个或多个明确验收检查点

如果前序 planning 已产出 success anchors，优先把它们作为验证的对照基线，而不是自己重新从聊天中推断验收标准。

对于 UI / 交互类任务，还应额外具备：
- 页面或模块范围
- 被改动的控件或行为
- 位置或相对顺序预期
- 可见性规则
- 如有必要，旧行为保留 / 移除规则

如果这些内容缺失，验证必须明确指出，并拒绝签收完成。

## 验证清单

### 需求匹配
- 实现是否匹配已澄清的业务目标？
- 是否解决了目标场景，而不是旁支场景？
- 是否遵守了非目标边界？
- 编码前定义的验收检查点是否真的被满足？
- 若前序阶段已产出 success anchors，是否逐条对照？

### UI / 交互匹配
- 控件是否只出现在正确场景？
- 必要的交互模式是否被保留？
- 如果控件位置发生变化，重复暴露是否被移除？
- 控件位置或相对顺序是否符合已确认预期？

### 技术匹配
- 参数映射是否被正确保留？
- 目标文件 / 模块是否与计划一致？
- 是否存在明显回归风险？

### 验收依据诚实性
- 可用的验收锚点有哪些？
- 哪些检查是直接验证过的？
- 哪些只是推断，尚未真正验证？
- 哪些仍需要人工确认？
- 哪些内容因上游 requirement-fit 证据缺失而无法验证？

### 证据等级
- A：真实环境 / 真实样本 / 实测结果 / 上线后观察证据
- B：代码证据 / 静态分析 / 结构化 diff / 文件级证据
- C：业务口头确认 / 聊天确认 / 规则性判断

如果某项结论只拿到了 B 或 C 级证据，就不要把它写成“效果已验证”。

## 输出格式

### 验证结果
- Runtime path:
- Outcome update:
- Acceptance anchors reviewed:
- Missing acceptance anchors:
- Return stage if failed:
- Evidence level:
- Requirement fit:
- Scene fit:
- Technical fit:
- Code complete:
- Requirement complete:
- Effect verified:
- Risks:
- Unverified points:
- Verification evidence summary:
- Accept as complete: yes/no

### 可复用产物
验证结果应默认充当 review-gate 的输入，而不是只留在聊天里。
- "Acceptance anchors reviewed" 应直接对齐 planning 阶段产出的 success anchors
- "Evidence level" 应说明当前结论主要依赖 A / B / C 哪一级证据
- "Risks" 和 "Unverified points" 应供 review-gate 当作审查起点
- 如果验证不通过，"Return stage" 应明确指出该退回到哪个阶段、带着什么问题

## 集成关系

在实现完成后、最终交付前使用。
对于 runtime 跟踪任务，应把验证结果组织成可更新 runtime outcome 状态的结构，而不是只留在聊天里。
如果任务属于 `medium` / `heavy`，且使用过外部执行器，优先同时阅读 plan / result / 其他运行证据，而不是只相信总结文本。
若验证对象依赖 `ACP opencode` 链路且环境为 Windows，应默认认可 `2026-04-08` 记录的本地 ACP 手动补丁为当前前提；若后续链路失效，先检查补丁是否被覆盖。
如果验证失败是因为验收锚点缺失，应返回 requirement-fit checkpoint 或 planning，而不是假装这只是实现质量问题。
如果验证失败是因为执行结果不正确，应通过 `nurse-station-subagent-execution` 派发一个聚焦的纠偏任务。
完整的阶段顺序和产物落地约定，见 `nurse-station-orchestrator`。

---
name: work-control
description: 面向日常职业执行的聊天驱动型工作控制技能。适用于用户希望记录临时工作、跟踪项目、排序每日优先级、编写每日总结、规范项目控制习惯，或围绕任务收集、项目档案、每日聚焦、每日总结与可追踪 Markdown 记录建立可复用 SOP 的场景。
---

# 工作控制

用这个 skill 在日常聊天里运行一套轻量但可持续的工作控制系统。把聊天视为输入层，把 `work-system/` 视为运行记录层，把这个 skill 视为操作标准。

中文高频触发默认有效，不要因为用户没有说英文而降级为普通聊天。像 `今日聚焦`、`今天聚焦`、`今天重点`、`今天先做什么`、`排一下今天优先级` 这类表达，默认按 `Daily Focus` 处理；像 `今日总结`、`今天总结`、`收个尾`、`做个今天的总结` 这类表达，默认按 `Daily Summary` 处理。

凡是出现明确时间节点或时间窗口的中文表达，也默认进入时间路由判断。像 `提醒我`、`下周要讲`、`周四要分享`、`某天前交付`、`前一天提醒我一下`、`这周要完成` 这类表达，优先判断是否写入 `work-system/inbox/reminders.md`，并在合适时机通过 `Daily Summary / Daily Focus` 主动抬头，而不是默认等到时间点机械提醒。

## 快速开始

当这个 skill 适用时，按下面顺序推进：
1. 判断这条消息属于仅聊天、候选记录，还是正式记录。
2. 如果属于正式记录，写入 `work-system/` 下对应文件。
3. 如果它属于一个长期推进事项，更新匹配的项目档案。
4. 如果用户要求排优先级，创建或更新今天的 Daily Focus 文件。
5. 如果用户要求收尾总结，创建或更新今天的 Daily Summary 文件。

按需阅读这些参考文件：
- `references/file-map.md`，查看记录落点
- `references/trigger-phrases.md`，查看自然语言触发语
- `references/usage-scenarios.md`，查看常见交互场景
- `work-system/sop/collaboration-sop.md`，查看端到端操作规则
- `work-system/sop/record-rules.md`，查看记录纪律与防杂乱规则

## 核心能力

### 1. 在不丢线索的前提下记录临时工作

对领导要求、会议跟进、提醒候选项、早期风险信号等短周期但重要的事项，使用 `work-system/inbox/temporary-work-pool.md`。

优先写入 temporary pool 的场景：
- 事项重要，但结构还不完整
- 暂时看不清该归到哪个项目
- 用户希望先快速记下，之后再整理

不要把 temporary pool 变成永久档案。要么继续推进、要么关闭、要么归档。

如果用户表达里已经带有明确时间节点、时间窗口、会前准备、交付前提醒等信息，优先考虑 `reminders.md`，而不是先落到 temporary pool。

### 2. 维护项目档案

每个活跃项目在 `work-system/projects/active/` 下使用一个 Markdown 文件。

保持这些部分是最新状态，因为它们直接影响判断质量：
- Goal
- Value
- Current Progress
- Milestones
- Risks And Blockers
- Next Action
- Latest Update

当用户更新项目时，优先做简洁、带状态的修改，不要把原始聊天内容整段倾倒进去。

### 3. 产出 Daily Focus

当用户要求安排当天工作时，除非用户另有说明，默认按这个顺序排序：
1. 今天或明天到期的事项
2. 紧急领导需求
3. 会卡住他人推进的阻塞项
4. 高价值里程碑
5. 重要但不紧急的维护类工作

把结果写入 `work-system/daily/focus/YYYY-MM-DD.md`，使用 `work-system/templates/daily-focus-template.md` 模板。

列表要刻意保持简短：
- 一个核心目标
- 三个最高优先级事项
- 少量次级跟进项
- 明显可见的风险观察项

在判断什么应该进入今天的 focus 时，不要只看截止时间和旧的常驻优先级。也要检查过去 24 小时里，活跃项目是否出现了高价值的新进展，尤其是像新协作路径被验证、阻塞链被打开、此前不确定的方法已证明可行这类信号。如果有，要重新评估它是否值得进入今天的 Top 3。

强触发规则：
- 像 `今日聚焦`、`今天聚焦`、`今天重点`、`今天先做什么`、`排一下今天优先级` 这样的请求，都是直接的 `Daily Focus` 触发语
- 不要因为觉得还可以补背景，就把它降级成普通聊天
- 默认行为是：读取相关 `work-system` 输入，生成当天文件，然后再回复结果
- 只有在缺少关键事实、导致正式 `Daily Focus` 根本无法产出时，才补一个很短的追问
- 不要只停在引导式提问，而不创建正式记录

### 4. 产出 Daily Summary

当用户要求做每日收尾时，写的是管理型总结，不是流水账日记。

把结果写入 `work-system/daily/summary/YYYY-MM-DD.md`，使用 `work-system/templates/daily-summary-template.md` 模板。

应包含：
- 已完成工作
- 项目推进变化
- 未完成或延期事项
- 风险与阻塞
- 明天可能的优先级
- 可直接用于周报或向上汇报的表述

### 5. 维持可追踪的记录纪律

正式项目记录应该主要落在 `work-system/`，而不是主要写在 `MEMORY.md`。

`MEMORY.md` 只用于保存长期有效的个人上下文、偏好，以及少量长期决策。不要让项目运行状态漂到 memory，变成主要事实来源。

### 6. 正确路由时间敏感事项

当用户提到明确时间节点、近期待办截止、或准备窗口时，优先把它视为提醒路由信号。

默认路由顺序：
- 如果消息主要围绕时间节点或准备窗口，写入或更新 `work-system/inbox/reminders.md`
- 如果它同时属于一个持续推进的事项，把提醒和相关项目关联起来
- 如果提醒已经进入近窗期，再在 `Daily Summary` 或 `Daily Focus` 里重新抬头

不要默认切到 `cron` 或独立提醒，除非用户明确要求精确时间提醒。

## 操作规则

### 默认记录行为

- 不要保存每一条聊天消息。
- 只保存具有管理价值的信息。
- 使用自然语言触发，不要求斜杠命令。
- 优先按语义意图判断，而不是死板关键词匹配。
- 把用户明确表达如 `record this`、`add to project`、`remind me`、`this is a rule`、`do not file this yet` 视为更强的路由信号。
- 把明确的中文工作控制表达，如 `今日聚焦`、`今天重点`、`今天先干什么`、`今日总结`、`记一下`、`加到项目里`、`记成风险`，同样视为强路由信号。
- 把明确的中文时间表达，如 `提醒我`、`下周要讲`、`周四要分享`、`某天前交付`、`前一天提醒我`、`这周要完成`，视为强提醒路由信号。
- 当目标文件、项目名、截止时间或系统层级存在实质性不清楚时，补一个简短追问。
- 如果仍有歧义，优先先做轻量记录，不要过早创建正式记录。

### 什么算正式记录

以下几类内容需要被记录并结构化：
- task
- progress
- risk
- milestone
- value
- decision

### 默认不进入正式记录的内容

默认不要归档：
- 随意闲聊
- 重复复述
- 没有行动或决策价值的半成型聊天
- 之后无法追踪的模糊提法

## 文件输出

直接使用这些文件和目录：
- `work-system/inbox/temporary-work-pool.md`
- `work-system/inbox/ideas.md`
- `work-system/inbox/reminders.md`
- `work-system/projects/index.md`
- `work-system/projects/active/`
- `work-system/projects/archived/`
- `work-system/daily/focus/`
- `work-system/daily/summary/`
- `work-system/templates/`

## 推荐交互模式

这个 skill 应支持的用户请求示例：
- `Record this: leader wants a draft by next Wednesday.`
- `Add to project Interface Governance: confirmed current environment limits today.`
- `Record as risk: the external team has not confirmed resources.`
- `Add value: this project mainly reduces complaints, not only improves efficiency.`
- `Plan today's focus.`
- `Do today's summary.`
- `今日聚焦。`
- `排一下今天优先级。`
- `今天先做什么？`
- `今日总结。`
- `提醒我周四前收一版分享提纲。`
- `这个下周要讲，前一天提醒我一下。`

## 维护

当系统演进时：
- 如果规则变了，先更新 SOP
- 如果结构变了，更新模板
- 保持项目名称稳定
- 避免把同一内容无目的地重复存到多个文件，除非这种重复有明确用途

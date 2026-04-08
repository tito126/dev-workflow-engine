# Trigger Phrases

Use natural language. Slash commands are optional.

## Capture triggers
- `record this`
- `记一下`
- `记录一下`
- `put this in the temporary pool`
- `放到临时池`
- `先放临时池`
- `add to project <name>`
- `加到项目 <name>`
- `更新项目 <name>`
- `update progress`
- `更新进展`
- `更新专项进度`
- `回写专项进展`
- `记录阶段性成果`
- `补充执行结论`
- `同步这轮结果`
- `record as risk`
- `记成风险`
- `记录为风险`
- `add milestone`
- `加个里程碑`
- `add value`
- `补充价值`
- `remind me`
- `提醒我`
- `前一天提醒我`
- `到时候提醒我`
- `临近了提醒我`
- `这周提醒我留意`
- `create a project`
- `建个项目`
- `建个专项`

## Reminder-routing triggers
- `下周要讲`
- `周四要分享`
- `某天前交付`
- `这周要完成`
- `下周要完成`
- `某天要汇报`
- `某天要评审`
- `某天要开会`
- `会前提醒我`
- `前一天提醒我一下`
- `提前提醒我`
- `留意这个时间点`
- `进入准备窗口了`

## Review triggers
- `plan today's focus`
- `rank today's priorities`
- `今日聚焦`
- `今天聚焦`
- `今天重点`
- `今天先做什么`
- `今天先干什么`
- `排一下今天优先级`
- `排个今日重点`
- `梳理一下今天要做什么`
- `do today's summary`
- `今日总结`
- `今天总结`
- `做个今日总结`
- `收个尾`
- `summarize project <name>`
- `总结一下项目 <name>`
- `show what is still open`
- `还有什么没关`
- `还有什么开着`
- `list important forgotten items`
- `看看有没有遗漏的重要事项`

## Clarification triggers
If the project name, due date, or target destination is unclear, ask one short follow-up before formal capture.

## Routing Notes
- Treat the Chinese review phrases under `Review triggers` as strong triggers, not weak hints.
- `今日聚焦` and similar wording should default to `Daily Focus`, even when the user does not explicitly say `plan` or `priority`.
- `今日总结` and similar wording should default to `Daily Summary`, even when the user does not explicitly say `summary`.
- Treat the phrases under `Reminder-routing triggers` as default signals for `work-system/inbox/reminders.md`.
- If a message contains both a time node and an ongoing project, keep the project link but route the time pressure through `reminders.md` first.
- For near-term items, prefer surfacing them again in `Daily Summary` and `Daily Focus` instead of defaulting to `cron`.

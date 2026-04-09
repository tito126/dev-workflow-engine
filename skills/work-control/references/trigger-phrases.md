# 触发语

使用自然语言即可，斜杠命令只是可选项。

## 记录触发语
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

## 提醒路由触发语
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

## 回顾触发语
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

## 澄清触发
如果项目名、截止时间或目标落点不清楚，在正式记录前补一个简短追问。

## 路由说明
- 把 `回顾触发语` 里的中文表达视为强触发，而不是弱提示。
- `今日聚焦` 及类似表达，应默认路由到 `Daily Focus`，即使用户没有明确说 `plan` 或 `priority`。
- `今日总结` 及类似表达，应默认路由到 `Daily Summary`，即使用户没有明确说 `summary`。
- 把 `提醒路由触发语` 里的表达默认视为写入 `work-system/inbox/reminders.md` 的信号。
- 如果一条消息同时包含时间节点和持续中的项目，保留项目关联，但时间压力优先经由 `reminders.md` 路由。
- 对近期待办，优先在 `Daily Summary` 和 `Daily Focus` 中再次抬头，而不是默认切到 `cron`。

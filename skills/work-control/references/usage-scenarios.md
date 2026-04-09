# 使用场景

## 1. 记录一个临时任务

用户说：
`Record this: leader wants a draft by next Wednesday.`

期望行为：
- 在 `work-system/inbox/temporary-work-pool.md` 中新增一条事项
- 将其标记为 task
- 如果带有时间信息，保留时间节点
- 如果截止时间重要，建议补充提醒

## 2. 记录一个想法

用户说：
`Put this in the temporary pool: split project C into two phases.`

期望行为：
- 根据成熟度，将其记录到 `ideas.md` 或 `temporary-work-pool.md`
- 备注它可能带来的价值
- 在确认前，保持它与正式项目结论分离

## 3. 更新项目进展

用户说：
`Add to project Interface Governance: confirmed environment limits today.`

期望行为：
- 更新 `projects/active/` 下对应的项目档案
- 刷新 `Latest Update`
- 如果新信息改变了计划，同步更新 `Next Action`

## 4. 记录一个风险

用户说：
`Record as risk: external team still has not confirmed resources.`

期望行为：
- 如果项目映射清楚，更新项目风险部分；如果不清楚，先写入 temporary pool
- 如果排期影响很明显，顺手指出可能影响

## 5. 规划今日聚焦

用户说：
`Plan today's focus.`

以下表达也适用：
- `今日聚焦。`
- `今天重点。`
- `排一下今天优先级。`
- `今天先做什么？`

期望行为：
- 读取待处理的临时事项与活跃项目信号
- 创建或更新 `daily/focus/` 下今天的文件
- 列表保持简短并带排序
- 把这些中文表达视为直接的 Daily Focus 请求，而不是普通聊天
- 如果某个活跃项目在过去 24 小时出现了有意义的新进展，或有新验证的方法跑通，即使它不是最近的日历截止项，也要重新评估它是否该进入今天的 focus

## 6. 吸收一个正在进行中的现有项目

用户说：
`把门诊护士站详设纳入新体系。`

期望行为：
- 不要把历史材料整包复制进新系统
- 在 `projects/active/` 下创建一个项目档案
- 将项目概括成基础项目画像
- 把已有产出文件作为引用式交付物挂上去
- 后续把这个档案作为唯一更新点

## 7. 编写今日总结

用户说：
`Do today's summary.`

以下表达也适用：
- `今日总结。`
- `今天总结。`
- `收个尾。`
- `做个今天的总结。`

期望行为：
- 总结已完成工作、项目推进、未关闭事项与风险
- 创建或更新 `daily/summary/` 下今天的文件
- 保留适合用于汇报的措辞

## 8. 正确路由中文 work-control 请求

用户说：
`今日聚焦，先读 work-control。`

期望行为：
- 识别 `今日聚焦` 是强 `Daily Focus` 触发语
- 如果用户还要求先阅读或先对齐方法，就先读 skill，再继续进入 focus 处理
- 不要因为触发语是中文，就误判成普通聊天

## 9. 把中文时间节点请求路由到 reminders

用户说：
`这个下周要讲，前一天提醒我一下。`

期望行为：
- 识别这是提醒路由请求，而不是普通聊天
- 写入或更新 `work-system/inbox/reminders.md` 中的条目
- 保留时间节点与提前提醒的要求
- 除非用户明确要求精确时间调度，否则优先通过后续 `Daily Summary / Daily Focus` 抬头来处理提醒

## 10. 正确路由准备窗口请求

用户说：
`周四要分享，今天开始进入准备窗口。`

期望行为：
- 同时识别明确时间节点与准备窗口
- 将时间压力路由到 `reminders.md`
- 如果这件事今天也值得关注，就同步抬到 `Daily Focus`
- 除非用户明确要求，不要依赖精确时间提醒机制

## 11. 把昨天的真实进展抬进今天的 focus

用户说：
`昨天 APC 联调 Codex 已经有实际进展，今天别漏掉。`

期望行为：
- 把它视为项目进展信号，而不只是评论
- 用新的已验证进展和下一步动作更新相关活跃项目
- 在生成 `Daily Focus` 时，重新评估这个新进展是否值得进入今天的 Top 3 或项目信号
- 不要只依赖截止时间远近，如果这个新进展在方法层或执行层有明显价值，也应给予足够权重

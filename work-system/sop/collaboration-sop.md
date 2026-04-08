# Work Control Collaboration SOP

## Purpose

Use this SOP to run a chat-driven work control system inside day-to-day conversations. The goal is to capture important work information without forcing manual system switching, while keeping records traceable, structured, and reusable.

## Core Principles

- Use chat as the input surface.
- Store formal records in files, not only in memory.
- Do not archive every message by default.
- Capture only information with management value.
- Keep the system light enough to sustain every day.

## System Modules

保持结构稳定，优先在现有模块内处理问题，不为单次想法频繁新增层级。

## 存量专项收编

当一个专项在新体系建立前已经推进过，不要把旧文件整包迁移进 `work-system/`。使用收编方式纳入：

1. 确认专项主名称，避免后续多名称并存。
2. 提炼专项基本画像，先压缩出专项定义、当前阶段、当前成果、下一步重点、风险或待确认、价值说明、外部依赖。
3. 在 `work-system/projects/active/` 建立专项主档案。
4. 在主档案中挂接原有产出物路径，不复制全部历史文件。
5. 从收编完成后开始，把后续进展统一更新到专项主档案。

### 1. Temporary Work Pool

Use for quick capture of items that should not be lost yet are not fully structured.

Typical content:
- leader's temporary assignments
- meeting follow-ups
- ideas and solution fragments
- pending confirmations
- early risk signals
- reminders

### 2. Project Dossier

Use for long-running initiatives that need continuity, status tracking, milestone control, risk awareness, and value review.

### 3. Daily Focus

Use to decide what deserves attention today, based on priority, urgency, dependency, and project value.

### 4. Daily Summary

Use to compress the day's work into a reusable daily record for handoff, weekly reporting, and next-day continuation.

## Information Tiers

### Tier A: Conversation Only

Keep content in the current conversation only when it is exploratory or has no management value.

Examples:
- rough discussion with no conclusion
- quick opinion checks
- temporary wording attempts
- general chat

### Tier B: Candidate Record

Treat content as a candidate when it appears important but has not been formally archived yet.

Examples:
- a likely task without confirmed owner
- a possible risk without impact confirmation
- a project idea not yet approved
- an important reminder without a due date

### Tier C: Formal Record

Write content into the file system when it belongs to one of these categories:
- task
- progress update
- risk or blocker
- milestone or time commitment
- value statement
- project decision

## Record Triggers

Use natural-language trigger phrases. Slash commands are optional and not required.

### Formal capture triggers

Use phrases like:
- record this
- 记一下
- 记录一下
- put this in the temporary pool
- 放到临时池
- 先放临时池
- add to project <name>
- 加到项目 <name>
- 更新项目 <name>
- update progress
- 更新进展
- record as risk
- 记成风险
- 记录为风险
- add milestone
- 加个里程碑
- add value
- 补充价值
- remind me
- 提醒我
- 前一天提醒我
- create a project
- 建个项目
- 建个专项

### Review triggers

Use phrases like:
- plan today's focus
- rank today's priorities
- 今日聚焦
- 今天聚焦
- 今天重点
- 今天先做什么
- 今天先干什么
- 排一下今天优先级
- do today's summary
- 今日总结
- 今天总结
- 收个尾
- summarize project <name>
- 总结一下项目 <name>
- show what is still open
- 还有什么没关
- list important forgotten items
- 看看有没有遗漏的重要事项

### Reminder-routing triggers

Use phrases like:
- 下周要讲
- 周四要分享
- 某天前交付
- 这周要完成
- 下周要完成
- 某天要汇报 / 评审 / 开会
- 会前提醒我
- 前一天提醒我一下
- 提前提醒我
- 留意这个时间点
- 进入准备窗口了

## Assistant Behavior Rules

### Default behavior

- Read the message semantically.
- Identify whether the content is a task, progress update, risk, milestone, value statement, or decision.
- If a trigger is explicit, write to the correct file.
- Treat clear Chinese operational phrases as equally strong triggers; do not downgrade them into ordinary chat only because they are not written in English.
- If the message contains a clear time node or preparation window, route it through `reminders.md` first unless the user explicitly wants exact-time scheduling.
- If the message looks important but the destination is unclear, ask one short clarification or place it in the temporary work pool when safe.

### Do not do by default

- Do not save every message.
- Do not treat casual chat as formal record.
- Do not create a new project without clear naming.
- Do not put project run-state into MEMORY.md as the primary source of truth.

## Naming Rules

### Project naming

- Use one stable name per project.
- Avoid aliases like "that project" or "the previous one" in formal records.
- Prefer short Chinese names or consistent Chinese-plus-English names.
- Once a project is created, keep the filename and header aligned.

### Daily files

Use ISO date filenames:
- `daily/focus/YYYY-MM-DD.md`
- `daily/summary/YYYY-MM-DD.md`

## Flow Rules

### Flow 1: Temporary work item

Conversation -> temporary work pool -> one of:
- complete and close
- convert into project update
- convert into reminder
- archive as no longer needed

### Flow 2: Project update

Conversation -> project dossier -> optionally:
- mark as today's focus
- include in daily summary
- carry into weekly review later

### Flow 3: Daily focus

Temporary pool + project dossiers -> daily focus -> execution

Also pull in reminder items that have entered a near-term preparation or delivery window.

### Flow 4: Daily summary

Conversation records + today's focus + project changes -> daily summary -> project dossier backfill

Also review `reminders.md` for items that should be proactively surfaced before the time node arrives.

## 专项类型与里程碑颗粒度

里程碑的颗粒度要跟专项类型匹配，不追求统一得过细。

### 详设/方案类专项

适用于详细设计、方案撰写、章节输出、文档型产出为主的专项。

里程碑建议按章节、模块或阶段性文档产出记录，例如：
- 完成 `4.2.2 门诊患者列表`
- 推进 `4.2.5 医嘱处理`
- 完成某章节评审版输出

管理重点：
- 当前做到哪个章节或模块
- 下一章是什么
- 哪些口径待确认
- 当前阶段的主要产出是什么

不要为了“看起来精细”把这类专项拆成过多小任务，否则会因为频繁改动导致维护成本过高。

### 开发/落地类专项

适用于开发实现、联调、测试、上线、验收等以可验证交付节点为主的专项。

里程碑建议按交付阶段和关键节点记录，例如：
- 完成需求确认
- 完成技术方案评审
- 完成开发
- 完成联调
- 完成测试
- 完成上线
- 完成验收

管理重点：
- 当前卡在哪个阶段
- 哪个依赖方在阻塞
- 时间节点是否受影响
- 是否已满足进入下一阶段的条件

## Priority Logic for Daily Focus

Rank by this order unless the user says otherwise:
1. hard deadline today or tomorrow
2. leader-assigned urgent work
3. blocked project that unblocks others
4. high-value project milestone
5. important but non-urgent maintenance work

When ranking, consider:
- deadline pressure
- business value
- dependency impact
- leadership attention
- effort versus outcome

## Daily Rhythm

### Morning or start of work

Use Daily Focus.

Expected outcome:
- one core goal
- top three focus items
- a small list of secondary follow-ups
- visible risks for today

### End of day

Use Daily Summary.

Expected outcome:
- completed work
- project progress
- unclosed items
- blockers and risks
- tomorrow's likely priorities

## What Goes Where

- `work-system/inbox/temporary-work-pool.md`: quick-capture operational items
- `work-system/inbox/ideas.md`: ideas worth revisiting and waiting for routing
- `work-system/inbox/reminders.md`: items with explicit time nodes, windows, or near-term timing pressure
- `work-system/projects/active/`: ongoing project dossiers
- `work-system/projects/archived/`: finished, paused, or canceled projects
- `work-system/daily/focus/`: daily focus files
- `work-system/daily/summary/`: daily summary files

## 三块协调规则

当前工作系统里，`ideas.md`、`reminders.md`、`projects` 不是三个并列待办池，而是三种不同职责的入口。

### 1. `ideas.md` 的职责

`ideas.md` 用于承接“值得保留，但暂未决定是否正式推进”的方向、机会点和设想。

适合进入 `ideas.md` 的内容：
- 方向型想法
- 新工具或新 skill 设想
- 还未确认是否要投入的方案机会
- 当前先记住、后续再判断的潜在线索

关键规则：
- `ideas.md` 不是长期沉底仓库，而是“待分流池”
- idea 后续可以直接进入 `projects`，不要求必须先升级到 `reminders.md`
- idea 也可以继续保留观察、转成 reminder、或明确归档
- 后续应在每日总结中择机回看，避免石沉大海

### 2. `reminders.md` 的职责

`reminders.md` 用于承接“已经存在明确时间节点、时间窗口或临近压力”的事项。

适合进入 `reminders.md` 的内容：
- 本周内要完成的事项
- 某天要开会、汇报、评审、答辩的事项
- 已有明确时间窗口，但尚未形成完整项目上下文的事项
- 虽未进入当天执行，但需要在未来几天持续抬头关注的事项

关键规则：
- `reminders.md` 不是自动提醒器，也不以 `cron` 为默认处理方式
- 它的主要价值是给助手在“今日总结 / Daily Focus”中主动抬头使用
- 对于临近事项，更重要的是在前一天总结里主动提醒，在当天聚焦里显性列出，而不是等到时间点再机械提醒

### 3. `projects` 的职责

`projects` 用于承接已经决定持续推进、需要积累上下文、需要反复更新进度、风险和下一步的事项。

适合进入 `projects` 的内容：
- 已明确要持续推进的专项或项目
- 需要保存目标、当前进度、风险、下一步、里程碑的事项
- 如果不建档就会反复丢失上下文、反复解释背景的事项

关键规则：
- 一旦某事项需要连续几轮推进，就不要只停留在 `ideas` 或 `reminders`
- `projects` 负责承接长期上下文，不负责直接替代当天执行判断

## Daily Summary 与 Daily Focus 的调度职责

真正把三块入口串起来工作的，不是它们自己，而是 `Daily Summary`、`Daily Focus` 和助手的主动判断。

### 1. `Daily Summary` 的职责

在每天结束前，助手应主动查看：
- `reminders.md` 中是否存在临近节点
- `ideas.md` 中是否有值得抬头回看的方向
- `projects` 中是否有已进入关键时间窗口或风险窗口的事项

`Daily Summary` 不只是复盘当天做了什么，也要承担“提前抬头看临近事项”的职责。

### 2. `Daily Focus` 的职责

在生成当天聚焦时，助手应把以下内容显性化：
- 今天真正要推进的项目项
- 进入临近时间窗口的 reminder 项
- 已经从 idea 升级为今日值得投入的事项

`Daily Focus` 负责把“今天该占用注意力的内容”浮到台面，而不是按记录先后顺序机械罗列。

## 默认路由规则

### 1. 时间节点规则

凡是出现以下表达，应默认考虑进入 `reminders.md`：
- 本周内完成
- 下周要讲
- 某天前交付
- 某天评审 / 汇报 / 开会
- 临近但尚未成形、仍需要提前感知压力的事项

### 2. 持续推进规则

凡是出现以下特征，应默认考虑进入 `projects`：
- 需要连续几轮推进
- 需要积累上下文
- 需要持续更新进度、风险、下一步
- 后续若不建档就会反复丢失背景

### 3. 想法分流规则

`ideas.md` 中的内容，后续只能进入以下几种去向之一：
- 升级为 `projects`
- 转为 `reminders.md`
- 保留观察
- 明确归档

不得默认长期保持“open 但无人回看”的状态。

## Traceability Requirements

Every formal record should make it possible to answer:
- when did this enter the system
- what is the item or update
- which project it belongs to, if any
- what is the current status
- what should happen next

## Recommended Working Style

### Scenario: quick temporary task

Example input:
`Record this: leader wants a draft by next Wednesday.`

Expected handling:
- add to temporary work pool
- mark type as task
- mark status as pending
- note due timing if provided

### Scenario: update a project

Example input:
`Add to project Interface Governance: confirmed current environment limits today.`

Expected handling:
- update project dossier
- revise latest update and next action
- add risk if the new information changes delivery

### Scenario: clarify value

Example input:
`Add value: this project is mainly to reduce complaints, not only improve efficiency.`

Expected handling:
- update the value section in the project dossier
- carry the wording into future summaries when useful

### Scenario: ask for focus

Example input:
`Plan today's focus.`

Also applies to:
- `今日聚焦。`
- `今天重点。`
- `排一下今天优先级。`

Expected handling:
- read open temporary items and active project signals
- read near-term reminder items
- produce a ranked daily focus file
- keep the list intentionally short

### Scenario: ask for summary

Example input:
`Do today's summary.`

Also applies to:
- `今日总结。`
- `今天总结。`
- `收个尾。`

Expected handling:
- summarize completed work and project movement
- list unclosed items and risks
- proactively check whether near-term reminder items need to be surfaced
- produce a reusable written record

### Scenario: ask for advance reminder

Example input:
`这个下周要讲，前一天提醒我一下。`

Expected handling:
- route the item into `reminders.md`
- preserve the time node and the request for advance prompting
- rely on future `Daily Summary / Daily Focus` surfacing by default instead of assuming `cron`

## Memory Boundary

Use MEMORY.md for durable personal context, preferences, and a small number of long-term decisions. Do not use MEMORY.md as the operating ledger for project management. Project operations must stay in `work-system/`.

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
- put this in the temporary pool
- add to project <name>
- update progress
- record as risk
- add milestone
- add value
- remind me
- create a project

### Review triggers

Use phrases like:
- plan today's focus
- rank today's priorities
- do today's summary
- summarize project <name>
- show what is still open
- list important forgotten items

## Assistant Behavior Rules

### Default behavior

- Read the message semantically.
- Identify whether the content is a task, progress update, risk, milestone, value statement, or decision.
- If a trigger is explicit, write to the correct file.
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

### Flow 4: Daily summary

Conversation records + today's focus + project changes -> daily summary -> project dossier backfill

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
- `work-system/inbox/ideas.md`: ideas worth revisiting
- `work-system/inbox/reminders.md`: reminder candidates and due reminders
- `work-system/projects/active/`: ongoing project dossiers
- `work-system/projects/archived/`: finished, paused, or canceled projects
- `work-system/daily/focus/`: daily focus files
- `work-system/daily/summary/`: daily summary files

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

Expected handling:
- read open temporary items and active project signals
- produce a ranked daily focus file
- keep the list intentionally short

### Scenario: ask for summary

Example input:
`Do today's summary.`

Expected handling:
- summarize completed work and project movement
- list unclosed items and risks
- produce a reusable written record

## Memory Boundary

Use MEMORY.md for durable personal context, preferences, and a small number of long-term decisions. Do not use MEMORY.md as the operating ledger for project management. Project operations must stay in `work-system/`.

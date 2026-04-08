# Usage Scenarios

## 1. Capture a temporary task

User says:
`Record this: leader wants a draft by next Wednesday.`

Expected behavior:
- add an item to `work-system/inbox/temporary-work-pool.md`
- mark it as a task
- preserve timing if present
- suggest a reminder if the due date matters

## 2. Capture an idea

User says:
`Put this in the temporary pool: split project C into two phases.`

Expected behavior:
- record it in `ideas.md` or `temporary-work-pool.md` based on maturity
- note the possible value
- keep it separate from the formal project conclusion until confirmed

## 3. Update project progress

User says:
`Add to project Interface Governance: confirmed environment limits today.`

Expected behavior:
- update the relevant project dossier in `projects/active/`
- refresh `Latest Update`
- update `Next Action` if the new information changes the plan

## 4. Record a risk

User says:
`Record as risk: external team still has not confirmed resources.`

Expected behavior:
- update the project risk section or temporary pool if project mapping is unclear
- surface the likely schedule impact if obvious

## 5. Plan daily focus

User says:
`Plan today's focus.`

Also applies when the user says:
- `今日聚焦。`
- `今天重点。`
- `排一下今天优先级。`
- `今天先做什么？`

Expected behavior:
- read pending temporary work items and active project signals
- create or update today's file in `daily/focus/`
- keep the list intentionally short and ranked
- treat these Chinese phrases as direct Daily Focus requests instead of general conversation
- if an active project had meaningful progress or a newly validated method in the last 24 hours, re-evaluate whether it should be surfaced in today's focus even if it is not the nearest calendar deadline

## 6. Absorb an existing in-flight project

User says:
`把门诊护士站详设纳入新体系。`

Expected behavior:
- do not copy all historical material into the new system
- create one project dossier in `projects/active/`
- summarize the project into a basic project profile
- attach existing output files as referenced deliverables
- use the dossier as the single update point going forward

## 7. Write daily summary

User says:
`Do today's summary.`

Also applies when the user says:
- `今日总结。`
- `今天总结。`
- `收个尾。`
- `做个今天的总结。`

Expected behavior:
- summarize completed work, project movement, open items, and risks
- create or update today's file in `daily/summary/`
- preserve wording useful for reporting

## 8. Route Chinese work-control prompts correctly

User says:
`今日聚焦，先读 work-control。`

Expected behavior:
- recognize `今日聚焦` as a strong `Daily Focus` trigger
- if the user also asks to read or align on the method first, read the skill and then continue into focus handling
- do not misclassify the request as ordinary chat just because the trigger phrase is in Chinese

## 9. Route Chinese time-node prompts into reminders

User says:
`这个下周要讲，前一天提醒我一下。`

Expected behavior:
- recognize this as a reminder-routing request, not ordinary chat
- write or update an item in `work-system/inbox/reminders.md`
- preserve the time node and the request for advance prompting
- prefer handling the reminder through future `Daily Summary / Daily Focus` surfacing unless the user explicitly asks for exact-time scheduling

## 10. Route preparation-window prompts correctly

User says:
`周四要分享，今天开始进入准备窗口。`

Expected behavior:
- recognize both the explicit time node and the preparation window
- route the timing pressure into `reminders.md`
- if the item also deserves attention today, surface it in `Daily Focus`
- avoid relying on exact-time reminder mechanisms unless the user explicitly asks for them

## 11. Surface yesterday's real progress into today's focus

User says:
`昨天 APC 联调 Codex 已经有实际进展，今天别漏掉。`

Expected behavior:
- treat this as a project-progress signal, not just commentary
- update the related active project with the new validated progress and next action
- when generating `Daily Focus`, re-evaluate whether this new progress deserves entry into today's Top 3 or project signals
- do not rely only on deadline proximity if the new progress has method-level or execution-level value

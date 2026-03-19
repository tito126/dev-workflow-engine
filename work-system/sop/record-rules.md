# Work Control Record Rules

## Formal Record Scope

Only create or update formal records for information that belongs to at least one of these classes:
- task
- progress
- risk
- milestone
- value
- decision

If a message does not belong to one of these classes, keep it in conversation unless the user explicitly asks to archive it.

## Minimum Required Fields

### Temporary work item

Each formal temporary item should include:
- created time
- content
- type
- source
- related project if known
- status
- next handling action if known

### Project update

Each meaningful project update should preserve enough detail to answer:
- what changed
- why it matters
- what is next
- whether it affects scope, timeline, value, or risk

## 存量专项收编规则

对于已经推进中的专项，先做一次“专项基本画像”提炼，再正式建档。不要把零散聊天、旧文档和历史记忆原样复制到新系统里。

专项基本画像至少应包含：
- 专项定义
- 当前阶段
- 当前成果
- 下一步重点
- 风险或待确认
- 价值说明
- 外部依赖

## Capture Rules

### Capture immediately

Write immediately when the user explicitly says:
- record this
- remember this in the system
- put this in the temporary pool
- add to project
- update progress
- record as risk
- add milestone
- remind me

### Capture after short clarification

Clarify before writing when any of these are missing and materially important:
- project name
- due date for a reminder
- whether a statement is final or still exploratory
- whether a new effort is a project or a one-off task

### Do not capture automatically

Do not write formal records for:
- casual brainstorming without clear action or conclusion
- repeated restatements of the same point
- emotional reactions without management value
- vague references that cannot be traced later

## Temporary Work Pool Rules

- Use the temporary pool as an inbox, not as permanent storage.
- Review it daily or every two days.
- Convert items out of it whenever possible.
- Avoid keeping stale items without status.

## Project Dossier Rules

- One active project should have one main markdown file.
- Keep the file focused on the durable project picture, not every chat detail.
- Update `Latest Update`, `Next Action`, `Risk`, and `Value` aggressively; these are the most decision-useful sections.
- When a project is completed, paused, or canceled, move it to `projects/archived/`.

## Daily Focus Rules

- Keep the list short enough to be actionable.
- Prefer one core goal and three key focus items.
- Rank by priority, not by message arrival order.
- Pull from both the temporary pool and active project dossiers.

## Daily Summary Rules

- Do not write a diary.
- Write a management summary.
- Focus on outcomes, project movement, unclosed items, risks, and tomorrow's priorities.
- Make the summary reusable for weekly reporting.

## Traceability Style

When possible, preserve these markers inside records:
- date
- owner or source
- due date or target node
- current state
- next action

## Update Discipline

When updating a record:
- prefer appending a dated update note instead of overwriting history blindly
- keep the most current state visible near the top
- avoid duplicate entries for the same event

## Escalation Rules

Escalate attention when any of these appear:
- due date within one to two days
- repeated blocker with no owner action
- project value becomes unclear
- scope increases materially
- dependency from another team is unresolved

## Anti-Clutter Rules

To control information sprawl:
- do not save whole conversations into files
- do not create a new file for every tiny task
- do not duplicate the same item in temporary pool, project file, and daily file without reason
- summarize, classify, and link instead of copying everything

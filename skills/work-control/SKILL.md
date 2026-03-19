---
name: work-control
description: Chat-driven work control for day-to-day professional execution. Use when the user wants to capture temporary work, track projects, rank daily priorities, write end-of-day summaries, standardize project control habits, or build a reusable SOP around task capture, project dossiers, daily focus, daily summaries, and traceable markdown records.
---

# Work Control

Use this skill to run a light but durable work control system inside normal chat. Treat chat as the input layer, `work-system/` as the operational record layer, and this skill as the operating standard.

## Quick Start

When this skill applies, work through this sequence:
1. Decide whether the message is conversation only, a candidate record, or a formal record.
2. If it is a formal record, write it into the right file under `work-system/`.
3. If it belongs to a long-running initiative, update the matching project dossier.
4. If the user asks for prioritization, create or update today's Daily Focus file.
5. If the user asks for a wrap-up, create or update today's Daily Summary file.

Read these references as needed:
- `references/file-map.md` for where records live
- `references/trigger-phrases.md` for natural-language triggers
- `references/usage-scenarios.md` for common interaction patterns
- `work-system/sop/collaboration-sop.md` for the end-to-end operating rules
- `work-system/sop/record-rules.md` for capture discipline and anti-clutter rules

## Core Capabilities

### 1. Capture temporary work without losing the thread

Use `work-system/inbox/temporary-work-pool.md` for short-lived but important items such as leader requests, meeting follow-ups, reminder candidates, and early risk signals.

Prefer the temporary pool when:
- the item matters but is not fully structured yet
- project mapping is unclear
- the user wants a quick capture first and refinement later

Do not turn the temporary pool into a permanent archive. Move items onward, close them, or archive them.

### 2. Maintain project dossiers

Use one markdown file per active project under `work-system/projects/active/`.

Keep these sections current because they drive good decisions:
- Goal
- Value
- Current Progress
- Milestones
- Risks And Blockers
- Next Action
- Latest Update

When the user updates a project, prefer concise stateful edits over dumping raw chat logs.

### 3. Produce Daily Focus

When the user asks to plan the day, rank work using this default order unless instructed otherwise:
1. deadline today or tomorrow
2. urgent leadership request
3. blocker that unblocks others
4. high-value milestone
5. important but non-urgent maintenance work

Write the result to `work-system/daily/focus/YYYY-MM-DD.md` using the template in `work-system/templates/daily-focus-template.md`.

Keep the list intentionally short:
- one core goal
- top three focus items
- a few secondary follow-ups
- visible risk watch items

### 4. Produce Daily Summary

When the user asks for an end-of-day summary, write a management summary, not a diary.

Write the result to `work-system/daily/summary/YYYY-MM-DD.md` using the template in `work-system/templates/daily-summary-template.md`.

Include:
- completed work
- project movement
- unfinished or delayed items
- risks and blockers
- tomorrow's likely priorities
- wording useful for weekly or leadership reporting

### 5. Enforce traceable record discipline

Formal project records should live in `work-system/`, not mainly in MEMORY.md.

Use MEMORY.md only for durable personal context, preferences, and a small number of long-term decisions. Do not let project run-state drift into memory as the primary source of truth.

## Operating Rules

### Default capture behavior

- Do not save every chat message.
- Save only information with management value.
- Use natural-language triggers; do not require slash commands.
- Ask one short clarification when the target file, project name, or due date is materially unclear.

### What counts as a formal record

Capture and structure content in these categories:
- task
- progress
- risk
- milestone
- value
- decision

### What stays out of formal records by default

Do not archive:
- casual discussion
- duplicate restatements
- half-formed chat without action or decision value
- vague references that cannot be traced later

## File Outputs

Use these files and directories directly:
- `work-system/inbox/temporary-work-pool.md`
- `work-system/inbox/ideas.md`
- `work-system/inbox/reminders.md`
- `work-system/projects/index.md`
- `work-system/projects/active/`
- `work-system/projects/archived/`
- `work-system/daily/focus/`
- `work-system/daily/summary/`
- `work-system/templates/`

## Recommended Interaction Patterns

Example user requests this skill should support:
- `Record this: leader wants a draft by next Wednesday.`
- `Add to project Interface Governance: confirmed current environment limits today.`
- `Record as risk: the external team has not confirmed resources.`
- `Add value: this project mainly reduces complaints, not only improves efficiency.`
- `Plan today's focus.`
- `Do today's summary.`

## Maintenance

When the system evolves:
- update the SOP first if the rule changes
- update templates if the structure changes
- keep project names stable
- avoid duplicate storage of the same content across multiple files unless the duplication has a clear purpose

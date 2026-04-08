---
name: work-control
description: Chat-driven work control for day-to-day professional execution. Use when the user wants to capture temporary work, track projects, rank daily priorities, write end-of-day summaries, standardize project control habits, or build a reusable SOP around task capture, project dossiers, daily focus, daily summaries, and traceable markdown records.
---

# Work Control

Use this skill to run a light but durable work control system inside normal chat. Treat chat as the input layer, `work-system/` as the operational record layer, and this skill as the operating standard.

中文高频触发默认有效，不要因为用户没有说英文而降级为普通聊天。像 `今日聚焦`、`今天聚焦`、`今天重点`、`今天先做什么`、`排一下今天优先级` 这类表达，默认按 `Daily Focus` 处理；像 `今日总结`、`今天总结`、`收个尾`、`做个今天的总结` 这类表达，默认按 `Daily Summary` 处理。

凡是出现明确时间节点或时间窗口的中文表达，也默认进入时间路由判断。像 `提醒我`、`下周要讲`、`周四要分享`、`某天前交付`、`前一天提醒我一下`、`这周要完成` 这类表达，优先判断是否写入 `work-system/inbox/reminders.md`，并在合适时机通过 `Daily Summary / Daily Focus` 主动抬头，而不是默认等到时间点机械提醒。

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

如果用户表达里已经带有明确时间节点、时间窗口、会前准备、交付前提醒等信息，优先考虑 `reminders.md`，而不是先落到 temporary pool。

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

When reviewing what should enter today's focus, do not look only at deadlines and old standing priorities. Also check whether the last 24 hours produced a high-value new development in an active project, especially things like a new collaboration path being validated, a blocked chain being opened, or a previously uncertain method proving workable. If yes, re-evaluate whether that item deserves entry into today's Top 3.

Strong-trigger rule:
- Requests like `今日聚焦`、`今天聚焦`、`今天重点`、`今天先做什么`、`排一下今天优先级` are direct `Daily Focus` triggers
- Do not downgrade them into ordinary conversation just because more context might be nice to have
- Default behavior is: read the relevant `work-system` inputs, generate the daily file, then reply with the result
- Only ask a short follow-up if a key missing fact makes a formal `Daily Focus` impossible to generate
- Do not stop at a guiding question without creating the daily record

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

### 6. Route time-sensitive work correctly

When the user mentions a clear time node, near-term deadline, or preparation window, treat it as a reminder-routing signal first.

Default routing order:
- if the message is mainly about a time node or preparation window, write or update `work-system/inbox/reminders.md`
- if it also belongs to a continuing initiative, link the reminder to the related project
- if the reminder is now within a near window, surface it again in `Daily Summary` or `Daily Focus`

Do not default to `cron` or isolated reminders unless the user explicitly wants exact-time reminding.

## Operating Rules

### Default capture behavior

- Do not save every chat message.
- Save only information with management value.
- Use natural-language triggers; do not require slash commands.
- Prefer semantic intent recognition over rigid keywords.
- Treat explicit user phrases such as `record this`, `add to project`, `remind me`, `this is a rule`, or `do not file this yet` as stronger routing signals.
- Treat clear Chinese operational phrases such as `今日聚焦`、`今天重点`、`今天先干什么`、`今日总结`、`记一下`、`加到项目里`、`记成风险` as equally strong routing signals.
- Treat clear Chinese time phrases such as `提醒我`、`下周要讲`、`周四要分享`、`某天前交付`、`前一天提醒我`、`这周要完成` as strong reminder-routing signals.
- Ask one short clarification when the target file, project name, due date, or system layer is materially unclear.
- When ambiguity remains, prefer lighter capture first instead of prematurely creating a formal record.

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
- `今日聚焦。`
- `排一下今天优先级。`
- `今天先做什么？`
- `今日总结。`
- `提醒我周四前收一版分享提纲。`
- `这个下周要讲，前一天提醒我一下。`

## Maintenance

When the system evolves:
- update the SOP first if the rule changes
- update templates if the structure changes
- keep project names stable
- avoid duplicate storage of the same content across multiple files unless the duplication has a clear purpose

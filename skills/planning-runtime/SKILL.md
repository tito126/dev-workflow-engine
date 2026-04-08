---
name: planning-runtime
description: Use when a complex task needs a runtime workspace to keep goals, findings, progress, errors, and final outcome stable across multiple turns. Triggers on multi-stage tasks, cross-turn execution, large reading / locating / implementation flows, or any task where chat-only state is no longer enough to keep execution aligned.
---

# Planning Runtime

Use this skill to create and maintain a runtime execution container for complex work.

## Goal

Do not use chat history alone as the primary execution container for multi-stage work.

Create a runtime task workspace that keeps:
- the task goal anchored
- findings captured
- progress visible
- errors persistent
- outcome ready for formal write-back

## Use when

Use this skill when one or more are true:
- the task is likely to take multiple stages
- the task is likely to continue across turns
- the task requires locating / implementation / review / verification coordination
- the task needs evidence-based retrospective later
- the task is too large to trust chat-only continuity

Do not use this skill for:
- one-shot simple fixes
- quick factual answers
- trivial file edits
- tasks that do not need runtime state

## Runtime location

Default runtime path pattern:

`work-system/projects/active/<project>/runtime/<task-id>/`

Recommended task-id pattern:

`YYYY-MM-DD-<short-slug>`

## Runtime files

Each runtime task should contain:

1. `task-plan.md`
   - goal
   - current phase
   - stage breakdown
   - decisions
   - error log
   - done definition

2. `findings.md`
   - research findings
   - code / doc reading results
   - evidence
   - risk notes

3. `progress.md`
   - actions taken
   - files changed or inspected
   - validations run
   - blockers and stop point

4. `outcome.md`
   - final result
   - unresolved items
   - residual risks
   - formal write-back targets
   - sync status

## Core rules

- Treat runtime files as the execution container, not as optional notes.
- Re-read `task-plan.md` before major task pivots.
- Persist important errors instead of trusting memory.
- Keep findings separate from progress.
- Do not confuse runtime state with long-term memory.
- Before claiming completion, check outcome and write-back status.

## Integration with `nurse-station-*`

- `nurse-station-brainstorming` decides whether runtime is recommended.
- `nurse-station-writing-plans` should bind plans to runtime path when present.
- `nurse-station-locator` should structure results for `findings.md`.
- `nurse-station-implementer` should structure outputs for `progress.md`.
- `nurse-station-review-gate` and `nurse-station-verification` should review runtime evidence.
- `nurse-station-mvp-retrospective` should prefer runtime evidence over memory alone.

## Minimal workflow

1. Decide the task is complex enough for runtime.
2. Create runtime directory and 4 files from templates.
3. Write initial plan and phase.
4. Keep findings and progress updated during execution.
5. Before completion, fill outcome and decide required write-back.
6. After completion, push stable conclusions into project / daily / memory layers as appropriate.

## Output expectation

At minimum, when this skill is invoked, the controller should be able to answer:
- Runtime path:
- Current phase:
- Which file should be updated next:
- What evidence must be preserved before continuing:

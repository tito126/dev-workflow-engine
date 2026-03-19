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

Expected behavior:
- read pending temporary work items and active project signals
- create or update today's file in `daily/focus/`
- keep the list intentionally short and ranked

## 6. Write daily summary

User says:
`Do today's summary.`

Expected behavior:
- summarize completed work, project movement, open items, and risks
- create or update today's file in `daily/summary/`
- preserve wording useful for reporting

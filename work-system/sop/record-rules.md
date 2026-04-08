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
- 记一下
- 记录一下
- remember this in the system
- put this in the temporary pool
- 放到临时池
- add to project
- 加到项目
- 更新项目
- update progress
- 更新进展
- record as risk
- 记成风险
- 记录为风险
- add milestone
- 加个里程碑
- remind me
- 提醒我
- 前一天提醒我

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
- If a message already contains a clear time node, due window, or preparation window, prefer `reminders.md` over the temporary pool.

## Project Dossier Rules

- One active project should have one main markdown file.
- Keep the file focused on the durable project picture, not every chat detail.
- Update `Latest Update`, `Next Action`, `Risk`, and `Value` aggressively; these are the most decision-useful sections.
- When a project is completed, paused, or canceled, move it to `projects/archived/`.

## 里程碑设计规则

### 详设/方案类专项

- 里程碑按章节、模块、文档产出记录即可。
- 优先记录“完成了什么章节”或“当前推进到哪个章节”。
- 如果内容会因客户、产品或评审意见频繁调整，不要拆成过细节点。
- 重点记录章节完成情况、待确认项、当前下一章。

### 开发/落地类专项

- 里程碑应比详设类更细，以便跟踪真实进展。
- 优先记录需求、方案、开发、联调、测试、上线、验收等阶段节点。
- 必要时补充阻塞、依赖方、目标时间、验收条件。

## Daily Focus Rules

- Keep the list short enough to be actionable.
- Prefer one core goal and three key focus items.
- Rank by priority, not by message arrival order.
- Pull from both the temporary pool and active project dossiers.
- Treat `今日聚焦`、`今天重点`、`排一下今天优先级` as direct Daily Focus triggers.
- Pull in reminder items that have entered a near-term window.

## Daily Summary Rules

- Do not write a diary.
- Write a management summary.
- Focus on outcomes, project movement, unclosed items, risks, and tomorrow's priorities.
- Make the summary reusable for weekly reporting.
- Treat `今日总结`、`今天总结`、`收个尾` as direct Daily Summary triggers.
- Before writing, check whether near-term reminder items should be proactively surfaced.

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

## 三类载体的路由补充规则

### 1. `ideas.md`

- 用于承接方向、机会点、工具设想、潜在线索
- 不要求 idea 必须先升级到 `reminders.md` 才能进入 `projects`
- 当 idea 已具备明确目标、价值、下一步，或已经需要持续积累上下文时，可以直接转入 `projects`

### 2. `reminders.md`

- 用于承接有明确时间节点、时间窗口或临近压力的事项
- 凡是出现“本周要完成”“下周要讲”“周四要分享”“某天前交付”“某天有评审/汇报”“前一天提醒我一下”“进入准备窗口了”这类表达，默认应考虑进入 `reminders.md`
- `reminders.md` 的职责不是自动提醒，而是为 `Daily Summary` 和 `Daily Focus` 提供临近事项输入

### 3. `projects`

- 用于承接持续推进、需要上下文积累的事项
- 进入 `projects` 的标准不是“是否很大”，而是“是否需要连续几轮推进和持续更新状态”
- 具备明确目标、价值、下一步的事项，即使最初来自 idea，也可以直接建档到 `projects`

## Daily Summary / Daily Focus 联动要求

### 1. 每日总结前

助手应至少检查一次：
- `reminders.md` 中是否存在临近节点
- `ideas.md` 中是否存在值得抬头回看的方向
- `projects` 中是否存在进入关键窗口的专项

### 2. 生成 Daily Focus 时

助手应把以下内容显性列出：
- 今天真的要推进的项目事项
- 已进入临近时间窗口的提醒事项
- 已从 idea 升级为当天值得投入的事项

如果用户直接使用 `今日聚焦`、`今天重点`、`排一下今天优先级` 等中文表达，也应按同样规则处理，不因语言形式不同而降级。

### 3. 防沉底要求

- `ideas.md` 不能只进不出
- `reminders.md` 不能只记不抬头
- `projects` 不能只建档不更新

## Anti-Clutter Rules

To control information sprawl:
- do not save whole conversations into files
- do not create a new file for every tiny task
- do not duplicate the same item in temporary pool, project file, and daily file without reason
- summarize, classify, and link instead of copying everything

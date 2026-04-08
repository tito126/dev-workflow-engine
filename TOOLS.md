# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics - the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## OpenClaw Health

### 升级 / 重装后必查

每次升级 `OpenClaw`、重装依赖、切换 Node 版本后,优先执行:

```powershell
openclaw health
openclaw memory status --deep
openclaw memory search "日志猎人"
```

重点确认:
- `memory_search` 没有失效
- `Embeddings: ready`
- `Vector: ready`
- `main / executor` 都正常

如果 `memory_search` 再失效,要第一时间明确告诉第别,不要默默跳过。

## Codex 调用规则 ⚠️

**每次派 Codex 干活必须指定工作目录**。

**规则**:
1. 用户指定了目录 → 用用户指定的
2. 用户没指定 → 从 acpx 配置读取默认 cwd (`E:\winning-code\akso5\winning-nis-ward`)
3. 优先确认一下更好,但可以直接用默认值执行

**推荐调用方式**(2026-04-03 测试验证):
```bash
cd E:\winning-code\akso5\winning-nis-ward && codex exec "你的任务"
```
- **稳定可靠**,能拿到完整反馈
- **ACP 方式有 bug**:Prompt 可能发不出去,完成通知丢失

**默认工作目录**(从 openclaw.json 读取):
```
E:\winning-code\akso5\winning-nis-ward
```

**示例**:
```
派 Codex 分析 winning-ward-execution-order 模块
```

我会执行(没指定目录就用默认配置的):
```bash
cd E:\winning-code\akso5\winning-nis-ward && codex exec "分析 winning-ward-execution-order 模块"
```

**禁止**:让 Codex 全盘扫描

### 执行效率规范(2026-04-03 教训)

### 技能阻塞处理规范(2026-04-03)

当用户明确要求"用某个 skill / 技能"处理任务时:
1. **优先走技能标准路径**,不要擅自换方案
2. 如果遇到阻塞(缺依赖、权限、编码、环境问题),**先汇报阻塞点**,再等用户决定
3. 不要因为想尽快完成,就私自改走其他实现路径
4. 若后续需要补依赖,先说明缺什么,再执行安装或等待确认
5. 这类阻塞和处理约束,优先记到 `TOOLS.md`

### `opencode` 执行链路规则（2026-04-07）

当前标准路径明确调整为：
1. **主路径**：`ACP / acpx -> opencode`
2. **降级路径**：最原始的 `exec opencode`
3. **禁止**：把 `wrapper opencode` 作为默认方案或降级方案

补充约束：
- `wrapper opencode` 这轮验证未跑通，不能写进标准执行链
- 如果后续再次研究 wrapper，必须明确标注为**实验/排障**，不能伪装成正式 carrier
- 后续在护士站框架、执行计划、子任务派发中，只要写到 `opencode` 路径，默认按 `ACP 优先，exec 降级` 理解

### `work-control` 触发规则(2026-04-05)

后续遇到以下场景,**优先按 `work-control` 语义处理**,不要只当成普通聊天回复或仅写 `memory/YYYY-MM-DD.md`:

1. 用户要求做:`今日总结`、`Daily Focus`、优先级整理、工作收口、明日衔接
2. 用户要求把聊天中的工作内容:归档、收编、纳入专项、转成正式工作流记录
3. 用户正在推动:专项跟踪、阶段复盘、执行计划整理、项目控制动作
4. 当前输出不只是"记住发生了什么",而是在形成**工作流层的正式产物**
5. 内容明显涉及:任务、进展、风险、里程碑、价值、决策 这类工作控制信息

### 判断边界

- **仅记连续性**:写 `memory/YYYY-MM-DD.md`
- **涉及工作收口/排序/专项衔接/正式总结**:优先触发 `work-control`
- 如果既有长期连续性价值、又属于正式工作控制动作:
  - 先按 `work-control` 处理正式产物
  - 再把关键判断同步到 `memory/YYYY-MM-DD.md`

### 提醒落点规则（2026-04-06）

后续只要第别**没有明确要求"定时任务 / 某个具体时间点提醒"**，就不要优先建 `cron`。

默认处理顺序：
1. 先按 `work-control` 语义处理
2. 优先写入 `work-system/inbox/reminders.md`
3. 再在合适时机通过 `今日聚焦`、`今日总结` 主动抬头

补充规则：
- 用户说的是：`记一下`、`后续提醒我`、`下周推进`、`前一天提醒我一下`、`这周别忘了` → 默认进 `reminders.md`
- 只有用户明确说：`几点提醒我`、`明天 9 点提醒`、`到时弹我一下` 这类需要**精确定时**的场景，才考虑 `cron`
- 不能只写进 `memory/YYYY-MM-DD.md` 就算完成；提醒类偏好和待提醒事项，必须尽量落到 `work-control` 可执行层

### 台账类文件编辑规则（2026-04-06）

**禁止整体覆盖台账类文件**，只能追加或精确编辑。

适用范围：
- `work-system/inbox/*.md`（reminders.md、temporary-work-pool.md、ideas.md）
- `work-system/projects/*.md`
- `work-system/daily/**/*.md`
- `MEMORY.md`
- 其他已存在且有固定结构的台账文件

正确做法：
1. 先 `read` 原文件
2. 用 `edit` 做精确替换，或在末尾追加内容
3. 禁止用 `write` 整体重写

### 今日总结时 push 规则（2026-04-06）

每次做 `今日总结` 时，需对以下核心文件执行 `git add + commit + push`：

**个人长期记忆 / 人格层**
- `MEMORY.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `AGENTS.md`

**每日记录层**
- `memory/` 目录下所有 `.md`

**工作管控层（work-control）**
- `work-system/projects/`
- `work-system/daily/`
- `work-system/inbox/`
- `work-system/deliverables/`
- `work-system/sop/`

**本地规则层**
- `TOOLS.md`
- `HEARTBEAT.md`

**说明**：`skills/` 目录不纳入每日 push，仅在有明显改动时单独提交。

**问题**: 14:39 codex 完成分析,但 14:55 才发送结果, **16分钟浪费在盲目 poll**

**规范:**
1. **立即处理完整输出**: poll 返回完整答案时,立即 kill 并返回
2. **检查输出完整性**: 眲输出是否已经包含完整答案(如 "如果你要,我可以下一步...")
3. **短 timeout**: poll timeout 设为 5000-10000ms, 不要 60000-120000ms
4. **不要盲目等待**: 有结果就立即处理

**错误示例**(今天的问题)。
```
poll(timeout=120000) → "Process still running" → 再 poll(timeout=120000) → ...
```

**正确做法**:
```
poll(timeout=10000) → 检查输出是否完整 → 如果完整, 立即 kill 并返回
```

---

## ⚠️ 经验教训(2026-04-03)

### Codex 协作 SOP

1. **先分型**:先判断用户是在要`解释 / 方案 / 判断 / 真执行`
2. **默认不执行**:只有用户明确说`用 Codex / 派 Codex / 让 Codex 做`,才允许调用 Codex
3. **执行前报备**:启动 Codex 前先明确告知这是分钟级任务,并说明目标与范围
4. **严格收口**:只做用户点名的那一步,不擅自升级成 benchmark / 环境探测 / 顺手优化
5. **结果即停**:拿到足够回答用户的结果后立即结束,不再为了"更完整"继续扩展
6. **少轮询**:后续不要依赖高频轮询;默认优先找完成通知/结果文件/一次性收口方式
7. **异常双落地**:出现越界执行、收口过慢、等待过长时,必须同时解释并写入当天 memory

### Codex 通知规则

- **ACP 路线**:理论上 Codex 完成后应该由 OpenClaw 收到完成事件;但当前已知有 bug,存在"完成通知丢失"问题,所以这条路不可靠
- **exec 直调 Codex CLI**:默认**不会主动通知我**,除非额外做一层包装(例如让完成后写结果文件/触发系统事件)
- 因此后续如果真要减少 token 消耗,优先考虑:
  1. **不用 Codex 就不用**
  2. 真要用时,尽量让它**一次跑完并输出最终结果**
  3. 只有在需要时才做低频状态检查,不走高频轮询

---

## Exec Commands

### Long-Running Commands
**Always use yieldMs for commands that take >10 seconds:**

```python
exec(
    command="python script.py",
    workdir="...",
    yieldMs=10000  # Yield after 10 seconds
)
```

**Why:**
- Without yieldMs, I hang and can't respond to you
- With yieldMs, I can tell you progress and do other things
- After yield, use `process(action=poll)` to check status

**Workflow:**
1. Command starts, yields after 10s if still running
2. I tell you "Running, will check progress..."
3. I poll every 1-2 minutes and update you
4. When done, I report the results

**Examples of long-running commands:**
- Log inspection (10+ minutes)
- Large file processing
- Network operations
- Build/compile tasks

---

Add whatever helps you do your job. This is your cheat sheet.

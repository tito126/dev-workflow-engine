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

### ACP 手动补丁（2026-04-08）⚠️ 升级会被覆盖

OpenClaw 2026.4.5 的 ACP backend 在 Windows 上无法正常初始化，需要手动打两处补丁。

**补丁 1**：`D:\nvm\v24.9.0\node_modules\openclaw\dist\register.runtime-DnI7Bmok.js` 第219行
```
// 修改前: this.healthy = false;
// 修改后: this.healthy = true;
```
原因：AcpxRuntime 构造时 healthy=false，需要异步 probe 成功才设为 true，但 probe 的 client.start() 在 Windows 上会卡住，导致后端永远标记为 unavailable。

**补丁 2**：`D:\nvm\v24.9.0\node_modules\openclaw\dist\server-Cv5hzFG4.js` 第25975行
在 `reconcilePendingSessionIdentities` 调用前，加入 `waitForAcpBackend` 轮询等待逻辑（对应 PR #40671），超时 5 秒，轮询间隔 50ms。
原因：Gateway 启动时 reconcile 在后端注册前就执行了，需要先等待后端就绪。

**⚠️ 注意**：每次 `npm update -g openclaw` 会覆盖这两处修改，升级后必须重新打补丁。

### ACP 结果回传补丁（2026-04-10 修复，2026-04-11 验证通过）

`OpenClaw 2026.4.5` 在 Windows 上还存在一类 ACP relay 问题：
- child session 已经产出 assistant 结果
- child transcript / 落盘文件已存在
- 但 parent 主会话可能收到空 result、timeout 或 gateway closed

**本地修复文件**：
- `D:\nvm\v24.9.0\node_modules\openclaw\dist\pi-embedded-DWASRjxE.js`

**修复思路**：
- 在 `captureSubagentCompletionReply`
- `freezeRunResultAtCompletion`
- `runSubagentAnnounceFlow`
三处补上 `readLatestAssistantReplyFromDisk(sessionKey)` transcript 磁盘 fallback，避免 gateway RPC 失败时结果丢失。

**验证结果（2026-04-11）**：
1. 正常场景：`sessions_spawn runtime="acp" agentId="opencode" mode="run"`，parent 正常收到 child 输出
2. 重启场景：spawn 后立刻 `openclaw gateway restart`，parent 仍收到 `ACP-RELAY-RESTART-TEST-OK`
3. 已核对 stream log 与 child transcript，结果一致

**验证产物**：
- 报告：`C:\Users\pc\.openclaw\workspace\acp-result-relay-fix-report.md`
- patch：`C:\Users\pc\.openclaw\workspace\work-system\projects\active\openclaw-tooling\runtime\2026-04-10-acp-result-relay\acp-result-relay-fix.patch`
- 验证记录：`C:\Users\pc\.openclaw\workspace\work-system\projects\active\openclaw-tooling\runtime\2026-04-10-acp-result-relay\validation-2026-04-11.md`

**后续规则**：
- 只要升级 `openclaw`、重装依赖、切换 Node，优先检查这处补丁是否被覆盖
- 若 ACP 再出现“child 有结果但 parent 空回”现象，先检查 `pi-embedded-DWASRjxE.js` 是否仍含磁盘 fallback 逻辑
- 若需要对外分发，优先提供 patch 文件，不要靠手工口述改法

### `opencode` 执行链路规则（2026-04-07 / 2026-04-08 更新）

当前标准路径明确调整为：
1. **主路径**：`ACP / acpx -> opencode`
2. **降级路径**：最原始的 `exec opencode`
3. **禁止**：把 `wrapper opencode` 作为默认方案或降级方案

补充约束：
- `wrapper opencode` 这轮验证未跑通，不能写进标准执行链
- 如果后续再次研究 wrapper，必须明确标注为**实验/排障**，不能伪装成正式 carrier
- 当前 `ACP -> opencode` 在本机 **仅在已打 2026-04-08 Windows 手动补丁后才视为正式可用**
- 后续在护士站框架、执行计划、子任务派发中，只要写到 `opencode` 路径，默认按 `ACP 优先，exec 降级` 理解
- 如果 OpenClaw 升级、重装或切版本后 ACP 再次报 `backend unavailable`，先检查补丁是否被覆盖，不要直接误判为 `opencode` 本身故障

### `win-code-scanner` 扫描前告知规则（2026-04-10）

后续只要是用 `win-code-scanner` 或其衍生链路（包括 `opencode` 代扫）执行真实扫描，必须先向第别明确说明以下三点，再执行：
1. **扫描范围**：全量 / 增量（如近 7 天改动）/ 指定模块 / 指定文件
2. **风险**：是否可能耗时较长、是否可能扩大读取范围、是否可能产生高噪音结果
3. **偏离点**：如果没有走 skill 的默认推荐路径（例如没有走增量扫描），必须先说明原因，不能擅自执行

补充约束：
- 没有明确授权时，**不要默认做全量扫描**
- 当用户已经点出 skill 内存在“增量扫描”等更稳妥选项时，优先先确认，再执行
- 若执行中途需要从窄范围扩大到更大范围，也要先汇报，不得自行升级
- **如果 ACP 链路出现结果回传异常、超时、空结果、或 OpenClaw 工具层异常，必须立刻中断并汇报，不要继续用 ACP 重试或擅自切换其他 carrier 空转**
- 这类情况默认判断为 **OpenClaw / ACP 工具问题**，不是第别的问题，也不要默认甩锅给 `opencode`

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

### `nurse-station` 本地执行约束（2026-04-18）

- 后续护士站开发链路**不使用 worktree**。
- 统一按 `nurse-station` 主技能与 `git-baseline-and-branch` 约束，直接在目标本地仓库目录修改、验证、收口。
- 如果历史产物、旧蓝图、旧 reference 或中间分析里仍出现 `worktree` 口径，默认视为**历史残留**，需要在后续 skill 清理中消除，**不再作为可执行默认路径**。

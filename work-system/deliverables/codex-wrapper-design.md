# Codex 执行包装（Wrapper）方案

## 1. 背景问题

当前 `Codex` 调用存在两个核心问题：

1. **ACP 路线不可靠**
   - `sessions_spawn` / ACP 理论上应有完成通知。
   - 但当前已确认存在 bridge 层问题：
     - prompt 可能没发出去；
     - 完成事件可能丢失。
   - 因此不适合作为正式执行链路。

2. **`exec + codex` 默认不会主动通知主会话**
   - 直调 `codex exec` 本质上只是本地进程。
   - 它结束后不会天然回推“我完成了”。
   - 如果没有额外机制，主会话只能靠 `poll`/查进程/读输出判断。

3. **高频轮询成本高且容易收口过晚**
   - 会消耗 token。
   - 也容易出现“结果已经够用了，但还在盯着等”的问题。
   - 这会把本来几分钟的任务放大成十几二十分钟。

## 2. 方案目标

目标是建立一条正式、可控、可追溯的 `Codex` 执行链路：

- **不用 ACP**
- **不靠高频轮询**
- **Codex 完成后自动通知主会话**
- **结果自动落盘，便于追溯**
- **状态与结果分离**
- **主会话只在收到通知后读取结果并回复用户**

## 3. 总体方案

引入一层本地 wrapper，统一管理 `Codex` 任务执行。

### 3.1 统一入口

后续 `Codex` 正式任务不再裸跑 `exec + codex`，统一走：

- `codex-run.ps1`（Windows wrapper）

### 3.2 wrapper 负责的职责

wrapper 必须统一负责：

1. 生成任务 id
2. 写入 prompt 文件
3. 写入状态文件
4. 启动 `codex exec`
5. 保存最终结果文件
6. 完成后触发本地通知 / wake

### 3.3 主会话负责的职责

主会话只负责：

1. 判断是否获得用户明确授权
2. 生成 prompt
3. 启动 wrapper
4. 收到完成通知后读取结果文件
5. 整理并回复用户

## 4. 目录与文件约定

建议固定目录：

```text
C:\Users\pc\.openclaw\workspace\codex-runs\
```

每个任务固定生成三件套：

```text
codex-runs/
  <id>.prompt.txt
  <id>.result.md
  <id>.status.json
```

### 4.1 `prompt.txt`

保存本次实际下发给 `Codex` 的 prompt，便于审计与复盘。

### 4.2 `result.md`

保存最终可读结果，不保存完整过程噪声。

建议结构：

```md
# Codex Result

## Summary
一句话总结

## Details
完整分析 / 修改说明 / 输出结果

## Notes
可选补充
```

若失败，可写成：

```md
# Codex Result

## Status
failed

## Error
简要错误说明

## Last Useful Output
最后一段有价值输出
```

### 4.3 `status.json`

保存结构化状态。

## 5. `status.json` 规范

### 5.1 最小字段

```json
{
  "id": "20260403-1913-sql-opt",
  "state": "running",
  "runner": "codex",
  "cwd": "E:\\winning-code\\akso5\\winning-nis-ward",
  "promptFile": "codex-runs/20260403-1913-sql-opt.prompt.txt",
  "resultFile": "codex-runs/20260403-1913-sql-opt.result.md",
  "startedAt": "2026-04-03T19:13:00+08:00",
  "finishedAt": null,
  "exitCode": null,
  "error": null
}
```

### 5.2 状态枚举

- `running`
- `done`
- `failed`
- `timeout`
- `killed`

### 5.3 状态流转

- 启动前写入：`running`
- 正常结束：`done`
- 退出码非 0：`failed`
- 超时终止：`timeout`
- 人工停止：`killed`

## 6. 通知机制

### 6.1 原则

wrapper 不直接给用户发消息，也不直接操作会话上下文。

wrapper 完成后只做一件事：
- **发送一条短通知 / system event / wake**

### 6.2 通知文本规范

- 成功：
  ```text
  Codex done: <id>
  ```
- 失败：
  ```text
  Codex failed: <id>
  ```
- 超时：
  ```text
  Codex timeout: <id>
  ```
- 被停止：
  ```text
  Codex killed: <id>
  ```

### 6.3 主会话收到通知后的动作

主会话收到通知后，再读取：

- `codex-runs/<id>.status.json`
- `codex-runs/<id>.result.md`

然后整理成用户可读回复。

### 6.4 为什么不用 wrapper 直接发消息

如果让 wrapper 直接发消息，会有几个问题：

- 不理解当前对话上下文
- 容易发错地方或重复发
- 失败场景更难统一处理

因此更合理的职责边界是：

- wrapper 只管执行和通知
- 主会话只管理解结果和回复用户

## 7. Windows 最小实现方向

建议使用 `codex-run.ps1` 作为 wrapper。

### 7.1 输入参数

```powershell
.\codex-run.ps1 `
  -TaskId "20260403-1916-sql-opt" `
  -Cwd "E:\winning-code\akso5\winning-nis-ward" `
  -PromptFile "C:\Users\pc\.openclaw\workspace\codex-runs\20260403-1916-sql-opt.prompt.txt" `
  -ResultFile "C:\Users\pc\.openclaw\workspace\codex-runs\20260403-1916-sql-opt.result.md" `
  -StatusFile "C:\Users\pc\.openclaw\workspace\codex-runs\20260403-1916-sql-opt.status.json"
```

可选扩展参数：

- `-TimeoutSeconds`
- `-Model`

### 7.2 脚本流程

1. 写 `status.json = running`
2. 读取 `prompt.txt`
3. `Push-Location $Cwd`
4. 执行 `codex exec`
5. 把最终输出写入 `result.md`
6. 根据退出结果更新 `status.json`
7. 触发本地通知 / wake

### 7.3 核心执行形态（概念）

```powershell
$prompt = Get-Content $PromptFile -Raw -Encoding UTF8
Push-Location $Cwd
try {
    $output = codex exec $prompt 2>&1
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
```

执行结果落盘到 `ResultFile`，状态更新到 `StatusFile`。

## 8. 标准执行链路

后续正式调用 `Codex` 的完整链路应为：

1. 用户明确授权：`用 Codex / 派 Codex / 让 Codex 做`
2. 主会话生成任务 id
3. 主会话写 `prompt.txt`
4. 主会话启动 `codex-run.ps1`
5. wrapper 写入 `running`
6. wrapper 执行 `codex exec`
7. wrapper 写入 `result.md`
8. wrapper 更新 `status.json`
9. wrapper 发送 `Codex done: <id>` 或失败通知
10. 主会话收到通知后读取结果文件并回复用户

## 9. 正式 SOP

### 9.1 启动条件

- **未获明确授权，不得启动 Codex**
- 解释 / 方案 / 判断类问题，默认不执行 Codex

### 9.2 执行约束

- 明确授权后，也必须走 wrapper
- 没走 wrapper 的 `Codex` 调用，视为不合规执行
- 任务只能做用户点名的那一步
- 禁止擅自扩展成 benchmark / 环境探测 / 顺手优化

### 9.3 收口规则

- 结果足够回答用户时，应立即收口
- 不再依赖高频轮询
- 仅保留低频兜底检查作为异常备用手段

## 10. 这套方案解决的问题

它主要解决三类问题：

1. **不知道 Codex 什么时候结束**
   - 由 wrapper 落盘状态并主动通知

2. **不得不靠轮询猜状态**
   - 改为通知驱动 + 文件驱动

3. **结果和状态混在终端输出里，不易追溯**
   - prompt / result / status 三者分离

## 11. 待定项

后续继续推进时，需要最终定死以下参数：

1. **通知入口**
   - wrapper 完成后具体走哪种本地 wake / system event

2. **超时阈值**
   - 建议为 `Codex` 任务设默认超时时间，例如 10 分钟

3. **清理策略**
   - `codex-runs/` 的保留周期
   - 是否按天归档或限制最大数量

## 12. 当前结论

后续 `Codex` 的正式执行方向不应继续停留在“裸 `exec + codex` + 高频轮询”。

应该收敛为：

- **默认不启动 Codex**
- **启动必须获得明确授权**
- **一旦启动，必须走 wrapper**
- **wrapper 负责状态落盘、结果落盘、完成通知**
- **主会话只在收到通知后读取结果并回复用户**

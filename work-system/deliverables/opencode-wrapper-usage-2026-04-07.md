# OpenCode Wrapper 使用说明（2026-04-07）

## 1. 文件

当前最小链路由四个脚本组成：

- `opencode-run.ps1`
  - 底层 runner
  - 负责执行 `opencode`、写状态、写结果、处理超时、可选 wake 通知

- `start-opencode-task.ps1`
  - 启动器
  - 负责生成 task id、写 prompt、组织三件套路径、后台启动 runner

- `stop-opencode-task.ps1`
  - 停止器
  - 负责按 `taskId` 停止运行中的任务，并写回 `killed` 状态

- `get-opencode-task.ps1`
  - 查询器
  - 负责查询单个任务状态，或列出当前 `opencode-runs/` 下的任务清单

## 1.1 推荐顺序

- 启动：`start-opencode-task.ps1`
- 查询：`get-opencode-task.ps1`
- 停止：`stop-opencode-task.ps1`
- 执行内核：`opencode-run.ps1`

默认运行目录：

```text
C:\Users\pc\.openclaw\workspace\opencode-runs\
```

每次任务生成：

```text
<task-id>.prompt.txt
<task-id>.result.md
<task-id>.status.json
```

---

## 2. 最小使用方式

```powershell
.\start-opencode-task.ps1 `
  -Prompt "分析 winning-ward-execution-order 模块的入口与主要职责" `
  -Cwd "E:\winning-code\akso5\winning-nis-ward" `
  -Model "zhipuai-coding-plan/glm-5" `
  -NotifyByWake
```

启动后会返回 JSON，例如：

```json
{
  "taskId": "20260407-123000-分析-winning-ward-execution-order",
  "pid": 12345,
  "cwd": "E:\\winning-code\\akso5\\winning-nis-ward",
  "promptFile": "...prompt.txt",
  "resultFile": "...result.md",
  "statusFile": "...status.json"
}
```

---

## 3. 等待式使用方式

如果是短任务，也可以加 `-Wait`：

```powershell
.\start-opencode-task.ps1 `
  -Prompt "Say hello" `
  -Cwd "E:\winning-code\akso5\winning-nis-ward" `
  -Model "zhipuai-coding-plan/glm-5" `
  -Wait
```

但对于中大任务，推荐后台执行 + wake 通知，而不是等待式。

---

## 4. 触发场景

## 4.1 应该触发 wrapper 的场景

当任务满足以下任一情况时，默认应使用 wrapper，而不是裸 `exec opencode`：

1. **中任务 / 重任务**
   - 需要代码定位、分析、实现、review 之一
   - 预计不是一句话输出能完成

2. **分钟级任务**
   - 预计执行超过 30-60 秒
   - 不希望主会话持续 poll

3. **需要追溯的任务**
   - 需要保留 prompt
   - 需要保留最终结果
   - 后续要做复盘或写入 runtime / framework 文档

4. **护士站框架正式执行链**
   - 任务属于 `medium / heavy`
   - 或需要接入 `planning-runtime`
   - 或需要作为 MVP / MVC 运行样本

5. **风险较高的外部执行**
   - 担心中断
   - 担心结果丢失
   - 担心轮询过久
   - 需要超时兜底

---

## 4.2 可以不触发 wrapper 的场景

以下情况可以继续裸 `exec opencode` 或直接不用外部 runner：

1. **纯聊天 / 判断 / 解释**
   - 用户只是要方案或分析，不要求派 runner

2. **极短任务**
   - 预计 10-30 秒内完成
   - 不需要保存结果
   - 没有复盘价值

3. **本地直接编辑更合适**
   - 一两行精确修改
   - 主控可以直接读写完成

4. **用户没有明确授权**
   - 不能因为有 wrapper 就默认外派执行

---

## 5. 与护士站任务分级的关系

### Light
默认不触发 wrapper。

只有当主控明确判断需要外部 runner，或用户明确要求用 `opencode` 时，才触发。

### Medium
默认优先考虑 wrapper。

如果任务需要定位 / 实现 / review，或者会持续超过 1 分钟，应走 wrapper。

### Heavy
默认必须走 wrapper 或更正式的执行容器。

Heavy 任务不应再裸跑 `exec opencode + poll`。

---

## 6. 状态判断

查看状态：

```powershell
Get-Content .\opencode-runs\<task-id>.status.json -Raw
```

状态枚举：

- `running`
- `done`
- `failed`
- `timeout`
- `killed`

停止任务：

```powershell
.\stop-opencode-task.ps1 -TaskId "<task-id>"
```

查看结果：

```powershell
Get-Content .\opencode-runs\<task-id>.result.md -Raw
```

---

## 7. 当前边界

当前是 MVP 版：

- 已支持 prompt / status / result 三件套
- 已支持 timeout
- 已支持可选 wake 通知
- 已支持外部 stop 脚本并写回 `killed`
- 未实现任务清理归档
- 未实现增量日志
- 未实现自动重试

这些可以后续按真实使用情况再补。

---

## 8. 直接怎么用

### 8.1 启动一个后台任务

```powershell
.\\start-opencode-task.ps1 `
  -Prompt "分析 winning-ward-execution-order 模块的入口与主要职责" `
  -Cwd "E:\winning-code\akso5\winning-nis-ward" `
  -Model "zhipuai-coding-plan/glm-5" `
  -NotifyByWake
```

### 8.2 查看它跑完没有

```powershell
.\\get-opencode-task.ps1 -List
```

或者：

```powershell
.\\get-opencode-task.ps1 -TaskId "<task-id>"
```

### 8.3 读取结果

```powershell
Get-Content .\\opencode-runs\\<task-id>.result.md -Raw
```

### 8.4 停掉任务

```powershell
.\\stop-opencode-task.ps1 -TaskId "<task-id>"
```

## 9. 一句话规则

后续执行规则建议定为：

> 轻任务默认不用 wrapper；中任务建议 wrapper；重任务必须 wrapper。用户未明确授权时，不外派 `opencode`。 

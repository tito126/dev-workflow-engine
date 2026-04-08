# OpenClaw 通过 ACP 连接 Codex 安装与调试指南

## 1. 背景说明

这套链路不是 OpenClaw 直接内嵌调用 Codex，而是通过 ACP（Agent Client Protocol）链路接入：

`OpenClaw -> @openclaw/acpx 扩展 -> acpx -> codex ACP 适配器 -> Codex`

其中：
- OpenClaw 负责聊天入口、会话管理、调度 `sessions_spawn`
- `@openclaw/acpx` 是 OpenClaw 的 ACP runtime 扩展
- `acpx` 是实际的 ACP 路由与会话驱动工具
- `codex` 在这条链路中通过 ACP 适配器接入，默认命令为：`npx @zed-industries/codex-acp@^0.9.5`

当前环境中查到的关键信息：
- `@openclaw/acpx` 扩展位置：`D:\nvm\v24.9.0\node_modules\openclaw\dist\extensions\acpx\package.json`
- 当前扩展版本：`2026.3.28`
- 当前扩展钉住的 `acpx` 版本：`0.3.1`

---

## 2. 安装前需要准备的信息

在开始前，建议先确认并记录以下信息，避免执行到一半才发现路径或环境不对。

### 2.1 运行环境信息

需要准备：
- 已安装 `Node.js`
- 已安装 `npm`
- 本机可以正常启动 OpenClaw
- 机器可以访问 npm 源（安装 `acpx` 和 `codex-acp` 时会用到）

建议先确认：
- `node -v`
- `npm -v`
- `openclaw status`

### 2.2 OpenClaw 安装目录

需要明确：
- OpenClaw 的安装根目录在哪里
- `extensions/acpx` 实际位于哪个目录

你当前环境里，OpenClaw 安装资源位于：
- `D:\nvm\v24.9.0\node_modules\openclaw\`

但要注意：
- 实际安装 `acpx` 时，不是随便在 workspace 根目录执行
- 必须切到 **OpenClaw 的 `extensions/acpx` 目录** 再装

如果你的 OpenClaw 是标准安装方式，目标目录应类似：
- `D:\nvm\v24.9.0\node_modules\openclaw\extensions\acpx`

如果这个目录不存在，需要先确认你当前安装包的目录结构。

### 2.3 需要确认的目标目录

安装前，你需要确认下面这个目录真实存在：
- `D:\nvm\v24.9.0\node_modules\openclaw\extensions\acpx`

如果不存在，可以继续检查这些候选位置：
- `D:\nvm\v24.9.0\node_modules\openclaw\dist\extensions\acpx`
- 你自己的自定义 OpenClaw 安装目录下的 `extensions\acpx`

原则是：
- **安装命令要在运行时实际使用的 `extensions/acpx` 目录内执行**
- 不建议在别的目录随意 `npm install -g acpx`

---

## 3. 安装步骤

### 第 1 步：确认 Node / npm / OpenClaw 基础环境

先执行：

```powershell
node -v
npm -v
openclaw status
```

预期结果：
- `node` 和 `npm` 有版本号输出
- `openclaw status` 能正常返回当前服务状态

如果这里失败：
- 先不要继续安装 `acpx`
- 优先把基础环境修好

---

### 第 2 步：进入 `extensions/acpx` 安装目录

**这一点很重要：安装前必须先切目录。**

你需要先切到 OpenClaw 的 ACP 扩展目录，例如：

```powershell
cd D:\nvm\v24.9.0\node_modules\openclaw\extensions\acpx
```

如果这个路径不存在，再尝试检查：

```powershell
cd D:\nvm\v24.9.0\node_modules\openclaw\dist\extensions\acpx
```

进入目录后，建议先看一眼是否有 `package.json`：

```powershell
dir
```

你应该至少能看到类似内容：
- `package.json`
- `index.js` 或扩展相关文件

---

### 第 3 步：安装与扩展版本匹配的 `acpx`

当前已确认 `@openclaw/acpx` 扩展依赖版本为：
- `acpx@0.3.1`

因此，进入正确目录后执行：

```powershell
npm install --omit=dev --no-save acpx@0.3.1
```

说明：
- `--omit=dev`：不装开发依赖
- `--no-save`：不改动项目依赖声明，只补齐运行依赖
- 不建议默认使用全局安装：
  - `npm install -g acpx`
- 因为全局版本容易漂移，和扩展声明版本不一致时会引发兼容问题

---

### 第 4 步：验证插件本地 `acpx` 是否可用

安装完成后，在当前目录执行：

```powershell
.\node_modules\.bin\acpx.cmd --version
```

如果你使用 bash 风格环境，也可用：

```bash
./node_modules/.bin/acpx --version
```

预期结果：
- 能输出版本号
- 且应与扩展依赖一致，优先期望看到 `0.3.1`

如果这里失败，先不要急着继续接 Codex，先看下面“调试排查”章节。

---

### 第 5 步：重启 OpenClaw Gateway

如果是首次安装、补装或修复 `acpx`，建议重启一次 OpenClaw gateway，让运行时重新加载扩展环境。

可执行：

```powershell
openclaw gateway restart
```

或者按你当前环境已有方式重启。

重启后，再执行：

```powershell
openclaw status
```

确认服务已经恢复正常。

---

## 4. Codex 在 ACP 链路中的默认接法

在 `acpx` 的内置适配器里，`codex` 默认映射到：

```bash
npx @zed-industries/codex-acp@^0.9.5
```

这表示：
- 一般不需要你自己额外写一个桥接脚本
- 只要 `acpx` 正常工作，它就会尝试按默认方式拉起 Codex 的 ACP 适配器

如果本机网络正常，并能访问 npm，这个默认链路通常就够用。

---

## 5. OpenClaw 内部如何调用 Codex

在 OpenClaw 里，推荐使用 ACP runtime 调用方式：

核心参数通常是：

```json
{
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session",
  "task": "<你要让 Codex 执行的任务>"
}
```

含义：
- `runtime: "acp"`：走 ACP runtime，而不是普通子代理
- `agentId: "codex"`：指定目标 harness 为 Codex
- `thread: true`：创建线程式持续对话
- `mode: "session"`：保持会话上下文，而不是一次性执行

这是最适合持续协作型编码任务的接法。

---

## 6. 手动调试：直接测试 `acpx -> codex` 链路

如果你想先不经过 OpenClaw UI，而是直接验证底层链路，可以手动做一次测试。

### 6.1 创建一个测试会话

先进入安装了 `acpx` 的目录，或确保你明确使用本地二进制：

```powershell
.\node_modules\.bin\acpx.cmd codex sessions new --name test-codex
```

预期结果：
- 创建一个名为 `test-codex` 的 Codex ACP 会话

### 6.2 向测试会话发送一句话

```powershell
.\node_modules\.bin\acpx.cmd codex -s test-codex --cwd C:\Users\pc\.openclaw\workspace --format quiet "Say hi"
```

说明：
- `-s test-codex`：复用刚创建的会话
- `--cwd`：指定工作目录
- `--format quiet`：尽量只输出最终文本结果，减少噪音

预期结果：
- Codex 能返回一句正常回复

### 6.3 一次性执行测试

如果你不想先建 session，也可以直接测试 one-shot：

```powershell
.\node_modules\.bin\acpx.cmd codex exec --cwd C:\Users\pc\.openclaw\workspace --format quiet "Say hi"
```

这个命令适合快速验证链路是否通。

---

## 7. 调试与排查指南

下面这部分建议保留，出问题时按顺序查，不要一上来就重装全部环境。

### 7.1 `acpx` 命令找不到

典型表现：
- `acpx: command not found`
- 或 PowerShell 提示找不到命令

排查步骤：
1. 确认你是不是在 `extensions/acpx` 目录里执行的
2. 不要默认直接敲 `acpx`
3. 优先显式使用插件本地命令：

```powershell
.\node_modules\.bin\acpx.cmd --version
```

如果本地命令也不存在：
- 说明 `acpx` 没装成功，或装错目录了
- 回到第 2 步重新确认目录，再重新执行安装

---

### 7.2 `acpx` 版本不对

排查方式：
- 查看扩展声明版本
- 再查看实际执行版本

当前已确认扩展要求：
- `acpx@0.3.1`

验证实际版本：

```powershell
.\node_modules\.bin\acpx.cmd --version
```

如果不一致：
- 建议重新在正确目录执行：

```powershell
npm install --omit=dev --no-save acpx@0.3.1
```

然后重启 gateway。

---

### 7.3 Codex 适配器拉起失败

可能表现为：
- `acpx` 能跑
- 但 `codex` 命令执行时报错
- 或创建 session 后无法响应

优先检查：
1. 本机网络是否能访问 npm
2. `npx @zed-industries/codex-acp@^0.9.5` 是否能被正常拉起
3. 是否存在覆盖默认 agent 配置的文件：
- `~/.acpx/config.json`

如果这个配置文件里改写了 `codex` agent 的默认命令，可能导致链路异常。

---

### 7.4 OpenClaw 里调用失败，但 `acpx` 单测正常

这种情况通常说明：
- 底层 `acpx -> codex` 是通的
- 但 OpenClaw runtime 没正确加载、没重启，或 ACP 扩展状态异常

建议排查：
1. 重启 gateway：

```powershell
openclaw gateway restart
```

2. 查看状态：

```powershell
openclaw status
```

3. 再从 OpenClaw 里发起一轮新的 ACP session 测试

---

### 7.5 报 `NO_SESSION`

说明会话不存在。

先手动创建：

```powershell
.\node_modules\.bin\acpx.cmd codex sessions new --name test-codex
```

再重试：

```powershell
.\node_modules\.bin\acpx.cmd codex -s test-codex --cwd C:\Users\pc\.openclaw\workspace --format quiet "Say hi"
```

---

## 8. 推荐的最小验证流程

如果你只想快速确认“这条链路到底通不通”，推荐按下面最短路径走：

### 最小验证步骤

1. 确认基础环境：

```powershell
node -v
npm -v
openclaw status
```

2. 切到 ACP 扩展目录：

```powershell
cd D:\nvm\v24.9.0\node_modules\openclaw\extensions\acpx
```

3. 安装钉住版本：

```powershell
npm install --omit=dev --no-save acpx@0.3.1
```

4. 验证 `acpx`：

```powershell
.\node_modules\.bin\acpx.cmd --version
```

5. 重启 gateway：

```powershell
openclaw gateway restart
```

6. 做一次手动 one-shot 测试：

```powershell
.\node_modules\.bin\acpx.cmd codex exec --cwd C:\Users\pc\.openclaw\workspace --format quiet "Say hi"
```

7. 再回到 OpenClaw 中发起 `runtime: "acp", agentId: "codex"` 的正式会话

---

## 9. 常见注意事项

- 不要默认全局安装 `acpx`
- 安装命令前一定先切到正确目录
- 优先使用插件本地 `acpx`，不要混用 PATH 上其他版本
- 装完或修复后，最好重启一次 gateway
- 如果手动 `acpx` 测试能通，而 OpenClaw 不通，优先怀疑 runtime/gateway 状态
- 如果 OpenClaw 能找到 `acpx`，但 `codex` 拉不起来，优先查网络和 `~/.acpx/config.json`

---

## 10. 一句话总结

最关键的不是“装上 acpx”本身，而是：
- **在正确的 `extensions/acpx` 目录里安装与扩展匹配的 `acpx` 版本**
- **先用本地 `acpx` 命令验证 `acpx -> codex` 通路**
- **再重启 OpenClaw，让 ACP runtime 正常接管这条链路**

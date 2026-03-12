# OpenClaw 迁移指南：公司机器 → 家里机器

**目标架构：** 家里机器作为主 Gateway，公司机器作为 Node

**迁移日期：** 2026-03-06

---

## 📋 前置准备

### 当前状态（公司机器）

- **系统：** Windows (LAPTOP-2STTCK0U)
- **OpenClaw 路径：** `C:\Users\pc\.openclaw`
- **Workspace 备份：** `C:\Users\pc\.openclaw\workspace-backup-20260306.zip` (12.5 MB)
- **Gateway Token：** `86f77cef7b355cc1c3f12f8e5420b5ab113bb29031acb346`

### 需要准备的东西

- [ ] 家里机器（Windows/Linux/Mac）
- [ ] 两台机器都能上网
- [ ] 记事本记录 Tailscale IP 地址

---

## 第一阶段：建立 Tailscale 网络

### 1.1 在公司机器上安装 Tailscale

**Windows（公司机器）：**

```powershell
# 方式 1：使用 winget
winget install tailscale.tailscale

# 方式 2：手动下载
# 访问：https://tailscale.com/download/windows
# 下载并安装
```

**启动 Tailscale：**

```powershell
# 启动 Tailscale（会弹出浏览器登录）
tailscale up

# 登录后，获取本机 Tailscale IP
tailscale ip -4
```

**记录公司机器的 Tailscale IP：** `_________________`

---

### 1.2 在家里机器上安装 Tailscale

**Windows：**
```powershell
winget install tailscale.tailscale
tailscale up
tailscale ip -4
```

**Linux：**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```

**Mac：**
```bash
brew install tailscale
sudo tailscale up
tailscale ip -4
```

**记录家里机器的 Tailscale IP：** `_________________`

---

### 1.3 测试连通性

**在家里机器上测试：**

```bash
# ping 公司机器的 Tailscale IP
ping <公司机器Tailscale IP>

# 应该能 ping 通！
```

✅ **检查点：** 两台机器能互相 ping 通

---

## 第二阶段：传输文件到家里机器

### 2.1 准备传输的文件

**在公司机器上，需要传输：**

1. **Workspace 备份：** `C:\Users\pc\.openclaw\workspace-backup-20260306.zip`
2. **配置文件：** `C:\Users\pc\.openclaw\openclaw.json`
3. **执行批准文件（可选）：** `C:\Users\pc\.openclaw\exec-approvals.json`

### 2.2 传输方式（选择一种）

#### 方式 A：通过 Tailscale 网络 SCP 传输（推荐）

**在公司机器上：**

```powershell
# 传输 workspace 备份
scp C:\Users\pc\.openclaw\workspace-backup-20260306.zip <家里用户>@<家里Tailscale IP>:~/

# 传输配置文件
scp C:\Users\pc\.openclaw\openclaw.json <家里用户>@<家里Tailscale IP>:~/

# 传输执行批准文件（可选）
scp C:\Users\pc\.openclaw\exec-approvals.json <家里用户>@<家里Tailscale IP>:~/
```

**注意：** Windows 可能需要先安装 OpenSSH 客户端，或者使用 WinSCP 等工具。

#### 方式 B：通过云盘传输

1. 将文件上传到云盘（百度网盘、OneDrive、Google Drive 等）
2. 在家里机器上下载

#### 方式 C：通过 U 盘传输

1. 复制文件到 U 盘
2. 带回家插入家里机器

✅ **检查点：** 文件已成功传输到家里机器

---

## 第三阶段：在家里机器上配置 OpenClaw

### 3.1 安装 OpenClaw

```bash
# 安装 OpenClaw
npm install -g openclaw

# 验证安装
openclaw --version
```

### 3.2 初始化并停止 Gateway

```bash
# 启动 Gateway（会创建 ~/.openclaw 目录）
openclaw gateway start

# 等待几秒后停止
openclaw gateway stop
```

### 3.3 恢复 Workspace

**Linux/Mac：**

```bash
# 解压 workspace 备份
unzip ~/workspace-backup-20260306.zip -d ~/.openclaw/

# 删除 BOOTSTRAP.md（不再需要）
rm ~/.openclaw/workspace/BOOTSTRAP.md

# 设置权限
chmod -R 755 ~/.openclaw/workspace
```

**Windows：**

```powershell
# 解压 workspace 备份
Expand-Archive -Path ~\workspace-backup-20260306.zip -DestinationPath $env:USERPROFILE\.openclaw\ -Force

# 删除 BOOTSTRAP.md
Remove-Item $env:USERPROFILE\.openclaw\workspace\BOOTSTRAP.md -ErrorAction SilentlyContinue
```

### 3.4 恢复配置文件

**Linux/Mac：**

```bash
# 复制配置文件
cp ~/openclaw.json ~/.openclaw/openclaw.json

# 复制执行批准文件（如果有）
cp ~/exec-approvals.json ~/.openclaw/exec-approvals.json
```

**Windows：**

```powershell
# 复制配置文件
Copy-Item ~\openclaw.json $env:USERPROFILE\.openclaw\openclaw.json -Force

# 复制执行批准文件（如果有）
Copy-Item ~\exec-approvals.json $env:USERPROFILE\.openclaw\exec-approvals.json -Force
```

### 3.5 配置 API Keys

**编辑配置文件（如果需要）：**

```bash
# Linux/Mac
nano ~/.openclaw/openclaw.json

# Windows
notepad %USERPROFILE%\.openclaw\openclaw.json
```

**检查以下配置是否正确：**

- Anthropic API Key（如果使用）
- ZAI API Key（如果使用）
- Feishu 配置（如果使用）

### 3.6 启动 Gateway

```bash
# 启动 Gateway
openclaw gateway start

# 检查状态
openclaw gateway status

# 查看日志（如果有问题）
openclaw gateway logs
```

✅ **检查点：** Gateway 在家里机器上成功运行

---

## 第四阶段：在公司机器上配置为 Node

### 4.1 停止公司机器的 Gateway

**在公司机器上：**

```powershell
# 停止 Gateway
openclaw gateway stop

# 确认已停止
openclaw gateway status
```

### 4.2 配置为 Node

```powershell
# 安装 node 服务，连接到家里的 Gateway
openclaw node install --host <家里机器Tailscale IP> --port 18789 --display-name "公司机器"

# 例如：
# openclaw node install --host 100.64.1.10 --port 18789 --display-name "公司机器"

# 检查 node 状态
openclaw node status
```

**预期输出：**
```
Node service is running
Connected to gateway at <家里机器Tailscale IP>:18789
Status: pending (waiting for approval)
```

✅ **检查点：** Node 服务运行中，等待批准

---

## 第五阶段：批准配对

### 5.1 在家里机器上批准

```bash
# 查看待批准的节点
openclaw nodes pending

# 会显示类似：
# Request ID: abc123
# Node: 公司机器
# IP: 100.64.1.2

# 批准配对
openclaw nodes approve <Request ID>

# 例如：
# openclaw nodes approve abc123
```

### 5.2 验证配对成功

**在家里机器上：**

```bash
# 查看已配对的节点
openclaw nodes status

# 应该看到公司机器已连接
```

**在公司机器上：**

```powershell
# 检查 node 状态
openclaw node status

# 应该显示：Status: connected
```

✅ **检查点：** 配对成功，公司机器显示 connected

---

## 第六阶段：测试和验证

### 6.1 测试 Node 执行

**在家里机器上，通过 OpenClaw 在公司机器上执行命令：**

```bash
# 启动 OpenClaw CLI 或 Web 界面
openclaw chat

# 在对话中测试：
# "在公司机器上执行 hostname 命令"
```

### 6.2 访问 Web 界面

**从任意位置访问家里的 Gateway：**

```
http://<家里机器Tailscale IP>:3000
```

**使用 Gateway Token 登录：**
```
Token: 86f77cef7b355cc1c3f12f8e5420b5ab113bb29031acb346
```

### 6.3 测试消息渠道

如果配置了 Telegram/WhatsApp/Feishu，测试是否能正常收发消息。

✅ **检查点：** 所有功能正常工作

---

## 🔧 故障排除

### 问题 1：Tailscale 无法连接

**解决方案：**
```bash
# 检查 Tailscale 状态
tailscale status

# 重启 Tailscale
sudo systemctl restart tailscaled  # Linux
# 或在 Windows 上重启 Tailscale 服务

# 重新登录
tailscale up
```

### 问题 2：Node 无法连接到 Gateway

**检查清单：**
- [ ] 家里机器的 Gateway 是否在运行？
- [ ] Tailscale IP 是否正确？
- [ ] 防火墙是否阻止了 18789 端口？

**测试连接：**
```bash
# 在公司机器上测试
telnet <家里机器Tailscale IP> 18789

# 或使用 PowerShell
Test-NetConnection -ComputerName <家里机器Tailscale IP> -Port 18789
```

### 问题 3：Gateway Token 不匹配

**解决方案：**
```bash
# 在家里机器上查看 token
cat ~/.openclaw/openclaw.json | grep token

# 确保公司机器的 node 配置使用相同的 token
```

### 问题 4：Workspace 文件缺失

**解决方案：**
```bash
# 检查 workspace 目录
ls -la ~/.openclaw/workspace/

# 确保以下文件存在：
# - SOUL.md
# - USER.md
# - IDENTITY.md
# - AGENTS.md
# - TOOLS.md
# - memory/ 目录
```

---

## 📱 从公司访问家里的 Gateway

### 方式 1：通过 Web 界面

```
http://<家里机器Tailscale IP>:3000
```

### 方式 2：通过命令行

**在公司机器上设置环境变量：**

```powershell
# PowerShell
$env:OPENCLAW_GATEWAY_URL = "http://<家里机器Tailscale IP>:18789"
$env:OPENCLAW_GATEWAY_TOKEN = "86f77cef7b355cc1c3f12f8e5420b5ab113bb29031acb346"

# 然后使用 openclaw 命令
openclaw status
openclaw chat
```

### 方式 3：通过消息渠道

配置的 Telegram/WhatsApp/Feishu 会自动连接到家里的 Gateway，无需额外配置。

---

## ✅ 迁移完成检查清单

- [ ] Tailscale 在两台机器上都正常运行
- [ ] 两台机器能互相 ping 通
- [ ] Workspace 已成功迁移到家里机器
- [ ] 配置文件已复制到家里机器
- [ ] 家里机器的 Gateway 正常运行
- [ ] 公司机器的 Node 服务正常运行
- [ ] 配对已批准，状态为 connected
- [ ] 能通过 Web 界面访问家里的 Gateway
- [ ] 能在公司机器上执行命令
- [ ] 消息渠道正常工作（如果配置了）

---

## 📝 重要信息记录

**家里机器 Tailscale IP：** `_________________`

**公司机器 Tailscale IP：** `_________________`

**Gateway Token：** `86f77cef7b355cc1c3f12f8e5420b5ab113bb29031acb346`

**Web 界面地址：** `http://<家里机器Tailscale IP>:3000`

**Node ID（配对后记录）：** `_________________`

---

## 🎯 后续优化建议

1. **配置 Tailscale MagicDNS：** 使用域名代替 IP 地址
2. **设置自动启动：** 确保家里机器重启后 Gateway 自动启动
3. **配置备份：** 定期备份 workspace 和配置文件
4. **监控告警：** 配置 Gateway 离线告警（通过 Telegram 等）

---

**祝迁移顺利！如有问题，随时联系我。** 🦞

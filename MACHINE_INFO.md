# 机器信息记录

**记录时间**：2026-03-08 23:00 GMT+8

## Tailscale 网络配置

### 家里机器（目标 Gateway）
- **用户名**：Administrator (实际登录用户)
- **机器名**：USERMIC-GRMLNLP
- **Tailscale IP**：100.75.81.20
- **角色**：主 Gateway
- **状态**：✅ 已配置并运行
- **端口**：
  - Web 界面：18789 (需要 token)
  - Gateway WebSocket：18789
  - 浏览器控制：18791
  - 健康检查：18792
- **Gateway Token**：86f77cef7b355cc1c3f12f8e5420b5ab113bb29031acb346
- **访问地址**：
  - 本地：http://localhost:18789
  - 远程：http://100.75.81.20:18789

### 公司机器（当前 Gateway，计划改为 Node）
- **用户名**：laptop-2sttck0u
- **Tailscale IP**：100.89.41.5
- **当前角色**：Gateway
- **计划角色**：Node
- **备份文件**：openclaw-backup-20260308.zip (234.4 MB)

## 连接配置

### Node 连接命令（公司机器）
```powershell
openclaw node install --host 100.75.81.20 --port 18789 --display-name "公司机器"
```

### 从公司访问家里 Gateway
```
Web 界面：http://100.75.81.20:3000
```

## 风险提示

⚠️ **重要**：如果家里的 Gateway 出现问题，公司机器配置为 Node 后将无法独立工作。

## 应急恢复方案

如果家里 Gateway 故障，在公司机器上执行：
```powershell
# 卸载 Node 模式
openclaw node uninstall

# 恢复 Gateway 模式
openclaw gateway start
```

恢复时间：约 1-2 分钟

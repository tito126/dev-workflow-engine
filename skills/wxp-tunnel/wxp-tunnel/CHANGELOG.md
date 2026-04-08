# WXP Tunnel 技能 - 变更记录

## 2025-02-10

### 新增文件

**open-service-tunnels.mjs** - 批量开启服务隧道脚本

- **位置**: `.claude/skills/wxp-tunnel/assets/wxp-tunnel/open-service-tunnels.mjs`
- **用途**: 一键开启多个服务隧道，无需手动逐个打开
- **原始位置**: `~/.local/share/wxp-tunnel/open-service-tunnels.mjs`

**配置的服务** (租户: 长春中医药大学附属医院_正式 `zczyydxfsyyzs`)

| 服务名称 | 本地端口 | 目标地址 |
|----------|----------|----------|
| 运维平台服务(8089) | 33353 | 192.168.88.123:8089 |
| InfluxDB(8086) | 38110 | 192.168.88.123:8086 |
| Prometheus(9090) | 35546 | 192.168.88.123:9090 |

**使用方法**:
```bash
# 从项目 skills 目录运行
node .claude/skills/wxp-tunnel/assets/wxp-tunnel/open-service-tunnels.mjs
```

**依赖**: 脚本与 `src/lib/bridge-client.js` 和 `config.json` 在同一目录下，可直接运行。

---
name: wxp-tunnel
description: TCP tunnel management using Lockjaw proxy service for connecting to remote hospital/tenant operation platforms. CLI tool for opening local port tunnels to remote targets via HTTP API. Use when connecting to hospital ops platforms, monitoring services (Prometheus/InfluxDB), or managing port forwarding.
---

# WXP Tunnel

TCP tunnel management tool using Lockjaw proxy service to connect to remote hospital/tenant operation platforms.

## Quick Start

```bash
# 列出所有租户
node assets/wxp-tunnel/dist/cli.js tenants

# 搜索租户（两种方式等效）
node assets/wxp-tunnel/dist/cli.js tenants "大华"
node assets/wxp-tunnel/dist/cli.js tenants -k "大华"

# 打开监控服务隧道
node assets/wxp-tunnel/dist/cli.js open-services <tenantCode>

# 查看所有活跃隧道
node assets/wxp-tunnel/dist/cli.js status

# 关闭隧道
node assets/wxp-tunnel/dist/cli.js close <channelId>
```

## Setup

### 使用（推荐）

打包后的 CLI 可直接运行，无需安装依赖：

```bash
node assets/wxp-tunnel/dist/cli.js tenants
```

### 构建（开发者）

如需修改源码并重新构建：

```bash
cd assets/wxp-tunnel
npm install
npm run build
```

## Configuration

Configuration is stored at `~/.cache/wxp-tunnel/config.json` (auto-created on first run):

```json
{
  "platform": {
    "baseUrl": "https://wxpcpp.winning.com.cn:2443/",
    "username": "your_username",
    "password": "your_password"
  },
  "lockjaw": {
    "baseUrl": "http://localhost:8765",
    "apiKey": "dev-test-key"
  },
  "portRange": {
    "min": 8000,
    "max": 9000
  }
}
```

- `platform.baseUrl`: Platform API address (fixed)
- `platform.username/password`: Platform login credentials
- `lockjaw.baseUrl`: Lockjaw proxy service address
- `lockjaw.apiKey`: API key for Lockjaw authentication

---

## 医院名称提取规范

> **重要**：所有使用 wxp-tunnel 的技能（prometheus-host-monitor、database-diagnostics、analyzing-slow-services、analyzing-network-situation）都应遵循此规范。

### 提取规则

| 用户输入 | 提取策略 | 查询命令 |
|---------|---------|---------|
| `巡检"长沙市妇幼保健院"` | **引号包含** → 完整名称，**不缩短** | `tenants -k "长沙市妇幼保健院"` |
| `巡检长沙妇幼保健院` | **无引号** → 先完整查询，无结果再缩短 | 先 `长沙妇幼保健院`，无结果再 `长沙妇幼` |

### 执行逻辑

```
用户输入 → 检测引号 → 提取医院名称 → 查询租户
                     │
                     ├─ 有引号 → 完整名称，直接查询
                     │
                     └─ 无引号 → 先完整查询
                                 │
                                 ├─ 有结果 → 使用
                                 │
                                 └─ 无结果 → 缩短关键词重试
```

### 缩短策略

仅当完整名称查询无结果时，按以下顺序尝试：

| 优先级 | 缩短方式 | 示例 |
|--------|---------|------|
| 1 | 去掉城市后缀"市" | `长沙市妇幼保健院` → `长沙妇幼保健院` |
| 2 | 去掉后缀"院" | `长沙妇幼保健院` → `长沙妇幼` |
| 3 | 保留核心词 | `长沙县妇幼保健院` → `长沙县妇幼` |
| 4 | 去掉城市前缀（最低优先级） | `长沙市妇幼保健院` → `妇幼保健院` |

> **注意**：去掉城市前缀可能导致匹配到其他城市的同名医院，仅在前三种方式都无结果时使用。

### 示例

```bash
# 示例 1: 引号包含 → 精确匹配
用户: 巡检"长沙市妇幼保健院"
执行: node assets/wxp-tunnel/dist/cli.js tenants -k "长沙市妇幼保健院"# 不缩短

# 示例 2: 无引号 → 先完整再缩短
用户: 巡检长沙妇幼保健院
执行: node assets/wxp-tunnel/dist/cli.js tenants -k "长沙妇幼保健院"
# 如果无结果，再尝试
执行: node assets/wxp-tunnel/dist/cli.js tenants -k "长沙妇幼"
```

---

## Commands

### tenants - 列出所有可用租户

```bash
# 列出所有
node assets/wxp-tunnel/dist/cli.js tenants

# 按关键字搜索（位置参数）
node assets/wxp-tunnel/dist/cli.js tenants "大华"

# 按关键字搜索（选项参数）
node assets/wxp-tunnel/dist/cli.js tenants -k "大华"
```

**返回字段**: `[{id, name, code, online, branchId}]`

### links - 列出指定租户的所有可用连接

```bash
node assets/wxp-tunnel/dist/cli.js links <tenantCode>
```

**返回字段**: `[{id, name, simpleName, type, typeLabel, url, targetPoint, ...}]`

**连接类型**:
| type | typeLabel |
|------|-----------|
| 0 | 运维平台 |
| 1 | 交付平台 |
| 2 | 门户Portal |
| 3 | 其他 |

### service-ports - 获取租户的监控服务端口映射

```bash
node assets/wxp-tunnel/dist/cli.js service-ports <tenantCode>
```

**智能匹配规则**:
- **运维平台**: 强制使用 http 8089 端口
- **Prometheus**: 匹配 9090 端口或名称关键字 (prometheus/prom)
- **InfluxDB**: 匹配 8086 端口或名称关键字 (influx)

**返回示例**:
```json
{
  "tenantCode": "shsxhqdhyyx",
  "internalIp": "172.168.16.xxx",
  "proxyHost": "172.17.1.xxx",
  "services": {
    "ops": {
      "name": "运维平台",
      "targetIp": "172.168.16.xxx",
      "targetPort": 8089,
      "internalAddress": "172.168.16.xxx:8089",
      "proxyAddress": "172.17.1.xxx:8003",
      "localPort": 8003,
      "channelId": "shsxhqdhyyx-172-168-16-91-8089",
      "status": "RUNNING",
      "needsCreate": false
    },
    "prometheus": {...},
    "influxdb": {...}
  }
}
```

### open-services - 自动打开租户的监控服务隧道

```bash
node assets/wxp-tunnel/dist/cli.js open-services <tenantCode>
```

- 复用已存在的隧道
- 自动创建新隧道
- 返回服务的代理地址

**返回示例**:
```json
{
  "success": true,
  "tenantCode": "shsxhqdhyyx",
  "internalIp": "172.168.16.xxx",
  "proxyHost": "172.17.1.xxx",
  "services": [
    {
      "service": "运维平台",
      "status": "created",
      "internalAddress": "172.168.16.xxx:8089",
      "proxyAddress": "172.17.1.xxx:8003",
      "channelId": "shsxhqdhyyx-172-168-16-91-8089"
    }
  ]
}
```

**状态说明**:
| status | 说明 |
|--------|------|
| `created` | 新创建的隧道 |
| `already_running` | 复用已存在的隧道 |
| `failed` | 创建失败 |
| `NONE` | 未创建 |

### status - 查看所有活跃隧道

```bash
node assets/wxp-tunnel/dist/cli.js status
```

**返回示例**:
```json
{
  "lockjawBaseUrl": "http://172.17.1.50:8765",
  "total": 3,
  "channels": [
    {
      "channelId": "shsxhqdhyyx-172-168-16-91-8089",
      "tenantName": "shsxhqdhyyx",
      "hostId": "172-168-16-91-8089",
      "targetPoint": "172.168.16.91:8089",
      "localPort": 8003,
      "status": "RUNNING",
      "createdAt": 1739200000000
    }
  ]
}
```

### close - 关闭指定隧道

```bash
node assets/wxp-tunnel/dist/cli.js close <channelId>
```

**参数**: `channelId` 来自 `status` 或 `open-services` 命令的输出

## Return Fields

| 字段 | 说明 |
|------|------|
| `internalAddress` | 内网地址 (targetIp:targetPort) |
| `proxyAddress` | 代理地址 (proxyHost:localPort) |
| `proxyHost` | Lockjaw 服务器主机 |
| `localPort` | 本地代理端口 |
| `channelId` | 隧道 ID（用于关闭隧道） |
| `status` | 状态 (created/already_running/failed/NONE/RUNNING) |

## Data Flow

```
┌─────────────────┐        隧道          ┌─────────────────┐
│   本地机器       │  ──────────────────► │   Lockjaw 代理   │
│                 │  proxyHost:localPort │   服务器         │
└─────────────────┘                      └────────┬────────┘
                                                   │ 转发
                                                   ▼
                                          ┌─────────────────┐
                                          │   目标服务       │
                                          │ targetIp:targetPort │
                                          │ (内网地址)       │
                                          └─────────────────┘
```

## Lockjaw API

The tool uses Lockjaw proxy service HTTP API:

- **POST /api/v1/lockjaw/channels** - Create tunnel
- **GET /api/v1/lockjaw/channels** - List tunnels
- **GET /api/v1/lockjaw/channels/{channelId}** - Get tunnel details
- **DELETE /api/v1/lockjaw/channels/{channelId}** - Delete tunnel

Port allocation: 8000-9000 (managed by Lockjaw server)

See `references/API.md` for full API documentation.

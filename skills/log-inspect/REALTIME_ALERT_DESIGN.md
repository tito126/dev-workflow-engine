# 异常实时告警架构设计

## 问题背景

**需求**：实现异常实时告警，当生产环境出现错误时立即通知相关人员。

**挑战**：
- 现场数量多（几百家医院）
- 无法实时读取所有现场的日志（资源消耗大）
- 需要真正的"实时"响应（秒级延迟）

## 架构方案

### 🎯 推荐方案：Loki/Grafana 告警 + Webhook

**核心思路**：利用现有的 Loki/Grafana 基础设施，配置告警规则，通过 Webhook 触发 OpenClaw。

```
┌─────────────────────────────────────────────────────────────┐
│                      生产环境（几百家）                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 医院A K8s │  │ 医院B K8s │  │ 医院C K8s │  │  ...     │   │
│  │  Loki    │  │  Loki    │  │  Loki    │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘   │
│       │             │             │                         │
│       └─────────────┴─────────────┘                         │
│                     │                                        │
│              ┌──────▼──────┐                                │
│              │   Grafana   │                                │
│              │ (告警规则)   │                                │
│              └──────┬──────┘                                │
└─────────────────────┼─────────────────────────────────────┘
                      │ Webhook
                      ▼
              ┌───────────────┐
              │   OpenClaw    │
              │   Gateway     │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   飞书机器人   │
              │  (推送告警)    │
              └───────────────┘
```

### 实现步骤

#### 1. 配置 Grafana 告警规则

在 Grafana 中为每个医院/服务配置告警规则：

```yaml
# 示例：ERROR 级别日志告警
alert: HighErrorRate
expr: |
  rate({app="winning-winex-ward-pbc"} |~ "ERROR")[5m] > 10
for: 1m
labels:
  severity: critical
  hospital: 桐乡市卫生健康局
  service: 病区护士站
annotations:
  summary: "{{ $labels.hospital }} {{ $labels.service }} 错误率过高"
  description: "最近5分钟 ERROR 日志超过 10 条/秒"
```

**告警规则示例**：
- ERROR 日志频率 > 阈值
- 特定异常类型出现（如 NullPointerException）
- 慢接口响应时间 > 阈值
- 服务不可用（日志停止输出）

#### 2. 配置 Webhook 通知

在 Grafana 的 Contact Points 中配置 Webhook：

```
Webhook URL: http://your-openclaw-server:18789/webhook/grafana
Method: POST
```

Grafana 会发送如下格式的告警：

```json
{
  "receiver": "openclaw",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "HighErrorRate",
        "severity": "critical",
        "hospital": "桐乡市卫生健康局",
        "service": "病区护士站"
      },
      "annotations": {
        "summary": "桐乡市卫生健康局 病区护士站 错误率过高",
        "description": "最近5分钟 ERROR 日志超过 10 条/秒"
      },
      "startsAt": "2026-03-03T10:00:00Z",
      "endsAt": "0001-01-01T00:00:00Z"
    }
  ]
}
```

#### 3. OpenClaw 接收 Webhook

创建 Webhook 处理脚本 `alert_handler.py`：

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/webhook/grafana', methods=['POST'])
def handle_grafana_alert():
    """处理 Grafana 告警"""
    data = request.json
    
    for alert in data.get('alerts', []):
        if alert['status'] == 'firing':
            # 提取告警信息
            labels = alert['labels']
            annotations = alert['annotations']
            
            hospital = labels.get('hospital', '未知医院')
            service = labels.get('service', '未知服务')
            summary = annotations.get('summary', '')
            description = annotations.get('description', '')
            
            # 构建告警消息
            message = f"""🚨 生产告警
            
医院: {hospital}
服务: {service}
级别: {labels.get('severity', 'warning')}

{summary}
{description}

时间: {alert['startsAt']}
"""
            
            # 推送到飞书
            push_to_feishu(message)
            
            # 可选：自动触发日志分析
            if labels.get('severity') == 'critical':
                trigger_log_analysis(hospital, service)
    
    return {'status': 'ok'}

def push_to_feishu(message):
    """推送到飞书"""
    # 使用 OpenClaw message 工具
    pass

def trigger_log_analysis(hospital, service):
    """自动触发日志分析"""
    # 调用 log_inspect_main.py
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18790)
```

#### 4. 集成到 OpenClaw Gateway

将 Webhook 处理器集成到 OpenClaw Gateway：

```bash
# 启动 Webhook 服务
python alert_handler.py &

# 或者集成到 OpenClaw Gateway 配置
# 在 gateway.yaml 中添加 webhook 路由
```

### 优势

✅ **真正的实时**：Loki 实时分析日志，秒级触发告警  
✅ **可扩展**：支持几百家医院，无需轮询  
✅ **低资源消耗**：告警由 Loki/Grafana 处理，OpenClaw 只接收通知  
✅ **灵活配置**：可以为不同医院/服务配置不同的告警规则  
✅ **自动化响应**：可以自动触发日志分析、生成报告  

### 劣势

⚠️ **需要 Grafana 配置权限**：需要在每个 Grafana 实例中配置告警规则  
⚠️ **依赖现有基础设施**：只适用于已部署 Loki/Grafana 的环境  
⚠️ **需要公网访问**：如果 OpenClaw 在本地，需要内网穿透或部署到公网服务器  

---

## 🔄 备选方案：定期轮询（不推荐）

如果无法配置 Grafana 告警，可以使用定期轮询：

```python
# alert_poller.py
import time
from log_inspect_main import LogInspector

def poll_alerts():
    """定期检查关键医院的日志"""
    inspector = LogInspector()
    
    # 只监控高优先级医院
    high_priority = [
        ("桐乡市卫生健康局", "病区护士站"),
        ("乐山市人民医院", "病区护士站")
    ]
    
    while True:
        for hospital, service in high_priority:
            # 检查最近5分钟的日志
            query = f"分析{hospital}{service}最近5分钟的ERROR日志"
            result = inspector.run(query)
            
            # 如果发现错误，推送告警
            if result['success']:
                check_and_alert(result['digest_file'])
        
        # 每5分钟检查一次
        time.sleep(300)

def check_and_alert(digest_file):
    """检查 digest 并发送告警"""
    with open(digest_file) as f:
        digest = json.load(f)
    
    error_count = digest['statistics']['error_count']
    if error_count > 10:  # 阈值
        # 发送告警
        pass
```

**问题**：
- ❌ 不是真正的实时（5分钟延迟）
- ❌ 资源消耗大（需要不断查询）
- ❌ 无法扩展到几百家医院

---

## 🎯 混合方案（推荐实施）

结合两种方案的优势：

1. **K8s 环境（有 Grafana）**：使用 Loki 告警 + Webhook（实时）
2. **传统服务器环境（无 Grafana）**：定期轮询高优先级医院（5-10分钟）
3. **按需分析**：用户主动触发深度分析（使用统一入口脚本）

```
实时告警 (K8s)
    ↓
  Webhook → OpenClaw → 飞书
    ↓
自动触发深度分析
    ↓
生成详细报告 → 推送

定期轮询 (传统服务器)
    ↓
发现异常 → OpenClaw → 飞书
    ↓
生成报告 → 推送

按需分析 (所有环境)
    ↓
用户请求 → 统一入口脚本 → 报告
```

---

## 实施建议

### 第一阶段（当前）
1. ✅ 完成统一入口脚本（已完成）
2. 🔄 测试 K8s 环境的完整流程
3. 🔄 配置 1-2 个医院的 Grafana 告警规则（试点）

### 第二阶段（1-2周）
1. 创建 Webhook 处理器 `alert_handler.py`
2. 集成到 OpenClaw Gateway
3. 测试告警 → 推送 → 自动分析流程

### 第三阶段（2-4周）
1. 推广到所有 K8s 环境（配置告警规则）
2. 为传统服务器环境实现定期轮询（高优先级医院）
3. 优化告警规则（减少误报）

---

## 总结

**对于"几百家医院"的实时告警场景**：

✅ **不要**尝试实时读取所有现场的日志（资源消耗太大）  
✅ **应该**利用现有的 Loki/Grafana 基础设施配置告警规则  
✅ **通过** Webhook 将告警推送到 OpenClaw，再转发到飞书  
✅ **可以**自动触发日志分析，生成详细报告  

这样既实现了真正的实时告警，又不会消耗过多资源，还能扩展到几百家医院。

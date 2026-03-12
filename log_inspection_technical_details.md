# 日志巡检核心模块技术原理详解

## 一、整体工作流程

```
┌─────────────────┐
│  Loki (K8s)     │  日志数据源
└────────┬────────┘
         │
         │ HTTP API 查询
         ▼
┌─────────────────────────────────────────────────────────┐
│  loki_fetcher.py - 日志拉取模块                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. 构建 LogQL 查询语句                            │  │
│  │    {app="xxx"} |~ "ERROR|WARN"                   │  │
│  │                                                   │  │
│  │ 2. 自适应分片查询                                 │  │
│  │    - 检测是否达到 limit (5000条)                 │  │
│  │    - 如果达到，分成两半递归查询                   │  │
│  │    - 直到时间片 <= 1分钟                         │  │
│  │                                                   │  │
│  │ 3. 合并所有分片结果                               │  │
│  └──────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         │ 输出 .log 文件
         ▼
┌─────────────────────────────────────────────────────────┐
│  logs_20260305_080000_第二集群.log                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ [traceId,spanId,parentId] [IP:Port] [用户]       │  │
│  │ 2026-03-05 08:00:01,234 [thread] ERROR           │  │
│  │ com.winning.Class (File.java:123) -- 错误信息    │  │
│  │                                                   │  │
│  │ [traceId,spanId,parentId] [IP:Port] [用户]       │  │
│  │ 2026-03-05 08:00:02,456 [thread] WARN            │  │
│  │ com.winning.Class (File.java:456) -- 业务处理耗时 │  │
│  │ :1234毫秒:/api/xxx                               │  │
│  └──────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         │ 读取并解析
         ▼
┌─────────────────────────────────────────────────────────┐
│  preprocess.py - 日志预处理模块                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. 逐行解析日志                                   │  │
│  │    - 正则表达式提取字段                           │  │
│  │    - 提取 traceId, 时间, 级别, 类名, 内容        │  │
│  │                                                   │  │
│  │ 2. 错误分类                                       │  │
│  │    - NullPointerException                        │  │
│  │    - SQLException                                │  │
│  │    - TimeoutException                            │  │
│  │    - 其他...                                     │  │
│  │                                                   │  │
│  │ 3. 慢接口识别                                     │  │
│  │    - 提取"业务处理耗时:XXX毫秒:/api/xxx"          │  │
│  │    - 按 API 路径聚合统计                         │  │
│  │                                                   │  │
│  │ 4. 生成结构化摘要                                 │  │
│  └──────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         │ 输出 JSON
         ▼
┌─────────────────────────────────────────────────────────┐
│  logs_20260305_080000_第二集群_digest.json               │
│  {                                                       │
│    "summary": {                                          │
│      "total_lines": 640010,                              │
│      "error_count": 196,                                 │
│      "warn_count": 639814                                │
│    },                                                    │
│    "errors": [...],                                      │
│    "slow_apis": [...]                                    │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 二、loki_fetcher.py 详解

### 2.1 核心功能

**目标**：从 Loki 拉取 K8s 环境的日志，突破 5000 条/次的限制。

### 2.2 关键技术：自适应分片查询

#### 问题背景

Loki 有 `max_entries_limit_per_query` 限制（通常是 5000 条）：
- 如果查询 2 小时的日志，但日志量很大（每秒 2000+ 条）
- Loki 只返回最后 5000 条
- 导致数据不完整

#### 解决方案：自适应分片

```python
def query_loki_adaptive(
    grafana_url, datasource_id, query,
    start, end, limit=5000, min_chunk_minutes=1.0
):
    \"\"\"
    工作原理：
    1. 先查询整个时间段 (如 08:00-10:00)
    2. 如果返回 < 5000 条，说明没有截断，直接返回
    3. 如果返回 >= 5000 条，说明可能有截断：
       - 分成两半：08:00-09:00 和 09:00-10:00
       - 递归查询每一半
    4. 直到时间片 <= 1 分钟，停止分片
    \"\"\"
```

#### 示例执行过程

假设查询 08:00-10:00（2小时），日志量极大：

```
第1次查询: 08:00-10:00 → 返回 5000 条 (达到限制!)
  ├─ 分片: 08:00-09:00
  │   第2次查询: 08:00-09:00 → 返回 5000 条 (达到限制!)
  │     ├─ 分片: 08:00-08:30
  │     │   第3次查询: 08:00-08:30 → 返回 5000 条 (达到限制!)
  │     │     ├─ 分片: 08:00-08:15
  │     │     │   第4次查询: 08:00-08:15 → 返回 4523 条 (未达到限制，完整)
  │     │     └─ 分片: 08:15-08:30
  │     │         第5次查询: 08:15-08:30 → 返回 4891 条 (未达到限制，完整)
  │     └─ 分片: 08:30-09:00
  │         第6次查询: 08:30-09:00 → 返回 5000 条 (达到限制!)
  │           ... (继续分片)
  └─ 分片: 09:00-10:00
      ... (类似过程)

最终结果: 合并所有分片，获取完整数据 (可能 64万+ 条)
```

### 2.3 LogQL 查询构建

```python
def build_query(app, namespace, pod, level_filter):
    \"\"\"
    构建 LogQL 查询语句
    
    示例:
    app="winning-winex-ward-pbc"
    level_filter="ERROR|WARN"
    
    生成:
    {app="winning-winex-ward-pbc"} |~ "ERROR|WARN"
    
    解释:
    - {app="xxx"}: 选择标签匹配的日志流
    - |~ "ERROR|WARN": 正则过滤，只保留包含 ERROR 或 WARN 的行
    \"\"\"
```

### 2.4 时间戳转换

Loki API 使用纳秒时间戳：

```python
def datetime_to_ns(dt: datetime) -> int:
    \"\"\"
    转换为纳秒时间戳
    
    示例:
    2026-03-05 08:00:00 → 1709611200000000000
    \"\"\"
    return int(dt.timestamp() * 1_000_000_000)
```

### 2.5 HTTP 请求

```python
url = (
    f"{grafana_url}/api/datasources/proxy/{datasource_id}"
    f"/loki/api/v1/query_range"
    f"?query={encoded_query}"
    f"&start={start_ns}"
    f"&end={end_ns}"
    f"&limit={limit}"
    f"&direction=forward"
)

# 示例 URL:
# http://127.0.0.1:16291/api/datasources/proxy/1/loki/api/v1/query_range
# ?query=%7Bapp%3D%22winning-winex-ward-pbc%22%7D+%7C~+%22ERROR%7CWARN%22
# &start=1709611200000000000
# &end=1709618400000000000
# &limit=5000
# &direction=forward
```

### 2.6 输出格式

输出的 `.log` 文件是纯文本，每行一条日志：

```
[8AB0D4C8F2ACF99C3C4F322CE5B752E6,8AB0D4C8F2ACF99C3C4F322CE5B752E6,] [10.244.1.23:8080] [张三(12345)] 2026-03-05 08:00:01,234 [http-nio-8080-exec-1] ERROR com.winning.service.FeeService (FeeService.java:123) -- 费用服务调用失败: AuthException
[9BC1E5D9G3BDG00D4D5G433DF6C863F7,9BC1E5D9G3BDG00D4D5G433DF6C863F7,] [10.244.1.23:8080] [李四(67890)] 2026-03-05 08:00:02,456 [http-nio-8080-exec-2] WARN com.winning.service.PatientService (PatientService.java:456) -- 业务处理耗时:1234毫秒:/api/patient/query
```

---

## 三、preprocess.py 详解

### 3.1 核心功能

**目标**：从原始日志文件中提取关键信息，生成结构化的 JSON 摘要。

### 3.2 日志解析：正则表达式

#### 日志格式

```
[traceId,spanId,parentId] [IP:Port] [用户(userId)] 时间 [线程] 级别 类名 (文件:行) -- 内容
```

#### 正则表达式

```python
LOG_PATTERN = re.compile(
    r'\[([^]]*)\]\s*'  # traceId,spanId,parentId
    r'(?:\[([^]]*)\]\s*)?'  # 可选的未知字段 [,,]
    r'\[([^]]*)\]\s*'  # IP:Port 或 用户
    r'(?:\[([^]]*)\]\s*)?'  # 可选的用户(userId)
    r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s*'  # 时间戳
    r'\[([^\]]+)\]\s*'  # 线程名
    r'(\w+)\s+'  # 日志级别
    r'(\S+)\s*'  # 类名
    r'\([^)]*\)\s*'  # (文件:行)
    r'--\s*'  # 分隔符
    r'(.*)'  # 日志内容
)
```

#### 解析结果

```python
{
    'trace_id': '8AB0D4C8F2ACF99C3C4F322CE5B752E6',
    'ip_port': '10.244.1.23:8080',
    'user_name': '张三',
    'user_id': '12345',
    'timestamp': datetime(2026, 3, 5, 8, 0, 1, 234000),
    'timestamp_str': '2026-03-05 08:00:01,234',
    'thread': 'http-nio-8080-exec-1',
    'level': 'ERROR',
    'class_name': 'com.winning.service.FeeService',
    'content': '费用服务调用失败: AuthException',
    'raw': '原始日志行...'
}
```

### 3.3 错误分类

#### 分类规则

```python
ERROR_CATEGORIES = {
    'NullPointerException': ['NullPointerException', 'null', 'NPE'],
    'SQLException': ['ORA-', 'SQLException', 'SQL Error', '数据库'],
    'TimeoutException': ['timeout', 'Timeout', '超时'],
    'AuthException': ['认证', '过期', 'token', 'Token', '权限'],
    'ValidationError': ['参数', '校验', 'validation', 'Validation'],
    'ConnectionError': ['Connection', '连接', 'refused', 'reset'],
    'OutOfMemory': ['OutOfMemory', 'OOM', '内存'],
}

def categorize_error(content: str) -> str:
    \"\"\"
    根据日志内容分类错误类型
    
    示例:
    "费用服务调用失败: AuthException" → "AuthException"
    "java.lang.NullPointerException" → "NullPointerException"
    "数据库连接超时" → "TimeoutException"
    \"\"\"
    for category, keywords in ERROR_CATEGORIES.items():
        for keyword in keywords:
            if keyword in content:
                return category
    return 'Other'
```

#### 错误聚合

```python
def aggregate_errors(error_samples):
    \"\"\"
    按 类名 + 错误类型 分组
    
    示例:
    com.winning.service.FeeService + AuthException → 108 次
    com.winning.service.PatientService + NullPointerException → 23 次
    
    输出:
    [
        {
            'category': 'AuthException',
            'class': 'com.winning.service.FeeService',
            'count': 108,
            'users': ['张三', '李四', ...],
            'samples': [前3个样本]
        },
        ...
    ]
    \"\"\"
```

### 3.4 慢接口识别

#### 识别规则

```python
SLOW_API_PATTERN = re.compile(
    r'[耗时:|耗时][:：]?\s*(\d+)\s*(?:毫秒|ms)[：:]?\s*(/\S+)?'
)

# 匹配示例:
# "业务处理耗时:1234毫秒:/api/patient/query"
# "耗时 2345ms /api/fee/calculate"
# "接口耗时：3456毫秒：/api/order/create"
```

#### 慢接口聚合

```python
def aggregate_slow_apis(slow_apis):
    \"\"\"
    按 API 路径聚合统计
    
    示例:
    /api/patient/query 出现 35 次，最慢 2410ms，平均 1523ms
    /api/fee/calculate 出现 12 次，最慢 1890ms，平均 1234ms
    
    输出:
    [
        {
            'api_path': '/api/patient/query',
            'count': 35,
            'max_ms': 2410,
            'avg_ms': 1523,
            'users': ['张三', '李四', ...],
            'samples': [前3个样本]
        },
        ...
    ]
    \"\"\"
```

### 3.5 输出格式：digest.json

```json
{
  "meta": {
    "generated_at": "2026-03-05T08:15:23",
    "files_processed": ["logs_20260305_080000_第二集群.log"],
    "time_range": {
      "start": "2026-03-05 08:00",
      "end": "2026-03-05 10:00"
    },
    "slow_threshold_ms": 1000
  },
  "summary": {
    "total_lines": 640010,
    "error_count": 196,
    "warn_count": 639814,
    "error_categories": {
      "AuthException": 108,
      "NullPointerException": 23,
      "TimeoutException": 15,
      "Other": 50
    }
  },
  "errors": [
    {
      "category": "AuthException",
      "class": "com.winning.service.FeeService",
      "count": 108,
      "users": ["张三", "李四", "王五"],
      "samples": [
        {
          "timestamp": "2026-03-05 08:00:01,234",
          "class": "com.winning.service.FeeService",
          "user": "张三",
          "content": "费用服务调用失败: AuthException",
          "category": "AuthException",
          "trace_id": "8AB0D4C8F2ACF99C3C4F322CE5B752E6"
        }
      ]
    }
  ],
  "slow_apis": [
    {
      "api_path": "/api/patient/query",
      "count": 35,
      "max_ms": 2410,
      "avg_ms": 1523,
      "users": ["张三", "李四"],
      "samples": [
        {
          "duration_ms": 2410,
          "api_path": "/api/patient/query",
          "timestamp": "2026-03-05 08:05:12,456",
          "user": "张三",
          "trace_id": "9BC1E5D9G3BDG00D4D5G433DF6C863F7"
        }
      ]
    }
  ],
  "warn_samples": [...],
  "internal_timings": [...]
}
```

---

## 四、关键技术点

### 4.1 为什么需要两步处理？

**分离关注点**：
1. **loki_fetcher.py**：专注于数据获取
   - 处理 Loki API 的限制
   - 处理网络请求
   - 处理分片和合并

2. **preprocess.py**：专注于数据分析
   - 解析日志格式
   - 提取关键信息
   - 统计和聚合

**优势**：
- 模块化：每个模块职责单一
- 可复用：preprocess.py 可以处理任何来源的日志（Loki、文件、gz 压缩包）
- 可调试：可以单独测试每个模块
- 可扩展：可以轻松添加新的数据源（如传统服务器）

### 4.2 自适应分片 vs 固定分片

**固定分片（旧版）**：
```
08:00-10:00 (2小时)
├─ 08:00-08:30 (30分钟) → 5000 条
├─ 08:30-09:00 (30分钟) → 5000 条
├─ 09:00-09:30 (30分钟) → 5000 条
└─ 09:30-10:00 (30分钟) → 5000 条
总计: 20000 条 (可能仍有截断)
```

**自适应分片（新版）**：
```
08:00-10:00 (2小时)
├─ 08:00-09:00 (1小时)
│   ├─ 08:00-08:30 (30分钟)
│   │   ├─ 08:00-08:15 (15分钟) → 4523 条 ✓
│   │   └─ 08:15-08:30 (15分钟) → 4891 条 ✓
│   └─ 08:30-09:00 (30分钟)
│       ├─ 08:30-08:45 (15分钟) → 4712 条 ✓
│       └─ 08:45-09:00 (15分钟) → 4956 条 ✓
└─ 09:00-10:00 (1小时)
    ... (类似过程)
总计: 640010 条 (完整数据)
```

**优势**：
- 自动适应日志密度
- 日志少的时间段：大块查询（快）
- 日志多的时间段：小块查询（完整）
- 最大化数据完整性

### 4.3 正则表达式的性能

**问题**：处理 64万+ 条日志，正则表达式会不会很慢？

**答案**：不会，因为：
1. Python 的 `re` 模块使用 C 实现，性能很好
2. 正则表达式是编译后的（`re.compile`），只编译一次
3. 每行日志只匹配一次
4. 实测：64万条日志，解析时间约 10-15 秒

**优化技巧**：
```python
# 预编译正则表达式（只编译一次）
LOG_PATTERN = re.compile(r'...')

# 在循环中使用
for line in file:
    match = LOG_PATTERN.match(line)  # 快速匹配
```

### 4.4 内存管理

**问题**：64万条日志，会不会内存溢出？

**答案**：不会，因为：
1. **流式处理**：逐行读取，不一次性加载全部
2. **样本限制**：只保留前 500 个错误样本，前 200 个警告样本
3. **聚合统计**：不保留所有原始数据，只保留统计结果

```python
# 流式处理
with open(log_file) as f:
    for line in f:  # 逐行读取，不占用大量内存
        parsed = parse_log_line(line)
        # 处理...

# 样本限制
if len(error_lines) < 500:  # 只保留前 500 个
    error_lines.append(...)

# 聚合统计
api_stats[path]['count'] += 1  # 只保留统计数字
```

---

## 五、使用示例

### 5.1 完整流程

```bash
# 步骤1: 拉取日志
python loki_fetcher.py \
  --grafana http://127.0.0.1:16291 \
  --datasource 1 \
  --app winning-winex-ward-akso5-pbc \
  --start \"2026-03-05 08:00\" \
  --end \"2026-03-05 10:00\" \
  --level \"ERROR|WARN\" \
  --output logs_20260305_080000_第二集群.log

# 输出:
# LogQL: {app=\"winning-winex-ward-akso5-pbc\"} |~ \"ERROR|WARN\"
# 查询模式: 自适应分片（推荐）
# 
# 查询 Loki: {app=\"winning-winex-ward-akso5-pbc\"} |~ \"ERROR|WARN\"
# 时间范围: 2026-03-05 08:00:00 ~ 2026-03-05 10:00:00
# 获取到 5000 条日志
# [分片] 检测到可能的数据截断，将 08:00~10:00 (120.0分钟) 分成两半重新查询...
#   查询 Loki: ...
#   获取到 5000 条日志
#   [分片] 检测到可能的数据截断，将 08:00~09:00 (60.0分钟) 分成两半重新查询...
#     ... (继续分片)
# 
# 完成! 共 640010 条日志，已保存到 logs_20260305_080000_第二集群.log

# 步骤2: 预处理分析
python preprocess.py \
  logs_20260305_080000_第二集群.log \
  -o logs_20260305_080000_第二集群_digest.json \
  -t 1000

# 输出:
# 找到 1 个日志文件
# 处理文件: logs_20260305_080000_第二集群.log
# 
# 处理完成!
# - 总行数: 640,010
# - ERROR: 196
# - WARN: 639,814
# - 慢接口: 35
# - 输出: logs_20260305_080000_第二集群_digest.json
```

### 5.2 生成的文件

```
skills/log-inspect/
├── logs_20260305_080000_第二集群.log          # 原始日志 (147 MB)
├── logs_20260305_080000_第二集群_digest.json  # 分析结果 (84 KB)
└── logs_20260305_080000_第二集群_report.html  # HTML 报告 (30 KB)
```

---

## 六、总结

### 6.1 核心优势

1. **突破 Loki 限制**：自适应分片查询，获取完整数据
2. **高效解析**：正则表达式 + 流式处理，10-15 秒处理 64万条日志
3. **智能分类**：自动识别错误类型，聚合统计
4. **结构化输出**：JSON 格式，易于后续处理和可视化

### 6.2 技术亮点

- **自适应算法**：根据数据密度自动调整分片大小
- **模块化设计**：数据获取和数据分析分离
- **内存优化**：流式处理 + 样本限制，不会内存溢出
- **可扩展性**：易于添加新的数据源和分析规则

### 6.3 数据流转

```
Loki API
  ↓ (HTTP 查询)
原始日志流
  ↓ (自适应分片)
完整日志数据
  ↓ (写入 .log 文件)
日志文件
  ↓ (逐行解析)
结构化日志对象
  ↓ (分类、聚合)
统计摘要
  ↓ (输出 JSON)
digest.json
  ↓ (生成报告)
HTML 报告
```

---

**报告生成时间**：2026-03-05 17:57

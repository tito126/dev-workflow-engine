# 日志分析增强方案

## 📋 需求背景

### 问题 1：ERROR 日志缺少上下文
**现状**：只拉取 ERROR 级别的日志行，丢失了同一 traceId 的其他日志  
**影响**：无法看到完整调用链，难以定位根因  
**需求**：遇到 ERROR 时，通过 traceId 将相关的所有日志都拉下来

### 问题 2：慢接口分析不够深入
**现状**：只知道"慢了"和"总耗时"，不知道"慢在哪"  
**影响**：无法精准优化  
**需求**：
1. 告诉我慢在什么地方
2. 如果判断不了，应该让我反哺（日志改进建议的初衷）

---

## 💡 解决方案

### 方案 1：两阶段拉取（解决 ERROR 上下文问题）

#### 实现思路

```
阶段 1：拉取 ERROR/WARN 日志
  ↓
提取所有 traceId
  ↓
阶段 2：针对每个 traceId，拉取完整日志（不过滤级别）
  ↓
合并去重，按时间排序
```

#### 优势
- ✅ 保留完整上下文（INFO、DEBUG 等）
- ✅ 不会拉取无关日志（只拉取有问题的 traceId）
- ✅ 数据量可控
- ✅ 自动化程度高

#### 实现细节

**新增函数**：`fetch_with_context()`

```python
def fetch_with_context(
    grafana_url: str,
    datasource_id: int,
    app: str,
    start: datetime,
    end: datetime,
    limit: int = 5000,
) -> list:
    """
    两阶段拉取：先拉取 ERROR/WARN，再根据 traceId 拉取完整上下文
    
    Returns:
        完整的日志行列表（包含所有级别）
    """
    # 阶段 1：拉取 ERROR/WARN
    print("[阶段 1] 拉取 ERROR/WARN 日志...")
    error_query = build_query(app=app, level_filter="ERROR|WARN")
    error_lines = query_loki_adaptive(
        grafana_url, datasource_id, error_query, start, end, limit
    )
    
    # 提取 traceId
    print("[阶段 1] 提取 traceId...")
    trace_ids = extract_trace_ids(error_lines)
    print(f"[阶段 1] 发现 {len(trace_ids)} 个问题 traceId")
    
    if not trace_ids:
        return error_lines
    
    # 阶段 2：针对每个 traceId 拉取完整日志
    print("[阶段 2] 拉取完整上下文...")
    all_lines = []
    
    for i, trace_id in enumerate(trace_ids, 1):
        print(f"[阶段 2] ({i}/{len(trace_ids)}) 拉取 traceId: {trace_id}")
        
        # 构建查询：{app="xxx"} |= "traceId"
        context_query = f'{{app="{app}"}} |= "{trace_id}"'
        
        context_lines = query_loki_adaptive(
            grafana_url, datasource_id, context_query, start, end, limit
        )
        
        all_lines.extend(context_lines)
    
    # 去重并排序
    print("[阶段 2] 去重和排序...")
    unique_lines = list(set(all_lines))
    unique_lines.sort(key=extract_timestamp)  # 按时间戳排序
    
    print(f"[完成] 共 {len(unique_lines)} 条日志（去重后）")
    return unique_lines


def extract_trace_ids(lines: list) -> set:
    """从日志行中提取 traceId"""
    import re
    trace_ids = set()
    
    # 匹配 traceId 的正则表达式
    # 示例：[traceId:abc123] 或 traceId=abc123
    pattern = r'(?:traceId[:\s=]+)([a-zA-Z0-9]+)'
    
    for line in lines:
        match = re.search(pattern, line)
        if match:
            trace_ids.add(match.group(1))
    
    return trace_ids


def extract_timestamp(line: str) -> str:
    """从日志行中提取时间戳（用于排序）"""
    import re
    # 匹配常见的时间戳格式
    # 示例：2026-03-09 16:00:00.123
    pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)'
    match = re.search(pattern, line)
    return match.group(1) if match else ""
```

**使用方式**：

```bash
# 新增参数：--with-context
python loki_fetcher.py \
  --grafana http://127.0.0.1:16291 \
  --datasource 1 \
  --app winning-winex-ward-pbc \
  --start "2026-03-09 08:00" \
  --end "2026-03-09 10:00" \
  --with-context \
  --output logs_with_context.log
```

---

### 方案 2：慢接口深度分析（解决"慢在哪"问题）

#### 实现思路

```
识别慢接口（总耗时 > 阈值）
  ↓
提取该 traceId 的完整日志
  ↓
解析调用链（识别关键步骤）
  ↓
计算每个步骤的耗时
  ↓
标注瓶颈 + 提供反馈入口
```

#### 关键步骤识别规则

基于日志内容识别常见的耗时步骤：

| 步骤类型 | 识别关键字 | 示例 |
|---------|-----------|------|
| 数据库查询 | `执行SQL`、`query`、`select` | `执行SQL耗时: 500ms` |
| 外部 API | `调用接口`、`http request`、`远程调用` | `调用XX接口耗时: 800ms` |
| 缓存操作 | `redis`、`cache`、`memcached` | `Redis查询耗时: 50ms` |
| 业务逻辑 | `业务处理`、`计算`、`处理` | `业务处理耗时: 300ms` |
| 文件 IO | `读取文件`、`写入文件`、`IO` | `文件读取耗时: 200ms` |

#### 新增分析模块

**文件**：`slow_interface_analyzer.py`

```python
class SlowInterfaceAnalyzer:
    """慢接口深度分析器"""
    
    def __init__(self):
        # 步骤识别规则
        self.step_patterns = {
            'database': {
                'keywords': ['执行SQL', 'query', 'select', 'insert', 'update'],
                'time_pattern': r'耗时[:\s]*(\d+)ms',
                'category': '数据库查询'
            },
            'external_api': {
                'keywords': ['调用接口', 'http request', '远程调用', 'RPC'],
                'time_pattern': r'耗时[:\s]*(\d+)ms',
                'category': '外部接口'
            },
            'cache': {
                'keywords': ['redis', 'cache', 'memcached'],
                'time_pattern': r'耗时[:\s]*(\d+)ms',
                'category': '缓存操作'
            },
            'business': {
                'keywords': ['业务处理', '计算', '处理'],
                'time_pattern': r'耗时[:\s]*(\d+)ms',
                'category': '业务逻辑'
            },
            'io': {
                'keywords': ['读取文件', '写入文件', 'IO', '文件操作'],
                'time_pattern': r'耗时[:\s]*(\d+)ms',
                'category': '文件IO'
            }
        }
    
    def analyze_slow_trace(self, trace_logs: list, total_time: int) -> dict:
        """
        分析单个慢接口的调用链
        
        Args:
            trace_logs: 该 traceId 的所有日志行
            total_time: 总耗时（毫秒）
        
        Returns:
            分析结果字典
        """
        steps = []
        unrecognized_time = total_time
        
        # 识别每个步骤
        for log_line in trace_logs:
            for step_type, pattern in self.step_patterns.items():
                # 检查是否包含关键字
                if any(kw in log_line for kw in pattern['keywords']):
                    # 提取耗时
                    import re
                    match = re.search(pattern['time_pattern'], log_line)
                    if match:
                        time_cost = int(match.group(1))
                        steps.append({
                            'type': step_type,
                            'category': pattern['category'],
                            'time': time_cost,
                            'log': log_line.strip()
                        })
                        unrecognized_time -= time_cost
        
        # 按耗时排序
        steps.sort(key=lambda x: x['time'], reverse=True)
        
        # 找出瓶颈（耗时最长的步骤）
        bottleneck = steps[0] if steps else None
        
        # 计算未识别的时间
        unrecognized_ratio = (unrecognized_time / total_time * 100) if total_time > 0 else 0
        
        return {
            'total_time': total_time,
            'steps': steps,
            'bottleneck': bottleneck,
            'unrecognized_time': unrecognized_time,
            'unrecognized_ratio': unrecognized_ratio,
            'needs_feedback': unrecognized_ratio > 30  # 超过 30% 未识别，需要反馈
        }
    
    def generate_feedback_prompt(self, trace_id: str, analysis: dict) -> str:
        """生成反馈提示"""
        if not analysis['needs_feedback']:
            return ""
        
        prompt = f"""
【需要您的反馈】traceId: {trace_id}

总耗时: {analysis['total_time']}ms
已识别步骤耗时: {analysis['total_time'] - analysis['unrecognized_time']}ms
未识别耗时: {analysis['unrecognized_time']}ms ({analysis['unrecognized_ratio']:.1f}%)

请查看完整日志，告诉我们：
1. 未识别的时间主要花在哪里？
2. 是否有新的步骤类型需要添加？

反馈方式：在报告中点击"提交反馈"按钮
"""
        return prompt
```

#### 报告增强

在 HTML 报告中添加：

1. **调用链可视化**（时间线图）
2. **瓶颈高亮**（最耗时的步骤）
3. **反馈按钮**（未识别时间 > 30% 时显示）

```html
<!-- 慢接口详情 -->
<div class="slow-interface-detail">
    <h4>traceId: abc123 (总耗时: 2500ms)</h4>
    
    <!-- 时间线 -->
    <div class="timeline">
        <div class="step database" style="width: 40%">
            数据库查询: 1000ms (40%)
        </div>
        <div class="step api" style="width: 32%">
            外部接口: 800ms (32%)
        </div>
        <div class="step business" style="width: 12%">
            业务逻辑: 300ms (12%)
        </div>
        <div class="step unknown" style="width: 16%">
            未识别: 400ms (16%)
        </div>
    </div>
    
    <!-- 瓶颈提示 -->
    <div class="bottleneck-alert">
        ⚠️ 瓶颈：数据库查询耗时 1000ms，占总耗时的 40%
        <br>
        建议：检查 SQL 语句是否有优化空间，考虑添加索引
    </div>
    
    <!-- 反馈按钮（未识别时间 > 30% 时显示）-->
    <button class="feedback-btn" onclick="submitFeedback('abc123')">
        📝 提交反馈（帮助改进分析）
    </button>
    
    <!-- 完整日志 -->
    <details>
        <summary>查看完整调用链</summary>
        <pre>
2026-03-09 16:00:00.100 [INFO] 接收请求 traceId=abc123
2026-03-09 16:00:00.150 [INFO] 执行SQL查询 耗时: 1000ms
2026-03-09 16:00:01.150 [INFO] 调用外部接口 耗时: 800ms
2026-03-09 16:00:01.950 [INFO] 业务处理 耗时: 300ms
2026-03-09 16:00:02.250 [INFO] 返回结果 总耗时: 2500ms
        </pre>
    </details>
</div>
```

---

## 🚀 实施计划

### 第一阶段：核心功能（本周）

**优先级 P0**：
1. ✅ 实现 `fetch_with_context()` 函数
2. ✅ 修改 `loki_fetcher.py`，添加 `--with-context` 参数
3. ✅ 实现 `SlowInterfaceAnalyzer` 类
4. ✅ 修改 `preprocess.py`，集成慢接口分析
5. ✅ 修改 `generate_html_report.py`，展示调用链和瓶颈

**预计工作量**：4-6 小时

### 第二阶段：反馈系统（下周）

**优先级 P1**：
1. 添加反馈收集功能（HTML 表单）
2. 创建反馈数据库（JSON 文件）
3. 基于反馈数据，扩展步骤识别规则

**预计工作量**：2-3 小时

### 第三阶段：智能优化（参赛后）

**优先级 P2**：
1. 基于历史数据，训练模式识别
2. 自动生成优化建议
3. 支持自定义规则

---

## 📊 效果预期

### 改进前
```
慢接口：/api/patient/list
总耗时：2500ms
traceId：abc123
```

### 改进后
```
慢接口：/api/patient/list
总耗时：2500ms
traceId：abc123

【调用链分析】
├─ 数据库查询: 1000ms (40%) ⚠️ 瓶颈
├─ 外部接口调用: 800ms (32%)
├─ 业务逻辑处理: 300ms (12%)
└─ 未识别步骤: 400ms (16%)

【优化建议】
1. 数据库查询是主要瓶颈，建议：
   - 检查 SQL 是否有 N+1 查询问题
   - 考虑添加索引
   - 使用缓存减少查询次数

2. 外部接口调用耗时较长，建议：
   - 检查网络延迟
   - 考虑异步调用
   - 添加超时控制

【需要您的反馈】
未识别的 400ms 主要花在哪里？
→ [提交反馈] 按钮
```

---

## 🎯 关键指标

- **上下文完整性**：ERROR 日志的 traceId 覆盖率 100%
- **瓶颈识别率**：慢接口的步骤识别率 > 70%
- **反馈响应率**：用户反馈率 > 20%
- **分析准确性**：基于反馈的准确性提升 > 30%

---

## 💬 用户反馈机制

### 反馈表单

```json
{
  "trace_id": "abc123",
  "total_time": 2500,
  "recognized_steps": [
    {"type": "database", "time": 1000},
    {"type": "api", "time": 800}
  ],
  "user_feedback": {
    "unrecognized_steps": [
      {
        "description": "JSON 序列化",
        "time": 300,
        "keywords": ["序列化", "JSON.stringify"]
      }
    ],
    "suggestions": "建议添加序列化步骤的识别"
  },
  "timestamp": "2026-03-09 16:00:00"
}
```

### 反馈处理流程

1. 用户提交反馈 → 保存到 `feedback/` 目录
2. 定期审查反馈 → 提取新的识别规则
3. 更新 `step_patterns` → 发布新版本
4. 通知用户改进结果

---

## 📝 文件清单

### 新增文件
- `loki_fetcher_enhanced.py` - 增强版 Loki 拉取器（支持上下文）
- `slow_interface_analyzer.py` - 慢接口分析器
- `feedback_collector.py` - 反馈收集器
- `feedback/` - 反馈数据目录

### 修改文件
- `loki_fetcher.py` - 添加 `--with-context` 参数
- `preprocess.py` - 集成慢接口分析
- `generate_html_report.py` - 增强报告展示
- `log_inspect_main.py` - 集成新功能

---

## ✅ 验收标准

### 功能验收
- [ ] ERROR 日志能拉取完整上下文（包含 INFO、DEBUG）
- [ ] 慢接口能识别主要步骤（数据库、API、业务逻辑等）
- [ ] 报告中能看到调用链时间线
- [ ] 报告中能看到瓶颈提示
- [ ] 未识别时间 > 30% 时显示反馈按钮

### 性能验收
- [ ] 两阶段拉取的总时间 < 单阶段的 2 倍
- [ ] 慢接口分析的处理时间 < 1 秒/条

### 用户体验验收
- [ ] 报告易读，调用链清晰
- [ ] 优化建议具体可行
- [ ] 反馈流程简单明了

---

## 🔄 迭代计划

### v1.0（本周）
- 基础功能：上下文拉取 + 步骤识别

### v1.1（下周）
- 反馈系统 + 规则扩展

### v2.0（参赛后）
- 智能分析 + 自动优化建议

# 日志分析对齐和优化方案

## 📋 问题 1：tool_api_fetcher 和 loki_fetcher 的对齐点

### 当前情况分析

**loki_fetcher（K8s 环境）**：
- 当前：只拉取 ERROR/WARN 级别的日志
- 问题：丢失上下文
- 优化后：两阶段拉取（先拉 ERROR/WARN，再根据 traceId 拉完整上下文）

**tool_api_fetcher（传统服务器）**：
- 当前：下载服务器的所有日志（完整日志文件）
- 特点：本身就包含所有级别的日志
- 问题：文件很大，包含很多无关日志

### 🎯 对齐方案：在 preprocess 阶段统一过滤

**核心思路**：
- loki_fetcher：在拉取阶段过滤（两阶段拉取）
- tool_api_fetcher：在分析阶段过滤（preprocess）
- 最终效果：两种方式都只分析"有问题的 traceId"

**实现方式**：

```
┌─────────────────────────────────────────────────────────────┐
│                    loki_fetcher (K8s)                       │
├─────────────────────────────────────────────────────────────┤
│ 阶段 1: 拉取 ERROR/WARN → 提取 traceId                      │
│ 阶段 2: 针对每个 traceId 拉取完整日志                       │
│ 输出: filtered.log (只包含有问题的 traceId)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 tool_api_fetcher (传统服务器)                │
├─────────────────────────────────────────────────────────────┤
│ 下载: 完整日志文件 (all.log)                                │
│ 输出: all.log (包含所有日志)                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              preprocess.py (统一分析入口)                    │
├─────────────────────────────────────────────────────────────┤
│ 新增参数: --filter-by-error-trace                           │
│                                                             │
│ 如果启用过滤:                                                │
│   1. 第一遍扫描: 找出所有 ERROR/WARN 的 traceId             │
│   2. 第二遍扫描: 只保留这些 traceId 的日志                   │
│   3. 进行分析                                               │
│                                                             │
│ 如果不启用过滤:                                              │
│   直接分析所有日志（当前行为）                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    digest.json + report.html
```

### 使用方式

```bash
# loki_fetcher: 在拉取阶段过滤（推荐）
python loki_fetcher.py \
  --grafana http://127.0.0.1:16291 \
  --app winning-winex-ward-pbc \
  --start "2026-03-09 08:00" \
  --end "2026-03-09 10:00" \
  --with-context \
  --output filtered.log

# preprocess: 直接分析（已经过滤）
python preprocess.py filtered.log -o digest.json

# ─────────────────────────────────────────────────

# tool_api_fetcher: 下载全量日志
python tool_api_fetcher.py \
  --base-url http://172.16.9.87:8089 \
  --app-id 9380 \
  --env-id xxx \
  --output all.log

# preprocess: 在分析阶段过滤（推荐）
python preprocess.py all.log \
  --filter-by-error-trace \
  -o digest.json

# 或者不过滤（分析所有日志）
python preprocess.py all.log -o digest.json
```

### 优势

1. **灵活性**：
   - K8s 环境：在拉取阶段过滤（减少网络传输）
   - 传统服务器：在分析阶段过滤（保留原始日志）

2. **一致性**：
   - 两种方式最终都只分析"有问题的 traceId"
   - 报告结果一致

3. **可选性**：
   - 可以选择是否过滤
   - 灵活应对不同场景

---

## 📋 问题 2：异常统计分类优化

### 当前问题

1. **"Other" 分类不清晰**：
   - 用户看到 "Other" 不知道是什么问题
   - 应该细化分类或提供更多信息

2. **统计数量过大**：
   - 可能是重复统计
   - 需要检查统计逻辑

3. **没有中文化**：
   - 分类名称是英文（NullPointerException、SQLException 等）
   - 应该翻译成中文

### 🎯 优化方案

#### 1. 细化错误分类 + 中文化

**当前分类**（preprocess.py 第 48-56 行）：
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
```

**优化后**：

```python
ERROR_CATEGORIES = {
    # 分类名 → (中文名, 关键词列表, 优先级)
    'null_pointer': {
        'name': '空指针异常',
        'keywords': ['NullPointerException', 'null', 'NPE', '空指针'],
        'priority': 1,
        'suggestion': '检查对象是否为空，添加空值校验'
    },
    'sql_error': {
        'name': 'SQL错误',
        'keywords': ['ORA-', 'SQLException', 'SQL Error', '数据库错误', 'SQL语法'],
        'priority': 2,
        'suggestion': '检查SQL语句语法，确认数据库连接正常'
    },
    'timeout': {
        'name': '超时异常',
        'keywords': ['timeout', 'Timeout', '超时', 'timed out'],
        'priority': 3,
        'suggestion': '检查网络连接，增加超时时间或优化接口性能'
    },
    'auth_error': {
        'name': '认证/权限问题',
        'keywords': ['认证失败', '过期', 'token', 'Token', '权限不足', 'unauthorized', '未授权'],
        'priority': 1,
        'suggestion': '检查token是否过期，确认用户权限配置'
    },
    'validation_error': {
        'name': '参数校验失败',
        'keywords': ['参数错误', '校验失败', 'validation', 'Validation', '参数不能为空'],
        'priority': 4,
        'suggestion': '检查请求参数是否完整，确认参数格式正确'
    },
    'connection_error': {
        'name': '连接异常',
        'keywords': ['Connection', '连接失败', 'refused', 'reset', '连接超时'],
        'priority': 2,
        'suggestion': '检查网络连接，确认目标服务是否正常'
    },
    'memory_error': {
        'name': '内存溢出',
        'keywords': ['OutOfMemory', 'OOM', '内存不足', 'heap space'],
        'priority': 1,
        'suggestion': '增加JVM内存配置，检查是否有内存泄漏'
    },
    'plugin_error': {
        'name': '插件配置问题',
        'keywords': ['找不到插件', 'plugin', '插件未找到', '事件管道'],
        'priority': 3,
        'suggestion': '检查插件配置文件，确认插件是否正确安装'
    },
    'json_parse_error': {
        'name': 'JSON解析错误',
        'keywords': ['JSON', 'parse', '解析失败', 'JsonParseException'],
        'priority': 4,
        'suggestion': '检查JSON格式是否正确，确认数据结构'
    },
    'file_not_found': {
        'name': '文件不存在',
        'keywords': ['FileNotFoundException', '文件不存在', 'No such file'],
        'priority': 3,
        'suggestion': '检查文件路径是否正确，确认文件是否存在'
    },
    'unknown': {
        'name': '其他异常',
        'keywords': [],  # 兜底分类
        'priority': 5,
        'suggestion': '需要查看详细日志进行分析'
    }
}
```

#### 2. 改进分类逻辑

**当前逻辑**（preprocess.py 第 73-78 行）：
```python
def categorize_error(content: str) -> str:
    """根据日志内容分类错误类型"""
    for category, keywords in ERROR_CATEGORIES.items():
        for keyword in keywords:
            if keyword in content:
                return category
    return 'Other'
```

**优化后**：

```python
def categorize_error(content: str) -> dict:
    """
    根据日志内容分类错误类型
    
    Returns:
        {
            'category': 'null_pointer',
            'name': '空指针异常',
            'matched_keyword': 'NullPointerException',
            'suggestion': '检查对象是否为空...'
        }
    """
    # 按优先级排序（优先级高的先匹配）
    sorted_categories = sorted(
        ERROR_CATEGORIES.items(),
        key=lambda x: x[1]['priority']
    )
    
    for category_id, category_info in sorted_categories:
        for keyword in category_info['keywords']:
            if keyword.lower() in content.lower():
                return {
                    'category': category_id,
                    'name': category_info['name'],
                    'matched_keyword': keyword,
                    'suggestion': category_info['suggestion']
                }
    
    # 兜底：未识别的错误
    return {
        'category': 'unknown',
        'name': '其他异常',
        'matched_keyword': None,
        'suggestion': ERROR_CATEGORIES['unknown']['suggestion'],
        'content_preview': content[:100]  # 提供内容预览帮助分析
    }
```

#### 3. 修复统计逻辑

**问题定位**：

查看 preprocess.py 第 223-236 行：
```python
if level in ('ERROR', 'FATAL'):
    category = categorize_error(content)
    stats['error_categories'][category] += 1  # ← 这里统计
    stats['error_count'] += 1
    if len(error_lines) < 500:
        error_lines.append({...})
```

**可能的问题**：
1. 同一个 traceId 的多行 ERROR 日志被重复统计
2. 需要按 traceId 去重

**优化方案**：

```python
# 在 process_file 函数中添加 traceId 去重
seen_error_traces = set()

if level in ('ERROR', 'FATAL'):
    trace_id = parsed['trace_id']
    
    # 按 traceId 去重统计
    if trace_id and trace_id not in seen_error_traces:
        seen_error_traces.add(trace_id)
        
        category_info = categorize_error(content)
        stats['error_categories'][category_info['name']] += 1
        stats['error_count'] += 1
        
        if len(error_lines) < 500:
            error_lines.append({
                'timestamp': parsed['timestamp_str'],
                'class': parsed['class_name'],
                'user': parsed['user_name'],
                'content': content[:500],
                'category': category_info['name'],  # 使用中文名
                'category_id': category_info['category'],
                'matched_keyword': category_info['matched_keyword'],
                'suggestion': category_info['suggestion'],
                'trace_id': trace_id
            })
    elif not trace_id:
        # 没有 traceId 的错误也要统计（但可能重复）
        category_info = categorize_error(content)
        stats['error_categories'][category_info['name']] += 1
        stats['error_count'] += 1
```

#### 4. 报告展示优化

**当前报告**（generate_html_report.py）：
```html
<tr>
    <td>NullPointerException</td>
    <td>654</td>
    <td>11.2%</td>
</tr>
```

**优化后**：
```html
<tr>
    <td>
        <strong>空指针异常</strong>
        <br>
        <small style="color: #666;">匹配关键词: NullPointerException</small>
    </td>
    <td>654</td>
    <td>11.2%</td>
    <td>
        <span class="suggestion">
            💡 检查对象是否为空，添加空值校验
        </span>
    </td>
</tr>
```

---

## 🚀 实施计划

### 第一步：修复分类和统计（今天）

1. ✅ 更新 ERROR_CATEGORIES（中文化 + 细化）
2. ✅ 改进 categorize_error 函数
3. ✅ 添加 traceId 去重逻辑
4. ✅ 测试统计准确性

### 第二步：添加过滤功能（明天）

1. ✅ 在 preprocess.py 添加 --filter-by-error-trace 参数
2. ✅ 实现两遍扫描逻辑
3. ✅ 测试过滤效果

### 第三步：优化报告展示（后天）

1. ✅ 更新 generate_html_report.py
2. ✅ 添加优化建议列
3. ✅ 美化展示效果

---

## 📊 预期效果

### 优化前
```
异常统计：
- NullPointerException: 654
- SQLException: 5
- Other: 3,272  ← 不清楚是什么
```

### 优化后
```
异常统计：
- 空指针异常: 654 (11.2%)
  💡 检查对象是否为空，添加空值校验
  
- 认证/权限问题: 1,794 (30.7%)
  💡 检查token是否过期，确认用户权限配置
  
- 插件配置问题: 207 (3.5%)
  💡 检查插件配置文件，确认插件是否正确安装
  
- SQL错误: 5 (0.1%)
  💡 检查SQL语句语法，确认数据库连接正常
  
- 其他异常: 184 (3.1%)
  💡 需要查看详细日志进行分析
  （展开查看未识别的错误内容）
```

---

## ✅ 验收标准

1. **分类清晰**：
   - [ ] 所有分类都有中文名称
   - [ ] "其他异常"占比 < 10%
   - [ ] 每个分类都有优化建议

2. **统计准确**：
   - [ ] 按 traceId 去重
   - [ ] 总数 = 各分类之和
   - [ ] 百分比计算正确

3. **用户体验**：
   - [ ] 报告易读
   - [ ] 建议具体可行
   - [ ] 没有英文术语（或有中文解释）

# 2026-03-12 22:32 代码恢复进度

## 背景
OpenClaw 升级（v2026.2.25 → v2026.3.11）后，workspace 里的文件被覆盖，丢失了今天所有的修改。

## 已完成的恢复工作

### 1. generate_html_report_v2.py - error 详情显示 ✅ (22:32)

### 2. generate_html_report_v2.py - 慢接口详情渲染 ✅ (22:38)

### 3. generate_html_report_v2.py - 日志质量分析和时间间隔分析 ✅ (23:05)
**修改内容：**
- 添加 `generate_log_quality_analysis` 函数
- 显示缺少 API 入口比例、null 异常比例、影响级别分布
- 在慢接口详情中添加时间间隔分析（>100ms）

### 4. preprocess.py - 四级分组和 caller_service 提取 ✅ (22:42)
**修改位置**：line 172-180 之后
**修改内容**：在 API 入口显示后，添加了：
- 调用方服务显示（caller_service）
  - SELF → 本服务
  - ASYNC → 异步任务
  - RPC → RPC调用
  - winning-winex-ipt-xxx-pbc → 简化显示为服务名
- 线程信息显示（thread）
- 影响级别显示（impact_level）
  - high → 高影响（红色）
  - medium → 中影响（橙色）
  - low → 低影响（绿色）

**代码片段**：
```python
# 调用方服务
caller_service = sample.get('caller_service', error.get('caller_service', 'UNKNOWN'))
if caller_service and caller_service != 'UNKNOWN':
    caller_display = {
        'SELF': '本服务',
        'ASYNC': '异步任务',
        'RPC': 'RPC调用',
        'UNKNOWN': '未知'
    }.get(caller_service, caller_service.replace('winning-winex-ipt-', '').replace('-pbc', ''))
    html += f'<p class="error-meta"><strong>调用方:</strong> {caller_display}</p>'

# 线程信息
thread = sample.get('thread', '')
if thread:
    html += f'<p class="error-meta"><strong>线程:</strong> {thread}</p>'

# 影响级别
impact_level = error.get('impact_level', sample.get('impact_level', ''))
if impact_level:
    impact_text = {'high': '高影响', 'medium': '中影响', 'low': '低影响'}.get(impact_level, impact_level)
    impact_color = {'high': '#d32f2f', 'medium': '#f57c00', 'low': '#388e3c'}.get(impact_level, '#666')
    html += f'<p class="error-meta"><strong>影响级别:</strong> <span style="color: {impact_color}; font-weight: bold;">{impact_text}</span></p>'
```

## 待完成的恢复工作

### 2. generate_html_report_v2.py - 慢接口详情渲染 ⏳
**需要添加**：
- representative_trace_logs 显示（完整调用链）
- analysis 显示（时间分析、瓶颈识别）
  - total_time
  - steps（每一步的耗时）
  - bottleneck（瓶颈）
  - suggestions（优化建议）

**参考数据结构**（从 logs_20260312_145058_默认集群_digest.json）：
```json
{
  "representative_trace_logs": [...],  // 完整调用链日志
  "analysis": {
    "total_time": 28188,
    "steps": [...],
    "bottleneck": {...},
    "suggestions": [...]
  }
}
```

### 3. preprocess.py - 四级分组和 caller_service 提取 ⏳
**需要添加**：
1. `extract_caller_service_from_thread(thread)` 函数
   - 识别跨服务调用：`winning-winex-xxx_Jetty-Worker`
   - 识别本服务调用：`Jetty-Worker_xxx`
   - 识别异步任务：`exe-xxx`, `enc-xxx`
   - 识别 RPC 调用：`rpc-exec-xxx`

2. 修改 `categorize_trace()` 函数
   - 提取 caller_service
   - 所有 return 语句添加 caller_service 字段

3. 修改 `aggregate_errors()` 函数
   - 分组键从三级改为四级：`category:root_class:api_entry:caller_service`
   - 添加 representative_traces 参数
   - 优先将代表 trace 插入 samples[0]

4. 修改 `process_file()` 函数
   - 读取代表 trace 列表（从日志文件第一行）
   - 传递 caller_service 和 thread 到 error_line

### 4. loki_fetcher.py - 按 root_class 分组 ⏳
**需要修改**：
1. 重写 `extract_error_representatives()` 函数
   - 分组键从 `category:api_entry:caller_service:error_signature` 改为 `category:class_name:api_entry:caller_service`
   - 添加 `extract_class_name()` 函数（从 ERROR 日志提取类名）
   - 效果：代表 trace 从 148 个降至 51 个

2. 在日志文件开头写入代表 trace 列表
   - 格式：`# REPRESENTATIVE_TRACES: trace1,trace2,...`

### 5. log_inspect_main.py - 实时输出和时间记录 ⏳
**需要修改**：
1. 去掉 `capture_output=True`（实时显示 loki_fetcher.py 输出）
2. `--max-context-traces` 从 50 改为 100
3. 记录拉取开始/结束时间（`fetch_start_ts`、`_last_fetch_meta`）
4. 传递 `--fetch-start/--fetch-end/--fetch-duration` 给 preprocess.py

## 参考资料

### 工作版本（14:50 生成）
- **报告**：`C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_145058_默认集群_report.html`
  - 包含完整功能：调用方(30次)、线程(31次)、影响级别(1次)、API入口(25次)
- **Digest**：`C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_145058_默认集群_digest.json`
  - 可以从这里反推数据结构

### 详细记录
- `memory/2026-03-12.md` - 今天完整的工作记录
- `memory/2026-03-12-code-lost.md` - 代码丢失的详细记录
- `RESTORE_PLAN.md` - 恢复计划

## 下次 session 的行动计划

1. **继续恢复 generate_html_report_v2.py**
   - 添加慢接口的 representative_trace_logs 和 analysis 显示
   - 参考旧报告的 HTML 结构

2. **恢复 preprocess.py**
   - 添加 extract_caller_service_from_thread 函数
   - 修改 categorize_trace、aggregate_errors、process_file

3. **恢复 loki_fetcher.py**
   - 重写 extract_error_representatives
   - 写入代表 trace 列表

4. **恢复 log_inspect_main.py**
   - 实时输出、max-context-traces=100

5. **测试验证**
   - 运行一次完整的日志拉取
   - 对比新旧报告，确保功能完整

## 估计工作量
- generate_html_report_v2.py 慢接口部分：30 分钟
- preprocess.py：1 小时
- loki_fetcher.py：30 分钟
- log_inspect_main.py：15 分钟
- 测试验证：15 分钟
- **总计**：约 2.5 小时

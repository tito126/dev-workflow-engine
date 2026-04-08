import json
import re
from collections import defaultdict

# 读取重新分析的digest
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed', encoding='utf-8') as f:
    digest = json.load(f)

# 读取原始日志
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_默认集群.log', encoding='utf-8') as f:
    all_lines = f.readlines()

# 生成markdown报告
output = []

output.append("# 日志分析报告 - 优化版")
output.append("**时间**: 2026-03-11 16:22~16:32 (10分钟)")
output.append("**生成时间**: 2026-03-11 17:45")
output.append("")

# 一、异常分类优化结果
output.append("## 一、异常分类优化结果")
output.append("")
cats = digest['summary']['error_categories']
total_errors = sum(cats.values())
output.append(f"**总ERROR数**: {total_errors}")
output.append("")
output.append("| 分类 | 数量 | 占比 |")
output.append("|------|------|------|")
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    pct = v / total_errors * 100
    output.append(f"| {k} | {v} | {pct:.1f}% |")
output.append("")
output.append("**优化效果**: '其他异常'从439降到0，新增'业务逻辑错误'和'日志系统异常'分类")
output.append("")

# 二、日志反哺模块
output.append("## 二、日志反哺模块 - 不明确日志案例")
output.append("")
output.append("以下异常的日志内容不够明确，建议开发团队改进：")
output.append("")

feedback_cases = []
for error_group in digest['errors']:
    category = error_group['category']
    samples = error_group['samples']
    
    unclear_samples = []
    for sample in samples[:5]:
        content = sample.get('content', '')
        error_reason = sample.get('error_reason', '')
        
        is_unclear = False
        reason = ""
        
        if content.strip() == 'null':
            is_unclear = True
            reason = "日志内容只有'null'，无法定位问题根因"
        elif error_reason == '未提取到明确错误信息':
            is_unclear = True
            reason = "无法提取明确的错误信息"
        elif len(content) < 20 and not re.search(r'[A-Z]{2}\d{4,}', content):
            is_unclear = True
            reason = "日志内容过短，缺少上下文信息"
        
        if is_unclear:
            unclear_samples.append({
                'content': content[:100],
                'reason': reason,
                'trace_id': sample.get('trace_id'),
                'class': sample.get('class')
            })
    
    if unclear_samples:
        feedback_cases.append({
            'category': category,
            'count': len(unclear_samples),
            'samples': unclear_samples
        })

if feedback_cases:
    output.append(f"发现 **{len(feedback_cases)}** 个分类存在不明确日志:")
    output.append("")
    for case in feedback_cases:
        output.append(f"### {case['category']}")
        output.append(f"**不明确样本数**: {case['count']}")
        output.append("")
        output.append("| 类 | 内容 | 问题 | traceId |")
        output.append("|---|---|---|---|")
        for sample in case['samples'][:3]:
            content_short = sample['content'][:50].replace('|', '\\|')
            output.append(f"| {sample['class']} | {content_short} | {sample['reason']} | {sample['trace_id']} |")
        output.append("")
else:
    output.append("所有异常日志内容都较为明确，无需反哺")
    output.append("")

# 三、慢接口完整调用链分析
output.append("## 三、慢接口完整调用链分析")
output.append("")

slow_apis = digest.get('slow_apis', [])[:3]

for i, api in enumerate(slow_apis, 1):
    api_path = api['api_path']
    top_traces = api.get('top_traces', [])
    if not top_traces:
        continue
    
    trace_id = top_traces[0]['trace_id']
    duration = top_traces[0]['duration_ms']
    
    output.append(f"### 慢接口 #{i}: {api_path}")
    output.append(f"- **最慢trace**: `{trace_id}`")
    output.append(f"- **总耗时**: {duration}ms")
    output.append("")
    
    # 从原始日志中提取该trace的所有日志
    trace_lines = []
    for line in all_lines:
        if trace_id in line:
            trace_lines.append(line.strip())
    
    if not trace_lines:
        output.append("未找到该trace的日志（可能被过滤）")
        output.append("")
        continue
    
    # 分析调用链
    call_chain = []
    timing_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*?(\S+\.\S+).*?耗时[：:]?\s*(\d+)\s*(?:毫秒|ms)')
    
    for line in trace_lines:
        match = timing_pattern.search(line)
        if match:
            timestamp = match.group(1)
            classname = match.group(2).split('.')[-1]
            timing_ms = int(match.group(3))
            call_chain.append({
                'timestamp': timestamp,
                'class': classname,
                'timing': timing_ms
            })
    
    if call_chain:
        call_chain.sort(key=lambda x: x['timestamp'])
        
        output.append("**完整调用链**:")
        output.append("")
        output.append("| 序号 | 时间戳 | 类名 | 耗时(ms) | 可视化 |")
        output.append("|------|--------|------|----------|--------|")
        for j, call in enumerate(call_chain, 1):
            bar = '█' * min(int(call['timing'] / 100), 50)
            output.append(f"| {j} | {call['timestamp']} | {call['class']} | {call['timing']} | {bar} |")
        output.append("")
        
        slowest = max(call_chain, key=lambda x: x['timing'])
        output.append(f"**最慢环节**: {slowest['class']} ({slowest['timing']}ms)")
        output.append("")
    else:
        output.append(f"该trace共{len(trace_lines)}条日志，但未找到明确的耗时信息")
        output.append("")
        output.append("**前3条日志**:")
        output.append("```")
        for line in trace_lines[:3]:
            parts = line.split('--')
            if len(parts) >= 2:
                output.append(parts[-1][:100])
        output.append("```")
        output.append("")

output.append("---")
output.append("**报告生成**: OpenClaw Log Inspector v2.1")
output.append("**优化内容**: 异常分类、日志反哺、慢接口调用链分析")

# 写入文件
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_final_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("报告已生成: logs_20260311_163218_final_report.md")

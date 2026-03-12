import json
import re
from collections import defaultdict

# 读取重新分析的digest
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed', encoding='utf-8') as f:
    digest = json.load(f)

# 读取原始日志
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_默认集群.log', encoding='utf-8') as f:
    all_lines = f.readlines()

print("="*80)
print("一、异常分类优化结果")
print("="*80)
cats = digest['summary']['error_categories']
total_errors = sum(cats.values())
print(f"\n总ERROR数: {total_errors}")
print(f"\n分类统计:")
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    pct = v / total_errors * 100
    print(f"  {k}: {v} ({pct:.1f}%)")

print("\n" + "="*80)
print("二、日志反哺模块 - 不明确日志案例")
print("="*80)

# 分析每个分类中日志内容不明确的案例
feedback_cases = []

for error_group in digest['errors']:
    category = error_group['category']
    samples = error_group['samples']
    
    # 检查是否有不明确的日志
    unclear_samples = []
    for sample in samples[:5]:  # 只看前5个样本
        content = sample.get('content', '')
        error_reason = sample.get('error_reason', '')
        
        # 判断标准：
        # 1. 内容只有"null"
        # 2. 错误原因是"未提取到明确错误信息"
        # 3. 内容过短（<20字符）且没有明确错误码
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
    print(f"\n发现 {len(feedback_cases)} 个分类存在不明确日志:\n")
    for case in feedback_cases:
        print(f"【{case['category']}】")
        print(f"  不明确样本数: {case['count']}")
        for i, sample in enumerate(case['samples'][:3], 1):
            print(f"  样本{i}:")
            print(f"    类: {sample['class']}")
            print(f"    内容: {sample['content']}")
            print(f"    问题: {sample['reason']}")
            print(f"    traceId: {sample['trace_id']}")
        print()
else:
    print("\n✅ 所有异常日志内容都较为明确，无需反哺")

print("="*80)
print("三、慢接口完整调用链分析")
print("="*80)

# 获取TOP 3慢接口的traceId
slow_apis = digest.get('slow_apis', [])[:3]

for i, api in enumerate(slow_apis, 1):
    api_path = api['api_path']
    top_traces = api.get('top_traces', [])
    if not top_traces:
        continue
    
    trace_id = top_traces[0]['trace_id']
    duration = top_traces[0]['duration_ms']
    
    print(f"\n【慢接口 #{i}】{api_path}")
    print(f"  最慢trace: {trace_id}")
    print(f"  总耗时: {duration}ms")
    print(f"\n  完整调用链:")
    
    # 从原始日志中提取该trace的所有日志
    trace_lines = []
    for line in all_lines:
        if trace_id in line:
            trace_lines.append(line.strip())
    
    if not trace_lines:
        print(f"    [!] 未找到该trace的日志（可能被过滤）")
        continue
    
    # 分析调用链
    # 提取关键信息：时间戳、类名、耗时
    call_chain = []
    timing_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*?(\S+\.\S+).*?耗时[：:]?\s*(\d+)\s*(?:毫秒|ms)')
    
    for line in trace_lines:
        match = timing_pattern.search(line)
        if match:
            timestamp = match.group(1)
            classname = match.group(2).split('.')[-1]  # 只取类名
            timing_ms = int(match.group(3))
            call_chain.append({
                'timestamp': timestamp,
                'class': classname,
                'timing': timing_ms
            })
    
    if call_chain:
        # 按时间排序
        call_chain.sort(key=lambda x: x['timestamp'])
        
        # 显示调用链
        for j, call in enumerate(call_chain, 1):
            bar = '█' * min(int(call['timing'] / 100), 50)
            print(f"    {j}. [{call['timestamp']}] {call['class']}: {call['timing']}ms {bar}")
        
        # 找出最慢的环节
        slowest = max(call_chain, key=lambda x: x['timing'])
        print(f"\n  [!] 最慢环节: {slowest['class']} ({slowest['timing']}ms)")
    else:
        print(f"    [i] 该trace共{len(trace_lines)}条日志，但未找到明确的耗时信息")
        print(f"    前3条日志:")
        for line in trace_lines[:3]:
            # 提取关键部分
            parts = line.split('--')
            if len(parts) >= 2:
                print(f"      {parts[-1][:80]}")

print("\n" + "="*80)
print("分析完成")
print("="*80)

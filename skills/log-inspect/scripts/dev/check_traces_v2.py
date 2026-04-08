import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_v5', encoding='utf-8') as f:
    d = json.load(f)

# 查找这两个traceId
target_traces = ['04ca3ff6a7b44e7a829716d56953065b', '03d8d9c89797413ebbd371624789a3c4']

print("查找目标traceId的分类：\n")
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('trace_id') in target_traces:
            print(f"TraceId: {sample['trace_id']}")
            print(f"Category: {sample['category']}")
            print(f"Content: {sample['content'][:150]}")
            print(f"Error Reason: {sample.get('error_reason', 'N/A')}")
            print("-" * 80)

print("\n第三方调用异常分类：")
for error_group in d['errors']:
    if error_group['category'] == '第三方调用异常':
        print(f"Count: {error_group['count']}")
        for sample in error_group['samples'][:5]:
            print(f"  - {sample.get('trace_id', 'N/A')[:20]}: {sample['content'][:80]}")

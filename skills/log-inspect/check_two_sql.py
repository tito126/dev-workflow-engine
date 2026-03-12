import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final13', encoding='utf-8') as f:
    d = json.load(f)

target_traces = ['12196f4a6f134ff590a208566d3c85e1', '01c4a350aea74f7baf877ca292967cf3']

print('查找这两个SQL错误trace：\n')
for trace_id in target_traces:
    found = False
    for error_group in d['errors']:
        for sample in error_group['samples']:
            if sample.get('trace_id') == trace_id:
                print(f"TraceId: {sample['trace_id']}")
                print(f"Category: {sample['category']}")
                print(f"Root Class: {sample.get('root_class', 'N/A')}")
                print(f"API入口: {sample.get('api_entry', 'N/A')}")
                print(f"Content: {sample.get('content', '')[:100]}")
                print("-" * 80)
                found = True
                break
        if found:
            break
    if not found:
        print(f"未找到 {trace_id}\n")

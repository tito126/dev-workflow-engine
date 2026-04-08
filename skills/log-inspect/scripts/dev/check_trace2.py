import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final6', encoding='utf-8') as f:
    d = json.load(f)

trace_id = '18ce65ca05634c0a9e00d02cfdeed774'

print(f'查找 {trace_id}：\n')
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('trace_id') == trace_id:
            print(f"TraceId: {sample['trace_id']}")
            print(f"Category: {sample['category']}")
            print(f"Root Class: {sample.get('root_class', 'N/A')}")
            print(f"API入口: {sample.get('api_entry', 'N/A')}")
            print(f"Content: {sample.get('content', '')[:80]}")
            break

import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final10', encoding='utf-8') as f:
    d = json.load(f)

trace_id = '01c8f97fbb7a47abb7052ff9ecaf99e7'

print(f'查找 {trace_id} 的分类：\n')
found = False
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('trace_id') == trace_id:
            print(f"TraceId: {sample['trace_id']}")
            print(f"Category: {sample['category']}")
            print(f"Root Class: {sample.get('root_class', 'N/A')}")
            print(f"Class: {sample.get('class', 'N/A')}")
            print(f"API入口: {sample.get('api_entry', 'N/A')}")
            print(f"Content: {sample.get('content', '')[:100]}")
            found = True
            break
    if found:
        break

if not found:
    print(f"未找到 {trace_id}")

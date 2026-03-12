import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final2', encoding='utf-8') as f:
    d = json.load(f)

trace_id = '01b0779fd15d40b2ad0383cbb1735d27'

print(f'查找 {trace_id} 的分类：\n')
found = False
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('trace_id') == trace_id:
            print(f"TraceId: {sample['trace_id']}")
            print(f"Category: {sample['category']}")
            print(f"Content: {sample['content'][:150]}")
            print(f"API入口: {sample.get('api_entry', 'N/A')}")
            found = True
            break
    if found:
        break

if not found:
    print(f"未找到 {trace_id}")

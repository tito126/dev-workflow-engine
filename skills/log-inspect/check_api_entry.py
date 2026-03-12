import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final3', encoding='utf-8') as f:
    d = json.load(f)

api_entry = '/api/v1/app_inpatient_encounter/invited_received/check'

print(f'查找所有使用 {api_entry} 的异常：\n')

results = []
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('api_entry') == api_entry:
            results.append({
                'trace_id': sample.get('trace_id'),
                'category': sample['category'],
                'content': sample['content'][:80]
            })

if results:
    print(f"找到 {len(results)} 个使用该API的异常：\n")
    for r in results:
        print(f"TraceId: {r['trace_id']}")
        print(f"Category: {r['category']}")
        print(f"Content: {r['content']}")
        print("-" * 80)
else:
    print("未找到使用该API的异常")

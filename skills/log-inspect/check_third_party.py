import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final11', encoding='utf-8') as f:
    d = json.load(f)

print('第三方调用异常：\n')
for error_group in d['errors']:
    if '第三方' in error_group['category']:
        print(f"Count: {error_group['count']} 个trace")
        print(f"Class: {error_group.get('class', 'N/A')}")
        print(f"API入口: {error_group.get('api_entries', [])[:3]}")
        if error_group.get('samples'):
            sample = error_group['samples'][0]
            print(f"Sample TraceId: {sample.get('trace_id', 'N/A')}")
            print(f"Matched Keyword: {sample.get('matched_keyword', 'N/A')}")
            print(f"Error Reason: {sample.get('error_reason', 'N/A')}")
        break

import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\test_digest2.json', encoding='utf-8') as f:
    d = json.load(f)

slow_apis = d.get('slow_apis', [])
print(f'slow_apis 数量: {len(slow_apis)}')

if slow_apis:
    s = slow_apis[0]
    print('第一个 slow_api 的字段:', list(s.keys()))
    print('有 representative_trace_logs:', 'representative_trace_logs' in s)
    print('有 analysis:', 'analysis' in s)

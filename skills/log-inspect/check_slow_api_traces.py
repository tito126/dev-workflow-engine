import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)

slow_apis = d.get('slow_apis', [])
print('慢接口Top 3:')
for i, api in enumerate(slow_apis[:3]):
    trace_id = api['top_traces'][0]['trace_id'] if api.get('top_traces') else 'N/A'
    print(f'{i+1}. {api["api_path"]}: {api["max_ms"]}ms')
    print(f'   traceId: {trace_id}')
    
    # 检查这个traceId在原始日志中有多少行
    with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群.log', encoding='utf-8') as f2:
        count = sum(1 for line in f2 if trace_id in line)
    print(f'   原始日志中: {count} 行')

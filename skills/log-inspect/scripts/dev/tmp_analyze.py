import json
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)
slow = d.get('slow_apis', [])
print('TOP SLOW APIS:')
for i, api in enumerate(slow[:10], 1):
    path = api.get('api_path', '')
    print(f'#{i} {path} max={api["max_ms"]}ms avg={api["avg_ms"]}ms count={api["count"]}')
    if api.get('top_traces'):
        t = api['top_traces'][0]
        print(f'   trace={str(t.get("trace_id",""))[:20]}... duration={t.get("duration_ms")}ms')

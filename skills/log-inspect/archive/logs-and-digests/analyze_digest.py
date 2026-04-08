import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)

slow = d.get('slow_apis', [])
print('=== TOP SLOW APIS ===')
for i, api in enumerate(slow[:10], 1):
    path = api.get('api_path', '')
    max_ms = api.get('max_ms')
    avg_ms = api.get('avg_ms')
    count = api.get('count')
    print(f'#{i} {path}')
    print(f'   max={max_ms}ms avg={avg_ms}ms count={count}')
    traces = api.get('top_traces', [])
    if traces:
        t = traces[0]
        tid = str(t.get('trace_id', ''))[:24]
        dur = t.get('duration_ms')
        print(f'   top_trace={tid} {dur}ms')

print()
print('=== ERROR SUMMARY ===')
cats = d.get('summary', {}).get('error_categories', {})
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

print()
print('=== ERROR DETAILS ===')
errors = d.get('errors', [])
for e in errors[:15]:
    cat = e.get('category')
    cls = e.get('class', '')
    count = e.get('count')
    samples = e.get('samples', [])
    content = samples[0].get('content', '')[:80] if samples else ''
    trace_id = samples[0].get('trace_id') if samples else None
    print(f'[{cat}] {cls} x{count}')
    print(f'   内容: {content}')
    print(f'   traceId: {trace_id}')

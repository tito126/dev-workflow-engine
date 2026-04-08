#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('test_digest_stage1_traces.json', encoding='utf-8') as f:
    d = json.load(f)

print(f'总数: {d["count"]}')
print(f'异常类: {sum(1 for t in d["traces"] if t["type"] == "error")}')
print(f'慢接口: {sum(1 for t in d["traces"] if t["type"] == "slow_api")}')

print('\n前5个:')
for i, t in enumerate(d['traces'][:5], 1):
    print(f"\n{i}. {t['type']}")
    print(f"   trace_id: {t['trace_id'][:8]}...")
    print(f"   timestamp: {t['timestamp']}")
    if t['type'] == 'error':
        print(f"   category: {t.get('category')}")
        print(f"   api_entry: {t.get('api_entry')}")
    else:
        print(f"   api: {t.get('api')}")
        print(f"   duration_ms: {t.get('duration_ms')}")

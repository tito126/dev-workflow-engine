#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('logs_leshan_latest_digest.json', encoding='utf-8') as f:
    d = json.load(f)

print(f'总异常数: {len(d["errors"])}')
no_api = sum(1 for e in d['errors'] if e.get('api_entry') == 'N/A')
print(f'缺少API入口: {no_api} ({no_api*100//len(d["errors"])}%)')

# 检查每个分组的 api_entry
for i, err in enumerate(d['errors'][:10]):
    print(f"\n分组 {i+1}:")
    print(f"  category: {err.get('category')}")
    print(f"  root_class: {err.get('root_class')}")
    print(f"  api_entry: {err.get('api_entry')}")
    print(f"  caller_service: {err.get('caller_service')}")
    print(f"  count: {err.get('count')}")

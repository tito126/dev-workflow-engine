import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final2', encoding='utf-8') as f:
    d = json.load(f)

target_traces = ['04ca3ff6a7b44e7a829716d56953065b', '03d8d9c89797413ebbd371624789a3c4']

print('验证API入口提取：\n')
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('trace_id') in target_traces:
            print(f"TraceId: {sample['trace_id']}")
            print(f"Category: {sample['category']}")
            print(f"API入口: {sample.get('api_entry', 'N/A')}")
            print("-" * 80)

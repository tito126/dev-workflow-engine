import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final6', encoding='utf-8') as f:
    d = json.load(f)

print('标签配置异常的分组情况：\n')

tag_errors = [e for e in d['errors'] if '标签' in e['category']]

print(f"总共有 {len(tag_errors)} 个标签配置异常分组\n")

for idx, e in enumerate(tag_errors, 1):
    print(f"{idx}. Category: {e['category']}")
    print(f"   Count: {e['count']}")
    print(f"   Class: {e.get('class', 'N/A')}")
    print(f"   Classes: {e.get('classes', [])}")
    print(f"   API入口: {e.get('api_entries', [])}")
    if e.get('samples'):
        sample = e['samples'][0]
        print(f"   Sample TraceId: {sample.get('trace_id', 'N/A')}")
        print(f"   Sample Content: {sample.get('content', '')[:80]}")
    print()

# 检查特定的两个trace
target_traces = ['18ce65ca05634c0a9e00d02cfdeed774', '00c582313f1c48e6b6695320108f9649']
print(f"\n查找目标trace：")
for error_group in d['errors']:
    for sample in error_group['samples']:
        if sample.get('trace_id') in target_traces:
            print(f"TraceId: {sample['trace_id']}")
            print(f"Category: {sample['category']}")
            print(f"Root Class: {sample.get('root_class', 'N/A')}")
            print(f"API入口: {sample.get('api_entry', 'N/A')}")
            print("-" * 80)

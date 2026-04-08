import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final4', encoding='utf-8') as f:
    d = json.load(f)

print('空指针异常的分组情况：\n')

null_pointer_errors = [e for e in d['errors'] if '空指针' in e['category']]

print(f"总共有 {len(null_pointer_errors)} 个空指针异常分组\n")

for idx, e in enumerate(null_pointer_errors[:10], 1):
    print(f"{idx}. Category: {e['category']}")
    print(f"   Count: {e['count']}")
    print(f"   Class: {e.get('class', 'N/A')}")
    print(f"   Classes: {e.get('classes', [])}")  # 新增：所有涉及的类
    if e.get('samples'):
        sample = e['samples'][0]
        print(f"   API入口: {sample.get('api_entry', 'N/A')}")
        print(f"   Content: {sample.get('content', '')[:80]}")
    print()

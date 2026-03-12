import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed_final8', encoding='utf-8') as f:
    d = json.load(f)

print('按trace去重的统计（summary.error_categories）：\n')

# 显示error_categories
for category, count in sorted(d['summary']['error_categories'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {category}: {count} 个trace")

print(f"\n总ERROR条数: {d['summary']['error_count']}")
print(f"总trace数（去重后）: {sum(d['summary']['error_categories'].values())}")

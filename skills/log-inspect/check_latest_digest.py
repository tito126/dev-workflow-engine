import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_010556_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)

errors = d['errors']
log_quality = d['summary'].get('log_quality', {})

print(f'异常分类总数: {len(errors)}')
print(f'\n日志质量:')
print(f'  缺少API入口: {log_quality.get("no_api_entry_count", 0)} ({log_quality.get("no_api_entry_pct", 0)}%)')
print(f'  只有null: {log_quality.get("null_only_count", 0)} ({log_quality.get("null_only_pct", 0)}%)')
print(f'  影响级别分布: 高{log_quality.get("impact_distribution", {}).get("high", 0)} 中{log_quality.get("impact_distribution", {}).get("medium", 0)} 低{log_quality.get("impact_distribution", {}).get("low", 0)}')

print(f'\n前10个异常分类:')
for i, e in enumerate(errors[:10]):
    impact = e.get('impact_level', 'N/A')
    impact_emoji = {'high': '[H]', 'medium': '[M]', 'low': '[L]'}.get(impact, '?')
    print(f'{i+1}. [{impact_emoji}] {e["category"]}: {e["count"]} 个trace')

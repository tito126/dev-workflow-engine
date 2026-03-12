with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_145058_默认集群_report.html', encoding='utf-8') as f:
    old_html = f.read()

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_183735_默认集群_report.html', encoding='utf-8') as f:
    new_html = f.read()

features = ['调用方', '线程', '影响级别', 'API入口', '拉取时间范围', '拉取耗时']

print('功能对比：')
for key in features:
    old_count = old_html.count(key)
    new_count = new_html.count(key)
    status = 'OK' if new_count >= old_count * 0.8 else 'MISSING'
    print(f'{key}: 旧={old_count} 新={new_count} [{status}]')

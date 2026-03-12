import re

def get_slow_api_info(html_file):
    with open(html_file, encoding='utf-8') as f:
        html = f.read()
    
    # 统计慢接口相关标签出现次数
    keys = ['慢接口', 'TraceID', 'trace_id', 'traceId', '耗时', 'ms', '调用链', 'slow']
    result = {}
    for k in keys:
        result[k] = html.count(k)
    
    # 找慢接口section的大致内容
    idx = html.find('慢接口')
    if idx > 0:
        result['sample'] = html[idx:idx+500].replace('\n', ' ')
    
    return result

old = r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_145058_默认集群_report.html'
new = r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_183735_默认集群_report.html'

print("=== 旧报告 ===")
old_info = get_slow_api_info(old)
for k, v in old_info.items():
    if k != 'sample':
        print(f'  {k}: {v}')

print("\n=== 新报告 ===")
new_info = get_slow_api_info(new)
for k, v in new_info.items():
    if k != 'sample':
        print(f'  {k}: {v}')

print("\n=== 旧报告慢接口section样本 ===")
print(old_info.get('sample', 'N/A')[:300])

print("\n=== 新报告慢接口section样本 ===")
print(new_info.get('sample', 'N/A')[:300])

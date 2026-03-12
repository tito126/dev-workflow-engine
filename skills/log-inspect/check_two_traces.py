import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)

trace_ids = ['0e23dd93ce484aa0a952e81ffbb04dff', '11493d13f41c4172b2ad2f085f9c9958']

print('检查这两个traceId:')
for tid in trace_ids:
    print(f'\n{tid}:')
    
    # 在errors中查找
    found = False
    for error in d['errors']:
        for sample in error.get('samples', []):
            if sample.get('trace_id') == tid:
                print(f'  分类: {error["category"]}')
                print(f'  影响级别: {error.get("impact_level", "N/A")}')
                print(f'  API入口: {sample.get("api_entry", "N/A")}')
                found = True
                break
        if found:
            break
    
    # 在slow_apis中查找
    if not found:
        for api in d.get('slow_apis', []):
            for trace in api.get('top_traces', []):
                if trace.get('trace_id') == tid:
                    print(f'  类型: 慢接口')
                    print(f'  API: {api["api_path"]}')
                    print(f'  耗时: {trace.get("duration_ms")}ms')
                    found = True
                    break
            if found:
                break
    
    if not found:
        print('  未找到（可能不是代表trace）')

# 检查原始日志中这两个trace的实际行数
print('\n\n检查原始日志中的实际行数:')
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群.log', encoding='utf-8') as f:
    for tid in trace_ids:
        count = 0
        for line in f:
            if tid in line:
                count += 1
        print(f'{tid}: {count} 行')
        f.seek(0)  # 重置文件指针

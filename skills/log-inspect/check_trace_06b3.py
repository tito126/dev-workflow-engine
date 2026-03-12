import json

trace_id = '06b37820368c41d6ab2156592c778fcc'

# 检查digest
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)

print(f'检查 traceId: {trace_id}\n')

# 1. 检查是否在errors中
found_in_errors = False
for error in d['errors']:
    for sample in error.get('samples', []):
        if sample.get('trace_id') == trace_id:
            print(f'[OK] 在异常分类中找到:')
            print(f'  分类: {error["category"]}')
            print(f'  影响级别: {error.get("impact_level", "N/A")}')
            print(f'  API入口: {sample.get("api_entry", "N/A")}')
            print(f'  该分组共 {error["count"]} 个trace')
            
            # 检查是否是代表trace（samples中的第一个）
            is_representative = (error['samples'][0].get('trace_id') == trace_id)
            print(f'  是否是代表trace: {"是" if is_representative else "否"}')
            found_in_errors = True
            break
    if found_in_errors:
        break

# 2. 检查是否在slow_apis中
found_in_slow = False
for api in d.get('slow_apis', []):
    for trace in api.get('top_traces', []):
        if trace.get('trace_id') == trace_id:
            print(f'[OK] 在慢接口中找到:')
            print(f'  API: {api["api_path"]}')
            print(f'  耗时: {trace.get("duration_ms")}ms')
            found_in_slow = True
            break
    if found_in_slow:
        break

if not found_in_errors and not found_in_slow:
    print('[X] 未在digest中找到（可能不是代表trace）')

# 3. 检查原始日志中的实际行数
print(f'\n原始日志文件中的行数:')
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群.log', encoding='utf-8') as f:
    lines = []
    for line in f:
        if trace_id in line:
            lines.append(line.strip())
    
    print(f'  总共: {len(lines)} 行')
    
    if len(lines) > 0:
        print(f'\n前5行:')
        for i, line in enumerate(lines[:5]):
            # 提取日志级别
            if 'ERROR' in line:
                level = 'ERROR'
            elif 'WARN' in line:
                level = 'WARN'
            elif 'INFO' in line:
                level = 'INFO'
            elif 'DEBUG' in line:
                level = 'DEBUG'
            else:
                level = '?'
            print(f'  {i+1}. [{level}] {line[:100]}...')

print(f'\n结论:')
if len(lines) == 2:
    print('  原始日志文件中确实只有2行，不是拉取问题')
elif len(lines) > 2 and not (found_in_errors or found_in_slow):
    print('  原始日志有更多行，但这个trace不是代表trace，所以没有拉取完整链路')
    print('  只拉取了ERROR和WARN日志')
elif len(lines) > 2:
    print('  原始日志有更多行，需要检查为什么没有全部拉取')

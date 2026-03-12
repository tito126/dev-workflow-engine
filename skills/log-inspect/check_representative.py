import re

trace_id = '06b37820368c41d6ab2156592c778fcc'

# 读取原始日志文件
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群.log', encoding='utf-8') as f:
    lines = f.readlines()

print(f'原始日志文件总行数: {len(lines)}')

# 模拟extract_error_representatives函数
trace_id_pattern = r'\[([a-zA-Z0-9]{16,})'
error_categories = {
    'sql_error': [r'ORA-', r'SQLException', r'SQL'],
    'validation': [r'参数', r'校验', r'不能为空'],
    'null_pointer': [r'NullPointer', r'null'],
    'timeout': [r'超时', r'timeout'],
    'connection': [r'连接', r'Connection'],
}

from collections import defaultdict
category_data = defaultdict(lambda: {'traces': [], 'representative': None})

for line in lines:
    if 'ERROR' not in line:
        continue
    
    # 提取traceId
    trace_match = re.search(trace_id_pattern, line)
    if not trace_match:
        continue
    
    tid = trace_match.group(1)
    if len(tid) < 16:
        continue
    
    # 分类
    matched_category = 'other'
    for category, patterns in error_categories.items():
        if any(re.search(p, line, re.IGNORECASE) for p in patterns):
            matched_category = category
            break
    
    category_data[matched_category]['traces'].append((tid, line[:200]))

print(f'\n异常分类统计:')
for category, data in category_data.items():
    unique_traces = {}
    for tid, content in data['traces']:
        if tid not in unique_traces:
            unique_traces[tid] = content
    
    representative = list(unique_traces.keys())[0] if unique_traces else None
    
    print(f'  {category}: {len(unique_traces)} 个trace, 代表: {representative}')
    
    if trace_id in unique_traces:
        print(f'    [OK] {trace_id} 在此分类中')
        if representative == trace_id:
            print(f'    [OK] {trace_id} 是代表trace，应该拉取完整链路')
        else:
            print(f'    [X] {trace_id} 不是代表trace（代表是 {representative}）')

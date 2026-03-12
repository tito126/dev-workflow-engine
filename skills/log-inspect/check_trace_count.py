import json

# 读取digest
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_010556_默认集群_digest.json', encoding='utf-8') as f:
    d = json.load(f)

# 统计慢接口代表trace数量
slow_apis = d.get('slow_apis', [])
slow_trace_count = len(slow_apis)

# 统计异常分类数量
errors = d['errors']
error_group_count = len(errors)

print(f'第二阶段应该拉取的trace数量:')
print(f'  慢接口: {slow_trace_count} 个')
print(f'  异常分类: {error_group_count} 个')
print(f'  总计: {slow_trace_count + error_group_count} 个')

# 检查日志文件中有多少trace有完整链路（包含INFO日志）
with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_010556_默认集群.log', encoding='utf-8') as f:
    lines = f.readlines()

# 统计包含INFO的trace数量
import re
trace_pattern = r'\[([a-f0-9]{32}),\1,'

traces_with_info = set()
for line in lines:
    if 'INFO' in line:
        match = re.search(trace_pattern, line)
        if match:
            traces_with_info.add(match.group(1))

print(f'\n实际拉取了完整链路的trace数量: {len(traces_with_info)} 个')

# 对比
if len(traces_with_info) < (slow_trace_count + error_group_count):
    print(f'\n注意: 实际拉取数量少于预期，可能有些trace没有INFO日志')

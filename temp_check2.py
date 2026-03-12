with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\generate_html_report_v2.py', encoding='utf-8') as f:
    lines = f.readlines()
print(f'总行数: {len(lines)}')

# 找慢接口相关函数
for i, line in enumerate(lines):
    stripped = line.rstrip()
    if any(k in stripped for k in ['slow_api', 'generate_slow', 'traceId', 'trace_id', '调用链', '耗时', 'caller', '调用方']):
        print(f'{i+1}: {stripped[:120]}')

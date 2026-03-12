import requests
import json
from urllib.parse import quote

trace_id = '06b37820368c41d6ab2156592c778fcc'
query = f'{{app="winning-winex-ipt-ward-pbc"}} |= `{trace_id}`'
start = '1773243360000000000'  # 2026-03-11 23:36:00
end = '1773244019000000000'    # 2026-03-11 23:46:59

url = f'http://127.0.0.1:14828/api/datasources/proxy/2/loki/api/v1/query_range'
params = {
    'query': query,
    'start': start,
    'end': end,
    'limit': 5000
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    if data.get('status') == 'success':
        results = data.get('data', {}).get('result', [])
        total_lines = 0
        
        print(f'Loki查询结果 (traceId: {trace_id}):')
        print(f'时间范围: 2026-03-11 23:36:00 ~ 23:46:59\n')
        
        for stream in results:
            lines = stream.get('values', [])
            total_lines += len(lines)
            print(f'Stream: {len(lines)} 行')
            
            # 显示前5行
            if len(lines) > 0:
                print(f'\n前5行:')
                for i, (ts, line) in enumerate(lines[:5]):
                    # 提取日志级别
                    if 'ERROR' in line:
                        level = 'ERROR'
                    elif 'WARN' in line:
                        level = 'WARN'
                    elif 'INFO' in line:
                        level = 'INFO'
                    else:
                        level = '?'
                    print(f'  {i+1}. [{level}] {line[:150]}')
        
        print(f'\n总计: {total_lines} 行')
        print(f'\n对比:')
        print(f'  Loki中: {total_lines} 行')
        print(f'  我们拉取的: 2 行')
        
        if total_lines > 2:
            print(f'\n差异: {total_lines - 2} 行未拉取')
            print(f'可能原因:')
            print(f'  1. 日志级别过滤（我们只拉ERROR和WARN）')
            print(f'  2. 拉取逻辑问题')
    else:
        print(f'查询失败: {data}')
        
except Exception as e:
    print(f'连接失败: {e}')
    print(f'\n请确认:')
    print(f'  1. 端口转发是否打开 (127.0.0.1:14828)')
    print(f'  2. Grafana是否正常运行')

import requests
import json

trace_id = '06b37820368c41d6ab2156592c778fcc'

# 模拟loki_fetcher.py第二阶段的查询
query = f'{{app="winning-winex-ipt-ward-pbc"}} |~ "{trace_id}"'
start = '1773243360000000000'  # 2026-03-11 23:36:00
end = '1773244019000000000'    # 2026-03-11 23:46:59

url = f'http://127.0.0.1:14828/api/datasources/proxy/2/loki/api/v1/query_range'
params = {
    'query': query,
    'start': start,
    'end': end,
    'limit': 5000,
    'direction': 'forward'
}

print(f'测试第二阶段查询:')
print(f'Query: {query}')
print(f'Time: 2026-03-11 23:36:00 ~ 23:46:59\n')

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    if data.get('status') == 'success':
        results = data.get('data', {}).get('result', [])
        total_lines = sum(len(stream.get('values', [])) for stream in results)
        
        print(f'查询成功！')
        print(f'返回 {len(results)} 个stream')
        print(f'总计 {total_lines} 行日志')
        
        if total_lines == 21:
            print(f'\n✓ 查询结果正确（21行）')
            print(f'\n结论: Loki查询本身没问题，问题在于loki_fetcher.py的第二阶段没有正确执行或写入')
        else:
            print(f'\n✗ 查询结果不对（期望21行，实际{total_lines}行）')
    else:
        print(f'查询失败: {data}')
        
except Exception as e:
    print(f'连接失败: {e}')

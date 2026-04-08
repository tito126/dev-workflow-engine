import requests
import json

trace_id = '15440caaef1948008369f18fa7cbc06d'

# 查询Loki
query = f'{{app="winning-winex-ipt-ward-pbc"}} |~ "{trace_id}"'
start = '1773243360000000000'
end = '1773244019000000000'

url = f'http://127.0.0.1:14828/api/datasources/proxy/2/loki/api/v1/query_range'
params = {'query': query, 'start': start, 'end': end, 'limit': 5000, 'direction': 'forward'}

try:
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    
    if data.get('status') == 'success':
        results = data.get('data', {}).get('result', [])
        total_lines = sum(len(stream.get('values', [])) for stream in results)
        
        print(f'Loki中: {total_lines} 行')
        
        # 统计日志级别
        levels = {'ERROR': 0, 'WARN': 0, 'INFO': 0, 'DEBUG': 0}
        for stream in results:
            for ts, line in stream.get('values', []):
                for level in levels:
                    if level in line:
                        levels[level] += 1
                        break
        
        print(f'  ERROR: {levels["ERROR"]}, WARN: {levels["WARN"]}, INFO: {levels["INFO"]}, DEBUG: {levels["DEBUG"]}')
    
    # 检查原始日志文件
    with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群.log', encoding='utf-8') as f:
        file_lines = sum(1 for line in f if trace_id in line)
    
    print(f'\n原始日志文件中: {file_lines} 行')
    print(f'差异: {total_lines - file_lines} 行未拉取')
    
except Exception as e:
    print(f'查询失败: {e}')

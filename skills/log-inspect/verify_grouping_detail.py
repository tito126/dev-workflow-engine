import re

trace_ids = {
    '0e23dd93ce484aa0a952e81ffbb04dff': '护理文书',
    '3460f17311ff4438a1b968c431eb3438': '医生站'
}

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_010100_默认集群.log', encoding='utf-8') as f:
    lines = f.readlines()

print('验证调用方识别:')
print('='*60)

for trace_id, desc in trace_ids.items():
    trace_lines = [line for line in lines if trace_id in line and 'ERROR' in line]
    
    if trace_lines:
        first_error = trace_lines[0]
        
        # 提取线程名
        thread_match = re.search(r'\[([^\]]+)\]\s+ERROR', first_error)
        if thread_match:
            thread = thread_match.group(1)
            
            # 提取调用方
            service_match = re.search(r'^(winning-winex-[a-z0-9-]+)_Jetty-Worker', thread)
            if service_match:
                caller = service_match.group(1)
            elif thread.startswith('Jetty-Worker_'):
                caller = 'SELF'
            else:
                caller = 'UNKNOWN'
            
            print(f'\n{desc} ({trace_id[:8]}...):')
            print(f'  线程名: {thread}')
            print(f'  调用方: {caller}')
            
            # 提取错误类型
            if 'ORA-' in first_error:
                ora_match = re.search(r'(ORA-\d+)', first_error)
                if ora_match:
                    print(f'  错误码: {ora_match.group(1)}')
            
            # 提取API
            api_match = re.search(r'(/api/[^\s,;]+)', first_error)
            if api_match:
                print(f'  API: {api_match.group(1)}')
            else:
                print(f'  API: N/A')
            
            print(f'  分组键: sql_error:{api_match.group(1) if api_match else "N/A"}:{caller}:{ora_match.group(1) if "ORA-" in first_error and ora_match else "?"}')

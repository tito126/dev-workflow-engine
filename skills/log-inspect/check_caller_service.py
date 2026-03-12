import re

trace_ids = {
    '0e23dd93ce484aa0a952e81ffbb04dff': '护理文书',
    '11a2ae3a70eb41f9b03958d8706f19d3': 'HIS费用',
    '05380bf5410e4936a4f45afcb009594d': 'exe-5577',
    '16ee2706322940d2b6cefaa3f0c9589a': 'exe线程',
    '3460f17311ff4438a1b968c431eb3438': '医生站'
}

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群.log', encoding='utf-8') as f:
    lines = f.readlines()

for trace_id, desc in trace_ids.items():
    print(f'\n{"="*60}')
    print(f'{desc} ({trace_id}):')
    print(f'{"="*60}')
    
    trace_lines = [line for line in lines if trace_id in line]
    
    if trace_lines:
        # 显示第一条日志
        first_line = trace_lines[0]
        print(f'第一条日志:')
        print(first_line[:300])
        
        # 提取线程名
        thread_match = re.search(r'\[([^\]]+)\]\s+(ERROR|WARN|INFO)', first_line)
        if thread_match:
            thread = thread_match.group(1)
            print(f'\n线程名: {thread}')
            
            # 尝试从线程名提取服务名
            service_match = re.search(r'(winning-winex-[a-z0-9-]+)', thread)
            if service_match:
                caller_service = service_match.group(1)
                print(f'调用方服务: {caller_service}')
            elif thread.startswith('exe-') or thread.startswith('[exe-'):
                print(f'调用方服务: 异步任务（{thread}）')
            else:
                print(f'调用方服务: 未识别')
        
        print(f'\n共 {len(trace_lines)} 行日志')
    else:
        print('未找到日志')

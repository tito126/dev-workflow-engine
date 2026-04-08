trace_ids = {
    '0e23dd93ce484aa0a952e81ffbb04dff': '护理文书',
    '11a2ae3a70eb41f9b03958d8706f19d3': 'HIS费用',
    '05380bf5410e4936a4f45afcb009594d': 'exe-5577',
    '16ee2706322940d2b6cefaa3f0c9589a': 'exe线程',
    '3460f17311ff4438a1b968c431eb3438': '医生站'
}

print('检查各traceId的日志行数:')
print('='*60)

for trace_id, desc in trace_ids.items():
    with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260312_010100_默认集群.log', encoding='utf-8') as f:
        count = sum(1 for line in f if trace_id in line)
    
    print(f'{desc} ({trace_id[:8]}...): {count} 行')

print('\n说明:')
print('- 如果行数>10，说明拉取了完整链路')
print('- 如果行数<10，说明只拉取了ERROR/WARN')

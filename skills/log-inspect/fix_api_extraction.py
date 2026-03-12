with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        # 按时间排序，取最后一条日志提取API入口
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
        api_entry = None
        
        if sorted_logs:
            last_log = sorted_logs[-1]
            # 从最后一条日志中提取API路径
            api_pattern = re.compile(r'(/api/[^\\s,;)\\]]+)')
            raw_line = last_log.get('raw_line', '')
            api_match = api_pattern.search(raw_line)
            if api_match:
                api_entry = api_match.group(1)'''

new = '''        # 提取API入口：优先从WARN日志中提取，如果没有WARN再从最后一条日志提取
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
        api_entry = None
        api_pattern = re.compile(r'(/api/[^\\s,;)\\]]+)')
        
        # 优先从WARN日志中提取（WARN通常包含API路径）
        for log in sorted_logs:
            if log.get('level') == 'WARN':
                raw_line = log.get('raw_line', '')
                api_match = api_pattern.search(raw_line)
                if api_match:
                    api_entry = api_match.group(1)
                    break
        
        # 如果WARN中没有找到，从最后一条日志提取
        if not api_entry and sorted_logs:
            last_log = sorted_logs[-1]
            raw_line = last_log.get('raw_line', '')
            api_match = api_pattern.search(raw_line)
            if api_match:
                api_entry = api_match.group(1)'''

new_content = content.replace(old, new)
count = content.count(old)

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'替换了 {count} 处API入口提取逻辑')

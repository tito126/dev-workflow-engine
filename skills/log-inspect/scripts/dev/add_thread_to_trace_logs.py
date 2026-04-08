with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """                # 收集trace日志（包括ERROR和WARN，保存原始日志行）
                if trace_id and level in ('ERROR', 'FATAL', 'WARN'):
                    trace_logs[trace_id].append({
                        'level': level,
                        'content': content,
                        'timestamp': parsed['timestamp_str'],
                        'class': parsed['class_name'],
                        'user': parsed['user_name'],
                        'raw_line': line.strip()"""

new = """                # 收集trace日志（包括ERROR和WARN，保存原始日志行）
                if trace_id and level in ('ERROR', 'FATAL', 'WARN'):
                    trace_logs[trace_id].append({
                        'level': level,
                        'content': content,
                        'timestamp': parsed['timestamp_str'],
                        'class': parsed['class_name'],
                        'user': parsed['user_name'],
                        'thread': parsed['thread'],  # 保存线程信息
                        'raw_line': line.strip()"""

new_content = content.replace(old, new)
count = content.count(old)

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'替换了 {count} 处，添加thread信息')

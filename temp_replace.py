import re

# 读取文件
with open(r"D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\loki_fetcher.py", 'r', encoding='utf-8') as f:
    content = f.read()

# 新的函数
new_function = '''def extract_error_representatives(lines: list) -> dict:
    """提取每个异常分类的代表traceId（按 category:root_class:api_entry:caller_service 四级分组，与preprocess.py保持一致）"""
    import re
    from collections import defaultdict
    
    trace_id_pattern = r'\\[([a-zA-Z0-9]{16,})'
    api_pattern = r'(/api/[^\\s,;]+)'
    thread_pattern = r'\\[([^\\]]+)\\]\\s+(ERROR|WARN|INFO)'
    class_pattern = r'(ERROR|WARN)\\s+([a-zA-Z0-9_.]+)\\s+'
    
    # 简单的异常分类规则
    error_categories = {
        'sql_error': [r'ORA-', r'SQLException', r'SQL'],
        'validation': [r'参数', r'校验', r'不能为空'],
        'null_pointer': [r'NullPointer', r'null'],
        'timeout': [r'超时', r'timeout'],
        'connection': [r'连接', r'Connection'],
    }
    
    def extract_caller_service(line: str) -> str:
        """从线程名提取调用方服务"""
        thread_match = re.search(thread_pattern, line)
        if not thread_match:
            return 'UNKNOWN'
        
        thread = thread_match.group(1)
        
        # 跨服务调用：winning-winex-xxx_Jetty-Worker
        service_match = re.search(r'^(winning-winex-[a-z0-9-]+)_Jetty-Worker', thread)
        if service_match:
            return service_match.group(1)
        
        # 本服务调用：Jetty-Worker_xxx
        if thread.startswith('Jetty-Worker_'):
            return 'SELF'
        
        # 异步任务：exe-xxx, enc-xxx
        if re.match(r'^(exe|enc)-\\d+$', thread):
            return 'ASYNC'
        
        # RPC调用：rpc-exec-xxx
        if thread.startswith('rpc-exec-'):
            return 'RPC'
        
        return 'UNKNOWN'
    
    def extract_class_name(line: str) -> str:
        """从ERROR日志中提取类名"""
        class_match = re.search(class_pattern, line)
        if class_match:
            full_class = class_match.group(2)
            # 简化类名：只保留最后几段
            parts = full_class.split('.')
            if len(parts) > 3:
                return '.'.join(parts[-3:])  # 保留最后3段
            return full_class
        return 'N/A'
    
    # {group_key: {'trace_id': xxx, 'api_path': xxx, 'caller_service': xxx, 'class_name': xxx}}
    grouped_traces = {}
    
    for line in lines:
        if 'ERROR' not in line:
            continue
        
        # 提取traceId
        trace_match = re.search(trace_id_pattern, line)
        if not trace_match:
            continue
        
        trace_id = trace_match.group(1)
        if len(trace_id) < 16:
            continue
        
        # 提取入口API
        api_match = re.search(api_pattern, line)
        api_path = api_match.group(1) if api_match else 'N/A'
        
        # 提取调用方服务
        caller_service = extract_caller_service(line)
        
        # 提取类名（作为root_class）
        class_name = extract_class_name(line)
        
        # 分类
        matched_category = 'other'
        for category, patterns in error_categories.items():
            if any(re.search(p, line, re.IGNORECASE) for p in patterns):
                matched_category = category
                break
        
        # 四级分组键：category:class_name:api_entry:caller_service（与preprocess.py一致）
        group_key = f"{matched_category}:{class_name}:{api_path}:{caller_service}"
        
        # 每个组只保留第一个trace（作为代表）
        if group_key not in grouped_traces:
            grouped_traces[group_key] = {
                'trace_id': trace_id,
                'api_path': api_path,
                'caller_service': caller_service,
                'category': matched_category,
                'class_name': class_name,
                'content': line[:200]
            }
    
    # 转换为返回格式（兼容原有逻辑）
    result = {}
    for group_key, info in grouped_traces.items():
        result[group_key] = {
            'representative': info['trace_id'],
            'category': info['category'],
            'api_path': info['api_path'],
            'caller_service': info['caller_service'],
            'class_name': info['class_name']
        }
    
    return result

'''

# 找到函数的开始和结束位置
pattern = r'def extract_error_representatives\(.*?\n(?=\ndef [a-z_]+\()'
match = re.search(pattern, content, re.DOTALL)

if match:
    # 替换函数
    new_content = content[:match.start()] + new_function + content[match.end():]
    
    # 写回文件
    with open(r"D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\loki_fetcher.py", 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("替换成功！")
else:
    print("未找到函数")

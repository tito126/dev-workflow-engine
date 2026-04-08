import re

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换
old_pattern = r"    # 构建输出\r?\n    digest = \{\r?\n        'meta': \{.*?\r?\n.*?'error_categories': dict\(stats\['error_categories'\]\),\r?\n        \},\r?\n        'errors': aggregate_errors\(stats\['error_samples'\]\),"

new_text = """    # 聚合错误（按trace去重）
    aggregated_errors = aggregate_errors(stats['error_samples'])
    
    # 根据聚合结果重新计算error_categories（按trace去重）
    error_categories_by_trace = defaultdict(int)
    for error_group in aggregated_errors:
        error_categories_by_trace[error_group['category']] += error_group['count']
    
    # 构建输出
    digest = {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'files_processed': stats['files_processed'],
            'time_range': {
                'start': args.start,
                'end': args.end
            },
            'slow_threshold_ms': args.threshold,
            'filter_mode': 'error_trace' if args.filter_by_error_trace else 'all',
            'filtered_trace_count': len(filter_trace_ids) if filter_trace_ids else 0,
        },
        'summary': {
            'total_lines': stats['total_lines'],
            'error_count': stats['error_count'],
            'warn_count': stats['warn_count'],
            'error_categories': dict(error_categories_by_trace),  # 使用按trace去重的统计
        },
        'errors': aggregated_errors,"""

# 使用正则替换
new_content = re.sub(old_pattern, new_text, content, flags=re.DOTALL)

if new_content == content:
    print("未找到匹配的文本，尝试简单替换...")
    # 简单替换
    old_simple = "'error_categories': dict(stats['error_categories']),"
    new_simple = "'error_categories': dict(error_categories_by_trace),  # 使用按trace去重的统计"
    
    old_simple2 = "'errors': aggregate_errors(stats['error_samples']),"
    new_simple2 = "'errors': aggregated_errors,"
    
    # 先在digest定义前添加代码
    insert_pos = content.find("    # 构建输出\n    digest = {")
    if insert_pos == -1:
        insert_pos = content.find("    # 构建输出\r\n    digest = {")
    
    if insert_pos != -1:
        insert_text = """    # 聚合错误（按trace去重）
    aggregated_errors = aggregate_errors(stats['error_samples'])
    
    # 根据聚合结果重新计算error_categories（按trace去重）
    error_categories_by_trace = defaultdict(int)
    for error_group in aggregated_errors:
        error_categories_by_trace[error_group['category']] += error_group['count']
    
"""
        new_content = content[:insert_pos] + insert_text + content[insert_pos:]
        
        # 然后替换两处引用
        new_content = new_content.replace(old_simple, new_simple)
        new_content = new_content.replace(old_simple2, new_simple2)
        
        with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("已修改error_categories统计为按trace去重")
    else:
        print("未找到插入位置")
else:
    with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("已修改error_categories统计为按trace去重")

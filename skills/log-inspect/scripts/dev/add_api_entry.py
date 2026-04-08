import re

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_text = '''    # 基于trace重新分类ERROR日志
    print(f"[Trace分类] 收集到 {len(trace_logs)} 个trace，seen_error_traces有 {len(seen_error_traces)} 个")
    reclassified_count = 0
    
    for trace_id, logs in trace_logs.items():
        if trace_id not in seen_error_traces:
            continue
        
        # 对这个trace进行综合分类
        trace_category = categorize_trace(logs)
        if trace_category is None:
            continue
        
        # 更新error_lines中对应trace的分类
        for error_line in error_lines:
            if error_line.get('trace_id') == trace_id:
                old_category = error_line['category']
                new_category = trace_category['name']
                
                if old_category != new_category:
                    # 更新分类
                    stats['error_categories'][old_category] -= 1
                    stats['error_categories'][new_category] += 1
                    
                    error_line['category'] = new_category
                    error_line['category_id'] = trace_category['category']
                    error_line['matched_keyword'] = trace_category.get('matched_keyword')
                    error_line['suggestion'] = trace_category['suggestion']
                    error_line['error_reason'] = trace_category.get('error_reason')
                    
                    reclassified_count += 1
                    print(f"[Trace分类] {trace_id[:16]}: {old_category} -> {new_category}")
    
    if reclassified_count > 0:
        print(f"[Trace分类] 重新分类了 {reclassified_count} 条ERROR日志")
    else:
        print(f"[Trace分类] 没有需要重新分类的日志")'''

new_text = '''    # 基于trace重新分类ERROR日志，并提取API入口
    print(f"[Trace分类] 收集到 {len(trace_logs)} 个trace，seen_error_traces有 {len(seen_error_traces)} 个")
    reclassified_count = 0
    
    for trace_id, logs in trace_logs.items():
        if trace_id not in seen_error_traces:
            continue
        
        # 按时间排序，取最后一条日志提取API入口
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
        api_entry = None
        
        if sorted_logs:
            last_log = sorted_logs[-1]
            # 从最后一条日志中提取API路径
            api_pattern = re.compile(r'(/api/[^\\s,;)\\]]+)')
            raw_line = last_log.get('raw_line', '')
            api_match = api_pattern.search(raw_line)
            if api_match:
                api_entry = api_match.group(1)
        
        # 对这个trace进行综合分类
        trace_category = categorize_trace(logs)
        if trace_category is None:
            continue
        
        # 更新error_lines中对应trace的分类和API入口
        for error_line in error_lines:
            if error_line.get('trace_id') == trace_id:
                old_category = error_line['category']
                new_category = trace_category['name']
                
                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                if old_category != new_category:
                    # 更新分类
                    stats['error_categories'][old_category] -= 1
                    stats['error_categories'][new_category] += 1
                    
                    error_line['category'] = new_category
                    error_line['category_id'] = trace_category['category']
                    error_line['matched_keyword'] = trace_category.get('matched_keyword')
                    error_line['suggestion'] = trace_category['suggestion']
                    error_line['error_reason'] = trace_category.get('error_reason')
                    
                    reclassified_count += 1
                    print(f"[Trace分类] {trace_id[:16]}: {old_category} -> {new_category}")
    
    if reclassified_count > 0:
        print(f"[Trace分类] 重新分类了 {reclassified_count} 条ERROR日志")
    else:
        print(f"[Trace分类] 没有需要重新分类的日志")'''

new_content = content.replace(old_text, new_text)

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('已添加API入口提取逻辑')

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                # 添加根本原因类名（用于分组）
                if trace_category.get('root_class'):
                    error_line['root_class'] = trace_category['root_class']'''

new = '''                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                # 添加根本原因类名（用于分组）
                if trace_category.get('root_class'):
                    error_line['root_class'] = trace_category['root_class']
                
                # 添加影响级别
                error_line['impact_level'] = analyze_impact_level(logs)'''

new_content = content.replace(old, new)
count = content.count(old)

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'替换了 {count} 处，添加影响级别')

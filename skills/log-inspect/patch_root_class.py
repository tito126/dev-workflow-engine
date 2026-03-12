with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                if old_category != new_category:'''

new = '''                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                # 添加根本原因类名（用于分组）
                if trace_category.get('root_class'):
                    error_line['root_class'] = trace_category['root_class']
                
                if old_category != new_category:'''

new_content = content.replace(old, new)
assert new_content != content, "替换失败"

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('已添加root_class传递')

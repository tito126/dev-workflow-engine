with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换两处 categorize_trace(logs) 为 categorize_trace(logs, current_service)
old = 'trace_category = categorize_trace(logs)'
new = 'trace_category = categorize_trace(logs, current_service)'

new_content = content.replace(old, new)
assert new_content != content, "替换失败"

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'替换了 {content.count(old)} 处')

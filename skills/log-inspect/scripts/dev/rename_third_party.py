with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有"第三方调用异常"为"三方接口异常"
old = '第三方调用异常'
new = '三方接口异常'

new_content = content.replace(old, new)
count = content.count(old)

with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'替换了 {count} 处 "{old}" 为 "{new}"')

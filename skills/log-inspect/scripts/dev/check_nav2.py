import re, sys
with open('logs_20260313_185546_第二集群_report.html', encoding='utf-8') as f:
    content = f.read()
# 找导航栏内容
idx = content.find('nav-sidebar')
print(content[idx:idx+800])

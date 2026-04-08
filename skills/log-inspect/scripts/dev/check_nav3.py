import re, sys
with open('logs_20260313_185546_第二集群_report.html', encoding='utf-8') as f:
    content = f.read()
idx = content.find('<div class="nav-sidebar">')
sys.stdout.buffer.write(content[idx:idx+1000].encode('utf-8'))

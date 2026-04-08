import re, sys
with open('logs_20260313_185546_第二集群_report.html', encoding='utf-8') as f:
    content = f.read()
sub_links = re.findall(r'nav-sub-link[^>]*href="(#[^"]+)"', content)
print('子导航数量:', len(sub_links))
print('前5个:', sub_links[:5])

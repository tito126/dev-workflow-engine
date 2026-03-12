import json

# 检查workspace版本的关键文件是否有修改内容
files_to_check = {
    'generate_html_report_v2.py': ['caller_service', 'fetch_range', '调用方', '影响级别', 'caller_display'],
    'preprocess.py': ['fetch_start', 'fetch_range', 'extract_caller_service_from_thread', 'representative_traces'],
    'loki_fetcher.py': ['extract_class_name', 'REPRESENTATIVE_TRACES', 'category:class_name'],
    'log_inspect_main.py': ['fetch_start_ts', '_last_fetch_meta', 'fetch-start'],
}

base = r'C:\Users\pc\.openclaw\workspace\skills\log-inspect'

for fname, keywords in files_to_check.items():
    path = f'{base}\\{fname}'
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        print(f'\n=== {fname} ===')
        for kw in keywords:
            status = '存在' if kw in content else '缺失'
            print(f'  {kw}: {status}')
    except Exception as e:
        print(f'{fname}: 读取失败 - {e}')

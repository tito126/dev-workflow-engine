import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\test_digest.json', encoding='utf-8') as f:
    d = json.load(f)

errors = d.get('errors', [])
print(f'errors 数量: {len(errors)}')
print()

if errors:
    e = errors[0]
    print('第一个 error 的字段:', list(e.keys()))
    print()
    print('category:', e.get('category'))
    print('root_class:', e.get('root_class'))
    print('api_entry:', e.get('api_entry'))
    print('caller_service:', e.get('caller_service'))
    print('thread:', e.get('thread'))
    print('count:', e.get('count'))
    print()
    print('samples 数量:', len(e.get('samples', [])))
    if e.get('samples'):
        s = e['samples'][0]
        print('第一个 sample 的字段:', list(s.keys()))
        print('sample caller_service:', s.get('caller_service'))
        print('sample thread:', s.get('thread'))

import json

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\test_digest2.json', encoding='utf-8') as f:
    d = json.load(f)

errors = d.get('errors', [])
print(f'errors 数量: {len(errors)}')
print()

if errors:
    # 找一个有 caller_service 的
    for e in errors[:10]:
        if e.get('caller_service') and e.get('caller_service') != 'UNKNOWN':
            print('找到一个有 caller_service 的 error:')
            print('category:', e.get('category'))
            print('root_class:', e.get('root_class'))
            print('api_entry:', e.get('api_entry'))
            print('caller_service:', e.get('caller_service'))
            print('threads:', e.get('threads'))
            print('count:', e.get('count'))
            print()
            if e.get('samples'):
                s = e['samples'][0]
                print('sample caller_service:', s.get('caller_service'))
                print('sample thread:', s.get('thread'))
            break
    else:
        print('前10个 error 都没有 caller_service（都是 UNKNOWN）')
        print()
        e = errors[0]
        print('第一个 error:')
        print('category:', e.get('category'))
        print('caller_service:', e.get('caller_service'))
        print('threads:', e.get('threads'))
        if e.get('samples'):
            s = e['samples'][0]
            print('sample caller_service:', s.get('caller_service'))
            print('sample thread:', s.get('thread'))

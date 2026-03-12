#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成日志分析报告
"""

import json

with open('logs_20260306_150657_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('='*60)
print('日志分析报告 - 测试医院病区护士站')
print('='*60)

print(f'\n总日志数: {data["summary"]["total_lines"]:,}')
print(f'ERROR: {data["summary"]["error_count"]:,}')
print(f'WARN: {data["summary"]["warn_count"]:,}')

print('\n' + '='*60)
print('错误分类统计')
print('='*60)
for cat, count in sorted(data['summary']['error_categories'].items(), key=lambda x: x[1], reverse=True):
    pct = count / data["summary"]["error_count"] * 100
    print(f'{cat:25s}: {count:5d} ({pct:5.1f}%)')

print('\n' + '='*60)
print('TOP 10 错误类型')
print('='*60)
for i, err in enumerate(data['errors'][:10], 1):
    print(f'\n{i}. [{err["category"]}] {err["class"]}')
    print(f'   出现次数: {err["count"]}')
    if err['users']:
        print(f'   影响用户: {", ".join(err["users"][:5])}')
    sample = err["samples"][0]["content"]
    if len(sample) > 150:
        sample = sample[:150] + '...'
    print(f'   示例: {sample}')

print('\n' + '='*60)
print('TOP 10 慢接口')
print('='*60)
slow_apis = data.get('slow_apis', [])
for i, api in enumerate(slow_apis[:10], 1):
    print(f'\n{i}. {api["api_path"]}')
    print(f'   调用次数: {api["count"]:,}')
    print(f'   最大耗时: {api["max_ms"]:,} ms')
    print(f'   平均耗时: {api["avg_ms"]:.0f} ms')
    if api.get('users'):
        print(f'   影响用户: {len(api["users"])} 人')

print('\n' + '='*60)
print('关键发现')
print('='*60)

# 分析关键问题
auth_errors = data['summary']['error_categories'].get('AuthException', 0)
null_errors = data['summary']['error_categories'].get('NullPointerException', 0)
timeout_errors = data['summary']['error_categories'].get('TimeoutException', 0)

print(f'\n1. 认证问题严重')
print(f'   - 认证错误: {auth_errors} 次 ({auth_errors/data["summary"]["error_count"]*100:.1f}%)')
print(f'   - 主要原因: Token 过期或未提供')
print(f'   - 建议: 检查 Token 刷新机制')

print(f'\n2. 空指针异常频繁')
print(f'   - 空指针错误: {null_errors} 次')
print(f'   - 建议: 加强参数校验和空值检查')

if timeout_errors > 0:
    print(f'\n3. 超时问题')
    print(f'   - 超时错误: {timeout_errors} 次')
    print(f'   - 建议: 优化接口性能或增加超时时间')

# 慢接口统计
slow_count = len(slow_apis)
if slow_count > 0:
    total_slow_calls = sum(api['count'] for api in slow_apis)
    print(f'\n4. 慢接口问题')
    print(f'   - 慢接口数量: {slow_count} 个')
    print(f'   - 慢调用总数: {total_slow_calls:,} 次')
    print(f'   - 建议: 优化数据库查询和接口性能')

print('\n' + '='*60)
print('报告生成完成')
print('='*60)
print(f'\n详细报告: logs_20260306_150657_report_fixed.html')

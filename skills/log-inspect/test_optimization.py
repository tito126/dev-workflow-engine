#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证优化效果
"""
import json

# 测试 categorize_error 函数
from preprocess import categorize_error, ERROR_CATEGORIES

print("=" * 60)
print("测试 1: 错误分类功能")
print("=" * 60)

test_cases = [
    "java.lang.NullPointerException: Cannot invoke method on null object",
    "认证失败：token已过期",
    "找不到插件实现：事件管道插件未配置",
    "参数校验失败：患者ID不能为空",
    "连接超时：无法连接到数据库",
    "这是一个未知的错误信息"
]

for content in test_cases:
    result = categorize_error(content)
    print(f"\n内容: {content[:50]}...")
    print(f"  分类: {result['name']}")
    print(f"  建议: {result['suggestion']}")
    if result.get('matched_keyword'):
        print(f"  关键词: {result['matched_keyword']}")

print("\n" + "=" * 60)
print("测试 2: 错误分类配置")
print("=" * 60)

print(f"\n共配置 {len(ERROR_CATEGORIES)} 种错误分类：")
for category_id, info in sorted(ERROR_CATEGORIES.items(), key=lambda x: x[1]['priority']):
    print(f"\n{info['priority']}. {info['name']} ({category_id})")
    print(f"   关键词: {', '.join(info['keywords'][:3])}...")
    print(f"   建议: {info['suggestion'][:50]}...")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

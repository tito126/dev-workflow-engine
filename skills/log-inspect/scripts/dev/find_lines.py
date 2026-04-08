#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修改 generate_html_report_v2.py
"""
import re

# 读取原文件
with open('generate_html_report_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修改的行号
for i, line in enumerate(lines):
    if '.container {' in line and 'max-width: 1200px' in line:
        print(f"找到 .container 定义在第 {i+1} 行")
    if '<body>' in line:
        print(f"找到 <body> 在第 {i+1} 行")
    if '<!-- 基本信息 -->' in line:
        print(f"找到基本信息在第 {i+1} 行")
    if '<!-- 异常统计概览 -->' in line:
        print(f"找到异常统计概览在第 {i+1} 行")
    if '<!-- 日志质量分析 -->' in line:
        print(f"找到日志质量分析在第 {i+1} 行")
    if '<!-- 详细异常分析 -->' in line:
        print(f"找到详细异常分析在第 {i+1} 行")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整修改 generate_html_report_v2.py：
1. 添加导航栏 CSS
2. 添加导航栏 HTML
3. 为 section 添加 id
4. 调整日志质量分析位置
"""

# 读取原文件
with open('generate_html_report_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加导航栏 CSS（在 .container 定义之前）
nav_css = """        /* 导航栏样式 */
        .nav-sidebar {
            position: fixed;
            left: 20px;
            top: 100px;
            width: 200px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 20px;
            max-height: calc(100vh - 140px);
            overflow-y: auto;
            z-index: 1000;
        }
        .nav-sidebar h3 {
            font-size: 1.2em;
            color: #1a1a2e;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .nav-sidebar ul {
            list-style: none;
        }
        .nav-sidebar li {
            margin-bottom: 10px;
        }
        .nav-sidebar a {
            color: #667eea;
            text-decoration: none;
            font-size: 0.95em;
            display: block;
            padding: 8px 12px;
            border-radius: 6px;
            transition: all 0.3s;
        }
        .nav-sidebar a:hover {
            background: #f0f0f0;
            color: #764ba2;
            transform: translateX(5px);
        }
        @media (max-width: 1400px) {
            .nav-sidebar {
                display: none;
            }
        }

"""

# 在 .container 定义之前插入导航栏样式
content = content.replace(
    '        .container {',
    nav_css + '        .container {'
)

# 修改 .container 的 margin-left
content = content.replace(
    '        .container {{\n            max-width: 1200px;\n            margin: 0 auto;',
    '        .container {{\n            max-width: 1200px;\n            margin: 0 auto;\n            margin-left: 240px;'
)

# 2. 添加导航栏 HTML（在 <body> 之后）
nav_html = """
    <!-- 左侧导航栏 -->
    <div class="nav-sidebar">
        <h3>📑 目录</h3>
        <ul>
            <li><a href="#basic-info">基本信息</a></li>
            <li><a href="#log-quality">日志质量分析</a></li>
            <li><a href="#error-stats">异常统计概览</a></li>
            <li><a href="#error-details">详细异常分析</a></li>
            <li><a href="#log-feedback">日志反哺建议</a></li>
            <li><a href="#slow-apis">慢接口 Trace 详情</a></li>
        </ul>
    </div>

"""

content = content.replace(
    '<body>\n    <div class="container">',
    '<body>\n' + nav_html + '    <div class="container">'
)

# 3. 为各个 section 添加 id
sections = [
    ('<!-- 基本信息 -->\n            <div class="section">', '<!-- 基本信息 -->\n            <div class="section" id="basic-info">'),
    ('<!-- 日志质量分析 -->\n            <div class="section">', '<!-- 日志质量分析 -->\n            <div class="section" id="log-quality">'),
    ('<!-- 异常统计概览 -->\n            <div class="section">', '<!-- 异常统计概览 -->\n            <div class="section" id="error-stats">'),
    ('<!-- 详细异常分析 -->\n            <div class="section">', '<!-- 详细异常分析 -->\n            <div class="section" id="error-details">'),
    ('<!-- 日志反哺模块 -->\n            <div class="section">', '<!-- 日志反哺模块 -->\n            <div class="section" id="log-feedback">'),
    ('<!-- 慢接口 Trace 详情 -->\n            <div class="section">', '<!-- 慢接口 Trace 详情 -->\n            <div class="section" id="slow-apis">'),
]

for old, new in sections:
    content = content.replace(old, new)

# 4. 调整日志质量分析的位置
# 提取日志质量分析部分
import re
log_quality_pattern = r'(<!-- 日志质量分析 -->.*?</div>\n\n)'
match = re.search(log_quality_pattern, content, re.DOTALL)
if match:
    log_quality_section = match.group(1)
    # 删除原位置的日志质量分析
    content = content.replace(log_quality_section, '')
    # 在基本信息之后插入
    content = content.replace(
        '            </div>\n\n            <!-- 异常统计概览 -->',
        '            </div>\n\n            ' + log_quality_section + '            <!-- 异常统计概览 -->'
    )
    print("OK: 已调整日志质量分析位置")
else:
    print("警告：未找到日志质量分析部分")

# 保存修改后的文件
with open('generate_html_report_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK: 已完成所有修改")

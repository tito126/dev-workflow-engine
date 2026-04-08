#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 generate_html_report_v2.py 添加左侧导航栏
"""

# 读取原文件
with open('generate_html_report_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 CSS 中添加导航栏样式
nav_css = """
        /* 导航栏样式 */
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
        .container {
            margin-left: 240px;
        }
        @media (max-width: 1400px) {
            .nav-sidebar {
                display: none;
            }
            .container {
                margin-left: auto;
            }
        }
"""

# 在 body 样式之后插入导航栏样式
content = content.replace(
    '        .container {{\n            max-width: 1200px;',
    nav_css + '\n        .container {{\n            max-width: 1200px;'
)

# 2. 在 <body> 后添加导航栏 HTML
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
    '<body>\n' + nav_html + '\n    <div class="container">'
)

# 3. 为各个 section 添加 id
sections = [
    ('<!-- 基本信息 -->', 'id="basic-info"'),
    ('<!-- 日志质量分析 -->', 'id="log-quality"'),
    ('<!-- 异常统计概览 -->', 'id="error-stats"'),
    ('<!-- 详细异常分析 -->', 'id="error-details"'),
    ('<!-- 日志反哺模块 -->', 'id="log-feedback"'),
    ('<!-- 慢接口 Trace 详情 -->', 'id="slow-apis"'),
]

for comment, id_attr in sections:
    content = content.replace(
        f'{comment}\n            <div class="section">',
        f'{comment}\n            <div class="section" {id_attr}>'
    )

# 4. 调整日志质量分析的位置（移到基本信息之后）
# 这个比较复杂，需要手动调整

# 保存修改后的文件
with open('generate_html_report_v2_with_nav.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK: 已生成 generate_html_report_v2_with_nav.py")
print("注意：日志质量分析的位置需要手动调整")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全地为 generate_html_report_v2.py 添加导航栏
"""

with open('generate_html_report_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 CSS 末尾（</style> 之前）添加导航栏样式
# 注意：文件中的 CSS 在 f-string 中，所以 { 已经是 {{
nav_css = """
        /* 导航栏样式 */
        .nav-sidebar {{
            position: fixed;
            left: 20px;
            top: 100px;
            width: 180px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 16px;
            max-height: calc(100vh - 140px);
            overflow-y: auto;
            z-index: 1000;
        }}
        .nav-sidebar h3 {{
            font-size: 1em;
            color: #1a1a2e;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #667eea;
        }}
        .nav-sidebar ul {{
            list-style: none;
        }}
        .nav-sidebar li {{
            margin-bottom: 6px;
        }}
        .nav-sidebar a {{
            color: #555;
            text-decoration: none;
            font-size: 0.88em;
            display: block;
            padding: 6px 10px;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .nav-sidebar a:hover {{
            background: #f0f0f0;
            color: #667eea;
            padding-left: 14px;
        }}
        @media (max-width: 1400px) {{
            .nav-sidebar {{ display: none; }}
        }}
"""

# 在 </style> 之前插入
content = content.replace(
    '    </style>\n</head>',
    nav_css + '    </style>\n</head>'
)

# 2. 在 <body> 之后添加导航栏 HTML（不在 f-string 中）
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
    ('<!-- 基本信息 -->\n            <div class="section">', '<!-- 基本信息 -->\n            <div class="section" id="basic-info">'),
    ('<!-- 日志质量分析 -->\n            <div class="section">', '<!-- 日志质量分析 -->\n            <div class="section" id="log-quality">'),
    ('<!-- 异常统计概览 -->\n            <div class="section">', '<!-- 异常统计概览 -->\n            <div class="section" id="error-stats">'),
    ('<!-- 详细异常分析 -->\n            <div class="section">', '<!-- 详细异常分析 -->\n            <div class="section" id="error-details">'),
    ('<!-- 日志反哺模块 -->\n            <div class="section">', '<!-- 日志反哺模块 -->\n            <div class="section" id="log-feedback">'),
    ('<!-- 慢接口 Trace 详情 -->\n            <div class="section">', '<!-- 慢接口 Trace 详情 -->\n            <div class="section" id="slow-apis">'),
]

for old, new in sections:
    if old in content:
        content = content.replace(old, new)
        print(f"OK: 添加 id 到 {old[:20]}...")
    else:
        print(f"警告: 未找到 {old[:20]}...")

# 4. 调整日志质量分析的位置（移到基本信息之后）
import re

# 找到日志质量分析部分（从注释到 </div>\n\n）
# 这个部分在 f-string 外面，所以可以直接操作
log_quality_pattern = r'(            <!-- 日志质量分析 -->.*?            </div>\n\n)'
match = re.search(log_quality_pattern, content, re.DOTALL)
if match:
    log_quality_section = match.group(1)
    # 删除原位置
    content = content.replace(log_quality_section, '')
    # 在基本信息之后插入（基本信息的 </div> 之后）
    # 找到基本信息结束的位置
    basic_info_end = '            </div>\n\n            <!-- 异常统计概览 -->'
    content = content.replace(
        basic_info_end,
        '            </div>\n\n' + log_quality_section + '            <!-- 异常统计概览 -->'
    )
    print("OK: 已调整日志质量分析位置")
else:
    print("警告: 未找到日志质量分析部分")

# 保存
with open('generate_html_report_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK: 所有修改完成")

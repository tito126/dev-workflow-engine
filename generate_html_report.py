#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 digest JSON 生成 HTML 报告
"""
import json
import sys
from datetime import datetime

def generate_html_report(digest_file, output_file, hospital_name, service_name):
    """生成 HTML 报告"""
    
    # 读取 digest
    with open(digest_file, 'r', encoding='utf-8') as f:
        digest = json.load(f)
    
    meta = digest['meta']
    summary = digest['summary']
    errors = digest['errors']
    slow_requests = digest.get('slow_requests', [])
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{hospital_name} - {service_name} 日志分析报告</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        .meta-info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card.error {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .summary-card.warn {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            color: #333;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
        }}
        .summary-card .number {{
            font-size: 32px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .error-detail {{
            background-color: #fff5f5;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .error-detail h4 {{
            margin: 0 0 10px 0;
            color: #e74c3c;
        }}
        .error-sample {{
            background-color: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 3px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 12px;
            overflow-x: auto;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 12px;
        }}
        .trace-id {{
            color: #3498db;
            font-size: 11px;
        }}
        .slow-request {{
            background-color: #fff9e6;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-error {{
            background-color: #e74c3c;
            color: white;
        }}
        .badge-warn {{
            background-color: #f39c12;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{hospital_name} - {service_name}</h1>
        <h2>日志分析报告</h2>
        
        <div class="meta-info">
            <p><strong>生成时间：</strong>{meta['generated_at']}</p>
            <p><strong>分析文件：</strong>{', '.join(meta['files_processed'])}</p>
            <p><strong>慢接口阈值：</strong>{meta['slow_threshold_ms']}ms</p>
        </div>
        
        <h2>概览</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>总日志数</h3>
                <div class="number">{summary['total_lines']:,}</div>
            </div>
            <div class="summary-card error">
                <h3>错误日志</h3>
                <div class="number">{summary['error_count']}</div>
            </div>
            <div class="summary-card warn">
                <h3>警告日志</h3>
                <div class="number">{summary['warn_count']}</div>
            </div>
            <div class="summary-card">
                <h3>慢接口</h3>
                <div class="number">{len(slow_requests)}</div>
            </div>
        </div>
        
        <h2>错误分类统计</h2>
        <table>
            <thead>
                <tr>
                    <th>错误类型</th>
                    <th>数量</th>
                    <th>占比</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # 错误分类统计
    for category, count in sorted(summary['error_categories'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / summary['error_count'] * 100) if summary['error_count'] > 0 else 0
        html += f"""
                <tr>
                    <td><span class="badge badge-error">{category}</span></td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <h2>错误详情</h2>
"""
    
    # 错误详情
    for error in errors[:10]:  # 只显示前10个错误类型
        html += f"""
        <div class="error-detail">
            <h4>{error['category']} - {error['class']}</h4>
            <p><strong>出现次数：</strong>{error['count']}</p>
            <p><strong>示例：</strong></p>
"""
        for sample in error['samples'][:3]:  # 每个错误类型显示3个示例
            html += f"""
            <div class="error-sample">
                <div class="timestamp">{sample['timestamp']}</div>
                {sample['content'][:500]}
                {f'<div class="trace-id">TraceID: {sample["trace_id"]}</div>' if sample.get('trace_id') else ''}
            </div>
"""
        html += """
        </div>
"""
    
    # 慢接口
    if slow_requests:
        html += """
        <h2>慢接口统计</h2>
"""
        for req in slow_requests[:20]:  # 显示前20个慢接口
            html += f"""
        <div class="slow-request">
            <p><strong>接口：</strong>{req.get('api', '未知')}</p>
            <p><strong>耗时：</strong>{req['time_ms']}ms</p>
            <p><strong>时间：</strong>{req.get('timestamp', '未知')}</p>
        </div>
"""
    
    html += """
        <h2>分析建议</h2>
        <div class="meta-info">
            <h3>关于 YGC 频率高的问题</h3>
            <ol>
                <li><strong>日志量分析：</strong>
                    <ul>
                        <li>警告日志占比很高（{:.1f}%），大量日志输出会产生临时对象</li>
                        <li>建议调整日志级别，减少不必要的日志输出</li>
                    </ul>
                </li>
                <li><strong>错误分析：</strong>
                    <ul>
                        <li>共发现 {} 条错误日志，需要排查具体原因</li>
                        <li>主要错误类型：{}</li>
                    </ul>
                </li>
                <li><strong>性能优化：</strong>
                    <ul>
                        <li>存在 {} 个慢接口（>={} ms），建议优化</li>
                        <li>慢接口可能导致线程阻塞，间接影响内存和 GC</li>
                    </ul>
                </li>
                <li><strong>JVM 调优建议：</strong>
                    <ul>
                        <li>在 Grafana 查看 JVM 监控面板，确认 YGC 频率</li>
                        <li>考虑增大年轻代空间（-Xmn 参数）</li>
                        <li>使用异步日志 Appender 减少日志对主线程的影响</li>
                    </ul>
                </li>
            </ol>
        </div>
    </div>
</body>
</html>
""".format(
        summary['warn_count'] / summary['total_lines'] * 100 if summary['total_lines'] > 0 else 0,
        summary['error_count'],
        ', '.join(list(summary['error_categories'].keys())[:3]),
        len(slow_requests),
        meta['slow_threshold_ms']
    )
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 报告已生成：{output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python generate_html_report.py <digest.json> <output.html> [医院名称] [服务名称]")
        sys.exit(1)
    
    digest_file = sys.argv[1]
    output_file = sys.argv[2]
    hospital_name = sys.argv[3] if len(sys.argv) > 3 else "医院"
    service_name = sys.argv[4] if len(sys.argv) > 4 else "服务"
    
    generate_html_report(digest_file, output_file, hospital_name, service_name)

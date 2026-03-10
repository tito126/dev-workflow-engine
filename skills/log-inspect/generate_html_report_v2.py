#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成优化后的 HTML 日志分析报告（支持中文分类和优化建议）
"""
import json
import sys
from datetime import datetime

def generate_error_category_cards(summary):
    """生成错误分类统计卡片"""
    html = ""
    for category, count in sorted(summary['error_categories'].items(), key=lambda x: x[1], reverse=True)[:3]:
        html += f"""
                    <div class="stat-card warning">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">{category}</div>
                    </div>
"""
    return html

def generate_error_category_table(summary):
    """生成错误分类详细表格"""
    html = """
                <table class="performance-table">
                    <thead>
                        <tr>
                            <th>错误类型</th>
                            <th>出现次数</th>
                            <th>占比</th>
                            <th>优化建议</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    total_errors = summary['error_count']
    
    for category, count in sorted(summary['error_categories'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_errors * 100) if total_errors > 0 else 0
        
        # 根据分类名称匹配建议（从 ERROR_CATEGORIES）
        suggestion = "需要查看详细日志进行分析"
        if '业务逻辑' in category:
            suggestion = "检查业务逻辑、数据完整性和上下游业务约束"
        elif '配置' in category or '兼容' in category:
            suggestion = "检查配置项、接口契约和版本兼容性；如已确认不影响业务可降低优先级"
        elif '空指针' in category:
            suggestion = "检查对象是否为空，添加空值校验"
        elif '数据格式' in category:
            suggestion = "检查入参格式、字段类型和返回内容格式是否符合预期"
        elif '下游服务' in category:
            suggestion = "检查下游服务状态、路由、网关和接口返回内容"
        elif '认证' in category or '权限' in category:
            suggestion = "检查token是否过期，确认用户权限配置"
        elif 'SQL' in category:
            suggestion = "检查SQL语句语法，确认数据库连接正常"
        elif '超时' in category:
            suggestion = "检查网络连接，增加超时时间或优化接口性能"
        elif '连接' in category:
            suggestion = "检查网络连接，确认目标服务是否正常"
        elif '插件' in category:
            suggestion = "检查插件配置文件，确认插件是否正确安装"
        elif '参数' in category or '校验' in category:
            suggestion = "检查请求参数是否完整，确认参数格式正确"
        elif 'JSON' in category:
            suggestion = "检查JSON格式是否正确，确认数据结构"
        elif '内存' in category:
            suggestion = "增加JVM内存配置，检查是否有内存泄漏"
        elif '文件' in category:
            suggestion = "检查文件路径是否正确，确认文件是否存在"
        
        html += f"""
                        <tr>
                            <td><strong>{category}</strong></td>
                            <td>{count}</td>
                            <td>{percentage:.1f}%</td>
                            <td><span style="color: #1565c0;">💡 {suggestion}</span></td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
"""
    return html

def generate_error_details(errors):
    """生成错误详情"""
    html = ""
    
    for idx, error in enumerate(errors[:10], 1):  # 最多显示10个
        # 确定严重程度
        severity = "high" if error['count'] >= 30 else "medium" if error['count'] >= 10 else "low"
        severity_text = "高严重程度" if severity == "high" else "中等严重程度" if severity == "medium" else "低严重程度"
        severity_emoji = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
        
        html += f"""
                <div class="error-item">
                    <div class="error-title">
                        <span>{severity_emoji} {idx}. {error['category']}</span>
                        <span class="severity-badge severity-{severity}">{severity_text}</span>
                    </div>
                    <p class="error-meta"><strong>出现次数:</strong> {error['count']} 次</p>
                    <p class="error-meta"><strong>位置:</strong> {error['class']}</p>
"""
        
        # 匹配的关键词
        if error.get('matched_keywords'):
            keywords_str = ', '.join(error['matched_keywords'])
            html += f"""
                    <p class="error-meta"><strong>匹配关键词:</strong> <code>{keywords_str}</code></p>
"""
        
        # 样例内容
        if error.get('samples'):
            sample = error['samples'][0]

            if sample.get('error_reason'):
                html += f"""
                    <p class="error-meta"><strong>真正原因:</strong> <span style="color: #c62828;">{sample.get('error_reason', '')}</span></p>
"""

            html += f"""
                    <div class="error-details">{sample.get('content', '')[:500]}</div>
"""
            
            # TraceID 列表
            trace_ids = [s.get('trace_id', '') for s in error['samples'][:5] if s.get('trace_id')]
            if trace_ids:
                html += """
                    <div class="trace-list">
                        <h5>🔍 traceId 样例（可用于追踪完整调用链）</h5>
                        <ul>
"""
                for s in error['samples'][:5]:
                    if s.get('trace_id'):
                        html += f"""
                            <li><span class="trace-id">{s['trace_id']}</span> <span class="trace-time">{s.get('timestamp', '')[:16]}</span></li>
"""
                html += """
                        </ul>
                    </div>
"""
        
        # 优化建议
        suggestion = error.get('suggestion', '需要查看详细日志进行分析')
        html += f"""
                    <div class="suggestion-box">
                        <h4>💡 优化建议</h4>
                        <p>{suggestion}</p>
                    </div>
                </div>
"""
    
    return html

def generate_html_report_v2(digest_file, output_file, hospital_name, service_name, time_range=""):
    """生成优化后的 HTML 报告"""
    
    # 读取 digest
    with open(digest_file, 'r', encoding='utf-8') as f:
        digest = json.load(f)
    
    meta = digest['meta']
    summary = digest['summary']
    errors = digest['errors']
    slow_apis = digest.get('slow_apis', [])
    
    # 计算总慢接口调用次数
    total_slow_calls = sum(api['count'] for api in slow_apis)
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日志分析报告 - {hospital_name} {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ font-size: 1.1em; opacity: 0.8; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            font-size: 1.8em;
            color: #1a1a2e;
            border-left: 5px solid #667eea;
            padding-left: 15px;
            margin-bottom: 25px;
        }}
        .info-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
        }}
        .info-table {{ width: 100%; border-collapse: collapse; }}
        .info-table td {{ padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }}
        .info-table td:first-child {{ font-weight: bold; color: #1a1a2e; width: 180px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: #fff;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .stat-card.danger {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .stat-card.warning {{ background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ font-size: 1em; opacity: 0.9; }}
        .performance-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .performance-table th, .performance-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        .performance-table th {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
        }}
        .performance-table tr:hover {{ background: #f5f5f5; }}
        .error-item {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .error-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.3em;
            font-weight: bold;
            color: #1a1a2e;
            margin-bottom: 15px;
        }}
        .severity-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        .severity-high {{ background: #f8d7da; color: #721c24; }}
        .severity-medium {{ background: #fff3cd; color: #856404; }}
        .severity-low {{ background: #d4edda; color: #155724; }}
        .error-meta {{ margin: 8px 0; color: #666; }}
        .error-details {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }}
        .trace-list {{
            background: #e3f2fd;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .trace-list h5 {{ color: #1565c0; margin-bottom: 10px; }}
        .trace-list ul {{ list-style: none; }}
        .trace-list li {{ margin: 8px 0; }}
        .trace-id {{
            background: #fff;
            padding: 4px 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #1565c0;
        }}
        .trace-time {{ color: #666; font-size: 0.9em; margin-left: 10px; }}
        .suggestion-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
        }}
        .suggestion-box h4 {{ color: #1565c0; margin-bottom: 10px; }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 日志分析报告</h1>
            <p class="subtitle">{hospital_name} | {time_range if time_range else datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        
        <div class="content">
            <!-- 基本信息 -->
            <div class="section">
                <h2 class="section-title">基本信息</h2>
                <div class="info-card">
                    <table class="info-table">
                        <tr><td>医院名称</td><td>{hospital_name}</td></tr>
                        <tr><td>服务名称</td><td>{service_name}</td></tr>
                        <tr><td>分析日志量</td><td>{summary['total_lines']:,} 条</td></tr>
                        <tr><td>慢接口阈值</td><td>{meta['slow_threshold_ms']}ms</td></tr>
                        <tr><td>生成时间</td><td>{meta['generated_at']}</td></tr>
                    </table>
                </div>
            </div>

            <!-- 异常统计概览 -->
            <div class="section">
                <h2 class="section-title">异常统计概览</h2>
                <div class="stats-grid">
                    <div class="stat-card danger">
                        <div class="stat-number">{summary['error_count']}</div>
                        <div class="stat-label">ERROR 总数</div>
                    </div>
{generate_error_category_cards(summary)}
                    <div class="stat-card danger">
                        <div class="stat-number">{len(slow_apis)}</div>
                        <div class="stat-label">慢接口类型</div>
                    </div>
                </div>
                
                <!-- 错误分类详细表格 -->
                <h3 style="margin-top: 30px; margin-bottom: 15px; color: #1a1a2e;">错误分类详情</h3>
{generate_error_category_table(summary)}
            </div>

            <!-- 详细异常分析 -->
            <div class="section">
                <h2 class="section-title">详细异常分析</h2>
{generate_error_details(errors)}
            </div>

            <!-- 慢接口分析 -->
            <div class="section">
                <h2 class="section-title">慢接口分析</h2>
                <p style="margin-bottom: 20px; color: #666;">共发现 {len(slow_apis)} 种慢接口，累计 {total_slow_calls} 次慢调用</p>
                <table class="performance-table">
                    <thead>
                        <tr>
                            <th>接口路径</th>
                            <th>调用次数</th>
                            <th>最大耗时</th>
                            <th>平均耗时</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for api in slow_apis[:20]:
        html += f"""
                        <tr>
                            <td><code>{api['api_path']}</code></td>
                            <td>{api['count']}</td>
                            <td><span class="time-badge time-critical">{api['max_ms']}ms</span></td>
                            <td><span class="time-badge time-warning">{api['avg_ms']}ms</span></td>
                        </tr>
"""

        analysis = api.get('analysis')
        if analysis:
            bottleneck = analysis.get('bottleneck')
            suggestions = api.get('suggestions', [])
            sample_trace = ''
            if api.get('samples'):
                sample_trace = api['samples'][0].get('trace_id', '') or ''

            html += """
                    <tr>
                        <td colspan="4" style="background:#f8f9ff;">
"""
            if sample_trace:
                html += f"<p><strong>traceId 样例：</strong><span class=\"trace-id\">{sample_trace}</span></p>"
            if bottleneck:
                html += f"<p><strong>主要瓶颈：</strong>{bottleneck.get('category', '未知')}，耗时 {bottleneck.get('time', 0)}ms</p>"
            html += f"<p><strong>已识别耗时：</strong>{analysis.get('recognized_time', 0)}ms，<strong>未识别耗时：</strong>{analysis.get('unrecognized_time', 0)}ms ({analysis.get('unrecognized_ratio', 0):.1f}%)</p>"

            steps = analysis.get('steps', [])[:5]
            if steps:
                html += "<div style='margin-top:10px;'><strong>调用链步骤：</strong><ul style='margin:8px 0 0 20px;'>"
                for step in steps:
                    html += f"<li>{step.get('category', '未知')}：{step.get('time', 0)}ms — <code>{step.get('log', '')}</code></li>"
                html += "</ul></div>"

            if suggestions:
                html += "<div style='margin-top:10px;'><strong>优化建议：</strong><ul style='margin:8px 0 0 20px;'>"
                for suggestion in suggestions[:5]:
                    html += f"<li>{suggestion}</li>"
                html += "</ul></div>"

            html += """
                        </td>
                    </tr>
"""
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>报告生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>日志巡检工具 v2.0 | 支持中文分类和智能建议</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"报告已生成: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python generate_html_report_v2.py <digest.json> <output.html> [医院名称] [服务名称] [时间范围]")
        sys.exit(1)
    
    digest_file = sys.argv[1]
    output_file = sys.argv[2]
    hospital_name = sys.argv[3] if len(sys.argv) > 3 else "未知医院"
    service_name = sys.argv[4] if len(sys.argv) > 4 else "未知服务"
    time_range = sys.argv[5] if len(sys.argv) > 5 else ""
    
    generate_html_report_v2(digest_file, output_file, hospital_name, service_name, time_range)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成高质量的 HTML 日志分析报告
"""
import json
import sys
from datetime import datetime
from collections import defaultdict

def generate_html_report(digest_file, output_file, hospital_name, service_name, time_range=""):
    """生成 HTML 报告"""
    
    # 读取 digest
    with open(digest_file, 'r', encoding='utf-8') as f:
        digest = json.load(f)
    
    meta = digest['meta']
    summary = digest['summary']
    errors = digest['errors']
    slow_apis = digest.get('slow_apis', [])
    
    # 计算总慢接口调用次数
    total_slow_calls = sum(api['count'] for api in slow_apis)
    
    # 按严重程度分类错误
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for error in errors:
        if error['count'] >= 30 or error['category'] in ['NullPointerException', 'AuthException']:
            high_priority.append(error)
        elif error['count'] >= 10:
            medium_priority.append(error)
        else:
            low_priority.append(error)
    
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
        .header .env-tag {{
            display: inline-block;
            background: #27ae60;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }}
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
            background: #fff;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-card.danger {{ border-left: 5px solid #e74c3c; }}
        .stat-card.warning {{ border-left: 5px solid #f39c12; }}
        .stat-card.info {{ border-left: 5px solid #3498db; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .stat-card.danger .stat-number {{ color: #e74c3c; }}
        .stat-card.warning .stat-number {{ color: #f39c12; }}
        .stat-card.info .stat-number {{ color: #3498db; }}
        .stat-label {{ color: #666; font-size: 0.95em; }}
        .error-item {{
            background: #fff;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #e74c3c;
        }}
        .error-item.warning {{ border-left-color: #f39c12; }}
        .error-item.info {{ border-left-color: #3498db; }}
        .error-title {{
            font-size: 1.2em;
            color: #1a1a2e;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .severity-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: bold;
        }}
        .severity-high {{ background: #fee; color: #e74c3c; }}
        .severity-medium {{ background: #fff3cd; color: #856404; }}
        .severity-low {{ background: #d4edda; color: #155724; }}
        .error-meta {{ color: #666; margin-bottom: 10px; font-size: 0.95em; }}
        .error-details {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            font-family: 'Consolas', monospace;
            font-size: 0.85em;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .trace-list {{
            background: #fff3cd;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }}
        .trace-list h5 {{
            color: #856404;
            margin-bottom: 10px;
            font-size: 0.95em;
        }}
        .trace-list ul {{
            list-style: none;
            font-family: 'Consolas', monospace;
            font-size: 0.85em;
        }}
        .trace-list li {{
            padding: 5px 0;
            border-bottom: 1px dashed #e0e0e0;
        }}
        .trace-list li:last-child {{ border-bottom: none; }}
        .trace-id {{
            color: #d63384;
            font-weight: bold;
        }}
        .trace-time {{
            color: #666;
            font-size: 0.9em;
        }}
        .suggestion-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
        }}
        .suggestion-box h4 {{ color: #2e7d32; margin-bottom: 10px; }}
        .suggestion-box ul {{ margin-left: 20px; color: #555; }}
        .suggestion-box li {{ margin-bottom: 8px; }}
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
        .time-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .time-critical {{ background: #f8d7da; color: #721c24; }}
        .time-warning {{ background: #fff3cd; color: #856404; }}
        .improvement-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }}
        .improvement-box h4 {{ color: #1565c0; margin-bottom: 10px; }}
        .summary-box {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            border-radius: 12px;
            padding: 30px;
            margin-top: 30px;
        }}
        .summary-box h3 {{ margin-bottom: 20px; font-size: 1.5em; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
        }}
        .summary-item {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
        }}
        .summary-item h4 {{ color: #f39c12; margin-bottom: 15px; }}
        .summary-item ul {{ margin-left: 20px; }}
        .summary-item li {{ margin-bottom: 10px; line-height: 1.6; }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .content {{ padding: 20px; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 日志分析报告</h1>
            <p class="subtitle">{hospital_name} | {time_range if time_range else datetime.now().strftime('%Y-%m-%d')}</p>
            <span class="env-tag">🐳 K8s 环境 (Loki)</span>
        </div>
        
        <div class="content">
            <!-- 基本信息 -->
            <div class="section">
                <h2 class="section-title">基本信息</h2>
                <div class="info-card">
                    <table class="info-table">
                        <tr><td>医院名称</td><td>{hospital_name}</td></tr>
                        <tr><td>服务名称</td><td>{service_name}</td></tr>
                        <tr><td>分析日志量</td><td>{summary['total_lines']:,} 条 (ERROR/WARN 级别)</td></tr>
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
                        <div class="stat-label">ERROR 级别</div>
                    </div>
"""
    
    # 添加错误分类统计卡片
    for category, count in sorted(summary['error_categories'].items(), key=lambda x: x[1], reverse=True)[:3]:
        html += f"""
                    <div class="stat-card warning">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">{category}</div>
                    </div>
"""
    
    html += f"""
                    <div class="stat-card danger">
                        <div class="stat-number">{len(slow_apis)}</div>
                        <div class="stat-label">慢接口类型 (>{meta['slow_threshold_ms']}ms)</div>
                    </div>
                </div>
            </div>

            <!-- 详细异常分析 -->
            <div class="section">
                <h2 class="section-title">详细异常分析</h2>
"""
    
    # 高优先级错误
    if high_priority:
        for idx, error in enumerate(high_priority[:5], 1):
            html += f"""
                <div class="error-item">
                    <div class="error-title">
                        <span>🔴 {idx}. {error['category']}</span>
                        <span class="severity-badge severity-high">高严重程度</span>
                    </div>
                    <p class="error-meta"><strong>出现次数:</strong> {error['count']} 次</p>
                    <p class="error-meta"><strong>位置:</strong> {error['class']}</p>
"""
            if error.get('samples'):
                sample = error['samples'][0]
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
            
            # 建议
            suggestions = []
            if 'NullPointerException' in error['category']:
                suggestions = [
                    "检查代码中的空指针引用，添加必要的空值判断",
                    "排查服务间调用返回 null 的场景",
                    "建议使用 Optional 或其他空安全机制"
                ]
            elif 'AuthException' in error['category'] or '认证' in error['category']:
                suggestions = [
                    "检查认证服务的可用性和响应时间",
                    "确认 Token 配置和有效期设置",
                    "排查服务间认证配置问题"
                ]
            elif '404' in error['category'] or 'Not Found' in error['category']:
                suggestions = [
                    "检查目标服务是否正常注册到服务中心",
                    "确认服务路由和网关配置",
                    "排查服务版本兼容性问题"
                ]
            else:
                suggestions = [
                    f"检查 {error['class']} 相关的业务逻辑",
                    "排查上游服务的数据返回是否正常",
                    "建议增加详细的错误日志和监控告警"
                ]
            
            if suggestions:
                html += """
                    <div class="suggestion-box">
                        <h4>💡 建议</h4>
                        <ul>
"""
                for suggestion in suggestions:
                    html += f"                            <li>{suggestion}</li>\n"
                html += """
                        </ul>
                    </div>
"""
            html += """
                </div>
"""
    
    # 中优先级错误
    if medium_priority:
        html += """
                <h3 style="margin-top: 30px; margin-bottom: 20px; color: #f39c12;">🟡 中优先级问题</h3>
"""
        for idx, error in enumerate(medium_priority[:3], 1):
            html += f"""
                <div class="error-item warning">
                    <div class="error-title">
                        <span>{idx}. {error['category']}</span>
                        <span class="severity-badge severity-medium">中严重程度</span>
                    </div>
                    <p class="error-meta"><strong>出现次数:</strong> {error['count']} 次 | <strong>位置:</strong> {error['class']}</p>
"""
            if error.get('samples'):
                sample = error['samples'][0]
                html += f"""
                    <div class="error-details">{sample.get('content', '')[:300]}</div>
"""
            html += """
                </div>
"""
    
    html += """
            </div>
"""
    
    # 性能问题分析
    if slow_apis:
        html += """
            <div class="section">
                <h2 class="section-title">性能问题分析</h2>
                <p style="margin-bottom: 20px; color: #666;">以下接口响应时间超过阈值，需要关注性能优化：</p>
                
                <table class="performance-table">
                    <thead>
                        <tr>
                            <th>接口路径</th>
                            <th>最大耗时</th>
                            <th>平均耗时</th>
                            <th>次数</th>
                            <th>traceId 样例</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for api in slow_apis[:10]:
            time_class = 'time-critical' if api['max_ms'] >= 3000 else 'time-warning'
            trace_id = api['samples'][0].get('trace_id', '') if api.get('samples') else ''
            html += f"""
                        <tr>
                            <td>{api['api_path']}</td>
                            <td><span class="time-badge {time_class}">{api['max_ms']:,}ms</span></td>
                            <td>{api['avg_ms']:,}ms</td>
                            <td>{api['count']}次</td>
                            <td><span class="trace-id" style="font-size:0.8em;">{trace_id[:32]}</span></td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>

                <div class="suggestion-box" style="margin-top: 20px;">
                    <h4>💡 性能优化建议</h4>
                    <ul>
"""
        # 针对最慢的接口给出建议
        if slow_apis:
            slowest = slow_apis[0]
            if slowest['max_ms'] >= 3000:
                html += f"""
                        <li><strong>{slowest['api_path']}（{slowest['max_ms']}ms）：</strong>响应时间严重超标，建议：
                            <ul style="margin-top: 5px;">
                                <li>检查数据库查询是否有慢SQL，添加必要的索引</li>
                                <li>排查是否有同步调用外部服务导致阻塞</li>
                                <li>考虑改为异步处理或增加缓存</li>
                            </ul>
                        </li>
"""
        html += """
                        <li>建议对所有超过1秒的接口增加性能监控告警</li>
                        <li>定期review慢接口，持续优化</li>
                    </ul>
                </div>
            </div>
"""
    
    # 总结与建议
    html += f"""
            <div class="section">
                <h2 class="section-title">总结与建议</h2>
                <div class="summary-box">
                    <div class="summary-grid">
                        <div class="summary-item">
                            <h4>🔴 高优先级问题</h4>
                            <ul>
"""
    for error in high_priority[:3]:
        html += f"""
                                <li><strong>{error['category']}：</strong>{error['count']} 次，需紧急排查</li>
"""
    html += """
                            </ul>
                        </div>
                        <div class="summary-item">
                            <h4>🟡 中优先级问题</h4>
                            <ul>
"""
    for error in medium_priority[:3]:
        html += f"""
                                <li><strong>{error['category']}：</strong>{error['count']} 次</li>
"""
    if slow_apis:
        html += f"""
                                <li><strong>慢接口：</strong>{len(slow_apis)} 种，共 {total_slow_calls} 次调用</li>
"""
    html += """
                            </ul>
                        </div>
                        <div class="summary-item">
                            <h4>📊 监控建议</h4>
                            <ul>
                                <li>对高频错误增加告警监控</li>
                                <li>对慢接口增加性能监控</li>
                                <li>建议每日生成日志分析报告</li>
                                <li>关注 YGC 频率和内存使用情况</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 数据来源: Loki (K8s) | 日志分析系统 v2.0</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 报告已生成：{output_file}")
    print(f"  - 错误：{summary['error_count']} 条")
    print(f"  - 高优先级：{len(high_priority)} 类")
    print(f"  - 中优先级：{len(medium_priority)} 类")
    print(f"  - 慢接口：{len(slow_apis)} 类，{total_slow_calls} 次调用")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python generate_html_report.py <digest.json> <output.html> [医院名称] [服务名称] [时间范围]")
        sys.exit(1)
    
    digest_file = sys.argv[1]
    output_file = sys.argv[2]
    hospital_name = sys.argv[3] if len(sys.argv) > 3 else "医院"
    service_name = sys.argv[4] if len(sys.argv) > 4 else "服务"
    time_range = sys.argv[5] if len(sys.argv) > 5 else ""
    
    generate_html_report(digest_file, output_file, hospital_name, service_name, time_range)

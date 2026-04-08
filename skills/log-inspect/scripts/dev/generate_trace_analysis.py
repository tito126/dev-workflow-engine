#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
慢接口调用链分析 - 分析相邻日志时间间隔
"""

import json
import re
from datetime import datetime
from collections import defaultdict

def parse_timestamp(ts_str):
    """解析时间戳"""
    try:
        return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S,%f')
    except:
        return None

def analyze_trace_timeline(trace_lines):
    """分析trace的时间线，找出时间间隔过长的地方"""
    # 解析每条日志的时间戳和内容
    log_pattern = re.compile(
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*?\[([^\]]+)\]\s+(\w+)\s+(\S+).*?--\s*(.*)'
    )
    
    timeline = []
    for line in trace_lines:
        match = log_pattern.search(line)
        if match:
            timestamp_str = match.group(1)
            thread = match.group(2)
            level = match.group(3)
            classname = match.group(4)
            content = match.group(5)
            
            timestamp = parse_timestamp(timestamp_str)
            if timestamp:
                timeline.append({
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'thread': thread,
                    'level': level,
                    'class': classname,
                    'content': content[:200]
                })
    
    # 按时间排序
    timeline.sort(key=lambda x: x['timestamp'])
    
    # 计算相邻日志的时间间隔
    gaps = []
    for i in range(1, len(timeline)):
        prev = timeline[i-1]
        curr = timeline[i]
        gap_ms = int((curr['timestamp'] - prev['timestamp']).total_seconds() * 1000)
        
        if gap_ms > 100:  # 只记录>100ms的间隔
            gaps.append({
                'gap_ms': gap_ms,
                'prev': prev,
                'curr': curr,
                'prev_index': i-1,
                'curr_index': i
            })
    
    return timeline, gaps

def generate_html_report(digest_path, log_path, output_path):
    """生成HTML报告"""
    
    # 读取digest
    with open(digest_path, encoding='utf-8') as f:
        digest = json.load(f)
    
    # 读取原始日志
    with open(log_path, encoding='utf-8') as f:
        all_lines = f.readlines()
    
    # 构建traceId索引
    print("构建traceId索引...")
    trace_index = defaultdict(list)
    trace_pattern = re.compile(r'\[([a-zA-Z0-9]{16,})')
    
    for i, line in enumerate(all_lines):
        match = trace_pattern.search(line)
        if match:
            trace_id = match.group(1)
            if len(trace_id) >= 16:
                trace_index[trace_id].append(i)
    
    print(f"索引完成，共 {len(trace_index)} 个trace")
    
    # 生成HTML
    html = []
    html.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日志分析报告 - 慢接口调用链分析</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-item {{ display: inline-block; margin-right: 30px; }}
        .summary-label {{ font-weight: bold; color: #7f8c8d; }}
        .summary-value {{ font-size: 1.2em; color: #2c3e50; }}
        
        .slow-api {{ background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin: 20px 0; }}
        .slow-api-header {{ background: #3498db; color: white; padding: 10px 15px; margin: -20px -20px 20px -20px; border-radius: 5px 5px 0 0; }}
        .slow-api-title {{ font-size: 1.2em; font-weight: bold; }}
        .slow-api-meta {{ margin-top: 5px; font-size: 0.9em; opacity: 0.9; }}
        
        .timeline {{ margin: 20px 0; }}
        .timeline-item {{ padding: 10px; margin: 5px 0; border-left: 3px solid #95a5a6; background: #f8f9fa; }}
        .timeline-item.gap {{ border-left-color: #e74c3c; background: #fee; }}
        .timeline-timestamp {{ font-family: monospace; color: #7f8c8d; font-size: 0.9em; }}
        .timeline-class {{ color: #2980b9; font-weight: bold; }}
        .timeline-content {{ color: #34495e; margin-top: 5px; }}
        
        .gap-analysis {{ background: #fff3cd; border: 2px solid #ffc107; border-radius: 5px; padding: 15px; margin: 15px 0; }}
        .gap-header {{ font-weight: bold; color: #856404; font-size: 1.1em; margin-bottom: 10px; }}
        .gap-time {{ color: #d63031; font-size: 1.3em; font-weight: bold; }}
        .gap-detail {{ margin: 10px 0; padding: 10px; background: white; border-radius: 3px; }}
        
        .error-categories {{ margin: 20px 0; }}
        .error-category {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .error-category-header {{ font-weight: bold; color: #2c3e50; font-size: 1.1em; }}
        .error-count {{ color: #e74c3c; font-weight: bold; }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #34495e; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f8f9fa; }}
        
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.85em; font-weight: bold; }}
        .badge-error {{ background: #e74c3c; color: white; }}
        .badge-warn {{ background: #f39c12; color: white; }}
        .badge-info {{ background: #3498db; color: white; }}
        
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 日志分析报告 - 慢接口调用链分析</h1>
        <div class="summary">
            <div class="summary-item">
                <span class="summary-label">时间窗口:</span>
                <span class="summary-value">2026-03-11 16:22~16:32 (10分钟)</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">日志总量:</span>
                <span class="summary-value">{total_lines:,}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">ERROR:</span>
                <span class="summary-value badge-error">{error_count:,}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">WARN:</span>
                <span class="summary-value badge-warn">{warn_count:,}</span>
            </div>
        </div>
""".format(
        total_lines=digest['summary']['total_lines'],
        error_count=digest['summary']['error_count'],
        warn_count=digest['summary']['warn_count']
    ))
    
    # 异常分类统计
    html.append("<h2>一、异常分类统计</h2>")
    html.append('<div class="error-categories">')
    
    cats = digest['summary']['error_categories']
    total_errors = sum(cats.values())
    
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        pct = count / total_errors * 100
        html.append(f'''
        <div class="error-category">
            <span class="error-category-header">{cat}</span>
            <span class="error-count">{count}</span>
            <span style="color: #7f8c8d;">({pct:.1f}%)</span>
        </div>
        ''')
    
    html.append('</div>')
    
    # 慢接口调用链分析
    html.append("<h2>二、慢接口调用链分析</h2>")
    
    slow_apis = digest.get('slow_apis', [])[:10]
    
    for i, api in enumerate(slow_apis, 1):
        api_path = api['api_path']
        max_ms = api['max_ms']
        avg_ms = api['avg_ms']
        count = api['count']
        
        top_traces = api.get('top_traces', [])
        if not top_traces:
            continue
        
        trace_id = top_traces[0]['trace_id']
        duration = top_traces[0]['duration_ms']
        
        html.append(f'''
        <div class="slow-api">
            <div class="slow-api-header">
                <div class="slow-api-title">#{i} {api_path}</div>
                <div class="slow-api-meta">
                    最慢: {max_ms}ms | 平均: {avg_ms}ms | 调用次数: {count} | 
                    分析trace: <code>{trace_id}</code> ({duration}ms)
                </div>
            </div>
        ''')
        
        # 获取该trace的所有日志
        if trace_id in trace_index:
            trace_line_indices = trace_index[trace_id]
            trace_lines = [all_lines[idx] for idx in trace_line_indices]
            
            # 分析时间线
            timeline, gaps = analyze_trace_timeline(trace_lines)
            
            if gaps:
                # 按时间间隔排序，显示最大的5个间隔
                gaps.sort(key=lambda x: -x['gap_ms'])
                
                html.append(f'<h3>⚠️ 发现 {len(gaps)} 个时间间隔 &gt; 100ms</h3>')
                
                for j, gap in enumerate(gaps[:5], 1):
                    gap_ms = gap['gap_ms']
                    prev = gap['prev']
                    curr = gap['curr']
                    
                    html.append(f'''
                    <div class="gap-analysis">
                        <div class="gap-header">间隔 #{j}: <span class="gap-time">{gap_ms}ms</span></div>
                        <div class="gap-detail">
                            <strong>前一条日志:</strong><br>
                            <span class="timeline-timestamp">{prev['timestamp_str']}</span>
                            <span class="timeline-class">{prev['class']}</span><br>
                            <span class="timeline-content">{prev['content']}</span>
                        </div>
                        <div class="gap-detail">
                            <strong>后一条日志:</strong><br>
                            <span class="timeline-timestamp">{curr['timestamp_str']}</span>
                            <span class="timeline-class">{curr['class']}</span><br>
                            <span class="timeline-content">{curr['content']}</span>
                        </div>
                        <div style="margin-top: 10px; padding: 10px; background: #e8f5e9; border-radius: 3px;">
                            <strong>分析:</strong> 在 <code>{prev['class']}</code> 和 <code>{curr['class']}</code> 之间耗时 {gap_ms}ms，
                            可能是数据库查询、远程调用或复杂计算导致。
                        </div>
                    </div>
                    ''')
                
                # 显示完整时间线
                html.append('<h3>完整调用时间线</h3>')
                html.append('<div class="timeline">')
                
                for k, log in enumerate(timeline):
                    # 检查是否是间隔点
                    is_gap = False
                    gap_info = ""
                    for gap in gaps[:5]:
                        if gap['curr_index'] == k:
                            is_gap = True
                            gap_info = f" (前方间隔 {gap['gap_ms']}ms)"
                            break
                    
                    css_class = "timeline-item gap" if is_gap else "timeline-item"
                    
                    html.append(f'''
                    <div class="{css_class}">
                        <span class="timeline-timestamp">{log['timestamp_str']}</span>
                        <span class="timeline-class">{log['class']}</span>
                        <span class="badge badge-{log['level'].lower()}">{log['level']}</span>
                        {gap_info}
                        <div class="timeline-content">{log['content']}</div>
                    </div>
                    ''')
                
                html.append('</div>')
            else:
                html.append('<p>该trace的日志时间间隔都很小，未发现明显性能瓶颈。</p>')
        else:
            html.append(f'<p>⚠️ 未找到trace <code>{trace_id}</code> 的日志</p>')
        
        html.append('</div>')
    
    # 结尾
    html.append('''
        <div style="margin-top: 40px; padding: 20px; background: #ecf0f1; border-radius: 5px; text-align: center;">
            <p style="color: #7f8c8d; margin: 0;">报告生成时间: 2026-03-11 18:01</p>
            <p style="color: #7f8c8d; margin: 5px 0 0 0;">OpenClaw Log Inspector v2.2</p>
        </div>
    </div>
</body>
</html>
    ''')
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(html))
    
    print(f"HTML报告已生成: {output_path}")

if __name__ == '__main__':
    digest_path = r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_reanalyzed'
    log_path = r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_默认集群.log'
    output_path = r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_163218_trace_analysis.html'
    
    generate_html_report(digest_path, log_path, output_path)

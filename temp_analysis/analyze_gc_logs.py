#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 Loki 日志中的 GC 信息
"""
import json
import re
from datetime import datetime
from collections import defaultdict

def parse_loki_logs(json_file):
    """解析 Loki JSON 格式的日志"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logs = []
    if data.get('status') == 'success':
        result = data.get('data', {}).get('result', [])
        for stream in result:
            for value in stream.get('values', []):
                timestamp_ns = int(value[0])
                log_line = value[1]
                timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
                logs.append({
                    'timestamp': timestamp,
                    'line': log_line
                })
    
    # 按时间排序
    logs.sort(key=lambda x: x['timestamp'])
    return logs

def analyze_gc_logs(logs):
    """分析 GC 日志"""
    gc_events = []
    gc_pattern = re.compile(r'(Young|Full|GC|gc)', re.IGNORECASE)
    ygc_pattern = re.compile(r'(Young\s+GC|YGC|Minor\s+GC)', re.IGNORECASE)
    
    # GC 时间模式（常见格式）
    gc_time_pattern = re.compile(r'(\d+\.\d+)\s*(ms|secs?)', re.IGNORECASE)
    
    for log in logs:
        line = log['line']
        if gc_pattern.search(line):
            gc_events.append({
                'timestamp': log['timestamp'],
                'line': line,
                'is_young': bool(ygc_pattern.search(line))
            })
    
    return gc_events

def generate_report(logs, gc_events):
    """生成 GC 分析报告"""
    if not logs:
        return "没有找到日志数据"
    
    report = []
    report.append("=" * 80)
    report.append("桐乡市卫生健康局健康云 - 病区护士站 GC 分析报告")
    report.append("=" * 80)
    report.append(f"\n分析时间范围：{logs[0]['timestamp']} 至 {logs[-1]['timestamp']}")
    report.append(f"总日志条数：{len(logs)}")
    report.append(f"GC 相关日志条数：{len(gc_events)}")
    
    if not gc_events:
        report.append("\n⚠️ 未找到 GC 相关日志")
        report.append("\n可能的原因：")
        report.append("1. GC 日志未输出到标准输出")
        report.append("2. GC 日志在单独的文件中")
        report.append("3. 日志格式不包含 'GC' 关键字")
        report.append("\n建议：")
        report.append("- 检查 JVM 启动参数是否包含 GC 日志配置")
        report.append("- 查看是否有单独的 GC 日志文件")
        return "\n".join(report)
    
    # 统计 Young GC
    young_gc_events = [e for e in gc_events if e['is_young']]
    report.append(f"\nYoung GC 事件数：{len(young_gc_events)}")
    
    # 计算 GC 频率
    if len(gc_events) > 1:
        time_span = (gc_events[-1]['timestamp'] - gc_events[0]['timestamp']).total_seconds()
        if time_span > 0:
            gc_frequency = len(gc_events) / (time_span / 3600)  # 每小时
            ygc_frequency = len(young_gc_events) / (time_span / 3600)
            report.append(f"GC 频率：{gc_frequency:.2f} 次/小时")
            report.append(f"Young GC 频率：{ygc_frequency:.2f} 次/小时")
    
    # 显示最近的 GC 事件
    report.append("\n" + "=" * 80)
    report.append("最近 20 条 GC 日志：")
    report.append("=" * 80)
    for event in gc_events[-20:]:
        report.append(f"\n[{event['timestamp']}]")
        report.append(event['line'][:500])  # 限制长度
    
    # 按小时统计 GC 频率
    report.append("\n" + "=" * 80)
    report.append("每小时 GC 频率统计：")
    report.append("=" * 80)
    hourly_gc = defaultdict(int)
    for event in gc_events:
        hour_key = event['timestamp'].strftime('%Y-%m-%d %H:00')
        hourly_gc[hour_key] += 1
    
    for hour in sorted(hourly_gc.keys()):
        report.append(f"{hour}: {hourly_gc[hour]} 次")
    
    return "\n".join(report)

def main():
    json_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_akso5_logs.json"
    output_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_gc_analysis.txt"
    
    print("正在解析日志...")
    logs = parse_loki_logs(json_file)
    print(f"解析完成，共 {len(logs)} 条日志")
    
    print("正在分析 GC 事件...")
    gc_events = analyze_gc_logs(logs)
    print(f"找到 {len(gc_events)} 条 GC 相关日志")
    
    print("正在生成报告...")
    report = generate_report(logs, gc_events)
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到：{output_file}")
    print("\n" + "=" * 80)
    print(report)

if __name__ == '__main__':
    main()

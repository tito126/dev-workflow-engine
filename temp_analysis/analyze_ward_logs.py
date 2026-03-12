#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 Loki 日志中的真实 JVM GC 信息
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

def analyze_real_gc_logs(logs):
    """分析真实的 JVM GC 日志"""
    gc_events = []
    
    # 真实的 GC 日志模式
    patterns = [
        re.compile(r'\[GC\s+\(', re.IGNORECASE),  # [GC (Allocation Failure)
        re.compile(r'\[Full\s+GC', re.IGNORECASE),  # [Full GC
        re.compile(r'Young\s+Generation', re.IGNORECASE),
        re.compile(r'Old\s+Generation', re.IGNORECASE),
        re.compile(r'PSYoungGen', re.IGNORECASE),
        re.compile(r'ParOldGen', re.IGNORECASE),
        re.compile(r'Metaspace', re.IGNORECASE),
        re.compile(r'GC\s+pause', re.IGNORECASE),
        re.compile(r'Allocation\s+Failure', re.IGNORECASE),
        re.compile(r'System\.gc\(\)', re.IGNORECASE),
    ]
    
    for log in logs:
        line = log['line']
        for pattern in patterns:
            if pattern.search(line):
                gc_events.append({
                    'timestamp': log['timestamp'],
                    'line': line
                })
                break
    
    return gc_events

def analyze_log_stats(logs):
    """分析日志统计信息"""
    if not logs:
        return {}
    
    # 按级别统计
    level_stats = defaultdict(int)
    error_logs = []
    warn_logs = []
    
    for log in logs:
        line = log['line']
        if ' ERROR ' in line or ' FATAL ' in line:
            level_stats['ERROR'] += 1
            error_logs.append(log)
        elif ' WARN ' in line:
            level_stats['WARN'] += 1
            warn_logs.append(log)
        elif ' INFO ' in line:
            level_stats['INFO'] += 1
    
    return {
        'level_stats': level_stats,
        'error_logs': error_logs[:20],  # 最近20条错误
        'warn_logs': warn_logs[:20]  # 最近20条警告
    }

def generate_report(logs, gc_events, stats):
    """生成分析报告"""
    if not logs:
        return "没有找到日志数据"
    
    report = []
    report.append("=" * 80)
    report.append("桐乡市卫生健康局健康云 - 病区护士站日志分析报告")
    report.append("服务：winning-winex-ward-akso5-pbc")
    report.append("=" * 80)
    report.append(f"\n分析时间范围：{logs[0]['timestamp']} 至 {logs[-1]['timestamp']}")
    
    time_span = (logs[-1]['timestamp'] - logs[0]['timestamp']).total_seconds()
    report.append(f"时间跨度：{time_span:.2f} 秒 ({time_span/3600:.2f} 小时)")
    report.append(f"总日志条数：{len(logs)}")
    
    # GC 分析
    report.append("\n" + "=" * 80)
    report.append("JVM GC 分析")
    report.append("=" * 80)
    
    if not gc_events:
        report.append("\n⚠️ 未找到标准的 JVM GC 日志")
        report.append("\n可能的原因：")
        report.append("1. JVM 启动参数未配置 GC 日志输出到 stdout")
        report.append("2. GC 日志在单独的文件中（如 gc.log）")
        report.append("3. 使用的 GC 日志格式不同")
        report.append("\n建议检查 JVM 启动参数：")
        report.append("  -Xlog:gc*:stdout:time,level,tags")
        report.append("  或旧版本：-XX:+PrintGCDetails -XX:+PrintGCDateStamps")
    else:
        report.append(f"\n找到 {len(gc_events)} 条 GC 日志")
        report.append("\n最近的 GC 事件：")
        for event in gc_events[-10:]:
            report.append(f"\n[{event['timestamp']}]")
            report.append(event['line'][:300])
    
    # 日志级别统计
    report.append("\n" + "=" * 80)
    report.append("日志级别统计")
    report.append("=" * 80)
    level_stats = stats.get('level_stats', {})
    for level, count in sorted(level_stats.items()):
        report.append(f"{level}: {count} 条")
    
    # 错误日志
    error_logs = stats.get('error_logs', [])
    if error_logs:
        report.append("\n" + "=" * 80)
        report.append(f"错误日志（最近 {len(error_logs)} 条）")
        report.append("=" * 80)
        for log in error_logs:
            report.append(f"\n[{log['timestamp']}]")
            report.append(log['line'][:500])
    
    # 警告日志
    warn_logs = stats.get('warn_logs', [])
    if warn_logs:
        report.append("\n" + "=" * 80)
        report.append(f"警告日志（最近 {len(warn_logs)} 条）")
        report.append("=" * 80)
        for log in warn_logs:
            report.append(f"\n[{log['timestamp']}]")
            report.append(log['line'][:500])
    
    # 建议
    report.append("\n" + "=" * 80)
    report.append("分析建议")
    report.append("=" * 80)
    report.append("\n关于 YGC 频率高的问题：")
    report.append("1. 当前日志中未找到标准的 GC 日志输出")
    report.append("2. 建议通过以下方式获取 GC 信息：")
    report.append("   - 检查 JVM 启动参数，确保 GC 日志输出到 stdout")
    report.append("   - 或者查看单独的 GC 日志文件")
    report.append("   - 使用 JMX/Prometheus 监控 GC 指标")
    report.append("3. 如果确实存在 YGC 频率高的问题，可能的原因：")
    report.append("   - 年轻代空间过小（-Xmn 参数）")
    report.append("   - 对象创建速率过快")
    report.append("   - 内存泄漏导致对象无法及时回收")
    
    return "\n".join(report)

def main():
    json_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_akso5_logs.json"
    output_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_analysis.txt"
    
    print("正在解析日志...")
    logs = parse_loki_logs(json_file)
    print(f"解析完成，共 {len(logs)} 条日志")
    
    print("正在分析 GC 事件...")
    gc_events = analyze_real_gc_logs(logs)
    print(f"找到 {len(gc_events)} 条真实 GC 日志")
    
    print("正在统计日志信息...")
    stats = analyze_log_stats(logs)
    
    print("正在生成报告...")
    report = generate_report(logs, gc_events, stats)
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到：{output_file}")
    print("\n" + report)

if __name__ == '__main__':
    main()

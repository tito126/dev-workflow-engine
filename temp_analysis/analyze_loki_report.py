#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析已下载的 Loki 日志
"""
import json
from datetime import datetime
from collections import defaultdict

def analyze_loki_json(json_file):
    """分析 Loki JSON 文件"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_logs = []
    if data.get('status') == 'success':
        for stream in data.get('data', {}).get('result', []):
            for value in stream.get('values', []):
                timestamp_ns = int(value[0])
                log_line = value[1]
                timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
                all_logs.append({
                    'timestamp': timestamp,
                    'line': log_line
                })
    
    all_logs.sort(key=lambda x: x['timestamp'])
    return all_logs

def analyze_logs(all_logs):
    """分析日志"""
    error_logs = []
    warn_logs = []
    slow_requests = []
    hourly_stats = defaultdict(lambda: {'total': 0, 'error': 0, 'warn': 0})
    
    for log in all_logs:
        line = log['line']
        hour_key = log['timestamp'].strftime('%Y-%m-%d %H:00')
        hourly_stats[hour_key]['total'] += 1
        
        if ' ERROR ' in line or ' FATAL ' in line:
            error_logs.append(log)
            hourly_stats[hour_key]['error'] += 1
        elif ' WARN ' in line:
            warn_logs.append(log)
            hourly_stats[hour_key]['warn'] += 1
        
        # 检测慢接口
        if '业务处理耗时:' in line:
            try:
                parts = line.split('业务处理耗时:')
                if len(parts) > 1:
                    time_str = parts[1].split('毫秒')[0]
                    time_ms = int(time_str)
                    if time_ms >= 1000:
                        slow_requests.append({
                            'timestamp': log['timestamp'],
                            'time_ms': time_ms,
                            'line': line
                        })
            except:
                pass
    
    return {
        'all_logs': all_logs,
        'error_logs': error_logs,
        'warn_logs': warn_logs,
        'slow_requests': slow_requests,
        'hourly_stats': hourly_stats
    }

def generate_report(analysis, app_name):
    """生成报告"""
    report_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_report.txt"
    
    all_logs = analysis['all_logs']
    error_logs = analysis['error_logs']
    warn_logs = analysis['warn_logs']
    slow_requests = analysis['slow_requests']
    hourly_stats = analysis['hourly_stats']
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("桐乡市卫生健康局健康云 - 病区护士站日志分析报告\n")
        f.write(f"服务：{app_name}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"日志时间范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}\n")
        time_span = (all_logs[-1]['timestamp'] - all_logs[0]['timestamp']).total_seconds() / 3600
        f.write(f"时间跨度：{time_span:.2f} 小时\n")
        f.write(f"总日志条数：{len(all_logs)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("日志级别统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"INFO: {len(all_logs) - len(error_logs) - len(warn_logs)} 条\n")
        f.write(f"WARN: {len(warn_logs)} 条 ({len(warn_logs)/len(all_logs)*100:.2f}%)\n")
        f.write(f"ERROR: {len(error_logs)} 条 ({len(error_logs)/len(all_logs)*100:.2f}%)\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("每小时日志统计\n")
        f.write("=" * 80 + "\n")
        for hour in sorted(hourly_stats.keys()):
            stats = hourly_stats[hour]
            f.write(f"{hour}: 总计 {stats['total']} 条 (ERROR: {stats['error']}, WARN: {stats['warn']})\n")
        
        if slow_requests:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"慢接口统计（>=1秒，共 {len(slow_requests)} 个）\n")
            f.write("=" * 80 + "\n")
            
            slow_requests.sort(key=lambda x: x['time_ms'], reverse=True)
            
            f.write("\nTop 20 最慢接口：\n")
            for i, req in enumerate(slow_requests[:20], 1):
                f.write(f"\n{i}. [{req['timestamp']}] 耗时：{req['time_ms']}ms\n")
                # 提取接口路径
                if '/api/' in req['line']:
                    try:
                        api_start = req['line'].find('/api/')
                        api_end = req['line'].find('毫秒', api_start)
                        if api_end > api_start:
                            api_path = req['line'][api_start:api_end].split(':')[-1].strip()
                            f.write(f"   接口：{api_path}\n")
                    except:
                        pass
        
        if error_logs:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"错误日志（共 {len(error_logs)} 条，显示最近 10 条）\n")
            f.write("=" * 80 + "\n")
            for log in error_logs[-10:]:
                f.write(f"\n[{log['timestamp']}]\n")
                f.write(log['line'][:500] + "\n")
        
        if warn_logs:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"警告日志（共 {len(warn_logs)} 条，显示最近 10 条）\n")
            f.write("=" * 80 + "\n")
            for log in warn_logs[-10:]:
                f.write(f"\n[{log['timestamp']}]\n")
                f.write(log['line'][:500] + "\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("分析建议\n")
        f.write("=" * 80 + "\n")
        f.write("\n关于 YGC 频率高的问题：\n")
        f.write("1. 当前应用日志中未找到标准的 JVM GC 日志输出\n")
        f.write("2. 建议通过以下方式获取 GC 信息：\n")
        f.write("   - 在 Grafana 中查看 JVM 监控面板（内存、GC 次数、GC 耗时）\n")
        f.write("   - 检查 Prometheus 中的 jvm_gc_pause_seconds_count 等指标\n")
        f.write("   - 或配置 JVM 参数输出 GC 日志：-Xlog:gc*:stdout:time,level,tags\n")
        f.write("\n3. 从当前日志分析：\n")
        if slow_requests:
            f.write(f"   - 存在 {len(slow_requests)} 个慢接口（>=1秒），最慢 {slow_requests[0]['time_ms']}ms\n")
            f.write("   - 慢接口可能导致线程阻塞，间接影响内存使用和 GC 频率\n")
            f.write("   - 建议优化慢接口的数据库查询和业务逻辑\n")
        if error_logs:
            f.write(f"   - 存在 {len(error_logs)} 条错误日志，需要排查具体原因\n")
        if len(warn_logs) > len(all_logs) * 0.1:
            f.write(f"   - 警告日志占比较高（{len(warn_logs)/len(all_logs)*100:.1f}%），建议关注\n")
        
        f.write("\n4. 如果 YGC 频率确实很高，可能的原因和解决方案：\n")
        f.write("   - 年轻代空间过小：增大 -Xmn 参数\n")
        f.write("   - 对象创建速率过快：优化代码，减少临时对象创建\n")
        f.write("   - Eden 区存活对象过多：检查是否有对象被意外引用\n")
        f.write("   - 考虑调整 GC 算法（如使用 G1GC）\n")
    
    return report_file

def main():
    json_file = r"C:\Users\pc\.openclaw\workspace\test_loki.json"
    app_name = "winning-winex-ward-akso5-pbc"
    
    print("=" * 80)
    print("桐乡市卫生健康局健康云 - 病区护士站日志分析")
    print(f"服务：{app_name}")
    print("=" * 80)
    
    print("\n[1/3] 正在解析日志...")
    all_logs = analyze_loki_json(json_file)
    print(f"OK - 共 {len(all_logs)} 条日志")
    
    if not all_logs:
        print("没有日志数据")
        return
    
    print(f"时间范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}")
    
    print("\n[2/3] 正在分析日志...")
    analysis = analyze_logs(all_logs)
    print(f"OK")
    print(f"  - ERROR: {len(analysis['error_logs'])} 条")
    print(f"  - WARN: {len(analysis['warn_logs'])} 条")
    print(f"  - 慢接口: {len(analysis['slow_requests'])} 个")
    
    print("\n[3/3] 正在生成报告...")
    report_file = generate_report(analysis, app_name)
    print(f"OK - {report_file}")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()

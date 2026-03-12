#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 8:00-10:00 时间段的日志
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
    minute_stats = defaultdict(int)
    
    for log in all_logs:
        line = log['line']
        hour_key = log['timestamp'].strftime('%Y-%m-%d %H:00')
        minute_key = log['timestamp'].strftime('%Y-%m-%d %H:%M')
        hourly_stats[hour_key]['total'] += 1
        minute_stats[minute_key] += 1
        
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
                    if time_ms >= 500:  # 降低阈值到500ms
                        # 提取接口路径
                        api_path = "未知"
                        if '/api/' in line:
                            try:
                                api_start = line.find('/api/')
                                api_end = line.find('毫秒', api_start)
                                if api_end > api_start:
                                    api_path = line[api_start:api_end].split(':')[-1].strip()
                            except:
                                pass
                        
                        slow_requests.append({
                            'timestamp': log['timestamp'],
                            'time_ms': time_ms,
                            'api_path': api_path,
                            'line': line
                        })
            except:
                pass
    
    return {
        'all_logs': all_logs,
        'error_logs': error_logs,
        'warn_logs': warn_logs,
        'slow_requests': slow_requests,
        'hourly_stats': hourly_stats,
        'minute_stats': minute_stats
    }

def generate_report(analysis, time_range):
    """生成报告"""
    report_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_8-10_report.txt"
    
    all_logs = analysis['all_logs']
    error_logs = analysis['error_logs']
    warn_logs = analysis['warn_logs']
    slow_requests = analysis['slow_requests']
    hourly_stats = analysis['hourly_stats']
    minute_stats = analysis['minute_stats']
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("桐乡市卫生健康局健康云 - 病区护士站日志分析报告\n")
        f.write("服务：winning-winex-ward-akso5-pbc\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"查询时间范围：{time_range}\n")
        f.write(f"实际日志范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}\n")
        time_span = (all_logs[-1]['timestamp'] - all_logs[0]['timestamp']).total_seconds() / 3600
        f.write(f"时间跨度：{time_span:.2f} 小时\n")
        f.write(f"总日志条数：{len(all_logs)}\n")
        f.write(f"平均日志速率：{len(all_logs)/time_span:.0f} 条/小时\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("日志级别统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"INFO: {len(all_logs) - len(error_logs) - len(warn_logs)} 条 ({(len(all_logs) - len(error_logs) - len(warn_logs))/len(all_logs)*100:.1f}%)\n")
        f.write(f"WARN: {len(warn_logs)} 条 ({len(warn_logs)/len(all_logs)*100:.1f}%)\n")
        f.write(f"ERROR: {len(error_logs)} 条 ({len(error_logs)/len(all_logs)*100:.1f}%)\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("每小时日志统计\n")
        f.write("=" * 80 + "\n")
        for hour in sorted(hourly_stats.keys()):
            stats = hourly_stats[hour]
            f.write(f"{hour}: 总计 {stats['total']} 条 (ERROR: {stats['error']}, WARN: {stats['warn']})\n")
        
        # 找出日志量最高的分钟
        f.write("\n" + "=" * 80 + "\n")
        f.write("日志量最高的10个分钟\n")
        f.write("=" * 80 + "\n")
        sorted_minutes = sorted(minute_stats.items(), key=lambda x: x[1], reverse=True)
        for minute, count in sorted_minutes[:10]:
            f.write(f"{minute}: {count} 条\n")
        
        if slow_requests:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"慢接口统计（>=500ms，共 {len(slow_requests)} 个）\n")
            f.write("=" * 80 + "\n")
            
            # 按接口路径分组统计
            api_stats = defaultdict(lambda: {'count': 0, 'max_time': 0, 'total_time': 0})
            for req in slow_requests:
                api = req['api_path']
                api_stats[api]['count'] += 1
                api_stats[api]['max_time'] = max(api_stats[api]['max_time'], req['time_ms'])
                api_stats[api]['total_time'] += req['time_ms']
            
            f.write("\n按接口统计（Top 10）：\n")
            sorted_apis = sorted(api_stats.items(), key=lambda x: x[1]['count'], reverse=True)
            for api, stats in sorted_apis[:10]:
                avg_time = stats['total_time'] / stats['count']
                f.write(f"\n{api}\n")
                f.write(f"  次数: {stats['count']}, 最慢: {stats['max_time']}ms, 平均: {avg_time:.0f}ms\n")
            
            # 最慢的请求
            slow_requests.sort(key=lambda x: x['time_ms'], reverse=True)
            f.write("\n" + "-" * 80 + "\n")
            f.write("Top 10 最慢请求：\n")
            for i, req in enumerate(slow_requests[:10], 1):
                f.write(f"\n{i}. [{req['timestamp']}] 耗时：{req['time_ms']}ms\n")
                f.write(f"   接口：{req['api_path']}\n")
        
        if error_logs:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"错误日志（共 {len(error_logs)} 条）\n")
            f.write("=" * 80 + "\n")
            
            # 错误分类
            error_types = defaultdict(list)
            for log in error_logs:
                # 简单分类
                if '404' in log['line']:
                    error_types['404 Not Found'].append(log)
                elif 'syntax error' in log['line']:
                    error_types['语法错误'].append(log)
                elif '未查询到' in log['line']:
                    error_types['数据未找到'].append(log)
                else:
                    error_types['其他错误'].append(log)
            
            f.write("\n错误分类：\n")
            for error_type, logs in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"  {error_type}: {len(logs)} 条\n")
            
            f.write("\n最近10条错误：\n")
            for log in error_logs[-10:]:
                f.write(f"\n[{log['timestamp']}]\n")
                f.write(log['line'][:500] + "\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("分析总结\n")
        f.write("=" * 80 + "\n")
        f.write("\n1. 日志量分析：\n")
        f.write(f"   - 2小时内共产生 {len(all_logs)} 条日志\n")
        f.write(f"   - 平均每小时 {len(all_logs)/time_span:.0f} 条\n")
        if len(all_logs) >= 5000:
            f.write(f"   - ⚠️ 注意：已达到 Loki 查询限制（5000条），实际日志可能更多\n")
        
        f.write("\n2. 性能分析：\n")
        if slow_requests:
            f.write(f"   - 存在 {len(slow_requests)} 个慢接口（>=500ms）\n")
            f.write(f"   - 最慢接口耗时：{slow_requests[0]['time_ms']}ms\n")
            # 找出最频繁的慢接口
            api_counts = defaultdict(int)
            for req in slow_requests:
                api_counts[req['api_path']] += 1
            most_frequent = max(api_counts.items(), key=lambda x: x[1])
            f.write(f"   - 最频繁的慢接口：{most_frequent[0]} ({most_frequent[1]}次)\n")
        else:
            f.write("   - 未发现明显的慢接口（>=500ms）\n")
        
        f.write("\n3. 错误分析：\n")
        if error_logs:
            f.write(f"   - 共 {len(error_logs)} 条错误日志\n")
            f.write(f"   - 错误率：{len(error_logs)/len(all_logs)*100:.2f}%\n")
        else:
            f.write("   - 未发现错误日志\n")
        
        f.write("\n4. 关于 YGC 频率高的问题：\n")
        f.write("   - 当前应用日志中未包含 JVM GC 日志\n")
        f.write("   - 建议查看 Grafana 的 JVM 监控面板获取 GC 指标\n")
        if slow_requests:
            f.write("   - 慢接口可能导致线程阻塞，间接影响内存和 GC\n")
            f.write("   - 建议优化慢接口，减少对象创建和内存占用\n")
    
    return report_file

def main():
    json_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_8-10.json"
    time_range = "2026-03-02 08:00 - 10:00 (GMT+8)"
    
    print("=" * 80)
    print("桐乡市卫生健康局健康云 - 病区护士站日志分析")
    print(f"时间段：{time_range}")
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
    print(f"  - 慢接口(>=500ms): {len(analysis['slow_requests'])} 个")
    
    print("\n[3/3] 正在生成报告...")
    report_file = generate_report(analysis, time_range)
    print(f"OK - {report_file}")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()

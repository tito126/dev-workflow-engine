#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分批查询桐乡 8:00-10:00 的 ERROR 和 WARN 日志
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict

def fetch_logs_chunked(grafana_url, datasource_id, app_name, start_time, end_time, chunk_minutes=30):
    """分批拉取 ERROR 和 WARN 日志"""
    all_logs = []
    current_start = start_time
    
    print(f"开始分批查询：{start_time} 至 {end_time}")
    print(f"每批时间跨度：{chunk_minutes} 分钟")
    print(f"过滤条件：ERROR|WARN")
    print("=" * 80)
    
    while current_start < end_time:
        current_end = min(current_start + timedelta(minutes=chunk_minutes), end_time)
        
        # 转换为纳秒时间戳
        start_ns = int(current_start.timestamp() * 1_000_000_000)
        end_ns = int(current_end.timestamp() * 1_000_000_000)
        
        # LogQL 查询：只拉取 ERROR 和 WARN
        query = f'{{app="{app_name}"}} |~ "ERROR|WARN"'
        encoded_query = urllib.parse.quote(query)
        
        url = (
            f"{grafana_url}/api/datasources/proxy/{datasource_id}"
            f"/loki/api/v1/query_range"
            f"?query={encoded_query}"
            f"&start={start_ns}"
            f"&end={end_ns}"
            f"&limit=5000"
        )
        
        print(f"查询：{current_start.strftime('%H:%M')} - {current_end.strftime('%H:%M')} ...", end=" ", flush=True)
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 'success':
                count = 0
                for stream in data.get('data', {}).get('result', []):
                    for value in stream.get('values', []):
                        timestamp_ns = int(value[0])
                        log_line = value[1]
                        timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
                        all_logs.append({
                            'timestamp': timestamp,
                            'line': log_line
                        })
                        count += 1
                print(f"OK - {count} 条")
            else:
                print(f"FAIL - {data}")
        except Exception as e:
            print(f"ERROR - {e}")
        
        current_start = current_end
    
    all_logs.sort(key=lambda x: x['timestamp'])
    return all_logs

def analyze_logs(all_logs):
    """分析日志"""
    error_logs = []
    warn_logs = []
    slow_requests = []
    hourly_stats = defaultdict(lambda: {'total': 0, 'error': 0, 'warn': 0})
    error_types = defaultdict(list)
    
    for log in all_logs:
        line = log['line']
        hour_key = log['timestamp'].strftime('%Y-%m-%d %H:00')
        hourly_stats[hour_key]['total'] += 1
        
        if ' ERROR ' in line or ' FATAL ' in line:
            error_logs.append(log)
            hourly_stats[hour_key]['error'] += 1
            
            # 错误分类
            if '404' in line or 'Not Found' in line:
                error_types['404 Not Found'].append(log)
            elif 'NullPointerException' in line:
                error_types['NullPointerException'].append(log)
            elif 'NumberFormatException' in line:
                error_types['NumberFormatException'].append(log)
            elif '标签算法' in line:
                error_types['标签算法服务失败'].append(log)
            elif 'syntax error' in line:
                error_types['语法错误'].append(log)
            else:
                error_types['其他错误'].append(log)
                
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
                        # 提取接口路径
                        api_path = "未知"
                        if '/api/' in line:
                            try:
                                api_start = line.find('/api/')
                                api_end = line.find('毫秒', api_start)
                                if api_end > api_start:
                                    api_part = line[api_start:api_end]
                                    # 提取最后一个冒号后的内容
                                    if ':' in api_part:
                                        api_path = api_part.split(':')[-1].strip()
                                    else:
                                        api_path = api_part
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
        'error_types': error_types
    }

def generate_report(analysis, time_range):
    """生成报告"""
    report_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_8-10_filtered_report.txt"
    
    all_logs = analysis['all_logs']
    error_logs = analysis['error_logs']
    warn_logs = analysis['warn_logs']
    slow_requests = analysis['slow_requests']
    hourly_stats = analysis['hourly_stats']
    error_types = analysis['error_types']
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("桐乡市卫生健康局健康云 - 病区护士站日志分析报告\n")
        f.write("服务：winning-winex-ward-akso5-pbc\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"查询时间范围：{time_range}\n")
        f.write(f"过滤条件：ERROR|WARN 级别\n")
        f.write(f"实际日志范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}\n")
        time_span = (all_logs[-1]['timestamp'] - all_logs[0]['timestamp']).total_seconds() / 3600
        f.write(f"时间跨度：{time_span:.2f} 小时\n")
        f.write(f"总日志条数（ERROR+WARN）：{len(all_logs)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("日志级别统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"ERROR: {len(error_logs)} 条 ({len(error_logs)/len(all_logs)*100:.1f}%)\n")
        f.write(f"WARN: {len(warn_logs)} 条 ({len(warn_logs)/len(all_logs)*100:.1f}%)\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("每小时统计\n")
        f.write("=" * 80 + "\n")
        for hour in sorted(hourly_stats.keys()):
            stats = hourly_stats[hour]
            f.write(f"{hour}: ERROR {stats['error']} 条, WARN {stats['warn']} 条, 合计 {stats['total']} 条\n")
        
        if error_logs:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"错误日志分析（共 {len(error_logs)} 条）\n")
            f.write("=" * 80 + "\n")
            
            f.write("\n错误分类：\n")
            for error_type, logs in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"  {error_type}: {len(logs)} 条\n")
            
            f.write("\n各类错误详情：\n")
            for error_type, logs in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"\n{'-' * 80}\n")
                f.write(f"{error_type}（{len(logs)} 条，显示前3条）：\n")
                for log in logs[:3]:
                    f.write(f"\n[{log['timestamp']}]\n")
                    f.write(log['line'][:400] + "\n")
        
        if slow_requests:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"慢接口统计（>=1秒，共 {len(slow_requests)} 个）\n")
            f.write("=" * 80 + "\n")
            
            # 按接口路径分组
            api_stats = defaultdict(lambda: {'count': 0, 'max_time': 0, 'total_time': 0})
            for req in slow_requests:
                api = req['api_path']
                api_stats[api]['count'] += 1
                api_stats[api]['max_time'] = max(api_stats[api]['max_time'], req['time_ms'])
                api_stats[api]['total_time'] += req['time_ms']
            
            f.write("\n按接口统计：\n")
            sorted_apis = sorted(api_stats.items(), key=lambda x: x[1]['count'], reverse=True)
            for api, stats in sorted_apis:
                avg_time = stats['total_time'] / stats['count']
                f.write(f"\n{api}\n")
                f.write(f"  次数: {stats['count']}, 最慢: {stats['max_time']}ms, 平均: {avg_time:.0f}ms\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("分析总结\n")
        f.write("=" * 80 + "\n")
        f.write(f"\n1. 在 {time_span:.1f} 小时内，共产生 {len(error_logs)} 条错误和 {len(warn_logs)} 条警告\n")
        f.write(f"2. 错误率：{len(error_logs)/(len(error_logs)+len(warn_logs))*100:.2f}%\n")
        if slow_requests:
            f.write(f"3. 存在 {len(slow_requests)} 个慢接口（>=1秒）\n")
        f.write("\n4. 关于 YGC 频率高的问题：\n")
        f.write("   - 当前日志中未包含 JVM GC 日志\n")
        f.write("   - 建议在 Grafana 查看 JVM 监控面板\n")
        if len(warn_logs) > 1000:
            f.write(f"   - 警告日志量较大（{len(warn_logs)} 条），可能产生大量临时对象\n")
        if slow_requests:
            f.write(f"   - 慢接口可能导致线程阻塞和内存占用\n")
    
    return report_file

def main():
    grafana_url = "http://127.0.0.1:16291"
    datasource_id = 1
    app_name = "winning-winex-ward-akso5-pbc"
    
    # 8:00-10:00
    start_time = datetime(2026, 3, 2, 8, 0, 0)
    end_time = datetime(2026, 3, 2, 10, 0, 0)
    time_range = "2026-03-02 08:00 - 10:00 (GMT+8)"
    
    print("=" * 80)
    print("桐乡市卫生健康局健康云 - 病区护士站日志分析")
    print(f"时间段：{time_range}")
    print("=" * 80)
    print()
    
    # 分批查询
    all_logs = fetch_logs_chunked(grafana_url, datasource_id, app_name, start_time, end_time, chunk_minutes=30)
    
    print()
    print(f"总计获取 {len(all_logs)} 条日志（ERROR+WARN）")
    
    if not all_logs:
        print("没有日志数据")
        return
    
    print(f"时间范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}")
    
    print("\n正在分析日志...")
    analysis = analyze_logs(all_logs)
    print(f"  - ERROR: {len(analysis['error_logs'])} 条")
    print(f"  - WARN: {len(analysis['warn_logs'])} 条")
    print(f"  - 慢接口(>=1秒): {len(analysis['slow_requests'])} 个")
    
    print("\n正在生成报告...")
    report_file = generate_report(analysis, time_range)
    print(f"报告已生成：{report_file}")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()

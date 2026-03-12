#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分批拉取 Loki 日志并生成报告
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict

def fetch_logs_chunked(grafana_url, datasource_id, app_name, start_time, end_time, chunk_hours=1):
    """分批拉取日志"""
    all_logs = []
    current_start = start_time
    
    while current_start < end_time:
        current_end = min(current_start + timedelta(hours=chunk_hours), end_time)
        
        start_str = current_start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_str = current_end.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        query = f'{{app="{app_name}"}}'
        encoded_query = urllib.parse.quote(query)
        
        url = (
            f"{grafana_url}/api/datasources/proxy/{datasource_id}"
            f"/loki/api/v1/query_range"
            f"?query={encoded_query}"
            f"&start={start_str}"
            f"&end={end_str}"
            f"&limit=5000"
        )
        
        print(f"拉取：{current_start.strftime('%H:%M')} - {current_end.strftime('%H:%M')} ...", end=" ")
        
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
                print(f"OK {count} tiao")
            else:
                print(f"FAIL")
        except Exception as e:
            print(f"ERROR: {e}")
        
        current_start = current_end
    
    all_logs.sort(key=lambda x: x['timestamp'])
    return all_logs

def analyze_logs(all_logs):
    """分析日志"""
    if not all_logs:
        return None
    
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

def generate_report(analysis, app_name, start_time, end_time):
    """生成报告"""
    report_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_6h_report.txt"
    
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
        f.write(f"查询时间范围：{start_time} 至 {end_time}\n")
        f.write(f"实际日志范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}\n")
        f.write(f"总日志条数：{len(all_logs)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("日志级别统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"INFO: {len(all_logs) - len(error_logs) - len(warn_logs)} 条\n")
        f.write(f"WARN: {len(warn_logs)} 条\n")
        f.write(f"ERROR: {len(error_logs)} 条\n\n")
        
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
            for req in slow_requests[:20]:
                f.write(f"\n[{req['timestamp']}] 耗时：{req['time_ms']}ms\n")
                # 提取接口路径
                if '/api/' in req['line']:
                    try:
                        api_part = req['line'].split('/api/')[1].split('毫秒')[0]
                        f.write(f"接口：/api/{api_part}\n")
                    except:
                        pass
                f.write(req['line'][:300] + "\n")
        
        if error_logs:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"错误日志（共 {len(error_logs)} 条，显示最近 20 条）\n")
            f.write("=" * 80 + "\n")
            for log in error_logs[-20:]:
                f.write(f"\n[{log['timestamp']}]\n")
                f.write(log['line'][:500] + "\n")
        
        if warn_logs:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"警告日志（共 {len(warn_logs)} 条，显示最近 20 条）\n")
            f.write("=" * 80 + "\n")
            for log in warn_logs[-20:]:
                f.write(f"\n[{log['timestamp']}]\n")
                f.write(log['line'][:500] + "\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("分析建议\n")
        f.write("=" * 80 + "\n")
        f.write("\n关于 YGC 频率高的问题：\n")
        f.write("1. 当前日志中未找到标准的 JVM GC 日志输出\n")
        f.write("2. 建议通过以下方式获取 GC 信息：\n")
        f.write("   - 在 Grafana 中查看 JVM 监控面板\n")
        f.write("   - 检查 Prometheus 中的 jvm_gc_* 指标\n")
        f.write("   - 或配置 JVM 参数输出 GC 日志到 stdout\n")
        f.write("\n3. 从当前日志分析：\n")
        if slow_requests:
            f.write(f"   - 存在 {len(slow_requests)} 个慢接口（>=1秒），最慢 {slow_requests[0]['time_ms']}ms\n")
            f.write("   - 慢接口可能导致线程阻塞，间接影响内存使用\n")
        if error_logs:
            f.write(f"   - 存在 {len(error_logs)} 条错误日志，需要排查\n")
        if len(warn_logs) > 1000:
            f.write(f"   - 警告日志较多（{len(warn_logs)} 条），建议关注\n")
    
    return report_file

def main():
    grafana_url = "http://127.0.0.1:16291"
    datasource_id = 1
    app_name = "winning-winex-ward-akso5-pbc"
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=6)
    
    print("=" * 80)
    print("桐乡市卫生健康局健康云 - 病区护士站日志分析")
    print(f"服务：{app_name}")
    print(f"时间：{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)
    
    print("\n[1/3] 正在拉取日志...")
    all_logs = fetch_logs_chunked(grafana_url, datasource_id, app_name, start_time, end_time, chunk_hours=1)
    print(f"\n✓ 共拉取 {len(all_logs)} 条日志")
    
    if not all_logs:
        print("没有日志数据")
        return
    
    print("\n[2/3] 正在分析日志...")
    analysis = analyze_logs(all_logs)
    print(f"✓ 分析完成")
    print(f"  - ERROR: {len(analysis['error_logs'])} 条")
    print(f"  - WARN: {len(analysis['warn_logs'])} 条")
    print(f"  - 慢接口: {len(analysis['slow_requests'])} 个")
    
    print("\n[3/3] 正在生成报告...")
    report_file = generate_report(analysis, app_name, start_time, end_time)
    print(f"✓ 报告已生成：{report_file}")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()

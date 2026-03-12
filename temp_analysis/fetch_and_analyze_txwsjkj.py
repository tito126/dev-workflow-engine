#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用 Python 拉取 Loki 日志并分析
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import sys

def fetch_and_analyze():
    grafana_url = "http://127.0.0.1:16291"
    datasource_id = 1
    app_name = "winning-winex-ward-akso5-pbc"
    
    # 时间范围：近6小时
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=6)
    
    start_ns = int(start_time.timestamp() * 1_000_000_000)
    end_ns = int(end_time.timestamp() * 1_000_000_000)
    
    query = f'{{app="{app_name}"}}'
    encoded_query = urllib.parse.quote(query)
    
    url = (
        f"{grafana_url}/api/datasources/proxy/{datasource_id}"
        f"/loki/api/v1/query_range"
        f"?query={encoded_query}"
        f"&start={start_ns}"
        f"&end={end_ns}"
        f"&limit=50000"
        f"&direction=forward"
    )
    
    print(f"正在拉取日志...")
    print(f"服务：{app_name}")
    print(f"时间：{start_time} 至 {end_time}")
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"拉取失败：{e}")
        return
    
    if data.get('status') != 'success':
        print(f"查询失败：{data}")
        return
    
    # 提取日志
    all_logs = []
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
    
    print(f"✓ 成功拉取 {len(all_logs)} 条日志")
    
    if not all_logs:
        print("没有日志数据")
        return
    
    # 统计分析
    print(f"\n时间范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}")
    
    error_logs = []
    warn_logs = []
    slow_requests = []
    
    for log in all_logs:
        line = log['line']
        if ' ERROR ' in line or ' FATAL ' in line:
            error_logs.append(log)
        elif ' WARN ' in line:
            warn_logs.append(log)
        
        # 检测慢接口（业务处理耗时）
        if '业务处理耗时:' in line:
            try:
                parts = line.split('业务处理耗时:')
                if len(parts) > 1:
                    time_str = parts[1].split('毫秒')[0]
                    time_ms = int(time_str)
                    if time_ms >= 1000:  # 1秒以上
                        slow_requests.append({
                            'timestamp': log['timestamp'],
                            'time_ms': time_ms,
                            'line': line
                        })
            except:
                pass
    
    print(f"\n日志级别统计：")
    print(f"  INFO: {len(all_logs) - len(error_logs) - len(warn_logs)} 条")
    print(f"  WARN: {len(warn_logs)} 条")
    print(f"  ERROR: {len(error_logs)} 条")
    print(f"\n慢接口（>=1秒）：{len(slow_requests)} 个")
    
    # 生成报告
    report_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_6h_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("桐乡市卫生健康局健康云 - 病区护士站日志分析报告\n")
        f.write(f"服务：{app_name}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"分析时间：{start_time} 至 {end_time}\n")
        f.write(f"实际日志范围：{all_logs[0]['timestamp']} 至 {all_logs[-1]['timestamp']}\n")
        f.write(f"总日志条数：{len(all_logs)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("日志级别统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"INFO: {len(all_logs) - len(error_logs) - len(warn_logs)} 条\n")
        f.write(f"WARN: {len(warn_logs)} 条\n")
        f.write(f"ERROR: {len(error_logs)} 条\n\n")
        
        if error_logs:
            f.write("=" * 80 + "\n")
            f.write(f"错误日志（共 {len(error_logs)} 条，显示最近 20 条）\n")
            f.write("=" * 80 + "\n")
            for log in error_logs[-20:]:
                f.write(f"\n[{log['timestamp']}]\n")
                f.write(log['line'][:500] + "\n")
        
        if slow_requests:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"慢接口统计（>=1秒，共 {len(slow_requests)} 个）\n")
            f.write("=" * 80 + "\n")
            
            # 按耗时排序
            slow_requests.sort(key=lambda x: x['time_ms'], reverse=True)
            
            f.write("\nTop 20 最慢接口：\n")
            for req in slow_requests[:20]:
                f.write(f"\n[{req['timestamp']}] 耗时：{req['time_ms']}ms\n")
                f.write(req['line'][:500] + "\n")
        
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
        f.write("   - 检查 JVM 启动参数，确保 GC 日志输出到 stdout\n")
        f.write("   - 或者查看单独的 GC 日志文件\n")
        f.write("   - 使用 Prometheus/Grafana 监控 JVM 指标\n")
        f.write("3. 从当前日志看，主要问题：\n")
        if slow_requests:
            f.write(f"   - 存在 {len(slow_requests)} 个慢接口（>=1秒）\n")
        if error_logs:
            f.write(f"   - 存在 {len(error_logs)} 条错误日志\n")
        if warn_logs:
            f.write(f"   - 存在 {len(warn_logs)} 条警告日志\n")
    
    print(f"\n✓ 报告已生成：{report_file}")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    fetch_and_analyze()

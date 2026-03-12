#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桐乡市卫生健康局健康云 - 病区护士站日志分析
"""
import sys
import os
import json
from datetime import datetime, timedelta

# 添加 skills/log-inspect 到路径
sys.path.insert(0, r'C:\Users\pc\.openclaw\workspace\skills\log-inspect')

from loki_fetcher import fetch_loki_logs
from preprocess import preprocess_logs, generate_html_report

def main():
    # 配置
    grafana_url = "http://127.0.0.1:16291"
    datasource_id = 1
    app_name = "winning-winex-ward-akso5-pbc"
    hospital_name = "桐乡市卫生健康局健康云"
    service_name = "病区护士站"
    
    # 时间范围：近6小时
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=6)
    
    print(f"=" * 80)
    print(f"开始分析：{hospital_name} - {service_name}")
    print(f"服务：{app_name}")
    print(f"时间范围：{start_time} 至 {end_time}")
    print(f"=" * 80)
    
    # 1. 拉取日志
    print("\n[1/3] 正在从 Loki 拉取日志...")
    log_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_6h.log"
    
    try:
        log_count = fetch_loki_logs(
            grafana_url=grafana_url,
            datasource_id=datasource_id,
            query=f'{{app="{app_name}"}}',
            start_time=start_time,
            end_time=end_time,
            output_file=log_file,
            limit=50000  # 限制最多5万条，避免过大
        )
        print(f"✓ 成功拉取 {log_count} 条日志")
    except Exception as e:
        print(f"✗ 拉取日志失败：{e}")
        return
    
    # 2. 预处理日志
    print("\n[2/3] 正在预处理日志...")
    digest_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_6h_digest.json"
    
    try:
        digest = preprocess_logs(
            log_file=log_file,
            output_file=digest_file,
            slow_threshold_ms=1000  # 慢接口阈值：1秒
        )
        print(f"✓ 预处理完成")
        print(f"  - ERROR: {digest['summary']['error_count']} 条")
        print(f"  - WARN: {digest['summary']['warn_count']} 条")
        print(f"  - 慢接口: {len(digest['slow_requests'])} 个")
    except Exception as e:
        print(f"✗ 预处理失败：{e}")
        return
    
    # 3. 生成报告
    print("\n[3/3] 正在生成 HTML 报告...")
    report_file = r"C:\Users\pc\.openclaw\workspace\txwsjkj_ward_6h_report.html"
    
    try:
        generate_html_report(
            digest_file=digest_file,
            output_file=report_file,
            hospital_name=hospital_name,
            service_name=service_name,
            time_range=f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}"
        )
        print(f"✓ 报告生成完成：{report_file}")
    except Exception as e:
        print(f"✗ 生成报告失败：{e}")
        return
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print(f"报告文件：{report_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()

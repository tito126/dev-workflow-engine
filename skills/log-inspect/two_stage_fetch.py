#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两阶段日志拉取脚本

第一阶段：拉取 ERROR | 业务处理耗时 日志
第二阶段：拉取代表 traces 的完整链路
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_command(cmd, description):
    """运行命令并实时输出"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"命令: {' '.join(cmd)}\n")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    duration = time.time() - start_time
    
    if result.returncode != 0:
        print(f"\n[失败] 耗时: {duration:.1f}秒")
        sys.exit(1)
    
    print(f"\n[成功] 耗时: {duration:.1f}秒")
    return duration


def main():
    parser = argparse.ArgumentParser(description='两阶段日志拉取')
    parser.add_argument('--grafana', '-g', required=True, help='Grafana URL')
    parser.add_argument('--datasource', '-d', type=int, default=2, help='数据源 ID')
    parser.add_argument('--app', '-a', required=True, help='应用名')
    parser.add_argument('--start', '-s', required=True, help='开始时间 (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end', '-e', required=True, help='结束时间 (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--output', '-o', default='logs.log', help='输出日志文件')
    parser.add_argument('--threshold', '-t', type=int, default=1000, help='慢接口阈值(ms)')
    parser.add_argument('--time-window', type=int, default=30, help='第二阶段时间窗口(秒)')
    parser.add_argument('--skip-stage2', action='store_true', help='跳过第二阶段')
    
    args = parser.parse_args()
    
    output_path = Path(args.output)
    digest_path = output_path.parent / (output_path.stem + '_digest.json')
    traces_path = output_path.parent / (output_path.stem + '_digest_traces.json')
    
    total_start = time.time()
    
    # 第一阶段：拉取 ERROR | 业务处理耗时 日志
    stage1_cmd = [
        'python', 'loki_fetcher.py',
        '--grafana', args.grafana,
        '--datasource', str(args.datasource),
        '--app', args.app,
        '--start', args.start,
        '--end', args.end,
        '--level', 'ERROR|业务处理耗时',
        '--output', str(output_path),
    ]
    
    stage1_duration = run_command(stage1_cmd, "第一阶段：拉取 ERROR | 业务处理耗时 日志")
    
    # 本地分析
    analyze_cmd = [
        'python', 'preprocess.py',
        str(output_path),
        '-t', str(args.threshold),
        '-o', str(digest_path),
        '--fetch-start', args.start,
        '--fetch-end', args.end,
        '--fetch-duration', str(int(stage1_duration)),
    ]
    
    run_command(analyze_cmd, "本地分析：生成 digest 和代表 traces 列表")
    
    # 检查 traces 文件
    if not traces_path.exists():
        print(f"\n❌ 未找到代表 traces 文件: {traces_path}")
        sys.exit(1)
    
    with open(traces_path, 'r', encoding='utf-8') as f:
        traces_data = json.load(f)
    
    trace_count = traces_data.get('count', 0)
    print(f"\n[代表 traces 统计]")
    print(f"   - 总数: {trace_count}")
    print(f"   - 异常类: {sum(1 for t in traces_data['traces'] if t['type'] == 'error')}")
    print(f"   - 慢接口: {sum(1 for t in traces_data['traces'] if t['type'] == 'slow_api')}")
    
    if args.skip_stage2:
        print("\n[跳过第二阶段] --skip-stage2")
        total_duration = time.time() - total_start
        print(f"\n[完成] 总耗时: {total_duration:.1f}秒")
        return
    
    if trace_count == 0:
        print("\n[警告] 没有代表 traces，跳过第二阶段")
        total_duration = time.time() - total_start
        print(f"\n[完成] 总耗时: {total_duration:.1f}秒")
        return
    
    # 第二阶段：拉取完整链路
    stage2_cmd = [
        'python', 'loki_fetcher.py',
        '--grafana', args.grafana,
        '--datasource', str(args.datasource),
        '--app', args.app,
        '--start', args.start,
        '--end', args.end,
        '--output', str(output_path),
        '--stage2-traces', str(traces_path),
        '--time-window', str(args.time_window),
    ]
    
    run_command(stage2_cmd, f"第二阶段：拉取 {trace_count} 个代表 traces 的完整链路")
    
    # 重新分析（包含完整链路）
    final_digest_path = output_path.parent / (output_path.stem + '_final_digest.json')
    final_analyze_cmd = [
        'python', 'preprocess.py',
        str(output_path),
        '-t', str(args.threshold),
        '-o', str(final_digest_path),
        '--fetch-start', args.start,
        '--fetch-end', args.end,
        '--fetch-duration', str(int(stage1_duration)),
    ]
    
    run_command(final_analyze_cmd, "最终分析：重新分析日志（包含完整链路）")
    
    total_duration = time.time() - total_start
    
    print(f"\n{'='*60}")
    print("[完成] 两阶段拉取完成!")
    print(f"{'='*60}")
    print(f"总耗时: {total_duration:.1f}秒")
    print(f"\n输出文件:")
    print(f"  - 日志: {output_path}")
    print(f"  - 第一阶段 digest: {digest_path}")
    print(f"  - 最终 digest: {final_digest_path}")
    print(f"  - 代表 traces: {traces_path}")


if __name__ == '__main__':
    main()

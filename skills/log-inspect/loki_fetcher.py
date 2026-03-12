#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loki 日志拉取模块 - 从 Grafana/Loki 拉取 K8s 环境日志
"""

import argparse
import json
import math
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def parse_time(time_str: str) -> datetime:
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间: {time_str}")


def datetime_to_ns(dt: datetime) -> int:
    return int(dt.timestamp() * 1_000_000_000)


def query_loki(grafana_url: str, datasource_id: int, query: str, start: datetime, end: datetime, limit: int = 5000) -> list:
    start_ns = datetime_to_ns(start)
    end_ns = datetime_to_ns(end)
    encoded_query = urllib.parse.quote(query)
    url = (
        f"{grafana_url}/api/datasources/proxy/{datasource_id}"
        f"/loki/api/v1/query_range"
        f"?query={encoded_query}"
        f"&start={start_ns}"
        f"&end={end_ns}"
        f"&limit={limit}"
        f"&direction=forward"
    )

    print(f"查询 Loki: {query}", flush=True)
    print(f"时间范围: {start} ~ {end}", flush=True)

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"查询失败: {e}", flush=True)
        return []

    if data.get('status') != 'success':
        print(f"查询返回错误: {data}", flush=True)
        return []

    lines = []
    for stream in data.get('data', {}).get('result', []):
        for value in stream.get('values', []):
            lines.append(value[1])

    print(f"获取到 {len(lines)} 条日志", flush=True)
    return lines


def query_loki_windowed(grafana_url: str, datasource_id: int, query: str, start: datetime, end: datetime, limit: int = 5000, window_seconds: int = 15) -> list:
    print(f"[窗口模式] 使用固定 {window_seconds} 秒时间片顺序拉取", flush=True)
    all_lines = []
    current = start
    window = timedelta(seconds=window_seconds)
    total_windows = max(1, math.ceil((end - start).total_seconds() / window_seconds))
    index = 0

    while current < end:
        index += 1
        current_end = min(current + window, end)
        print(
            f"[窗口 {index}/{total_windows}] {current.strftime('%H:%M:%S')}~{current_end.strftime('%H:%M:%S')}",
            flush=True,
        )
        lines = query_loki(grafana_url, datasource_id, query, current, current_end, limit)
        if len(lines) >= limit:
            print(
                f"[警告] 窗口 {current.strftime('%H:%M:%S')}~{current_end.strftime('%H:%M:%S')} 仍然达到 {limit} 条上限，可能还有截断",
                flush=True,
            )
        all_lines.extend(lines)
        current = current_end

    return all_lines


def query_loki_adaptive(grafana_url: str, datasource_id: int, query: str, start: datetime, end: datetime, limit: int = 5000, min_chunk_minutes: float = 1.0, depth: int = 0, saturation_count: int = 0, saturation_threshold: int = 4, fallback_window_seconds: int = 15) -> list:
    indent = '  ' * depth
    time_span = (end - start).total_seconds() / 60

    lines = query_loki(grafana_url, datasource_id, query, start, end, limit)

    if time_span <= min_chunk_minutes:
        if len(lines) >= limit:
            print(f"{indent}[警告] {start.strftime('%H:%M:%S')}~{end.strftime('%H:%M:%S')} 达到 {limit} 条限制，可能有截断", flush=True)
        return lines

    if len(lines) < limit:
        return lines

    next_saturation = saturation_count + 1
    if next_saturation >= saturation_threshold:
        print(
            f"{indent}[降级] 连续 {next_saturation} 次命中 {limit} 上限，切换为固定窗口拉取",
            flush=True,
        )
        return query_loki_windowed(
            grafana_url=grafana_url,
            datasource_id=datasource_id,
            query=query,
            start=start,
            end=end,
            limit=limit,
            window_seconds=fallback_window_seconds,
        )

    print(
        f"{indent}[分片] {start.strftime('%H:%M:%S')}~{end.strftime('%H:%M:%S')} 命中 {limit} 上限，继续二分",
        flush=True,
    )
    mid = start + (end - start) / 2
    left = query_loki_adaptive(grafana_url, datasource_id, query, start, mid, limit, min_chunk_minutes, depth + 1, next_saturation, saturation_threshold, fallback_window_seconds)
    right = query_loki_adaptive(grafana_url, datasource_id, query, mid, end, limit, min_chunk_minutes, depth + 1, next_saturation, saturation_threshold, fallback_window_seconds)
    return left + right


def build_query(app: Optional[str] = None, namespace: Optional[str] = None, pod: Optional[str] = None, level_filter: Optional[str] = None, trace_id: Optional[str] = None) -> str:
    labels = []
    if app:
        labels.append(f'app="{app}"')
    if namespace:
        labels.append(f'namespace="{namespace}"')
    if pod:
        labels.append(f'pod=~"{pod}.*"')
    if not labels:
        raise ValueError('至少需要指定一个 label (app/namespace/pod)')

    query = '{' + ', '.join(labels) + '}'
    if level_filter:
        query += f' |~ "{level_filter}"'
    if trace_id:
        query += f' |= "{trace_id}"'
    return query


def fetch_trace_full_context(grafana_url: str, datasource_id: int, app: str, trace_id: str, trace_time: datetime, time_window_seconds: int = 30, limit: int = 5000) -> list:
    """拉取指定 traceId 的完整链路日志
    
    Args:
        grafana_url: Grafana URL
        datasource_id: 数据源 ID
        app: 应用名
        trace_id: traceId
        trace_time: trace 的时间戳
        time_window_seconds: 时间窗口（秒），默认 ±30s
        limit: 单次查询限制
    
    Returns:
        完整链路日志列表
    """
    # 时间范围：trace_time ± time_window_seconds
    start = trace_time - timedelta(seconds=time_window_seconds)
    end = trace_time + timedelta(seconds=time_window_seconds)
    
    query = build_query(app=app, trace_id=trace_id)
    
    print(f"[完整链路] 拉取 trace {trace_id[:8]}... 时间窗口: {start.strftime('%H:%M:%S')}~{end.strftime('%H:%M:%S')}", flush=True)
    
    lines = query_loki(grafana_url, datasource_id, query, start, end, limit)
    
    return lines


def main():
    parser = argparse.ArgumentParser(description='从 Loki 拉取日志')
    parser.add_argument('--grafana', '-g', required=True)
    parser.add_argument('--datasource', '-d', type=int, default=1)
    parser.add_argument('--app', '-a')
    parser.add_argument('--namespace', '-n')
    parser.add_argument('--pod', '-p')
    parser.add_argument('--start', '-s', required=True)
    parser.add_argument('--end', '-e', required=True)
    parser.add_argument('--level', '-l', default='ERROR|业务处理耗时')
    parser.add_argument('--output', '-o', default='loki_logs.log')
    parser.add_argument('--limit', type=int, default=5000)
    parser.add_argument('--min-chunk', type=float, default=1.0)
    parser.add_argument('--with-context', action='store_true')
    parser.add_argument('--fallback-window-seconds', type=int, default=15)
    parser.add_argument('--saturation-threshold', type=int, default=4)
    parser.add_argument('--stage2-traces', help='第二阶段：拉取指定 traces 的完整链路（JSON 文件路径）')
    parser.add_argument('--time-window', type=int, default=30, help='第二阶段时间窗口（秒）')
    args = parser.parse_args()

    try:
        start_time = parse_time(args.start)
        end_time = parse_time(args.end)
    except ValueError as e:
        print(f"时间格式错误: {e}", flush=True)
        sys.exit(1)

    # 第二阶段：拉取完整链路
    if args.stage2_traces:
        print("=" * 60, flush=True)
        print("第二阶段：拉取代表 traces 的完整链路", flush=True)
        print("=" * 60, flush=True)
        
        with open(args.stage2_traces, 'r', encoding='utf-8') as f:
            traces_data = json.load(f)
        
        traces = traces_data.get('traces', [])
        print(f"需要拉取 {len(traces)} 个 trace 的完整链路", flush=True)
        
        all_full_lines = []
        for i, trace_info in enumerate(traces, 1):
            trace_id = trace_info['trace_id']
            trace_time_str = trace_info['timestamp']
            trace_time = datetime.strptime(trace_time_str, '%Y-%m-%d %H:%M:%S,%f')
            
            print(f"\n[{i}/{len(traces)}] trace: {trace_id[:8]}...", flush=True)
            
            lines = fetch_trace_full_context(
                grafana_url=args.grafana.rstrip('/'),
                datasource_id=args.datasource,
                app=args.app,
                trace_id=trace_id,
                trace_time=trace_time,
                time_window_seconds=args.time_window,
                limit=args.limit
            )
            
            all_full_lines.extend(lines)
        
        # 追加到原日志文件
        output_path = Path(args.output)
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write('\n# ========== 完整链路日志 ==========\n')
            for line in all_full_lines:
                f.write(line + '\n')
        
        print(f"\n完成! 共拉取 {len(all_full_lines)} 条完整链路日志，已追加到 {output_path}", flush=True)
        return

    # 第一阶段：拉取 ERROR | 业务处理耗时 日志
    try:
        query = build_query(
            app=args.app,
            namespace=args.namespace,
            pod=args.pod,
            level_filter=args.level if args.level else None,
        )
    except ValueError as e:
        print(f"查询参数错误: {e}", flush=True)
        sys.exit(1)

    print(f"LogQL: {query}", flush=True)
    print('查询模式: 自适应分片', flush=True)

    lines = query_loki_adaptive(
        grafana_url=args.grafana.rstrip('/'),
        datasource_id=args.datasource,
        query=query,
        start=start_time,
        end=end_time,
        limit=args.limit,
        min_chunk_minutes=args.min_chunk,
        saturation_threshold=args.saturation_threshold,
        fallback_window_seconds=args.fallback_window_seconds,
    )

    if not lines:
        print('未获取到任何日志', flush=True)
        sys.exit(0)

    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

    print(f"完成! 共 {len(lines)} 条日志，已保存到 {output_path}", flush=True)


if __name__ == '__main__':
    main()

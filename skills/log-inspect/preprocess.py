#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志预处理脚本 - 从大日志文件中提取关键信息供 AI 分析

支持功能:
- 多文件/目录输入
- 自动解压 .gz 文件
- 时间范围过滤
- 提取 ERROR/WARN/FATAL 日志
- 提取慢接口 (响应时间 > 阈值)
- 错误分类统计
- 输出结构化 JSON 摘要
"""

import argparse
import gzip
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from slow_interface_analyzer import analyze_slow_apis_with_context

# 日志行正则表达式
# 格式1 (普通服务器): [traceId,spanId,parentId] [,,] [IP:Port] [用户(userId)] 时间 [线程] 级别 类名 (文件:行) -- 内容
# 格式2 (K8s): [traceId,spanId,parentId] [IP:Port] [用户(userId)] 时间 [线程] 级别 类名 (文件:行) -- 内容
# 格式3 (工具组): [traceId,spanId,parentId] [,,] [IP:Port] [] [] 时间 [线程] 级别 类名 (文件:行) -- 内容
LOG_PATTERN = re.compile(
    r'\[([^]]*)\]\s*'  # traceId
    r'(?:\[([^]]*)\]\s*)?'  # [,,]
    r'\[([^]]*)\]\s*'  # IP:Port
    r'(?:\[([^]]*)\]\s*)?'  # field1
    r'(?:\[([^]]*)\]\s*)?'  # field2
    r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s*'  # timestamp
    r'\[([^\]]+)\]\s*'  # thread
    r'(\w+)\s+'  # level
    r'(\S+)\s*'  # class
    r'\([^)]*\)\s*'  # (file:line)
    r'--\s*'  # separator
    r'(.*)'  # content
)

# 慢接口正则: 业务处理耗时:XXX毫秒:/api/xxx 或 耗时:XXXms
SLOW_API_PATTERN = re.compile(r'[耗时:|耗时][:：]?\s*(\d+)\s*(?:毫秒|ms)[：:]?\s*(/\S+)?')

# 内部耗时日志正则: xxx耗时XXXms
INTERNAL_TIMING_PATTERN = re.compile(r'(.{0,50})耗时\s*(\d+)\s*(?:毫秒|ms)')

# 错误分类配置（中文化 + 细化）
ERROR_CATEGORIES = {
    'business_error': {
        'name': '业务逻辑错误',
        'keywords': [
            '批次冻结失败', '库存不足', '操作失败', '数据校验失败',
            '业务处理失败', '保存失败', '删除失败', '更新失败',
            'buildData失败', '消息处理事件', '冻结失败', '库存', '业务异常',
            '未查询到就诊记录', '在区查询下需传入科室ID或病区ID'
        ],
        'priority': 0,
        'suggestion': '检查业务逻辑、输入数据完整性及上下游业务约束'
    },
    'config_warning': {
        'name': '配置/兼容性问题',
        'keywords': ['标签算法', 'initForceContextData', 'initForce 方法已过时', '已过时', 'deprecated'],
        'priority': 1,
        'suggestion': '检查配置项、接口契约和版本兼容性；如对业务无影响可降级关注'
    },
    'null_pointer': {
        'name': '空指针异常',
        'keywords': ['NullPointerException', 'NPE', '空指针'],
        'priority': 2,
        'suggestion': '检查对象是否为空，添加空值校验'
    },
    'data_format_error': {
        'name': '数据格式错误',
        'keywords': ['NumberFormatException', 'For input string', 'syntax error', 'column 2<html>', 'BINARY'],
        'priority': 2,
        'suggestion': '检查入参格式、字段类型和下游返回内容是否符合预期'
    },
    'downstream_service_error': {
        'name': '下游服务异常',
        'keywords': ['404 Not Found', 'RPC调用错误', '<html>', '远程服务调用失败', 'FeignException'],
        'priority': 2,
        'suggestion': '检查下游服务状态、路由、网关和接口返回格式'
    },
    'auth_error': {
        'name': '认证/权限问题',
        'keywords': ['认证失败', '过期', 'token', 'Token', '权限不足', 'unauthorized', '未授权', '认证'],
        'priority': 3,
        'suggestion': '检查token是否过期，确认用户权限配置'
    },
    'sql_error': {
        'name': 'SQL错误',
        'keywords': ['ORA-', 'SQLException', 'SQL Error', '数据库错误', 'SQL语法'],
        'priority': 3,
        'suggestion': '检查SQL语句语法，确认数据库连接正常'
    },
    'timeout': {
        'name': '超时异常',
        'keywords': ['timeout', 'Timeout', '超时', 'timed out'],
        'priority': 4,
        'suggestion': '检查网络连接，增加超时时间或优化接口性能'
    },
    'connection_error': {
        'name': '连接异常',
        'keywords': ['Connection', '连接失败', 'refused', 'reset', '连接超时', '连接'],
        'priority': 4,
        'suggestion': '检查网络连接，确认目标服务是否正常'
    },
    'plugin_error': {
        'name': '插件配置问题',
        'keywords': ['找不到插件', 'plugin', '插件未找到', '事件管道'],
        'priority': 5,
        'suggestion': '检查插件配置文件，确认插件是否正确安装'
    },
    'validation_error': {
        'name': '参数校验失败',
        'keywords': ['参数错误', '校验失败', 'validation', 'Validation', '参数不能为空', '参数'],
        'priority': 5,
        'suggestion': '检查请求参数是否完整，确认参数格式正确'
    },
    'json_parse_error': {
        'name': 'JSON解析错误',
        'keywords': ['JSON', 'parse', '解析失败', 'JsonParseException'],
        'priority': 5,
        'suggestion': '检查JSON格式是否正确，确认数据结构'
    },
    'memory_error': {
        'name': '内存溢出',
        'keywords': ['OutOfMemory', 'OOM', '内存不足', 'heap space', '内存'],
        'priority': 2,
        'suggestion': '增加JVM内存配置，检查是否有内存泄漏'
    },
    'file_not_found': {
        'name': '文件不存在',
        'keywords': ['FileNotFoundException', '文件不存在', 'No such file'],
        'priority': 5,
        'suggestion': '检查文件路径是否正确，确认文件是否存在'
    },
    'unknown': {
        'name': '其他异常',
        'keywords': [],
        'priority': 99,
        'suggestion': '需要查看详细日志进行分析'
    }
}


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """解析日志时间戳"""
    try:
        return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S,%f')
    except ValueError:
        return None


def clean_error_reason(reason: str) -> Optional[str]:
    """清洗提取出的错误原因"""
    if not reason:
        return None

    reason = re.sub(r'\s+', ' ', reason).strip(' ,，。;；:：')
    if len(reason) < 6:
        return None

    return reason[:300]


def extract_error_reason(content: str) -> Optional[str]:
    """提取错误的真正原因"""
    patterns = [
        r'(批次冻结失败[^\n]*)',
        r'(执行Fhir消息处理事件\d+[^\n]*?buildData失败[^\n]*)',
        r'(标签算法[^\n]*)',
        r'原因[：:]\s*(.+?)(?:$|[,，。；;])',
        r'失败[：:]\s*(.+?)(?:$|[,，。；;])',
        r'错误[：:]\s*(.+?)(?:$|[,，。；;])',
        r'异常[：:]\s*(.+?)(?:$|[,，。；;])',
        r'message[：:]\s*(.+?)(?:$|[,，。；;])',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            reason = clean_error_reason(match.group(1))
            if reason:
                return reason

    fallback_patterns = [
        r'((?:库存不足|冻结失败|保存失败|删除失败|更新失败)[^\n]*)',
        r'((?:业务处理失败|数据校验失败|业务异常)[^\n]*)',
    ]
    for pattern in fallback_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            reason = clean_error_reason(match.group(1))
            if reason:
                return reason

    return clean_error_reason(content[:300])


def categorize_error(content: str, class_name: str = '') -> dict:
    """根据日志内容分类错误类型（改进版：提取真正原因）"""
    error_reason = extract_error_reason(content)
    content_lower = content.lower()
    class_lower = (class_name or '').lower()

    # 组件级归并：同一组件的配置类问题不要拆散
    if 'autotagalgorithmserviceimpl' in class_lower:
        category_info = ERROR_CATEGORIES['config_warning']
        return {
            'category': 'config_warning',
            'name': category_info['name'],
            'matched_keyword': 'AutoTagAlgorithmServiceImpl',
            'suggestion': category_info['suggestion'],
            'error_reason': error_reason or content[:200]
        }

    # 精细规则优先：让分类更贴近稳定性视角
    if '标签算法' in content_lower or 'initforce' in content_lower or '已过时' in content_lower:
        category_info = ERROR_CATEGORIES['config_warning']
        return {
            'category': 'config_warning',
            'name': category_info['name'],
            'matched_keyword': '标签算法' if '标签算法' in content else '兼容性/过时配置',
            'suggestion': category_info['suggestion'],
            'error_reason': error_reason or content[:200]
        }

    if 'numberformatexception' in content_lower or 'for input string' in content_lower:
        category_info = ERROR_CATEGORIES['data_format_error']
        return {
            'category': 'data_format_error',
            'name': category_info['name'],
            'matched_keyword': 'NumberFormatException',
            'suggestion': category_info['suggestion'],
            'error_reason': error_reason or content[:200]
        }

    if 'syntax error' in content_lower and '<html>' in content_lower:
        category_info = ERROR_CATEGORIES['config_warning'] if 'autotagalgorithmserviceimpl' in class_lower else ERROR_CATEGORIES['downstream_service_error']
        category_id = 'config_warning' if 'autotagalgorithmserviceimpl' in class_lower else 'downstream_service_error'
        return {
            'category': category_id,
            'name': category_info['name'],
            'matched_keyword': '返回HTML页面',
            'suggestion': category_info['suggestion'],
            'error_reason': error_reason or content[:200]
        }

    if '404 not found' in content_lower or 'rpc调用错误' in content_lower or '远程服务调用失败' in content_lower:
        category_info = ERROR_CATEGORIES['config_warning'] if 'autotagalgorithmserviceimpl' in class_lower else ERROR_CATEGORIES['downstream_service_error']
        category_id = 'config_warning' if 'autotagalgorithmserviceimpl' in class_lower else 'downstream_service_error'
        return {
            'category': category_id,
            'name': category_info['name'],
            'matched_keyword': '下游服务调用异常',
            'suggestion': category_info['suggestion'],
            'error_reason': error_reason or content[:200]
        }

    if '未查询到就诊记录' in content or '在区查询下需传入科室id或病区id' in content_lower:
        category_info = ERROR_CATEGORIES['business_error']
        return {
            'category': 'business_error',
            'name': category_info['name'],
            'matched_keyword': '业务数据缺失/参数约束',
            'suggestion': category_info['suggestion'],
            'error_reason': error_reason or content[:200]
        }

    sorted_categories = sorted(
        ERROR_CATEGORIES.items(),
        key=lambda x: x[1]['priority']
    )

    for category_id, category_info in sorted_categories:
        if category_id == 'unknown':
            continue

        for keyword in category_info['keywords']:
            if keyword.lower() in content_lower:
                return {
                    'category': category_id,
                    'name': category_info['name'],
                    'matched_keyword': keyword,
                    'suggestion': category_info['suggestion'],
                    'error_reason': error_reason or content[:200]
                }

    return {
        'category': 'unknown',
        'name': '其他异常',
        'matched_keyword': None,
        'suggestion': ERROR_CATEGORIES['unknown']['suggestion'],
        'error_reason': error_reason or content[:200],
        'content_preview': content[:100]
    }


def extract_user_info(user_field: str) -> Tuple[Optional[str], Optional[str]]:
    """从用户字段提取用户名和ID"""
    if not user_field:
        return None, None
    match = re.match(r'([^(]+)\((\d+)\)', user_field)
    if match:
        return match.group(1), match.group(2)
    return user_field, None


def parse_log_line(line: str) -> Optional[Dict]:
    """解析单行日志 - 支持多种格式"""
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    
    groups = match.groups()
    trace_info = groups[0]
    
    # 现在有10个捕获组: trace, [,,], ip, field1, field2, time, thread, level, class, content
    # 找到时间戳的位置（最可靠的标识）
    timestamp_idx = None
    for i, g in enumerate(groups):
        if g and re.match(r'\d{4}-\d{2}-\d{2}', g):
            timestamp_idx = i
            break
    
    if timestamp_idx is None:
        return None
    
    # 时间戳之后的字段是固定的: thread, level, class, content
    timestamp = groups[timestamp_idx]
    thread = groups[timestamp_idx + 1] if timestamp_idx + 1 < len(groups) else ''
    level = groups[timestamp_idx + 2] if timestamp_idx + 2 < len(groups) else ''
    class_name = groups[timestamp_idx + 3] if timestamp_idx + 3 < len(groups) else ''
    content = groups[timestamp_idx + 4] if timestamp_idx + 4 < len(groups) else ''
    
    # 时间戳之前的字段: trace, [,,], ip, field1, field2
    # 找到 IP:Port (包含冒号和数字)
    ip_port = None
    user_field = None
    for i in range(1, timestamp_idx):
        if groups[i] and ':' in groups[i] and any(c.isdigit() for c in groups[i]):
            ip_port = groups[i]
        elif groups[i] and groups[i] != ',,' and groups[i].strip():
            # 非空且不是 [,,] 的字段可能是用户信息
            if '(' in groups[i] and ')' in groups[i]:
                user_field = groups[i]
    
    # 解析 traceId
    trace_parts = trace_info.split(',')
    trace_id = trace_parts[0] if trace_parts else None
    
    # 解析用户信息
    user_name, user_id = extract_user_info(user_field)
    
    # 解析时间戳
    ts = parse_timestamp(timestamp)
    
    return {
        'trace_id': trace_id,
        'ip_port': ip_port,
        'user_name': user_name,
        'user_id': user_id,
        'timestamp': ts,
        'timestamp_str': timestamp,
        'thread': thread,
        'level': level.upper() if level else '',
        'class_name': class_name,
        'content': content,
        'raw': line.strip()
    }



def is_in_time_range(ts: Optional[datetime], start: Optional[datetime], end: Optional[datetime]) -> bool:
    """检查时间是否在范围内"""
    if ts is None:
        return True  # 无法解析时间的行默认包含
    if start and ts < start:
        return False
    if end and ts > end:
        return False
    return True


def extract_slow_api(content: str) -> Optional[Dict]:
    """提取慢接口信息"""
    match = SLOW_API_PATTERN.search(content)
    if match:
        duration = int(match.group(1))
        api_path = match.group(2) if match.group(2) else 'unknown'
        return {'duration_ms': duration, 'api_path': api_path}
    return None


def extract_internal_timing(content: str) -> Optional[Dict]:
    """提取内部耗时信息"""
    match = INTERNAL_TIMING_PATTERN.search(content)
    if match:
        context = match.group(1).strip()
        duration = int(match.group(2))
        return {'context': context, 'duration_ms': duration}
    return None


def open_log_file(file_path: Path, encoding: str = 'utf-8'):
    """打开日志文件，支持 .gz 压缩"""
    if file_path.suffix == '.gz':
        return gzip.open(file_path, 'rt', encoding=encoding, errors='replace')
    else:
        return open(file_path, 'r', encoding=encoding, errors='replace')


def process_file(
    file_path: Path,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    slow_threshold_ms: int,
    encoding: str,
    stats: Dict
) -> None:
    """处理单个日志文件"""
    print(f"处理文件: {file_path}")
    
    line_count = 0
    error_lines = []
    warn_lines = []
    slow_apis = []
    internal_timings = []
    
    # 用于 traceId 去重
    seen_error_traces = set()
    
    try:
        with open_log_file(file_path, encoding) as f:
            for line in f:
                line_count += 1
                
                # 解析日志行
                parsed = parse_log_line(line)
                if not parsed:
                    continue
                
                # 时间范围过滤
                if not is_in_time_range(parsed['timestamp'], start_time, end_time):
                    continue
                
                level = parsed['level']
                content = parsed['content']
                trace_id = parsed['trace_id']
                
                # 提取 ERROR/WARN
                if level in ('ERROR', 'FATAL'):
                    # 按 traceId 去重统计
                    if trace_id and trace_id not in seen_error_traces:
                        seen_error_traces.add(trace_id)
                        
                        category_info = categorize_error(content, parsed['class_name'])
                        stats['error_categories'][category_info['name']] += 1
                        stats['error_count'] += 1
                        
                        if len(error_lines) < 500:  # 限制样本数量
                            error_lines.append({
                                'timestamp': parsed['timestamp_str'],
                                'class': parsed['class_name'],
                                'user': parsed['user_name'],
                                'content': content[:500],  # 截断过长内容
                                'category': category_info['name'],
                                'category_id': category_info['category'],
                                'matched_keyword': category_info.get('matched_keyword'),
                                'suggestion': category_info['suggestion'],
                                'trace_id': trace_id,
                                'content_preview': category_info.get('content_preview')
                            })
                    elif not trace_id:
                        # 没有 traceId 的错误也要统计（但可能重复）
                        category_info = categorize_error(content, parsed['class_name'])
                        stats['error_categories'][category_info['name']] += 1
                        stats['error_count'] += 1
                        
                        if len(error_lines) < 500:
                            error_lines.append({
                                'timestamp': parsed['timestamp_str'],
                                'class': parsed['class_name'],
                                'user': parsed['user_name'],
                                'content': content[:500],
                                'category': category_info['name'],
                                'category_id': category_info['category'],
                                'matched_keyword': category_info.get('matched_keyword'),
                                'suggestion': category_info['suggestion'],
                                'trace_id': None,
                                'content_preview': category_info.get('content_preview')
                            })
                
                elif level == 'WARN':
                    stats['warn_count'] += 1
                    # 检查是否是慢接口日志
                    slow_api = extract_slow_api(content)
                    if slow_api and slow_api['duration_ms'] >= slow_threshold_ms:
                        slow_api['timestamp'] = parsed['timestamp_str']
                        slow_api['user'] = parsed['user_name']
                        slow_api['trace_id'] = trace_id
                        slow_apis.append(slow_api)
                    elif len(warn_lines) < 200:
                        warn_lines.append({
                            'timestamp': parsed['timestamp_str'],
                            'class': parsed['class_name'],
                            'content': content[:300],
                        })
                
                # 提取内部耗时（INFO 级别也可能有）
                if '耗时' in content:
                    timing = extract_internal_timing(content)
                    if timing and timing['duration_ms'] >= slow_threshold_ms:
                        timing['timestamp'] = parsed['timestamp_str']
                        timing['trace_id'] = trace_id
                        internal_timings.append(timing)
    
    except Exception as e:
        print(f"处理文件 {file_path} 出错: {e}")
        return
    
    stats['total_lines'] += line_count
    stats['error_samples'].extend(error_lines)
    stats['warn_samples'].extend(warn_lines)
    stats['slow_apis'].extend(slow_apis)
    stats['internal_timings'].extend(internal_timings)
    stats['files_processed'].append(str(file_path))


def aggregate_feedback_items(feedback_items: List[Dict]) -> List[Dict]:
    """按同类问题归总日志反哺项"""
    grouped = {}
    for item in feedback_items:
        key = item.get('group_key') or f"{item.get('name')}|{item.get('class')}"
        if key not in grouped:
            grouped[key] = {
                'name': item.get('name'),
                'class': item.get('class'),
                'count': 0,
                'suggestion': item.get('suggestion'),
                'samples': []
            }
        grouped[key]['count'] += 1
        if len(grouped[key]['samples']) < 5:
            grouped[key]['samples'].append({
                'timestamp': item.get('timestamp'),
                'trace_id': item.get('trace_id'),
                'content': item.get('content'),
                'user': item.get('user')
            })

    return sorted(grouped.values(), key=lambda x: x['count'], reverse=True)


def aggregate_slow_apis(slow_apis: List[Dict]) -> List[Dict]:
    """聚合慢接口统计"""
    api_stats = defaultdict(lambda: {'count': 0, 'max_ms': 0, 'total_ms': 0, 'users': set(), 'samples': []})
    
    for api in slow_apis:
        path = api['api_path']
        duration = api['duration_ms']
        api_stats[path]['count'] += 1
        api_stats[path]['total_ms'] += duration
        api_stats[path]['max_ms'] = max(api_stats[path]['max_ms'], duration)
        if api.get('user'):
            api_stats[path]['users'].add(api['user'])
        if len(api_stats[path]['samples']) < 3:
            api_stats[path]['samples'].append(api)
    
    result = []
    for path, stat in sorted(api_stats.items(), key=lambda x: x[1]['max_ms'], reverse=True):
        result.append({
            'api_path': path,
            'count': stat['count'],
            'max_ms': stat['max_ms'],
            'avg_ms': stat['total_ms'] // stat['count'] if stat['count'] > 0 else 0,
            'users': list(stat['users'])[:5],  # 最多显示5个用户
            'samples': stat['samples']
        })
    
    return result[:50]  # 最多返回50个慢接口


def aggregate_errors(error_samples: List[Dict]) -> List[Dict]:
    """聚合错误统计，按内容相似度分组"""
    # 按类名+错误类型分组
    error_groups = defaultdict(lambda: {
        'count': 0, 
        'samples': [], 
        'users': set(),
        'suggestion': '',
        'matched_keywords': set()
    })
    
    for err in error_samples:
        key = f"{err['category']}:{err['class']}"
        error_groups[key]['count'] += 1
        error_groups[key]['category'] = err['category']
        error_groups[key]['class'] = err['class']
        error_groups[key]['suggestion'] = err.get('suggestion', '')
        
        if err.get('matched_keyword'):
            error_groups[key]['matched_keywords'].add(err['matched_keyword'])
        
        if err.get('user'):
            error_groups[key]['users'].add(err['user'])
        
        if len(error_groups[key]['samples']) < 3:
            error_groups[key]['samples'].append(err)
    
    result = []
    for key, group in sorted(error_groups.items(), key=lambda x: x[1]['count'], reverse=True):
        result.append({
            'category': group['category'],
            'class': group['class'],
            'count': group['count'],
            'users': list(group['users'])[:5],
            'samples': group['samples'],
            'suggestion': group['suggestion'],
            'matched_keywords': list(group['matched_keywords'])
        })
    
    return result[:30]  # 最多返回30种错误


def find_log_files(input_path: str) -> List[Path]:
    """查找所有日志文件"""
    path = Path(input_path)
    files = []
    
    if path.is_file():
        files.append(path)
    elif path.is_dir():
        # 查找 .log, .log.*, .gz 文件
        for pattern in ['*.log', '*.log.*', '*.gz']:
            files.extend(path.glob(pattern))
    else:
        # 可能是 glob 模式
        files.extend(Path('.').glob(input_path))
    
    return sorted(files)


def extract_error_trace_ids(
    files: List[Path],
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    encoding: str
) -> set:
    """
    第一遍扫描：提取所有 ERROR/WARN 的 traceId
    
    Args:
        files: 日志文件列表
        start_time: 开始时间
        end_time: 结束时间
        encoding: 文件编码
    
    Returns:
        包含 ERROR/WARN 的 traceId 集合
    """
    print("[阶段 1/2] 扫描 ERROR/WARN 日志，提取 traceId...")
    
    error_trace_ids = set()
    total_errors = 0
    
    for file_path in files:
        try:
            with open_log_file(file_path, encoding) as f:
                for line in f:
                    parsed = parse_log_line(line)
                    if not parsed:
                        continue
                    
                    # 时间范围过滤
                    if not is_in_time_range(parsed['timestamp'], start_time, end_time):
                        continue
                    
                    level = parsed['level']
                    trace_id = parsed['trace_id']
                    
                    # 只关注 ERROR/WARN
                    if level in ('ERROR', 'FATAL', 'WARN') and trace_id:
                        error_trace_ids.add(trace_id)
                        total_errors += 1
        
        except Exception as e:
            print(f"  [警告] 扫描文件 {file_path} 出错: {e}")
            continue
    
    print(f"[阶段 1/2] 完成！发现 {total_errors} 条 ERROR/WARN，涉及 {len(error_trace_ids)} 个 traceId")
    return error_trace_ids


def should_feedback_not_error(parsed: Dict, content: str) -> Optional[Dict]:
    """识别应进入日志反哺、而不是异常统计的场景"""
    class_name = parsed.get('class_name', '') or ''
    trace_id = parsed.get('trace_id')
    user_name = parsed.get('user_name')

    if class_name.endswith('ParamMdmSdkHelper') and content.strip().lower() == 'null':
        return {
            'type': 'null_response_feedback',
            'name': '对象直接返回null',
            'group_key': f'{class_name}|null',
            'class': class_name,
            'trace_id': trace_id,
            'user': user_name,
            'timestamp': parsed.get('timestamp_str'),
            'content': content[:200],
            'suggestion': '建议增加上下文日志（入参、对象类型、查询条件、数据源返回状态），并评估改为 INFO/WARN 或显式空结果日志'
        }

    return None


def process_file_with_filter(
    file_path: Path,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    slow_threshold_ms: int,
    encoding: str,
    stats: Dict,
    filter_trace_ids: Optional[set] = None,
    skip_no_trace: bool = False
) -> None:
    """
    处理单个日志文件（支持 traceId 过滤）
    
    Args:
        filter_trace_ids: 如果提供，只处理这些 traceId 的日志
    """
    print(f"  处理文件: {file_path.name}")
    
    line_count = 0
    filtered_count = 0
    error_lines = []
    warn_lines = []
    slow_apis = []
    internal_timings = []
    
    # 用于 traceId 去重
    seen_error_traces = set()
    
    try:
        with open_log_file(file_path, encoding) as f:
            for line in f:
                line_count += 1
                
                # 解析日志行
                parsed = parse_log_line(line)
                if not parsed:
                    continue
                
                # 时间范围过滤
                if not is_in_time_range(parsed['timestamp'], start_time, end_time):
                    continue
                
                trace_id = parsed['trace_id']
                
                # traceId 过滤（如果启用）
                if filter_trace_ids is not None:
                    if not trace_id or trace_id not in filter_trace_ids:
                        filtered_count += 1
                        continue
                
                level = parsed['level']
                content = parsed['content']
                
                # 提取 ERROR/WARN
                if level in ('ERROR', 'FATAL'):
                    feedback_info = should_feedback_not_error(parsed, content)
                    if feedback_info:
                        stats['feedback_categories'][feedback_info['name']] += 1
                        if len(stats['feedback_samples']) < 200:
                            stats['feedback_samples'].append(feedback_info)
                        continue

                    if skip_no_trace and not trace_id:
                        continue

                    # 按 traceId 去重统计
                    if trace_id and trace_id not in seen_error_traces:
                        seen_error_traces.add(trace_id)

                        category_info = categorize_error(content, parsed['class_name'])
                        stats['error_categories'][category_info['name']] += 1
                        stats['error_count'] += 1

                        if len(error_lines) < 500:
                            error_lines.append({
                                'timestamp': parsed['timestamp_str'],
                                'class': parsed['class_name'],
                                'user': parsed['user_name'],
                                'content': content[:500],
                                'category': category_info['name'],
                                'category_id': category_info['category'],
                                'matched_keyword': category_info.get('matched_keyword'),
                                'suggestion': category_info['suggestion'],
                                'trace_id': trace_id,
                                'error_reason': category_info.get('error_reason'),
                                'content_preview': category_info.get('content_preview')
                            })
                    elif not trace_id:
                        category_info = categorize_error(content, parsed['class_name'])
                        stats['error_categories'][category_info['name']] += 1
                        stats['error_count'] += 1

                        if len(error_lines) < 500:
                            error_lines.append({
                                'timestamp': parsed['timestamp_str'],
                                'class': parsed['class_name'],
                                'user': parsed['user_name'],
                                'content': content[:500],
                                'category': category_info['name'],
                                'category_id': category_info['category'],
                                'matched_keyword': category_info.get('matched_keyword'),
                                'suggestion': category_info['suggestion'],
                                'trace_id': None,
                                'error_reason': category_info.get('error_reason'),
                                'content_preview': category_info.get('content_preview')
                            })
                
                elif level == 'WARN':
                    stats['warn_count'] += 1
                    # 检查是否是慢接口日志
                    slow_api = extract_slow_api(content)
                    if slow_api and slow_api['duration_ms'] >= slow_threshold_ms:
                        slow_api['timestamp'] = parsed['timestamp_str']
                        slow_api['user'] = parsed['user_name']
                        slow_api['trace_id'] = trace_id
                        slow_apis.append(slow_api)
                    elif len(warn_lines) < 200:
                        warn_lines.append({
                            'timestamp': parsed['timestamp_str'],
                            'class': parsed['class_name'],
                            'content': content[:300],
                        })
                
                # 提取内部耗时（INFO 级别也可能有）
                if '耗时' in content:
                    timing = extract_internal_timing(content)
                    if timing and timing['duration_ms'] >= slow_threshold_ms:
                        timing['timestamp'] = parsed['timestamp_str']
                        timing['trace_id'] = trace_id
                        internal_timings.append(timing)
    
    except Exception as e:
        print(f"  [错误] 处理文件 {file_path} 出错: {e}")
        return
    
    stats['total_lines'] += line_count
    stats['error_samples'].extend(error_lines)
    stats['warn_samples'].extend(warn_lines)
    stats['slow_apis'].extend(slow_apis)
    stats['internal_timings'].extend(internal_timings)
    stats['files_processed'].append(str(file_path))
    
    if filter_trace_ids is not None:
        print(f"    扫描 {line_count:,} 行，过滤掉 {filtered_count:,} 行，保留 {line_count - filtered_count:,} 行")


def main():
    parser = argparse.ArgumentParser(description='日志预处理脚本')
    parser.add_argument('input', nargs='+', help='输入文件或目录')
    parser.add_argument('-s', '--start', help='开始时间 (YYYY-MM-DD HH:MM)')
    parser.add_argument('-e', '--end', help='结束时间 (YYYY-MM-DD HH:MM)')
    parser.add_argument('-t', '--threshold', type=int, default=1000, help='慢接口阈值(ms)，默认1000')
    parser.add_argument('-o', '--output', default='digest.json', help='输出文件路径')
    parser.add_argument('--encoding', default='utf-8', help='日志文件编码')
    parser.add_argument('--filter-by-error-trace', action='store_true',
                       help='只分析包含 ERROR/WARN 的 traceId（适用于全量日志）')
    parser.add_argument('--skip-no-trace', action='store_true',
                       help='跳过没有 traceId 的 ERROR/FATAL 日志，减少噪音干扰')
    
    args = parser.parse_args()
    
    # 解析时间范围
    start_time = None
    end_time = None
    if args.start:
        try:
            start_time = datetime.strptime(args.start, '%Y-%m-%d %H:%M')
        except ValueError:
            print(f"无效的开始时间格式: {args.start}")
            sys.exit(1)
    if args.end:
        try:
            end_time = datetime.strptime(args.end, '%Y-%m-%d %H:%M')
        except ValueError:
            print(f"无效的结束时间格式: {args.end}")
            sys.exit(1)
    
    # 查找所有日志文件
    all_files = []
    for input_path in args.input:
        all_files.extend(find_log_files(input_path))
    
    if not all_files:
        print("未找到任何日志文件")
        sys.exit(1)
    
    print(f"找到 {len(all_files)} 个日志文件")
    
    # 如果启用了 traceId 过滤，先提取 ERROR/WARN 的 traceId
    filter_trace_ids = None
    if args.filter_by_error_trace:
        print("\n[模式] 启用 traceId 过滤（只分析有问题的 traceId）")
        filter_trace_ids = extract_error_trace_ids(
            all_files, start_time, end_time, args.encoding
        )
        
        if not filter_trace_ids:
            print("\n[警告] 未发现任何 ERROR/WARN 日志，将分析所有日志")
            filter_trace_ids = None
        else:
            print(f"\n[阶段 2/2] 开始分析这 {len(filter_trace_ids)} 个 traceId 的完整日志...")
    else:
        print("\n[模式] 标准模式（分析所有日志）")
    
    # 初始化统计
    stats = {
        'total_lines': 0,
        'error_count': 0,
        'warn_count': 0,
        'error_categories': defaultdict(int),
        'error_samples': [],
        'warn_samples': [],
        'slow_apis': [],
        'internal_timings': [],
        'files_processed': [],
        'feedback_categories': defaultdict(int),
        'feedback_samples': [],
    }
    
    # 处理每个文件
    for file_path in all_files:
        process_file_with_filter(
            file_path, start_time, end_time, args.threshold,
            args.encoding, stats, filter_trace_ids, args.skip_no_trace
        )
    
    # 聚合结果
    aggregated_slow_apis = aggregate_slow_apis(stats['slow_apis'])

    trace_logs_map = defaultdict(list)
    if aggregated_slow_apis:
        slow_trace_ids = {
            sample.get('trace_id')
            for api in aggregated_slow_apis
            for sample in api.get('samples', [])
            if sample.get('trace_id')
        }

        if slow_trace_ids:
            for file_path_str in stats['files_processed']:
                file_path = Path(file_path_str)
                try:
                    with open_log_file(file_path, args.encoding) as f:
                        for line in f:
                            parsed = parse_log_line(line)
                            if not parsed:
                                continue
                            if not is_in_time_range(parsed['timestamp'], start_time, end_time):
                                continue
                            trace_id = parsed.get('trace_id')
                            if trace_id in slow_trace_ids:
                                trace_logs_map[trace_id].append(parsed['raw'])
                except Exception as e:
                    print(f"  [警告] 收集慢接口上下文失败 {file_path}: {e}")

    enhanced_slow_apis = analyze_slow_apis_with_context(aggregated_slow_apis, trace_logs_map)

    digest = {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'files_processed': stats['files_processed'],
            'time_range': {
                'start': args.start,
                'end': args.end
            },
            'slow_threshold_ms': args.threshold,
            'filter_mode': 'error_trace' if args.filter_by_error_trace else 'all',
            'filtered_trace_count': len(filter_trace_ids) if filter_trace_ids else 0,
            'skip_no_trace': args.skip_no_trace,
        },
        'summary': {
            'total_lines': stats['total_lines'],
            'error_count': stats['error_count'],
            'warn_count': stats['warn_count'],
            'error_categories': dict(stats['error_categories']),
            'feedback_count': len(stats['feedback_samples']),
            'feedback_categories': dict(stats['feedback_categories']),
        },
        'errors': aggregate_errors(stats['error_samples']),
        'feedback_items': aggregate_feedback_items(stats['feedback_samples']),
        'slow_apis': enhanced_slow_apis,
        'internal_timings': stats['internal_timings'][:50],  # 限制数量
        'warn_samples': stats['warn_samples'][:50],
    }
    
    # 输出结果
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成!")
    print(f"- 总行数: {stats['total_lines']:,}")
    print(f"- ERROR: {stats['error_count']:,}")
    print(f"- WARN: {stats['warn_count']:,}")
    print(f"- 慢接口: {len(stats['slow_apis']):,}")
    if args.filter_by_error_trace and filter_trace_ids:
        print(f"- 过滤模式: 只分析了 {len(filter_trace_ids)} 个有问题的 traceId")
    print(f"- 输出: {output_path}")


if __name__ == '__main__':
    main()

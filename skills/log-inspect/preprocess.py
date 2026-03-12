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

MAX_TRACE_CONTEXT_LINES = 400
TRACE_CONTEXT_PADDING = 12

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
    'null_pointer': {
        'name': '空指针异常',
        'keywords': ['NullPointerException', 'null', 'NPE', '空指针'],
        'priority': 1,
        'suggestion': '检查对象是否为空，添加空值校验'
    },
    'auth_error': {
        'name': '认证/权限问题',
        'keywords': ['认证失败', '过期', 'token', 'Token', '权限不足', 'unauthorized', '未授权', '认证'],
        'priority': 1,
        'suggestion': '检查token是否过期，确认用户权限配置',
        'exclude_content': ['认证过期,请重新刷新']  # 排除这类简单提示
    },
    'tag_config_error': {
        'name': '标签配置问题',
        'keywords': ['AutoTagAlgorithmServiceImpl', '标签', '没有获取到远程服务'],
        'priority': 0,  # 最高优先级，因为它是最具体的错误类型
        'suggestion': '检查标签配置，确认标签服务是否正常'
    },
    'third_party_error': {
        'name': '第三方调用异常',
        'keywords': ['winning-winex-finance', 'winning-winex-.*-aaio', '调用.*服务.*失败', '远程调用'],
        'priority': 2,
        'suggestion': '检查第三方服务状态，确认接口调用参数'
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
        'priority': 5,
        'suggestion': '检查网络连接，确认目标服务是否正常'
    },
    'plugin_error': {
        'name': '插件配置问题',
        'keywords': ['找不到插件', 'plugin', '插件未找到', '事件管道'],
        'priority': 6,
        'suggestion': '检查插件配置文件，确认插件是否正确安装'
    },
    'validation_error': {
        'name': '参数校验失败',
        'keywords': ['参数错误', '校验失败', 'validation', 'Validation', '参数不能为空', '参数', '需传入', 'WB\\d+'],
        'priority': 7,
        'suggestion': '检查请求参数是否完整，确认参数格式正确'
    },
    'json_parse_error': {
        'name': 'JSON解析错误',
        'keywords': ['JSON', 'parse', '解析失败', 'JsonParseException'],
        'priority': 8,
        'suggestion': '检查JSON格式是否正确，确认数据结构'
    },
    'date_format_error': {
        'name': '日期格式错误',
        'keywords': ['Unparseable date', '日期格式', 'DateTimeParseException', 'DateFormat'],
        'priority': 8,
        'suggestion': '检查日期格式是否正确，确认日期解析规则'
    },
    'business_logic_error': {
        'name': '业务逻辑错误',
        'keywords': ['查询.*错误', '业务.*失败', '摆药失败', 'encounterId', '费用.*错误'],
        'priority': 9,
        'suggestion': '检查业务数据完整性，确认业务规则配置'
    },
    'log_system_error': {
        'name': '日志系统异常',
        'keywords': ['业务日志.*失败', '日志.*异常', 'AksoLoggerAppender', '发送端.*失败'],
        'priority': 10,
        'suggestion': '检查日志系统配置，确认日志服务是否正常'
    },
    'memory_error': {
        'name': '内存溢出',
        'keywords': ['OutOfMemory', 'OOM', '内存不足', 'heap space', '内存'],
        'priority': 1,
        'suggestion': '增加JVM内存配置，检查是否有内存泄漏'
    },
    'file_not_found': {
        'name': '文件不存在',
        'keywords': ['FileNotFoundException', '文件不存在', 'No such file'],
        'priority': 3,
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


def extract_error_reason(content: str) -> str:
    """提取更友好的错误原因摘要"""
    text = ' '.join(str(content).split())
    if not text:
        return '未提取到明确错误信息'

    patterns = [
        r'real exception message:(.*)',
        r'nested exception is ([^\[]+)',
        r'(ORA-\d+:[^,;]+)',
        r'([A-Z]{2}\d{4,}:[^,;]+)',
        r'(WB\d+:[^,;]+)',  # 新增：业务错误码
        r'(Unparseable date:[^,;]+)',
        r'(查询.*错误[^,;]*)',  # 新增：业务查询错误
        r'(.*失败[^,;]{0,30})',  # 新增：各类失败信息
        r'(must not be empty[^,;]*)',
        r'(No such file[^,;]*)',
        r'(could not extract ResultSet[^,;]*)',
        r'(cannot be null[^,;]*)',
        r'(NullPointerException[^,;]*)',
        r'(没有获取到[^,;]*)',  # 新增：获取失败
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reason = match.group(1).strip(' :;-')
            if reason:
                return reason[:160]

    if '$core{' in text:
        core_match = re.search(r'\$core\{([^}]*)\}core\$', text)
        if core_match and core_match.group(1).strip():
            return core_match.group(1).strip()[:160]


    return text[:160]


def categorize_error(content: str) -> dict:
    """根据日志内容分类错误类型，并补充更友好的原因摘要"""
    text = str(content)
    content_lower = text.lower()
    error_reason = extract_error_reason(text)
    
    # 检查是否应该排除（如"认证过期,请重新刷新"）
    for category_id, category_info in ERROR_CATEGORIES.items():
        exclude_list = category_info.get('exclude_content', [])
        for exclude_text in exclude_list:
            if exclude_text in text:
                return None  # 返回None表示应该排除这条日志
    
    # 优先级匹配（按priority排序）
    sorted_categories = sorted(
        ERROR_CATEGORIES.items(),
        key=lambda x: x[1]['priority']
    )
    
    # 启发式规则（更精确的匹配）
    heuristics = [
        # 第三方调用异常（最高优先级，因为可能包含其他关键词）
        ('third_party_error', [r'winning-winex-finance', r'winning-winex-.*-aaio', r'winning-winex-.*-inp-aaio']),
        # 标签配置问题
        ('tag_config_error', [r'AutoTagAlgorithmServiceImpl', r'标签', r'没有获取到远程服务']),
        # 空指针（检查特定模式，如 encounterIdList is null）
        ('null_pointer', [r'encounterIdList\s+is\s+null', r'encounterId.*is\s+null', r'nullpointerexception', r'\bnull\b', r'cannot be null', r'空指针']),
        # SQL错误
        ('sql_error', [r'ora-\d+', r'sqlgrammar', r'resultset', r'invaliddataaccess', r'constraintviolation']),
        # 认证问题
        ('auth_error', [r'token', r'认证', r'未授权', r'unauthorized', r'权限', r'过期']),
        # 参数校验（优先级低于空指针，避免误判）
        ('validation_error', [r'must not be empty', r'must not be null', r'不能为空', r'参数', r'validation', r'校验']),
        # JSON解析
        ('json_parse_error', [r'unparseable', r'json', r'parse', r'日期格式', r'解析']),
        # 连接异常
        ('connection_error', [r'connection', r'refused', r'reset', r'connect']),
        # 超时
        ('timeout', [r'timeout', r'timed out', r'超时']),
        # 文件不存在
        ('file_not_found', [r'filenotfound', r'no such file', r'文件不存在'])
    ]

    for category_id, patterns in heuristics:
        if category_id not in ERROR_CATEGORIES:
            continue
        for pattern in patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                info = ERROR_CATEGORIES[category_id]
                return {
                    'category': category_id,
                    'name': info['name'],
                    'matched_keyword': pattern,
                    'suggestion': info['suggestion'],
                    'error_reason': error_reason
                }

    # 关键词匹配
    for category_id, category_info in sorted_categories:
        if category_id == 'unknown':
            continue

        for keyword in category_info['keywords']:
            if re.search(keyword, text, re.IGNORECASE):
                return {
                    'category': category_id,
                    'name': category_info['name'],
                    'matched_keyword': keyword,
                    'suggestion': category_info['suggestion'],
                    'error_reason': error_reason
                }

    return {
        'category': 'unknown',
        'name': '其他异常',
        'matched_keyword': None,
        'suggestion': ERROR_CATEGORIES['unknown']['suggestion'],
        'content_preview': text[:100],
        'error_reason': error_reason
    }


def extract_caller_service_from_thread(thread: str) -> str:
    """从线程名提取调用方服务
    
    识别规则：
    - winning-winex-xxx_Jetty-Worker → 跨服务调用（返回服务名）
    - Jetty-Worker_xxx → 本服务调用（返回 SELF）
    - exe-xxx, enc-xxx → 异步任务（返回 ASYNC）
    - rpc-exec-xxx → RPC调用（返回 RPC）
    """
    if not thread:
        return 'UNKNOWN'
    
    # 跨服务调用：winning-winex-xxx_Jetty-Worker
    match = re.match(r'(winning-winex-[^_]+)_Jetty-Worker', thread)
    if match:
        return match.group(1)
    
    # 本服务调用：Jetty-Worker_xxx
    if thread.startswith('Jetty-Worker'):
        return 'SELF'
    
    # 异步任务：exe-xxx, enc-xxx
    if thread.startswith('exe-') or thread.startswith('enc-'):
        return 'ASYNC'
    
    # RPC调用：rpc-exec-xxx
    if thread.startswith('rpc-exec-'):
        return 'RPC'
    
    return 'UNKNOWN'


def categorize_trace(trace_logs: list) -> dict:
    """基于整个trace的所有日志进行分类（包括ERROR和WARN）"""
    if not trace_logs:
        return None
    
    # 提取线程名和调用方服务（从第一条ERROR日志，如果没有ERROR则从第一条日志）
    thread = ''
    caller_service = 'UNKNOWN'
    for log in trace_logs:
        if log.get('level') == 'ERROR':
            thread = log.get('thread', '')
            caller_service = extract_caller_service_from_thread(thread)
            break
    if not thread and trace_logs:
        thread = trace_logs[0].get('thread', '')
        caller_service = extract_caller_service_from_thread(thread)
    
    # 合并所有原始日志行进行分析（包含线程名等完整信息）
    all_content = '\n'.join([log.get('raw_line', log.get('content', '')) for log in trace_logs])
    
    # 检查是否包含第三方服务调用（最高优先级）
    third_party_patterns = [
        r'winning-winex-finance',
        r'winning-winex-.*-aaio',
        r'winning-winex-.*-inp-aaio'
    ]
    
    for pattern in third_party_patterns:
        if re.search(pattern, all_content, re.IGNORECASE):
            return {
                'category': 'third_party_error',
                'name': '第三方调用异常',
                'matched_keyword': pattern,
                'suggestion': ERROR_CATEGORIES['third_party_error']['suggestion'],
                'error_reason': '调用链中包含第三方服务',
                'caller_service': caller_service,
                'thread': thread
            }
    
    # 收集所有ERROR日志的分类，按优先级选择
    error_categories = []
    for log in trace_logs:
        if log.get('level') == 'ERROR':
            cat = categorize_error(log.get('content', ''))
            if cat:
                # 同时记录这条ERROR的类名（根本原因类名）
                cat['root_class'] = log.get('class', '')
                error_categories.append(cat)
    
    # 如果有多个ERROR分类，按优先级选择（priority越小越优先）
    if error_categories:
        sorted_cats = sorted(error_categories, key=lambda x: ERROR_CATEGORIES.get(x['category'], {}).get('priority', 99))
        result = sorted_cats[0]
        result['caller_service'] = caller_service
        result['thread'] = thread
        return result
    
    # 如果没有ERROR，使用第一条日志的分类
    if trace_logs:
        result = categorize_error(trace_logs[0].get('content', ''))
        if result:
            result['caller_service'] = caller_service
            result['thread'] = thread
        return result
    
    return None


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
    
    # 收集所有trace的日志（用于基于trace的分类）
    trace_logs = defaultdict(list)
    
    # 读取代表trace列表（从文件第一行）
    representative_traces = set()
    try:
        with open_log_file(file_path, encoding) as f:
            first_line = f.readline().strip()
            if first_line.startswith('# REPRESENTATIVE_TRACES:'):
                trace_list_str = first_line.replace('# REPRESENTATIVE_TRACES:', '').strip()
                if trace_list_str:
                    representative_traces = set(trace_list_str.split(','))
                    print(f"[代表trace] 读取到 {len(representative_traces)} 个代表trace")
    except Exception as e:
        print(f"读取代表trace列表失败: {e}")
    
    # 保存到stats中，供aggregate_errors使用
    stats['representative_traces'] = representative_traces
    
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
                
                # 收集trace日志（包括ERROR和WARN，保存原始日志行）
                if trace_id and level in ('ERROR', 'FATAL', 'WARN'):
                    trace_logs[trace_id].append({
                        'level': level,
                        'content': content,
                        'timestamp': parsed['timestamp_str'],
                        'class': parsed['class_name'],
                        'user': parsed['user_name'],
                        'thread': parsed.get('thread', ''),
                        'raw_line': line.strip()  # 保存原始日志行
                    })
                
                # 提取 ERROR/WARN
                if level in ('ERROR', 'FATAL'):
                    # 按 traceId 去重统计
                    if trace_id and trace_id not in seen_error_traces:
                        seen_error_traces.add(trace_id)
                        
                        category_info = categorize_error(content)
                        if category_info is None:  # 排除的日志
                            continue
                        
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
                                'content_preview': category_info.get('content_preview'),
                                'error_reason': category_info.get('error_reason')
                            })
                    elif not trace_id:
                        # 没有 traceId 的错误也要统计（但可能重复）
                        category_info = categorize_error(content)
                        if category_info is None:  # 排除的日志
                            continue
                        
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
                                'content_preview': category_info.get('content_preview'),
                                'error_reason': category_info.get('error_reason')
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
    
    # 基于trace重新分类ERROR日志，并提取API入口
    print(f"[Trace分类] 收集到 {len(trace_logs)} 个trace，seen_error_traces有 {len(seen_error_traces)} 个")
    reclassified_count = 0
    
    for trace_id, logs in trace_logs.items():
        if trace_id not in seen_error_traces:
            continue
        
        # 按时间排序，取最后一条日志提取API入口
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
        api_entry = None
        
        if sorted_logs:
            last_log = sorted_logs[-1]
            # 从最后一条日志中提取API路径
            api_pattern = re.compile(r'(/api/[^\s,;)\]]+)')
            raw_line = last_log.get('raw_line', '')
            api_match = api_pattern.search(raw_line)
            if api_match:
                api_entry = api_match.group(1)
        
        # 对这个trace进行综合分类
        trace_category = categorize_trace(logs)
        if trace_category is None:
            continue
        
        # 更新error_lines中对应trace的分类和API入口
        for error_line in error_lines:
            if error_line.get('trace_id') == trace_id:
                old_category = error_line['category']
                new_category = trace_category['name']
                
                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                # 添加根本原因类名（用于分组）
                if trace_category.get('root_class'):
                    error_line['root_class'] = trace_category['root_class']
                
                # 添加调用方服务和线程信息
                if trace_category.get('caller_service'):
                    error_line['caller_service'] = trace_category['caller_service']
                if trace_category.get('thread'):
                    error_line['thread'] = trace_category['thread']
                
                if old_category != new_category:
                    # 更新分类
                    stats['error_categories'][old_category] -= 1
                    stats['error_categories'][new_category] += 1
                    
                    error_line['category'] = new_category
                    error_line['category_id'] = trace_category['category']
                    error_line['matched_keyword'] = trace_category.get('matched_keyword')
                    error_line['suggestion'] = trace_category['suggestion']
                    error_line['error_reason'] = trace_category.get('error_reason')
                    
                    reclassified_count += 1
                    print(f"[Trace分类] {trace_id[:16]}: {old_category} -> {new_category}")
    
    if reclassified_count > 0:
        print(f"[Trace分类] 重新分类了 {reclassified_count} 条ERROR日志")
    else:
        print(f"[Trace分类] 没有需要重新分类的日志")
    
    stats['total_lines'] += line_count
    stats['error_samples'].extend(error_lines)
    stats['warn_samples'].extend(warn_lines)
    stats['slow_apis'].extend(slow_apis)
    stats['internal_timings'].extend(internal_timings)
    stats['files_processed'].append(str(file_path))


def aggregate_slow_apis(slow_apis: List[Dict]) -> List[Dict]:
    """聚合慢接口统计，并保留代表 trace 信息"""
    api_stats = defaultdict(lambda: {
        'count': 0,
        'max_ms': 0,
        'total_ms': 0,
        'users': set(),
        'samples': [],
        'trace_ids': set(),
        'top_traces': []
    })
    
    for api in slow_apis:
        path = api['api_path']
        duration = api['duration_ms']
        stat = api_stats[path]
        stat['count'] += 1
        stat['total_ms'] += duration
        stat['max_ms'] = max(stat['max_ms'], duration)
        if api.get('user'):
            stat['users'].add(api['user'])
        if api.get('trace_id'):
            stat['trace_ids'].add(api['trace_id'])
        if len(stat['samples']) < 3:
            stat['samples'].append(api)

        candidate = {
            'trace_id': api.get('trace_id'),
            'duration_ms': duration,
            'timestamp': api.get('timestamp'),
            'user': api.get('user')
        }
        if candidate['trace_id']:
            existing = next((t for t in stat['top_traces'] if t.get('trace_id') == candidate['trace_id']), None)
            if existing:
                if duration > existing.get('duration_ms', 0):
                    existing.update(candidate)
            else:
                stat['top_traces'].append(candidate)
                stat['top_traces'].sort(key=lambda x: x.get('duration_ms', 0), reverse=True)
                if len(stat['top_traces']) > 5:
                    stat['top_traces'] = stat['top_traces'][:5]
    
    result = []
    for path, stat in sorted(api_stats.items(), key=lambda x: x[1]['max_ms'], reverse=True):
        result.append({
            'api_path': path,
            'count': stat['count'],
            'max_ms': stat['max_ms'],
            'avg_ms': stat['total_ms'] // stat['count'] if stat['count'] > 0 else 0,
            'users': list(stat['users'])[:5],
            'samples': stat['samples'],
            'trace_count': len(stat['trace_ids']),
            'top_traces': stat['top_traces']
        })
    
    return result[:50]


def aggregate_errors(error_samples: List[Dict], representative_traces: set = None) -> List[Dict]:
    """聚合错误统计，按四级分组键分组，按trace去重统计
    
    分组键：category:root_class:api_entry:caller_service
    """
    if representative_traces is None:
        representative_traces = set()
    
    # 按四级分组键分组
    error_groups = defaultdict(lambda: {
        'trace_ids': set(),  # 按trace去重统计
        'samples': [], 
        'users': set(),
        'suggestion': '',
        'matched_keywords': set(),
        'classes': set(),  # 记录涉及的所有类
        'api_entries': set(),  # 记录涉及的所有API入口
        'caller_services': set(),  # 记录涉及的所有调用方
        'threads': set()  # 记录涉及的所有线程
    })
    
    for err in error_samples:
        # 四级分组键：category:root_class:api_entry:caller_service
        root_class = err.get('root_class', err.get('class', 'N/A'))
        api_entry = err.get('api_entry', 'N/A')
        caller_service = err.get('caller_service', 'UNKNOWN')
        key = f"{err['category']}:{root_class}:{api_entry}:{caller_service}"
        
        # 按trace去重统计
        trace_id = err.get('trace_id')
        if trace_id:
            error_groups[key]['trace_ids'].add(trace_id)
        
        error_groups[key]['category'] = err['category']
        error_groups[key]['root_class'] = root_class
        error_groups[key]['api_entry'] = api_entry
        error_groups[key]['caller_service'] = caller_service
        error_groups[key]['suggestion'] = err.get('suggestion', '')
        
        # 记录涉及的类名
        if err.get('class'):
            error_groups[key]['classes'].add(err['class'])
        
        # 记录涉及的API入口
        if err.get('api_entry'):
            error_groups[key]['api_entries'].add(err['api_entry'])
        
        # 记录涉及的调用方
        if err.get('caller_service'):
            error_groups[key]['caller_services'].add(err['caller_service'])
        
        # 记录涉及的线程
        if err.get('thread'):
            error_groups[key]['threads'].add(err['thread'])
        
        if err.get('matched_keyword'):
            error_groups[key]['matched_keywords'].add(err['matched_keyword'])
        
        if err.get('user'):
            error_groups[key]['users'].add(err['user'])
        
        # 代表trace优先插入samples[0]
        if trace_id in representative_traces and len(error_groups[key]['samples']) == 0:
            error_groups[key]['samples'].insert(0, err)
        elif len(error_groups[key]['samples']) < 3:
            error_groups[key]['samples'].append(err)
    
    result = []
    for key, group in sorted(error_groups.items(), key=lambda x: len(x[1]['trace_ids']), reverse=True):
        # 使用root_class作为主要类名
        main_class = group['root_class']
        
        result.append({
            'category': group['category'],
            'class': main_class,  # 根本原因类名
            'root_class': group['root_class'],
            'api_entry': group['api_entry'],
            'caller_service': group['caller_service'],
            'classes': list(group['classes']),  # 所有涉及的类
            'api_entries': list(group['api_entries'])[:5],  # 涉及的API入口（最多5个）
            'caller_services': list(group['caller_services'])[:5],  # 涉及的调用方（最多5个）
            'threads': list(group['threads'])[:5],  # 涉及的线程（最多5个）
            'count': len(group['trace_ids']),  # 按trace数量统计
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


def process_file_with_filter(
    file_path: Path,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    slow_threshold_ms: int,
    encoding: str,
    stats: Dict,
    filter_trace_ids: Optional[set] = None
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
    
    # 收集所有trace的日志（用于基于trace的分类）
    trace_logs = defaultdict(list)
    
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
                
                # 收集trace日志（包括ERROR和WARN，保存原始日志行）
                if trace_id and level in ('ERROR', 'FATAL', 'WARN'):
                    trace_logs[trace_id].append({
                        'level': level,
                        'content': content,
                        'timestamp': parsed['timestamp_str'],
                        'class': parsed['class_name'],
                        'user': parsed['user_name'],
                        'thread': parsed.get('thread', ''),
                        'raw_line': line.strip()  # 保存原始日志行
                    })
                content = parsed['content']
                
                # 提取 ERROR/WARN
                if level in ('ERROR', 'FATAL'):
                    # 按 traceId 去重统计
                    if trace_id and trace_id not in seen_error_traces:
                        seen_error_traces.add(trace_id)
                        
                        category_info = categorize_error(content)
                        if category_info is None:  # 排除的日志
                            continue
                        
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
                                'content_preview': category_info.get('content_preview')
                            })
                    elif not trace_id:
                        # 没有 traceId 的错误也要统计
                        category_info = categorize_error(content)
                        if category_info is None:  # 排除的日志
                            continue
                        
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
                                'content_preview': category_info.get('content_preview'),
                                'error_reason': category_info.get('error_reason')
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
    
    # 基于trace重新分类ERROR日志，并提取API入口
    print(f"[Trace分类] 收集到 {len(trace_logs)} 个trace，seen_error_traces有 {len(seen_error_traces)} 个")
    reclassified_count = 0
    
    for trace_id, logs in trace_logs.items():
        if trace_id not in seen_error_traces:
            continue
        
        # 按时间排序，取最后一条日志提取API入口
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
        api_entry = None
        
        if sorted_logs:
            last_log = sorted_logs[-1]
            # 从最后一条日志中提取API路径
            api_pattern = re.compile(r'(/api/[^\s,;)\]]+)')
            raw_line = last_log.get('raw_line', '')
            api_match = api_pattern.search(raw_line)
            if api_match:
                api_entry = api_match.group(1)
        
        # 对这个trace进行综合分类
        trace_category = categorize_trace(logs)
        if trace_category is None:
            continue
        
        # 更新error_lines中对应trace的分类和API入口
        for error_line in error_lines:
            if error_line.get('trace_id') == trace_id:
                old_category = error_line['category']
                new_category = trace_category['name']
                
                # 添加API入口信息
                if api_entry:
                    error_line['api_entry'] = api_entry
                
                # 添加根本原因类名（用于分组）
                if trace_category.get('root_class'):
                    error_line['root_class'] = trace_category['root_class']
                
                # 添加调用方服务和线程信息
                if trace_category.get('caller_service'):
                    error_line['caller_service'] = trace_category['caller_service']
                if trace_category.get('thread'):
                    error_line['thread'] = trace_category['thread']
                
                if old_category != new_category:
                    # 更新分类
                    stats['error_categories'][old_category] -= 1
                    stats['error_categories'][new_category] += 1
                    
                    error_line['category'] = new_category
                    error_line['category_id'] = trace_category['category']
                    error_line['matched_keyword'] = trace_category.get('matched_keyword')
                    error_line['suggestion'] = trace_category['suggestion']
                    error_line['error_reason'] = trace_category.get('error_reason')
                    
                    reclassified_count += 1
                    print(f"[Trace分类] {trace_id[:16]}: {old_category} -> {new_category}")
    
    if reclassified_count > 0:
        print(f"[Trace分类] 重新分类了 {reclassified_count} 条ERROR日志")
    else:
        print(f"[Trace分类] 没有需要重新分类的日志")
    
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
    parser.add_argument('--fetch-start', type=str, default='', help='日志拉取开始时间')
    parser.add_argument('--fetch-end', type=str, default='', help='日志拉取结束时间')
    parser.add_argument('--fetch-duration', type=int, default=0, help='日志拉取耗时（秒）')
    
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
    }
    
    # 处理每个文件
    for file_path in all_files:
        process_file_with_filter(
            file_path, start_time, end_time, args.threshold, 
            args.encoding, stats, filter_trace_ids
        )
    
    slow_api_summary = aggregate_slow_apis(stats['slow_apis'])

    trace_logs = defaultdict(list)
    if slow_api_summary:
        top_slow_trace_ids = set()
        for api in slow_api_summary[:10]:
            for trace in api.get('top_traces', []):
                trace_id = trace.get('trace_id')
                if trace_id:
                    top_slow_trace_ids.add(trace_id)

        if top_slow_trace_ids:
            print(f"[慢接口补强] 为 {len(top_slow_trace_ids)} 个代表 trace 补充上下文...")
            for file_path in all_files:
                try:
                    pending_buffers = {trace_id: [] for trace_id in top_slow_trace_ids}
                    with open_log_file(file_path, args.encoding) as f:
                        for line in f:
                            parsed = parse_log_line(line)
                            if not parsed:
                                continue
                            if not is_in_time_range(parsed['timestamp'], start_time, end_time):
                                continue

                            clean_line = line.strip()
                            line_trace_id = parsed['trace_id']

                            for trace_id in list(pending_buffers.keys()):
                                if len(trace_logs[trace_id]) >= MAX_TRACE_CONTEXT_LINES:
                                    pending_buffers.pop(trace_id, None)
                                    continue

                                buffer_lines = pending_buffers[trace_id]
                                buffer_lines.append(clean_line)
                                if len(buffer_lines) > TRACE_CONTEXT_PADDING:
                                    buffer_lines.pop(0)

                            if line_trace_id and line_trace_id in top_slow_trace_ids:
                                existing = trace_logs[line_trace_id]
                                if not existing:
                                    existing.extend(pending_buffers.get(line_trace_id, [])[:-1])
                                if len(existing) < MAX_TRACE_CONTEXT_LINES:
                                    existing.append(clean_line)

                                pending_buffers[line_trace_id] = []

                    for trace_id in top_slow_trace_ids:
                        if trace_logs[trace_id]:
                            trace_logs[trace_id] = trace_logs[trace_id][:MAX_TRACE_CONTEXT_LINES]
                except Exception as e:
                    print(f"  [警告] 慢接口上下文补强读取文件 {file_path} 出错: {e}")

            if trace_logs:
                slow_api_summary = analyze_slow_apis_with_context(slow_api_summary, trace_logs)

    # 聚合错误（按trace去重）
    representative_traces = stats.get('representative_traces', set())
    
    # 统计原始 error_samples 的质量信息（用于日志质量分析）
    total_error_samples = len(stats['error_samples'])
    no_api_entry_count = sum(1 for e in stats['error_samples'] if not e.get('api_entry'))
    null_content_count = sum(1 for e in stats['error_samples'] if e.get('content', '').strip() == 'null')
    
    aggregated_errors = aggregate_errors(stats['error_samples'], representative_traces)
    
    # 根据聚合结果重新计算error_categories（按trace去重）
    error_categories_by_trace = defaultdict(int)
    for error_group in aggregated_errors:
        error_categories_by_trace[error_group['category']] += error_group['count']
    
    # 聚合结果
    digest = {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'files_processed': stats['files_processed'],
            'time_range': {
                'start': args.start,
                'end': args.end
            },
            'fetch_range': {
                'start': args.fetch_start if args.fetch_start else None,
                'end': args.fetch_end if args.fetch_end else None,
                'duration_s': args.fetch_duration if args.fetch_duration else None
            },
            'slow_threshold_ms': args.threshold,
            'filter_mode': 'error_trace' if args.filter_by_error_trace else 'all',
            'filtered_trace_count': len(filter_trace_ids) if filter_trace_ids else 0,
        },
        'summary': {
            'total_lines': stats['total_lines'],
            'error_count': stats['error_count'],
            'warn_count': stats['warn_count'],
            'error_categories': dict(error_categories_by_trace),  # 使用按trace去重的统计
            'error_samples_count': total_error_samples,  # 原始错误样本总数
            'no_api_entry_count': no_api_entry_count,  # 缺少API入口的数量
            'null_content_count': null_content_count,  # null内容的数量
        },
        'errors': aggregated_errors,
        'slow_apis': slow_api_summary,
        'internal_timings': stats['internal_timings'][:50],
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

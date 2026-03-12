#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
慢接口深度分析器 - 识别调用链中的瓶颈
"""
import re
from typing import Dict, List, Optional


class SlowInterfaceAnalyzer:
    """慢接口深度分析器"""
    
    def __init__(self):
        # 步骤识别规则
        self.step_patterns = {
            'database': {
                'keywords': ['执行SQL', 'query', 'select', 'insert', 'update', 'delete', 'SQL', '数据库'],
                'time_pattern': r'耗时[:\s]*(\d+)\s*(?:毫秒|ms)',
                'category': '数据库查询',
                'priority': 1,
                'suggestion': '检查SQL语句是否有优化空间，考虑添加索引或使用缓存'
            },
            'external_api': {
                'keywords': ['调用接口', 'http request', '远程调用', 'RPC', 'REST', 'API'],
                'time_pattern': r'耗时[:\s]*(\d+)\s*(?:毫秒|ms)',
                'category': '外部接口',
                'priority': 2,
                'suggestion': '检查网络延迟，考虑异步调用或添加超时控制'
            },
            'cache': {
                'keywords': ['redis', 'cache', 'memcached', '缓存'],
                'time_pattern': r'耗时[:\s]*(\d+)\s*(?:毫秒|ms)',
                'category': '缓存操作',
                'priority': 3,
                'suggestion': '检查缓存命中率，优化缓存策略'
            },
            'business': {
                'keywords': ['业务处理', '计算', '处理', 'process'],
                'time_pattern': r'耗时[:\s]*(\d+)\s*(?:毫秒|ms)',
                'category': '业务逻辑',
                'priority': 4,
                'suggestion': '优化业务逻辑，减少不必要的计算'
            },
            'io': {
                'keywords': ['读取文件', '写入文件', 'IO', '文件操作', 'file'],
                'time_pattern': r'耗时[:\s]*(\d+)\s*(?:毫秒|ms)',
                'category': '文件IO',
                'priority': 5,
                'suggestion': '优化文件读写，考虑使用缓冲或异步IO'
            },
            'serialization': {
                'keywords': ['序列化', 'JSON', 'XML', 'serialize', 'deserialize'],
                'time_pattern': r'耗时[:\s]*(\d+)\s*(?:毫秒|ms)',
                'category': '序列化/反序列化',
                'priority': 6,
                'suggestion': '优化序列化方式，考虑使用更高效的格式'
            }
        }
    
    def analyze_slow_trace(self, trace_logs: List[str], total_time: int) -> Dict:
        """
        分析单个慢接口的调用链
        
        Args:
            trace_logs: 该 traceId 的所有日志行
            total_time: 总耗时（毫秒）
        
        Returns:
            分析结果字典
        """
        steps = []
        recognized_time = 0
        
        # 识别每个步骤
        for log_line in trace_logs:
            for step_type, pattern in self.step_patterns.items():
                # 检查是否包含关键字
                if any(kw.lower() in log_line.lower() for kw in pattern['keywords']):
                    # 提取耗时
                    match = re.search(pattern['time_pattern'], log_line)
                    if match:
                        time_cost = int(match.group(1))
                        steps.append({
                            'type': step_type,
                            'category': pattern['category'],
                            'time': time_cost,
                            'log': log_line.strip()[:200],  # 截断过长的日志
                            'suggestion': pattern['suggestion']
                        })
                        recognized_time += time_cost
                        break  # 一行日志只匹配一个步骤
        
        # 按耗时排序
        steps.sort(key=lambda x: x['time'], reverse=True)
        
        # 找出瓶颈（耗时最长的步骤）
        bottleneck = steps[0] if steps else None
        
        # 计算未识别的时间
        unrecognized_time = max(0, total_time - recognized_time)
        unrecognized_ratio = (unrecognized_time / total_time * 100) if total_time > 0 else 0
        
        # 判断是否需要反馈
        needs_feedback = unrecognized_ratio > 30  # 超过 30% 未识别
        
        return {
            'total_time': total_time,
            'steps': steps,
            'bottleneck': bottleneck,
            'recognized_time': recognized_time,
            'unrecognized_time': unrecognized_time,
            'unrecognized_ratio': unrecognized_ratio,
            'needs_feedback': needs_feedback
        }
    
    def generate_optimization_suggestions(self, analysis: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if not analysis['steps']:
            suggestions.append("未能识别具体的耗时步骤，建议增加详细的性能日志")
            return suggestions
        
        # 基于瓶颈生成建议
        bottleneck = analysis['bottleneck']
        if bottleneck:
            suggestions.append(
                f"主要瓶颈：{bottleneck['category']}耗时 {bottleneck['time']}ms "
                f"({bottleneck['time']/analysis['total_time']*100:.1f}%)"
            )
            suggestions.append(f"建议：{bottleneck['suggestion']}")
        
        # 基于步骤类型统计生成建议
        step_stats = {}
        for step in analysis['steps']:
            category = step['category']
            if category not in step_stats:
                step_stats[category] = {'count': 0, 'total_time': 0}
            step_stats[category]['count'] += 1
            step_stats[category]['total_time'] += step['time']
        
        # 如果某类步骤占比过高
        for category, stats in sorted(step_stats.items(), key=lambda x: x[1]['total_time'], reverse=True):
            ratio = stats['total_time'] / analysis['total_time'] * 100
            if ratio > 40:
                suggestions.append(
                    f"{category}累计耗时 {stats['total_time']}ms ({ratio:.1f}%)，"
                    f"出现 {stats['count']} 次，建议重点优化"
                )
        
        # 如果未识别时间过多
        if analysis['needs_feedback']:
            suggestions.append(
                f"有 {analysis['unrecognized_time']}ms ({analysis['unrecognized_ratio']:.1f}%) "
                f"的耗时未能识别，建议查看完整日志或提供反馈帮助改进分析"
            )
        
        return suggestions
    
    def generate_feedback_prompt(self, trace_id: str, analysis: Dict) -> Optional[str]:
        """生成反馈提示"""
        if not analysis['needs_feedback']:
            return None
        
        prompt = f"""
【需要您的反馈】traceId: {trace_id}

总耗时: {analysis['total_time']}ms
已识别步骤耗时: {analysis['recognized_time']}ms
未识别耗时: {analysis['unrecognized_time']}ms ({analysis['unrecognized_ratio']:.1f}%)

请查看完整日志，告诉我们：
1. 未识别的时间主要花在哪里？
2. 是否有新的步骤类型需要添加？

反馈方式：在报告中点击"提交反馈"按钮
"""
        return prompt


def analyze_slow_apis_with_context(slow_apis: List[Dict], all_logs: Dict[str, List[str]]) -> List[Dict]:
    """分析慢接口（带上下文）"""
    analyzer = SlowInterfaceAnalyzer()
    enhanced_apis = []

    for api in slow_apis:
        top_traces = api.get('top_traces', [])
        selected_trace = None
        trace_logs = []
        total_time = api.get('max_ms', 0)

        for trace in top_traces:
            trace_id = trace.get('trace_id')
            if trace_id and trace_id in all_logs and all_logs[trace_id]:
                selected_trace = trace
                trace_logs = all_logs[trace_id]
                total_time = trace.get('duration_ms', total_time)
                break

        if not selected_trace:
            enhanced_apis.append(api)
            continue

        analysis = analyzer.analyze_slow_trace(trace_logs, total_time)
        suggestions = analyzer.generate_optimization_suggestions(analysis)
        feedback_prompt = analyzer.generate_feedback_prompt(selected_trace.get('trace_id'), analysis)

        enhanced_api = {
            **api,
            'representative_trace_id': selected_trace.get('trace_id'),
            'representative_trace_logs': trace_logs[:80],
            'analysis': analysis,
            'suggestions': suggestions,
            'feedback_prompt': feedback_prompt
        }

        enhanced_apis.append(enhanced_api)

    return enhanced_apis


if __name__ == '__main__':
    # 测试代码
    analyzer = SlowInterfaceAnalyzer()
    
    # 模拟日志
    test_logs = [
        "2026-03-09 16:00:00.100 [INFO] 接收请求 traceId=abc123",
        "2026-03-09 16:00:00.150 [INFO] 执行SQL查询 耗时: 1000ms",
        "2026-03-09 16:00:01.150 [INFO] 调用外部接口 耗时: 800ms",
        "2026-03-09 16:00:01.950 [INFO] 业务处理 耗时: 300ms",
        "2026-03-09 16:00:02.250 [INFO] 返回结果 总耗时: 2500ms"
    ]
    
    analysis = analyzer.analyze_slow_trace(test_logs, 2500)
    
    print("分析结果：")
    print(f"总耗时: {analysis['total_time']}ms")
    print(f"已识别: {analysis['recognized_time']}ms")
    print(f"未识别: {analysis['unrecognized_time']}ms ({analysis['unrecognized_ratio']:.1f}%)")
    print(f"\n步骤详情:")
    for step in analysis['steps']:
        print(f"  - {step['category']}: {step['time']}ms")
    
    if analysis['bottleneck']:
        print(f"\n瓶颈: {analysis['bottleneck']['category']} ({analysis['bottleneck']['time']}ms)")
    
    suggestions = analyzer.generate_optimization_suggestions(analysis)
    print(f"\n优化建议:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

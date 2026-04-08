import re

# 读取文件
with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\generate_html_report_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到插入点（在"详细异常分析"结束和"慢接口分析"开始之间）
insert_marker = '            </div>\n\n            <!-- 慢接口分析 -->'

# 准备要插入的代码
feedback_module = '''            </div>

            <!-- 日志反哺模块 -->
            <div class="section">
                <h2 class="section-title">📝 日志反哺建议</h2>
                <p style="margin-bottom: 20px; color: #666;">以下异常的日志内容不够明确，建议开发团队改进日志输出</p>
"""
    
    # 分析不明确的日志
    feedback_cases = []
    for error_group in errors:
        category = error_group['category']
        samples = error_group['samples']
        
        unclear_samples = []
        for sample in samples[:5]:
            content_text = sample.get('content', '')
            error_reason = sample.get('error_reason', '')
            trace_id = sample.get('trace_id')
            
            is_unclear = False
            reason = ""
            
            if content_text.strip() == 'null':
                is_unclear = True
                reason = "日志内容只有'null'，无法定位问题根因"
            elif error_reason == '未提取到明确错误信息':
                is_unclear = True
                reason = "无法提取明确的错误信息"
            elif len(content_text) < 20 and not re.search(r'[A-Z]{2}\\d{4,}', content_text):
                is_unclear = True
                reason = "日志内容过短，缺少上下文信息"
            elif not trace_id and category != '认证/权限问题':
                is_unclear = True
                reason = "缺少traceId，无法追踪完整调用链"
            
            if is_unclear:
                unclear_samples.append({
                    'content': content_text[:100],
                    'reason': reason,
                    'trace_id': trace_id,
                    'class': sample.get('class')
                })
        
        if unclear_samples:
            feedback_cases.append({
                'category': category,
                'count': len(unclear_samples),
                'samples': unclear_samples
            })
    
    if feedback_cases:
        html += f"""
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <h4 style="color: #856404; margin-bottom: 15px;">⚠️ 发现 {len(feedback_cases)} 个分类存在不明确日志</h4>
"""
        for case in feedback_cases[:5]:
            html += f"""
                    <div style="background: white; border-radius: 8px; padding: 15px; margin: 15px 0;">
                        <h5 style="color: #1a1a2e; margin-bottom: 10px;">{case['category']} ({case['count']} 个样本)</h5>
                        <table class="performance-table">
                            <thead>
                                <tr>
                                    <th>类</th>
                                    <th>内容</th>
                                    <th>问题</th>
                                    <th>traceId</th>
                                </tr>
                            </thead>
                            <tbody>
"""
            for sample in case['samples'][:3]:
                content_short = sample['content'][:50].replace('<', '&lt;').replace('>', '&gt;')
                trace_display = sample['trace_id'] if sample['trace_id'] else '<span style="color: #e74c3c;">无</span>'
                html += f"""
                                <tr>
                                    <td><code>{sample['class']}</code></td>
                                    <td>{content_short}</td>
                                    <td style="color: #856404;">{sample['reason']}</td>
                                    <td><code>{trace_display}</code></td>
                                </tr>
"""
            html += """
                            </tbody>
                        </table>
                    </div>
"""
        html += """
                </div>
"""
    else:
        html += """
                <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <p style="color: #155724; margin: 0;">✅ 所有异常日志内容都较为明确，无需反哺</p>
                </div>
"""
    
    html += """
            </div>

            <!-- 慢接口分析 -->'''

# 替换
new_content = content.replace(insert_marker, feedback_module)

# 写回文件
with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\generate_html_report_v2.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("已添加日志反哺模块")

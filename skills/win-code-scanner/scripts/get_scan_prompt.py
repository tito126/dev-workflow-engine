#!/usr/bin/env python3
"""
扫描提示词生成脚本
使用规则索引和精简规则，减少 prompt token 消耗

支持新的规则文件结构：
- backend_rules_index.json + backend_rules.json
- frontend_rules_index.json + frontend_rules.json
"""

import json
import os

# 规则文件路径（相对于脚本目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 后端规则
BACKEND_RULES_FILE = os.path.join(BASE_DIR, "references/backend_rules.json")
BACKEND_INDEX_FILE = os.path.join(BASE_DIR, "references/backend_rules_index.json")

# 前端规则
FRONTEND_RULES_FILE = os.path.join(BASE_DIR, "references/frontend_rules.json")
FRONTEND_INDEX_FILE = os.path.join(BASE_DIR, "references/frontend_rules_index.json")


def load_rule_index(file_type: str) -> dict:
    """加载规则索引"""
    index_file = BACKEND_INDEX_FILE if file_type == 'backend' else FRONTEND_INDEX_FILE

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"警告: 索引文件不存在，将使用完整规则文件: {index_file}")
        return None


def load_full_rules(file_type: str) -> list:
    """加载完整规则列表"""
    rules_file = BACKEND_RULES_FILE if file_type == 'backend' else FRONTEND_RULES_FILE

    with open(rules_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_rule_by_code(rules: list, code: str) -> dict:
    """根据规则代码获取完整规则"""
    for rule in rules:
        if rule.get('code') == code:
            return rule
    return None


def filter_rules_by_extension(rules: list, file_extensions: list) -> list:
    """根据文件扩展名筛选适用的规则"""
    filtered = []
    for rule in rules:
        applicable_exts = rule.get('applicable_extensions', '[]')

        # 解析扩展名列表（JSON字符串格式）
        try:
            ext_list = json.loads(applicable_exts) if isinstance(applicable_exts, str) else applicable_exts
        except:
            ext_list = []

        # 检查是否有匹配的扩展名
        for file_ext in file_extensions:
            # 移除点号进行比较
            clean_ext = file_ext.lstrip('.')
            if f".{clean_ext}" in ext_list or clean_ext in ext_list:
                filtered.append(rule)
                break

    return filtered


def generate_scan_prompt(file_type: str, file_extensions: list = None,
                       rule_codes: list = None, use_index: bool = True) -> str:
    """
    生成扫描提示词

    Args:
        file_type: 'backend' 或 'frontend'
        file_extensions: 文件扩展名列表，用于筛选规则（如 ['.java', '.sql']）
        rule_codes: 指定的规则代码列表（为空则使用全部）
        use_index: 是否优先使用索引（减少token消耗）

    Returns:
        扫描提示词
    """
    # 1. 首先尝试加载索引（token消耗更少）
    rule_index = None
    if use_index:
        rule_index = load_rule_index(file_type)

    # 2. 加载完整规则（用于详细信息）
    full_rules = load_full_rules(file_type)

    # 3. 根据文件扩展名筛选规则
    if file_extensions:
        full_rules = filter_rules_by_extension(full_rules, file_extensions)
        if rule_index:
            # 同步更新索引
            filtered_index = {}
            for category, rules in rule_index.items():
                filtered_rules = {}
                for code, rule_info in rules.items():
                    # 检查是否在筛选后的规则中
                    if any(r.get('code') == code for r in full_rules):
                        filtered_rules[code] = rule_info
                if filtered_rules:
                    filtered_index[category] = filtered_rules
            rule_index = filtered_index if filtered_index else None

    # 4. 根据指定规则代码进一步筛选
    if rule_codes:
        filtered_rules = []
        for code in rule_codes:
            rule = get_rule_by_code(full_rules, code)
            if rule:
                filtered_rules.append(rule)
        full_rules = filtered_rules if filtered_rules else full_rules

        if rule_index:
            # 同步更新索引
            filtered_index = {}
            for category, rules in rule_index.items():
                filtered_rules = {}
                for code_idx, rule_info in rules.items():
                    if code_idx in rule_codes:
                        filtered_rules[code_idx] = rule_info
                if filtered_rules:
                    filtered_index[category] = filtered_rules
            rule_index = filtered_index if filtered_index else None

    # 5. 构建提示词
    prompt_parts = []

    # 添加规则概要（使用索引或精简格式）
    if rule_index:
        prompt_parts.append(format_index_prompt(rule_index))
    else:
        prompt_parts.append(format_rules_compact(full_rules))

    # 添加扫描要求
    prompt_parts.append("""
## 扫描要求

1. 严格按照上述规则逐条检查代码
2. 对发现的每个问题必须输出：
   - rule_code: 规则编号（如 PERF-B007）
   - rule_name: 规则名称
   - severity: 严重程度（严重/警告/提示）
   - category: 规则分类（性能/安全/业务/框架/架构/质量/语法/工程）
   - file: 文件相对路径
   - line: 问题所在行号
   - code_snippet: 问题代码片段（包含上下文）
   - description: 问题描述
   - suggestion: 修复建议
3. 只输出纯 JSON 格式，不包含额外说明文本
4. 使用上述规则进行判断，不添加额外的自定义规则
5. 确保报告包含所有发现的问题，不能遗漏
""")

    return "\n".join(prompt_parts)


def format_index_prompt(rule_index: dict) -> str:
    """格式化索引提示词（精简版，token消耗少）"""
    lines = ["## 扫描规则索引\n"]

    for category, rules in rule_index.items():
        lines.append(f"\n### {category}")
        for code, rule_info in rules.items():
            lines.append(f"**{code}** - {rule_info['name']}")
            lines.append(f"- 严重程度: {rule_info['severity']}")
            lines.append(f"- 描述: {rule_info['description']}")
            lines.append(f"- 检查点数量: {rule_info['checkpoints']}")
            lines.append("")

    return "\n".join(lines)


def format_rules_compact(rules: list) -> str:
    """格式化完整规则（精简版）"""
    lines = ["## 扫描规则\n"]

    for rule in rules:
        code = rule.get('code', '')
        name = rule.get('name', '')
        severity = rule.get('severity', '')
        desc = rule.get('description', '')

        # 精简描述
        if len(desc) > 100:
            desc = desc[:97] + "..."

        lines.append(f"**{code}** - {name}")
        lines.append(f"- 严重程度: {severity}")
        lines.append(f"- 描述: {desc}")

        # 添加检查点
        checkpoints = rule.get('checkpoints', [])
        if checkpoints:
            lines.append(f"- 检查点:")
            for cp in checkpoints[:3]:  # 只显示前3个
                cp_id = cp.get('id', '')
                cp_desc = cp.get('description', '')
                if len(cp_desc) > 50:
                    cp_desc = cp_desc[:47] + "..."
                lines.append(f"  - [{cp_id}] {cp_desc}")
            if len(checkpoints) > 3:
                lines.append(f"  - ... (共{len(checkpoints)}个检查点)")

        lines.append("")

    return "\n".join(lines)


def get_applicable_rules(file_type: str, file_extensions: list) -> list:
    """
    获取适用于指定文件扩展名的规则列表

    Args:
        file_type: 'backend' 或 'frontend'
        file_extensions: 文件扩展名列表（如 ['.java', '.sql']）

    Returns:
        适用的规则列表
    """
    full_rules = load_full_rules(file_type)
    return filter_rules_by_extension(full_rules, file_extensions)


def get_rule_summary(file_type: str) -> dict:
    """
    获取规则统计摘要

    Returns:
        {
            'total': 总规则数,
            'by_category': {'分类': 数量},
            'by_severity': {'严重': 数量, '警告': 数量}
        }
    """
    index = load_rule_index(file_type)
    if not index:
        rules = load_full_rules(file_type)
        return {
            'total': len(rules),
            'by_category': {},
            'by_severity': {}
        }

    summary = {
        'total': 0,
        'by_category': {},
        'by_severity': {}
    }

    for category, rules in index.items():
        summary['by_category'][category] = len(rules)
        summary['total'] += len(rules)

        for rule_info in rules.values():
            severity = rule_info.get('severity', '未知')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1

    return summary


def main():
    """命令行入口"""
    import sys

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" 扫描提示词生成工具")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 解析参数
    file_type = sys.argv[1] if len(sys.argv) > 1 else 'backend'
    rule_codes = sys.argv[2].split(',') if len(sys.argv) > 2 else None

    if file_type not in ['backend', 'frontend']:
        print(f"错误: 文件类型必须是 'backend' 或 'frontend'")
        sys.exit(1)

    # 生成提示词
    prompt = generate_scan_prompt(file_type, rule_codes=rule_codes)

    # 输出到文件
    output_file = f"/tmp/scan_prompt_{file_type}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prompt)

    print(f"✓ 提示词已生成: {output_file}")
    print(f"  提示词大小: {len(prompt.encode('utf-8'))} 字节")

    # 显示规则统计
    summary = get_rule_summary(file_type)
    print(f"  规则总数: {summary['total']}")
    print(f"  预计节省约 30-50% token（相比完整规则）")
    print()

    # 显示提示词预览
    print("提示词预览:")
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)


if __name__ == "__main__":
    main()

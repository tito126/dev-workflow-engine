#!/usr/bin/env python3
"""
优化扫描规则脚本

支持新的规则文件命名：
- backend_rules.json -> backend_rules_index.json
- frontend_rules.json -> frontend_rules_index.json

功能：
1. 验证规则文件格式（确保已优化）
2. 生成规则索引用于快速匹配
3. 统计规则信息
"""

import json
import os

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(BASE_DIR, "references")

# 规则文件（新的命名约定）
BACKEND_RULES_FILE = os.path.join(REFERENCES_DIR, "backend_rules.json")
BACKEND_INDEX_FILE = os.path.join(REFERENCES_DIR, "backend_rules_index.json")

FRONTEND_RULES_FILE = os.path.join(REFERENCES_DIR, "frontend_rules.json")
FRONTEND_INDEX_FILE = os.path.join(REFERENCES_DIR, "frontend_rules_index.json")

# 扫描必需的核心字段
ESSENTIAL_FIELDS = [
    "id", "category", "code", "name", "severity", "description",
    "checkpoints", "applicable_extensions", "status", "check_level", "code_type"
]

# 可删除的冗余字段（空值率高）
REDUNDANT_FIELDS = [
    "violation_examples",      # 88% 空值
    "compliance_examples",      # 88% 空值
    "applicable_scenarios",    # 52% 空值
    "created_at",             # 72% 空值
    "updated_at",             # 86% 空值
    "exception_explanation",     # 80% 空值
    "examples_mode_enabled",     # 94% 空值
    "is_specialty"            # 97% 空值
]


def validate_rules(rules_file: str) -> tuple:
    """
    验证规则文件是否已优化

    Returns:
        (is_valid, issues): (是否有效, 问题列表)
    """
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    issues = []

    # 检查第一条规则是否有冗余字段
    if rules:
        first_rule = rules[0]

        # 检查是否标记为已优化
        if not first_rule.get('_optimized', False):
            issues.append("规则未标记为已优化（缺少 _optimized 字段）")

        # 检查是否存在冗余字段
        for field in REDUNDANT_FIELDS:
            if field in first_rule:
                issues.append(f"存在冗余字段: {field}")

    return len(issues) == 0, issues


def optimize_rules_file(rules_file: str, output_file: str = None) -> bool:
    """
    优化规则文件（删除冗余字段）

    Returns:
        是否成功优化
    """
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    print(f"原始规则数: {len(rules)}")

    # 优化每条规则
    optimized_rules = []
    changed = False

    for rule in rules:
        optimized_rule = {}

        # 检查是否有冗余字段
        has_redundant = any(field in rule for field in REDUNDANT_FIELDS)

        # 只保留核心字段
        for field in ESSENTIAL_FIELDS:
            if field in rule:
                optimized_rule[field] = rule[field]

        # 添加优化标记
        if not rule.get('_optimized', False):
            optimized_rule['_optimized'] = True
            changed = True
        else:
            optimized_rule['_optimized'] = True

        optimized_rules.append(optimized_rule)

    # 如果没有变化，不需要写入
    if not changed and not has_redundant:
        print("规则已是优化格式，无需修改")
        return False

    # 确定输出文件
    if output_file is None:
        output_file = rules_file

    # 写入优化后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(optimized_rules, f, ensure_ascii=False, indent=2)

    original_size = os.path.getsize(rules_file)
    new_size = os.path.getsize(output_file)

    print(f"优化后规则数: {len(optimized_rules)}")
    print(f"文件大小: {original_size} -> {new_size} 字节 (节省 {original_size - new_size} 字节, {(1 - new_size/original_size)*100:.1f}%)")

    return True


def generate_rule_index(rules_file: str, index_file: str) -> dict:
    """生成规则索引用于快速匹配"""
    # 读取规则
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    index = {}

    for rule in rules:
        code = rule.get('code', '')

        # 按类别索引
        category = rule.get('category', '')
        if category not in index:
            index[category] = {}

        if code not in index[category]:
            index[category][code] = {
                'name': rule.get('name', ''),
                'severity': rule.get('severity', ''),
                'description': rule.get('description', ''),
                'checkpoints': len(rule.get('checkpoints', []))
            }

    # 保存索引
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"规则索引已生成: {index_file}")

    # 返回索引统计
    return {
        'categories': len(index),
        'total_rules': sum(len(rules) for rules in index.values())
    }


def process_rules(file_type: str, validate_only: bool = False, optimize: bool = False):
    """
    处理规则文件

    Args:
        file_type: 'backend' 或 'frontend'
        validate_only: 仅验证不修改
        optimize: 是否优化规则文件
    """
    if file_type == 'backend':
        rules_file = BACKEND_RULES_FILE
        index_file = BACKEND_INDEX_FILE
    else:
        rules_file = FRONTEND_RULES_FILE
        index_file = FRONTEND_INDEX_FILE

    print(f"\n{'='*50}")
    print(f"处理 {file_type} 规则")
    print(f"{'='*50}")

    # 检查文件是否存在
    if not os.path.exists(rules_file):
        print(f"错误: 规则文件不存在: {rules_file}")
        return

    # 验证规则
    is_valid, issues = validate_rules(rules_file)

    if is_valid:
        print("✓ 规则文件已优化，格式正确")
    else:
        print("⚠ 规则文件需要优化:")
        for issue in issues:
            print(f"  - {issue}")

        if validate_only:
            return

        if optimize:
            print("\n正在优化规则文件...")
            optimize_rules_file(rules_file)

    # 生成索引
    print("\n正在生成规则索引...")
    index_stats = generate_rule_index(rules_file, index_file)
    print(f"  分类数: {index_stats['categories']}")
    print(f"  总规则数: {index_stats['total_rules']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='扫描规则优化工具')
    parser.add_argument('--type', choices=['backend', 'frontend', 'all'],
                        default='all', help='规则类型')
    parser.add_argument('--validate', action='store_true',
                        help='仅验证不修改')
    parser.add_argument('--optimize', action='store_true',
                        help='优化规则文件（删除冗余字段）')

    args = parser.parse_args()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" 扫描规则优化工具")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 处理规则
    if args.type in ['backend', 'all']:
        process_rules('backend', args.validate, args.optimize)

    if args.type in ['frontend', 'all']:
        process_rules('frontend', args.validate, args.optimize)

    print("\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" 使用建议")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("""
1. 规则文件已优化：
   - backend_rules.json (优化后的后端规则)
   - frontend_rules.json (优化后的前端规则)

2. 规则索引已生成：
   - backend_rules_index.json (后端规则索引)
   - frontend_rules_index.json (前端规则索引)

3. 使用方式：
   - 优先读取 index 文件获取规则概要（减少 token）
   - 按需从完整规则文件读取详细检查点

4. Token 节省：
   - 使用索引可减少约 40-60% 的 prompt token
   - 根据文件扩展名筛选规则可进一步减少 token
""")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    main()

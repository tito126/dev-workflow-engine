#!/usr/bin/env python3
"""
低价值文件排除工具

用于在代码扫描前排除低价值文件，加快扫描速度

使用方式:
    python scripts/exclude_low_value_files.py backend <file_list.txt>
    python scripts/exclude_low_value_files.py frontend <file_list.txt>
"""

import sys
import os
import re
from typing import List

# 后端排除规则
BACKEND_EXCLUDE_SUFFIXES = [
    # 数据模型类
    "DTO.java", "InputDTO.java", "OutputDTO.java",
    "BO.java", "VO.java", "PO.java", "DO.java",
    "Entity.java", "Model.java",
    "Dto.java", "Bo.java", "Vo.java", "Po.java", "Do.java",
    # 注释类（纯说明性质，不包含业务逻辑）
    "Configuration.java", "Config.java",
    "Constants.java", "Constant.java",
    "Enum.java", "Enums.java"
]

# 前端排除规则
FRONTEND_EXCLUDE = {
    "exclude_dirs": [
        "node_modules/", "dist/", "build/", "coverage/",
        ".next/", ".vite/", "__tests__/"
    ],
    "exclude_suffixes": [
        ".d.ts", ".css", ".scss", ".less", ".sass", ".module.css",
        ".png", ".jpg", ".jpeg", ".svg", ".gif", ".ico",
        ".spec.ts", ".test.ts", ".spec.js", ".test.js"
    ],
    "exclude_file_names": [
        "types.ts", "interface.ts", "interfaces.ts",
        "constants.ts", "enums.ts", "enum.ts"
    ]
}


def should_exclude_backend(file_path: str) -> bool:
    """判断后端文件是否应该被排除"""
    for suffix in BACKEND_EXCLUDE_SUFFIXES:
        if file_path.endswith(suffix):
            return True
    return False


def should_exclude_frontend(file_path: str) -> bool:
    """判断前端文件是否应该被排除"""
    # 检查排除目录
    for exclude_dir in FRONTEND_EXCLUDE["exclude_dirs"]:
        if exclude_dir in file_path:
            return True

    # 检查排除后缀
    for suffix in FRONTEND_EXCLUDE["exclude_suffixes"]:
        if file_path.endswith(suffix):
            return True

    # 检查排除文件名
    basename = os.path.basename(file_path)
    for exclude_name in FRONTEND_EXCLUDE["exclude_file_names"]:
        if basename == exclude_name:
            return True

    return False


def filter_files(project_type: str, file_list: List[str]) -> tuple:
    """
    过滤文件列表

    Args:
        project_type: 'backend' 或 'frontend'
        file_list: 原始文件列表

    Returns:
        (filtered_files, excluded_count, original_count)
    """
    original_count = len(file_list)
    filtered_files = []

    should_exclude = should_exclude_backend if project_type == 'backend' else should_exclude_frontend

    for file_path in file_list:
        if not should_exclude(file_path):
            filtered_files.append(file_path)

    excluded_count = original_count - len(filtered_files)

    return filtered_files, excluded_count, original_count


def print_summary(project_type: str, filtered_files: List[str], excluded_count: int, original_count: int):
    """打印排除摘要"""
    print()
    print("排除低价值文件")
    print("=" * 50)

    print(f"原始文件数: {original_count} 个")
    print(f"排除后文件数: {len(filtered_files)} 个")
    print(f"排除文件数: {excluded_count} 个 ({excluded_count/original_count*100:.1f}%)")

    if project_type == 'backend':
        print("\n排除类型:")
        print("  - DTO/VO/BO/PO/DO/Entity/Model 等数据模型类")
        print("  - 文件名包含: InputDTO, OutputDTO, Dto, Bo, Vo, Po, Do 等")
        print("  - 注释类: Configuration/Config/Constants/Enum 等纯说明性质的类")
    else:
        print("\n排除类型:")
        print("  - 目录: node_modules/, dist/, build/, coverage/, .next/, .vite/, __tests__/")
        print("  - 文件后缀: .d.ts, .css, .scss, .less, .png, .jpg, .svg, .spec.ts, .test.ts")
        print("  - 文件名: types.ts, interface.ts, constants.ts, enums.ts")

    print()
    print("=" * 50)


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法:")
        print(f"  {sys.argv[0]} <backend|frontend> <file_list.txt>")
        print(f"  {sys.argv[0]} <backend|frontend> --stdin  # 从 stdin 读取文件列表")
        sys.exit(1)

    project_type = sys.argv[1].lower()
    input_file = sys.argv[2]

    if project_type not in ['backend', 'frontend']:
        print(f"错误: 项目类型必须是 'backend' 或 'frontend'")
        sys.exit(1)

    # 读取文件列表
    if input_file == '--stdin':
        file_list = [line.strip() for line in sys.stdin if line.strip()]
    else:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"错误: 文件不存在: {input_file}")
            sys.exit(1)

    # 过滤文件
    filtered_files, excluded_count, original_count = filter_files(project_type, file_list)

    # 打印摘要
    print_summary(project_type, filtered_files, excluded_count, original_count)

    # 输出过滤后的文件列表
    for file_path in filtered_files:
        print(file_path)

    # 同时保存到临时文件
    output_file = f"/tmp/filtered_{project_type}_files.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_path in filtered_files:
            f.write(file_path + '\n')

    print(f"\n过滤后的文件列表已保存到: {output_file}")


if __name__ == "__main__":
    main()

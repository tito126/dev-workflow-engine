#!/bin/bash
set -e

# 读取代码扫描配置文件
# 用法: ./read-config.sh [配置项名称]
# 返回: 配置项的值，如果配置文件不存在则返回空

CONFIG_FILE="$HOME/.cache/skills/win-code-scanner/config.json"
CONFIG_KEY="${1:-default_scan_path}"

if [ ! -f "$CONFIG_FILE" ]; then
    # 配置文件不存在，返回空表示走原有流程
    exit 0
fi

# 使用 Python 解析 JSON，通过环境变量安全传递参数
python3 -c "
import json
import os

config_file = os.environ.get('CONFIG_FILE', '')
config_key = os.environ.get('CONFIG_KEY', '')

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
        value = config.get(config_key, '')
        if value:
            print(value)
except Exception:
    # 配置读取失败，走原有流程
    pass
" CONFIG_FILE="$CONFIG_FILE" CONFIG_KEY="$CONFIG_KEY"

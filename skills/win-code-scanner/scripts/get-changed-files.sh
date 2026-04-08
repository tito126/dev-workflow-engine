#!/bin/bash
#
# 获取指定天数内修改的文件列表
# 用法: ./get-changed-files.sh [天数] [文件扩展名]
# 示例: ./get-changed-files.sh 3 "java vue js"
#

set -e

# 默认参数
DAYS=${1:-3}
EXTENSIONS=${2:-""}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}错误: 当前目录不是 git 仓库${NC}"
    exit 1
fi

echo -e "${GREEN}=== 增量扫描文件获取工具 ===${NC}"
echo ""
echo "仓库路径: $(git rev-parse --show-toplevel)"
echo "时间范围: 最近 ${DAYS} 天"
echo "扫描时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 获取修改的文件列表
echo -e "${YELLOW}正在获取修改的文件...${NC}"

# 方法1: 使用 git log (更准确，包含已提交的修改)
COMMITTED_FILES=$(git log --name-only --since="${DAYS} days ago" --pretty=format: | sort | uniq | grep -v '^$')

# 方法2: 使用 git diff (包含未提交的修改)
UNCOMMITTED_FILES=$(git diff --name-only HEAD 2>/dev/null || echo "")

# 合并文件列表
ALL_FILES=$(echo -e "${COMMITTED_FILES}\n${UNCOMMITTED_FILES}" | sort | uniq | grep -v '^$')

# 按扩展名过滤
if [ -n "$EXTENSIONS" ]; then
    FILTERED_FILES=""
    for ext in $EXTENSIONS; do
        FILTERED_FILES="${FILTERED_FILES}\n$(echo "$ALL_FILES" | grep -i "\.${ext}\$" || true)"
    done
    FILTERED_FILES=$(echo -e "${FILTERED_FILES}" | grep -v '^$' | sort | uniq)
else
    FILTERED_FILES="$ALL_FILES"
fi

# 统计信息
TOTAL_COUNT=$(echo "$FILTERED_FILES" | wc -l | tr -d ' ')

echo -e "${GREEN}找到 ${TOTAL_COUNT} 个修改的文件${NC}"
echo ""

# 按扩展名统计
echo "文件类型统计:"
echo "$FILTERED_FILES" | sed 's/.*\.//' | sort | uniq -c | sort -rn | while read count ext; do
    if [ -n "$ext" ]; then
        echo "  .${ext}: ${count} 个"
    fi
done
echo ""

# 输出文件列表
echo "=== 修改的文件列表 ==="
echo "$FILTERED_FILES"
echo ""

# 输出到临时文件（供其他程序调用）
TEMP_FILE="/tmp/changed_files_${DAYS}days.txt"
echo "$FILTERED_FILES" > "$TEMP_FILE"
echo -e "${GREEN}文件列表已保存到: ${TEMP_FILE}${NC}"
echo ""

# 验证文件是否存在
echo "=== 验证文件存在性 ==="
EXIST_COUNT=0
MISSING_COUNT=0

while IFS= read -r file; do
    if [ -f "$file" ]; then
        EXIST_COUNT=$((EXIST_COUNT + 1))
    else
        MISSING_COUNT=$((MISSING_COUNT + 1))
        echo -e "${RED}✗${NC} ${file} (不存在)"
    fi
done <<< "$FILTERED_FILES"

echo -e "${GREEN}存在: ${EXIST_COUNT} 个${NC}"
echo -e "${RED}缺失: ${MISSING_COUNT} 个${NC}"
echo ""

# 只输出存在的文件
if [ $MISSING_COUNT -gt 0 ]; then
    echo "=== 仅存在的文件列表 ==="
    while IFS= read -r file; do
        [ -f "$file" ] && echo "$file"
    done <<< "$FILTERED_FILES"
fi

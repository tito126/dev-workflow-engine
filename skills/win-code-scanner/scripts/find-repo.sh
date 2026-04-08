#!/bin/bash
set -e

# 在默认路径下递归搜索匹配的 git 仓库
# 用法: ./find-repo.sh <关键词> <默认路径>

KEYWORD="$1"
DEFAULT_PATH="$2"

if [ -z "$KEYWORD" ] || [ -z "$DEFAULT_PATH" ]; then
    echo "用法: $0 <关键词> <默认路径>"
    exit 1
fi

if [ ! -d "$DEFAULT_PATH" ]; then
    echo "错误: 默认路径不存在: $DEFAULT_PATH"
    exit 1
fi

# 计数器
FOUND_COUNT=0

# 递归搜索包含 .git 目录且名称匹配关键词的仓库
echo "正在搜索匹配 '$KEYWORD' 的仓库..."
echo "搜索路径: $DEFAULT_PATH"
echo ""

# 使用进程替换避免子 shell 问题
while IFS= read -r gitdir; do
    repodir=$(dirname "$gitdir")
    reponame=$(basename "$repodir")

    # 不区分大小写匹配整个路径（使用 -F 进行固定字符串匹配）
    if echo "$repodir" | grep -qiF "$KEYWORD"; then
        # 使用 git -C 替代 cd
        git_url=$(git -C "$repodir" config --get remote.origin.url 2>/dev/null || echo "无")

        echo "FOUND_REPO:$repodir|$reponame|$git_url"
        FOUND_COUNT=$((FOUND_COUNT + 1))
    fi
done < <(find "$DEFAULT_PATH" -maxdepth 4 -type d -name ".git" 2>/dev/null)

# 输出总结
echo ""
echo "搜索完成，找到 ${FOUND_COUNT} 个匹配的仓库"

# 设置退出状态码
if [ $FOUND_COUNT -eq 0 ]; then
    exit 1
fi

exit 0

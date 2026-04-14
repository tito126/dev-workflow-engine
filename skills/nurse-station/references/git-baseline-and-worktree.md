# git-baseline-and-worktree — 代码基线与工作区准备

根据 YAML 配置自动同步代码基线、创建 worktree，让 locator / implementer 总是基于一份干净可追溯的代码工作。

## 配置说明

### 用户只需维护的字段

```yaml
repo_profiles:
  backend_main:
    root_key: backend_main
    git:
      source_branch: sr-next
  frontend_main:
    root_key: frontend_main
    git:
      source_branch: sr-next
```

就三个概念：
- **repo key**：仓库代号（不是 Git 知识）
- **root_key**：对应 YAML `roots` 里的哪个仓
- **source_branch**：默认从哪条基线拉最新代码

### 系统默认值（不需要用户手填）

```yaml
git_defaults:
  auto_pull: true
  fetch_first: true
  use_worktree: true
  worktree_base_dir: C:\Users\pc\.openclaw\workspace\.nurse-station-worktrees
```

## prepare-workspace 步骤

1. 读取 YAML，确认 `status=ready`
2. 根据 repo key 找到仓库根路径
3. 读取 `source_branch`
4. 在源仓库执行 `git fetch` → `git checkout <source_branch>` → `git pull`
5. 基于 `branch_pattern`（默认 `feature/{taskId}`）创建功能分支
6. 创建或刷新 worktree
7. 输出路由与代码基线摘要

## 输出摘要（给人看的版本）

```text
【nurse-station 路由与代码基线摘要】
- 任务号：1555189
- 目标 repo key：frontend_main
- 实际扫描根：D:\workspace\winx-sr-next\winning-webui-inpatient-costcheck
- 基线分支：sr-next
- 当前 commit：abc1234
- 本轮 worktree 路径：C:\Users\pc\.openclaw\workspace\.nurse-station-worktrees\1555189-frontend_main
- 禁止扩扫根：
  - E:\winning-code\work
  - E:\winning-code\ai
- 当前阶段：brainstorming
```

## 输出摘要（给程序消费的版本，可选）

```json
{
  "taskId": "1555189",
  "repoKey": "frontend_main",
  "scanRoot": "D:\\workspace\\winx-sr-next\\winning-webui-inpatient-costcheck",
  "sourceBranch": "sr-next",
  "commit": "abc1234",
  "worktree": "C:\\Users\\pc\\.openclaw\\workspace\\.nurse-station-worktrees\\1555189-frontend_main",
  "excludedRoots": ["E:\\winning-code\\work", "E:\\winning-code\\ai"]
}
```

建议对用户展示时优先使用自然语言摘要，对脚本和主流程则保留结构化结果。

## 安全保护

- 默认不在源仓库里直接开发
- 优先在 worktree 中做 locator / implementer
- 若源仓库有未提交改动，不把它当作安全开发区
- 若 worktree 已存在，提示复用还是重建

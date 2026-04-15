# git-baseline-and-branch — 代码基线与本地仓库准备

根据 YAML 配置同步目标仓库的基线分支最新代码，并明确后续直接在哪个本地仓库目录修改与验证。

## 配置说明

当前以 `work-system/config/nurse-station-repo-routing.yaml` 为准。

关键字段：

```yaml
repos:
  backend_main:
    path: "E:\\winning-code\\akso5\\winning-nis-ward"
    source_branch: "sr-next"

git_defaults:
  auto_pull: true
  fetch_first: true
```

这里的重点是：
- **repo key**：本轮命中的目标仓库标识
- **path**：实际本地仓库目录
- **source_branch**：该仓库默认拉取最新代码的基线分支
- **同目录多仓 / 多分支场景**：按 `repos.<repoKey>.path + source_branch` 精确定位，不再只靠根目录推断

## prepare-workspace 步骤

1. 读取 YAML，确认 `status=ready`
2. 根据 repo key 找到 `repos.<repoKey>.path`
3. 读取 `repos.<repoKey>.source_branch`
4. 在该本地仓库执行 `git fetch` → `git checkout <source_branch>` → `git pull`
5. 按 `branch_pattern`（默认 `feature/{taskId}`）创建或切换到本轮任务分支
6. 记录当前 commit
7. 输出路由与代码基线摘要，明确后续直接在该本地目录修改

## 输出摘要（给人看的版本）

```text
【nurse-station 路由与代码基线摘要】
- 任务号：1555189
- 目标 repo key：admin_execution_inpatient
- 实际扫描根：E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient
- 基线分支：sr-next
- 当前 commit：abc1234
- 本地修改目录：E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient
- 禁止扩扫根：
  - E:\winning-code\work
  - E:\winning-code\ai
- 当前阶段：brainstorming
```

## 输出摘要（给程序消费的版本，可选）

```json
{
  "taskId": "1555189",
  "repoKey": "admin_execution_inpatient",
  "scanRoot": "E:\\winning-code\\frontend\\webui-next\\winning-webui-admin-execution-inpatient",
  "sourceBranch": "sr-next",
  "commit": "abc1234",
  "repoPath": "E:\\winning-code\\frontend\\webui-next\\winning-webui-admin-execution-inpatient",
  "excludedRoots": ["E:\\winning-code\\work", "E:\\winning-code\\ai"]
}
```

## 异常处理

- YAML 不存在或 `status` 不是 `ready`：停止，回到配置维护，不进入 locator / implementer
- 目标 `repoKey` 无法映射到 `repos.<repoKey>`：停止，回到路由配置或任务选择
- `repos.<repoKey>.path` 或 `source_branch` 缺失：停止，补配置后再继续
- 本地仓库目录不存在：停止，先修正配置或本地环境
- `git fetch / checkout / pull` 失败：停止，保留错误信息，不继续进入实现
- `feature/{taskId}` 分支创建或切换失败：停止，先处理本地 Git 状态或分支冲突
- 当前 commit 无法获取：停止，不能输出不完整路由摘要
- 如果同一目录下存在多个分支使用要求，以 `repoKey` 对应配置为准，不允许凭聊天口头切换到其他分支

## 安全保护

- 默认直接在目标本地仓库目录修改，便于联调与验证
- 修改前必须先明确当前仓库路径、基线分支和任务分支
- 如果实际打开目录与 YAML 命中的目录不一致，先停下纠偏
- 如果验证环境跑的不是当前基线同步后的目录或分支，不能宣称“效果已验证”

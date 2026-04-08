# Branch Management

在准备研发分支时，先读 `config/git-config.json`，再决定是否询问用户。

## 配置文件

使用以下 JSON 结构：

```json
{
  "default_source_branch": "sr-next",
  "source_branches": ["sr-next", "sr-rc"],
  "branch_patterns": {
    "by_task": "feature/{taskId}",
    "by_demand": "feature/{demandId}_{sourceBranch}"
  }
}
```

字段含义如下：

| 字段 | 说明 |
| --- | --- |
| `default_source_branch` | 默认源分支；存在且可用时直接使用 |
| `source_branches` | 建议给用户展示的源分支选项 |
| `branch_patterns.by_task` | 按任务号命名功能分支 |
| `branch_patterns.by_demand` | 按需求号和源分支命名功能分支 |

## 源分支选择

1. 如果配置文件存在且 `default_source_branch` 有值，默认使用该分支。
2. 如果配置缺失、值为空，或当前仓库没有该分支，再询问用户。
3. 推荐优先提供 `sr-next`、`sr-rc` 和配置文件中的其他候选分支。

## 同步代码

确认源分支后，先切换到源分支，再拉取最新代码。

```bash
git checkout <source-branch>
git pull
```

## 功能分支命名

优先支持以下两种命名方式：

| 方式 | 格式 |
| --- | --- |
| 按任务号 | `feature/<任务号>` |
| 按需求号和源分支 | `feature/<需求号>_<源分支>` |

如果用户提供自定义分支名，直接使用用户输入。

创建分支时执行：

```bash
git checkout -b <feature-branch>
```

# task-resolution — 任务选择

在需求信息拿到后，先确定本轮基于哪个任务号开发，再准备代码基线。

## 默认规则

### 场景 A：需求下已有前端 / 后端任务
- 路由到 `frontend_main` 时，优先选择前端任务
- 路由到 `backend_main` 时，优先选择后端任务
- 选中后，默认功能分支名使用 `feature/{taskId}`

### 场景 B：需求下只有一个通用任务
- 直接复用该任务
- 仍按 `feature/{taskId}` 建分支

### 场景 C：需求下没有合适任务
- 默认行为：提示用户创建任务或确认使用通用任务
- 未来可选行为：若已开启 `auto_create_task_when_missing: true`，可自动在需求下创建任务

## 任务类型识别

YAML 中可配置关键词辅助匹配：

```yaml
task_policy:
  frontend_task_keywords: ["前端", "web", "vue", "页面"]
  backend_task_keywords: ["后端", "java", "接口", "服务"]
```

匹配时用任务标题 / 描述中的关键词做分类，不做精确匹配。

## 缺任务时的提示模板

```text
当前需求下未找到与本轮目标仓匹配的任务。

- 当前目标 repo：{repoKey}
- 建议任务类型：{suggestedType}任务
- 建议分支名：feature/{taskId}

请选择：
1. 使用现有通用任务
2. 新建前端 / 后端任务后再继续
3. 若已开启自动创建能力，则由系统自动创建任务
```

## 输出

- 选中的任务号
- 任务类型（前端 / 后端 / 通用）
- 默认功能分支名（`feature/{taskId}`）

---
name: nurse-station
description: |
  护士站任务统一主入口。用于护士站相关需求、缺陷、优化项、TFS 需求开发、代码定位、实现、验证、复盘，
  以及需要按统一流程处理仓库路由、任务选择、代码基线、worktree、设计澄清和交付产物的场景。
  优先在任何护士站开发任务中使用本技能，而不是直接点名旧的 nurse-station-* 单阶段技能。
---

# nurse-station

把护士站任务统一收口到一个入口，内部再按阶段读取 references。

## 主流程

默认顺序：

```text
tfs2018-integration
  → nurse-station（本入口）
    → YAML 校验
    → resolve-task（选任务号，定 feature 分支名）
    → prepare-workspace（同步基线，创建 worktree）
    → brainstorming
    → planning
    → locator（按需）
    → implementer
    → verification
    → review-gate
    → retrospective（按需）
```

## 阶段与 references 映射

根据当前阶段按需读取：

| 阶段 | reference | 何时读 |
| --- | --- | --- |
| 需求澄清 | `references/brainstorming.md` | 需求还没收敛时 |
| 共享底稿 | `references/planning.md` | 需要形成可复用计划时 |
| 任务选择 | `references/task-resolution.md` | 需要决定用哪个任务号时 |
| 代码基线 | `references/git-baseline-and-worktree.md` | 需要准备基线分支 / worktree 时 |
| 代码定位 | `references/locator.md` | 需要追踪代码链路时 |
| 代码实现 | `references/implementer.md` | 范围已清楚，准备改码时 |
| 结果验收 | `references/verification.md` | 需要对照需求做验收时 |
| 正式评审 | `references/review-gate.md` | 需要多闸门评审时 |
| 子任务派发 | `references/dispatch.md` | 需要派给 ACP opencode 等执行器时 |
| 复盘 | `references/retrospective.md` | 一轮 MVP / 真实运行结束后 |
| prompt 模板 | `references/entry-prompt-templates.md` | 自己用或转发给同事时 |
| UI 效果排查 | `references/ui-effect-checklist.md` | 代码已改但页面不生效时 |

## 强制规则

1. **YAML 闸门**：`work-system/config/nurse-station-repo-routing.yaml` 未 ready 时，不继续代码阶段
2. **任务号先行**：先确定任务号，再准备代码基线
3. **worktree 优先**：默认基于 worktree 工作，不直接在源仓库里开发
4. **回显路由摘要**：进入执行态前，默认输出本轮路由与代码基线摘要
5. **设计闸门**：需求边界不清时，先停在澄清 / 设计摘要阶段，不直接改码
6. **效果闸门**：代码已改但效果未出现时，先排查 UI 承载 / 显隐 / 弹层遮挡，不直接判定实现失败
7. **文案保护**：如果产品给了正式原文，默认不允许自行改写
8. **ACP 阻塞处理**：若 ACP 出现 backend unavailable / timeout / empty output / relay 异常，先报阻塞，等用户确认后再决定是否降级

## 默认回显模板

每次进入执行态前，至少回显以下字段：

```text
【nurse-station 路由与代码基线摘要】
- 任务号：{taskId}
- 目标 repo key：{repoKey}
- 实际扫描根：{scanRoot}
- 基线分支：{sourceBranch}
- 当前 commit：{commit}
- 本轮 worktree 路径：{worktreePath}
- 禁止扩扫根：{excludedRoots}
- 当前阶段：{currentPhase}
```

## 三条路径

### light
适用：小范围、本地化、目标清晰，改动目标已从 API 入口独立验证。

不需要运行时跟踪，不需要计划文档，不需要外部执行器。

### medium
适用：边界可控，需要定位 / 窄范围实现 / 明确验证，大概率用 ACP opencode。

### heavy
适用：多阶段、高不确定性、跨仓库、需要运行时跟踪。

## 产物落地

所有持久化产物统一落到：

```text
work-system/deliverables/nurse-station/{taskId}-{date}/
```

标准文件：
- `requirement-summary.md`（brainstorming 产出）
- `plan.md`（planning 产出）
- `findings.md`（locator 产出）
- `implementation-result.md`（implementer 产出）
- `verification-evidence.md`（verification 产出）
- `review-conclusion.md`（review-gate 产出）
- `retrospective.md`（retrospective 产出）

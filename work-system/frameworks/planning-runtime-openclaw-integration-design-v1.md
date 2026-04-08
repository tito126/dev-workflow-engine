# `planning-runtime`：面向当前 OpenClaw 体系的本地化集成设计 v1

## 1. 文档定位

本文档用于定义如何将 `planning-with-files` 的核心设计思想，真正集成到当前本地 `OpenClaw` 体系中，形成一个可落地、可演进、与现有 `memory / work-system / work-control` 协同工作的本地 skill：

`planning-runtime`

本文档不讨论“是否值得研究 planning-with-files”，而直接回答：

1. 应该如何集成
2. 集成后放在哪里
3. 与现有体系如何分工
4. 哪些资产直接复用，哪些必须本地化改造
5. 一条真实任务如何流转

---

## 2. 核心结论

## 2.1 一句话结论

`planning-with-files` 不应作为“补充记忆层”的 skill 接入，而应作为：

**复杂任务执行态控制层（runtime control layer）**

接入当前 `OpenClaw` 体系。

## 2.2 本地化 skill 名称

按当前约定，建议 skill 名称定为：

`planning-runtime`

## 2.3 本地化核心定位

`planning-runtime` 的职责不是管理长期记忆，也不是替代 `work-control`，而是：

- 为复杂任务建立运行态工作区
- 在任务执行过程中维持目标锚点
- 将研究发现、错误、阶段进展卸载到文件
- 帮助任务跨轮续接
- 在任务结束前做状态闭环检查
- 将稳定结论回流到正式工作流层

---

## 3. 为什么不能直接照搬 `planning-with-files`

虽然原项目已具备较成熟的工程化资产，但它的默认假设和当前本地体系并不一致。

## 3.1 原项目默认假设

原项目默认的运行模型更接近：

- 一个复杂任务
- 一个项目目录
- 一套 `task_plan.md / findings.md / progress.md`
- 一个以编码或研究为中心的连续执行过程

并且大量设计围绕 Claude / Codex 等 IDE 环境的 hooks 展开。

## 3.2 当前本地体系现实

当前本地体系已经存在：

- `memory/YYYY-MM-DD.md`：日常连续性记录
- `MEMORY.md`：长期记忆与稳定判断
- `work-system/`：正式工作记录层
- `skills/work-control/`：聊天驱动工作控制 skill
- 多个长期持续项目与临时任务并存
- 并非所有复杂任务都天然属于一个单独项目根目录

## 3.3 直接照搬会出现的问题

如果直接把原项目的 3-file pattern 原样复制进当前体系，会产生以下问题：

1. **目录污染**：在不同项目根目录或 workspace 根下散落大量 `task_plan.md`
2. **边界冲突**：执行态文件和正式项目档案容易混在一起
3. **技能职责重叠**：与 `work-control` 在“记录什么、写到哪里”上发生重叠
4. **Hook 依赖不稳**：原始自动行为依赖特定 IDE 生命周期 hook，不适合无改造直接复用
5. **长期记忆错位**：容易误把 runtime 文件当长期记忆主存储层

因此，正确方向不是“照搬”，而是“抽取其执行控制精髓，嵌入本地工作系统”。

---

## 4. `planning-runtime` 的目标定位

## 4.1 解决的问题

`planning-runtime` 主要解决以下问题：

1. 复杂任务执行过程中目标漂移
2. 多轮协作后上下文切换成本过高
3. 研究发现、浏览信息、局部结论没有及时落盘
4. 错误记录停留在复盘层，没有变成当前任务约束
5. 任务阶段状态不显式，完成与否容易凭感觉判断

## 4.2 不解决的问题

`planning-runtime` 不负责：

1. 长期个人记忆管理
2. 所有日常聊天记录归档
3. 正式项目台账主存储
4. 精确定时提醒
5. 替代 coding agent 或执行引擎

---

## 5. 在当前体系中的架构位置

建议将当前体系明确拆成四层：

```text
第 1 层：长期连续性层
  - memory/YYYY-MM-DD.md
  - MEMORY.md
  - memory_search

第 2 层：正式工作流层
  - work-system/projects/
  - work-system/daily/
  - work-system/inbox/
  - work-system/deliverables/

第 3 层：执行态运行层
  - work-system/projects/active/<project>/runtime/<task-id>/

第 4 层：技能控制层
  - skills/work-control/
  - skills/planning-runtime/
```

其中：

- `work-control` 负责正式记录路由与日常工作控制
- `planning-runtime` 负责复杂任务的执行态控制

---

## 6. 推荐目录结构

按当前约定，runtime 文件放到项目档案下，而不是 workspace 根或项目源码根。

推荐结构如下：

```text
work-system/
  projects/
    active/
      <project>.md
      <project>/
        runtime/
          <task-id>/
            task-plan.md
            findings.md
            progress.md
            outcome.md
            attachments/
```

说明如下。

## 6.1 项目档案文件

```text
work-system/projects/active/<project>.md
```

继续作为该项目的正式项目 dossier。

## 6.2 项目运行目录

```text
work-system/projects/active/<project>/
```

作为该项目的运行时配套目录。

## 6.3 runtime 目录

```text
work-system/projects/active/<project>/runtime/
```

用于承载该项目下各个复杂任务的运行态上下文。

## 6.4 task 目录

```text
work-system/projects/active/<project>/runtime/<task-id>/
```

一个复杂任务一个 task 目录。

`<task-id>` 建议格式：

```text
YYYY-MM-DD-<short-slug>
```

例如：

- `2026-04-06-planning-runtime-integration`
- `2026-04-07-yaoyun-risk-clustering`
- `2026-04-07-nurse-station-mvp-run`

---

## 7. 文件职责设计

## 7.1 `task-plan.md`

作用：

- 任务目标
- 当前阶段
- 阶段拆解
- 关键决策
- 错误记录
- 完成定义

这是当前任务的**目标锚文件**。

## 7.2 `findings.md`

作用：

- 调研发现
- 文档/网页/代码阅读发现
- 视觉/浏览结果转文字
- 技术判断依据
- 可复用资源链接

这是当前任务的**研究卸载文件**。

## 7.3 `progress.md`

作用：

- 本轮做了什么
- 改了哪些文件
- 做了哪些测试/验证
- 发生了哪些错误
- 当前停在哪

这是当前任务的**过程日志文件**。

## 7.4 `outcome.md`

这是建议新增的本地化文件，原项目中没有强制要求，但对当前体系很重要。

作用：

- 输出正式结果摘要
- 说明任务最终产物
- 明确需要回写到哪些正式层
- 记录是否已同步项目档案 / 交付物 / memory

这是 runtime 与正式工作流之间的**交付桥接文件**。

## 7.5 `attachments/`

用于放置当前任务产生的辅助材料，例如：

- 临时草图
- 导出的对比文本
- 分析中间结果
- 截图转存文件

避免把所有中间材料都塞进 `findings.md`。

---

## 8. `planning-runtime` 与现有机制的边界

## 8.1 与 `memory/YYYY-MM-DD.md` 的边界

`memory/YYYY-MM-DD.md` 记录的是：

- 今天发生了什么
- 有哪些关键事件值得保留连续性

`planning-runtime` 记录的是：

- 某个复杂任务当前如何推进

因此：

- daily memory 负责“今天发生了什么”
- runtime 负责“这件事当前怎么推进”

## 8.2 与 `MEMORY.md` 的边界

`MEMORY.md` 只保留长期稳定的判断，例如：

- 目标偏好
- 决策方式
- 长期规则
- 可跨项目迁移的重要经验

runtime 文件不应直接承担长期记忆职责。

## 8.3 与 `work-control` 的边界

`work-control` 负责：

- 任务/进展/风险/里程碑/价值/决策 的正式记录
- `今日聚焦`
- `今日总结`
- reminders
- 项目档案维护

`planning-runtime` 负责：

- 复杂任务开始时建运行态工作区
- 复杂任务中维持目标、发现、过程、错误和阶段状态
- 复杂任务结束时推动回写正式记录

二者关系是：

**`planning-runtime` 负责执行态，`work-control` 负责正式态。**

## 8.4 与 coding agent 的边界

`planning-runtime` 不直接执行代码，只负责：

- 让进入执行前的目标更清楚
- 让执行中的发现和错误可持续
- 让结果更容易回收与验证

真正执行代码仍由：

- `exec + Codex`
- `exec + OpenCode`
- 或其他执行引擎

承接。

---

## 9. 推荐触发条件

以下场景建议自动或半自动触发 `planning-runtime`：

1. 预计需要 `>5` 次工具调用
2. 任务明显分阶段（研究/分析/实现/验证）
3. 任务需要跨轮续接
4. 任务涉及大量阅读/搜索/代码定位
5. 任务可能调用 coding agent 或多 Agent 协作
6. 任务结束后需要正式回写项目档案或交付物

以下场景不建议触发：

1. 单文件小修
2. 简单问答
3. 一次性快速查找
4. 纯聊天层判断，不进入正式执行

---

## 10. 从 `planning-with-files` 可直接复用的资产

## 10.1 方法论资产（建议直接吸收）

1. Filesystem as external memory
2. Re-read plan before major decisions
3. Log all errors
4. Never repeat failures
5. 2-Action Rule
6. 5-Question Reboot Test
7. Completion verification before stop

## 10.2 文件模板思想（建议本地化改造后复用）

可复用：

- `task_plan.md` 的阶段结构
- `findings.md` 的研究卸载结构
- `progress.md` 的阶段日志结构

需要本地化的点：

- 文件名统一改为 kebab-case：`task-plan.md`
- 字段改成更贴当前工作流的中文/双语结构
- 增加 `outcome.md`
- 增加“回写状态”字段

## 10.3 脚本资产（建议择优复用）

### 可复用

1. `session-catchup.py`
2. `check-complete.ps1`
3. `init-session.ps1`

### 复用方式

不是原样照搬，而是改造成：

- 面向 `runtime/<task-id>/` 路径
- 不再默认当前目录生成文件
- 增加对本地项目档案的联动判断

---

## 11. 必须本地化改造的部分

## 11.1 文件落点改造

原项目：

- 默认在项目根目录生成 3 个 planning 文件

本地化后：

- 统一生成到：
  `work-system/projects/active/<project>/runtime/<task-id>/`

## 11.2 hooks 依赖改造

原项目很多行为依赖 IDE hook。

本地化后不应把能否生效押在 hook 上，而应：

1. 在 `SKILL.md` 中明确要求“复杂任务先建 runtime 工作区”
2. 用脚本辅助初始化和检查
3. 通过任务模板与运行规则驱动，而不是完全依赖 IDE 生命周期触发

## 11.3 单任务模型改造

原项目偏单任务、单项目连续执行。

本地化后必须支持：

- 同一项目多个 runtime task 并存
- 任务结束后回写项目档案
- 任务中间暂停，后续继续续接

## 11.4 与正式记录层的桥接

原项目更关注任务本身完成；
本地体系更需要：

- 结果是否写入项目档案
- 是否需要进 `今日总结`
- 是否要沉淀到 `MEMORY.md`

因此需要新增 `outcome.md` 与“回写检查”逻辑。

---

## 12. 推荐的 skill 目录结构

建议在本地 workspace 建如下结构：

```text
skills/
  planning-runtime/
    SKILL.md
    reference.md
    examples.md
    templates/
      task-plan.md
      findings.md
      progress.md
      outcome.md
    scripts/
      init-runtime-task.ps1
      check-runtime-complete.ps1
      session-catchup.py
```

说明如下。

## 12.1 `SKILL.md`

定义：

- skill 定位
- 触发条件
- 与 `work-control` 的边界
- 启动 runtime task 的标准动作
- 执行中更新文件的规则
- 结束前检查规则

## 12.2 `reference.md`

沉淀：

- Manus 式上下文工程原则
- 本地化 runtime 规则
- 为什么不直接把所有内容塞进 context

## 12.3 `examples.md`

给出本地典型案例，例如：

- 日志巡检分析任务
- 护士站高危问题分批治理任务
- 开发框架 MVP 跑一次真实需求

## 12.4 `templates/`

存放 4 个模板文件。

## 12.5 `scripts/`

存放本地化后的辅助脚本。

---

## 13. 4 个模板文件建议字段

## 13.1 `task-plan.md`

建议字段：

- 任务名称
- 所属项目
- 任务目标
- 当前阶段
- 阶段列表
- 成功标准
- 范围边界
- 关键问题
- 关键决策
- 错误记录
- 完成定义

## 13.2 `findings.md`

建议字段：

- 需求/任务理解
- 调研发现
- 代码/文档阅读发现
- 技术判断依据
- 风险发现
- 资源链接
- 视觉/浏览结果转写

## 13.3 `progress.md`

建议字段：

- 当前会话
- 当前阶段状态
- 已执行动作
- 修改文件
- 测试/验证结果
- 错误日志
- 当前停点
- 下一步建议

## 13.4 `outcome.md`

建议字段：

- 最终产物
- 关键结论
- 未解决项
- 风险残留
- 需要同步到哪里
- 已同步状态

---

## 14. 一条真实任务的运行链路

以下以“病区护士高危问题按批次分类治理”举例。

## 14.1 任务进入

用户提出：

“下周开始推进病区护士高危代码修复清单，先让 AI 做分类、聚类、批次拆分。”

主控判断：

- 这是复杂任务
- 需要跨轮推进
- 预计会有大量阅读和结构化判断
- 适合进入 `planning-runtime`

## 14.2 建立 runtime task

在以下位置新建：

```text
work-system/projects/active/bingqu-hushi-gaowei-xiufu-genzong/
  runtime/
    2026-04-07-risk-clustering/
```

初始化：

- `task-plan.md`
- `findings.md`
- `progress.md`
- `outcome.md`

## 14.3 执行中更新

随着阅读问题清单、聚类、形成批次策略：

- 目标和阶段写进 `task-plan.md`
- 分类维度、聚类规则写进 `findings.md`
- 每轮处理了哪些问题、出了什么判断、有哪些测试或验证，写进 `progress.md`
- 如果某轮方法失效，错误与调整写进 `task-plan.md` / `progress.md`

## 14.4 任务结束前检查

在交付前检查：

1. 阶段是否都已完成或明确停留在哪
2. 是否形成了可复用的分类规则
3. 是否产出了正式交付物
4. 是否需要更新项目档案
5. 是否需要写入 `今日总结`

## 14.5 结果回写

任务结束后：

- 将正式结果写入项目档案或交付物
- 在 `outcome.md` 标记已同步位置
- 视情况将稳定经验写入 `MEMORY.md` 或 daily memory

这时 runtime task 可以视为“当前阶段已收口”。

---

## 15. 推荐的实施顺序

建议分三步实施。

## 15.1 第一步：先建 skill 骨架

建立：

- `skills/planning-runtime/`
- `templates/`
- `scripts/`
- `reference.md`
- `examples.md`

## 15.2 第二步：先做一个真实任务试运行

优先拿以下任务之一试跑：

1. 病区护士高危问题分类治理
2. 护士站专项开发框架 MVP 跑一次真实需求
3. 日志巡检工具下一轮结构优化

## 15.3 第三步：再决定是否深度联动 `work-control`

试跑有效后，再考虑：

- `work-control` 是否在复杂任务场景下自动建议启用 `planning-runtime`
- `今日总结` 是否读取 runtime outcome
- 项目档案模板是否补“最近 runtime task”入口

---

## 16. 最终结论

`planning-with-files` 对当前体系真正有价值的，不是“多三个文件”，而是它把复杂任务执行这件事，从模糊、易漂移、靠临时上下文维持，变成：

- 有运行态工作区
- 有目标锚点
- 有研究卸载文件
- 有过程日志
- 有错误持久化
- 有阶段闭环检查
- 有正式回写桥接

因此，面向当前 `OpenClaw` 体系，最合理的落地方向不是“记忆框架表面增强”，而是建设一个与 `work-control` 并列、专门承接复杂任务执行态的本地 skill：

`planning-runtime`

并将其运行文件落到：

`work-system/projects/active/<project>/runtime/<task-id>/`

这才是它真正能落地生效的集成方式。

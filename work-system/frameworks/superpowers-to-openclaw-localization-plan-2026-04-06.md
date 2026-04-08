# `superpowers` → `OpenClaw` 本地化映射方案（2026-04-06）

## 1. 文档目的

本文档用于把 `E:\winning-code\ai\superpowers-main` 的核心工程化设计，映射到本地 `OpenClaw` 工作体系与技能目录：

- 本地技能目录：`C:\Users\pc\.openclaw\workspace\skills`
- 当前主控方式：`OpenClaw main session`
- 当前真实执行链：`main -> executor/opencode -> 回收 -> 复核 -> 沉淀`
- 当前真实样本：`TFS 需求 1543024` 的护士站前端 MVP 流程

目标不是“照搬 superpowers”，而是提炼其最有价值的工程化骨架，改造成适配当前 OpenClaw 环境、当前人机协作方式、当前护士站专项目标的本地化技能系统。

---

## 2. 结论先行

### 2.1 一句话结论

`superpowers` 最值得借的，不是 skill 名称本身，而是它把**设计、计划、执行、审查、验证、收尾**写成了强约束工作流。

### 2.2 本地化原则

对当前 `OpenClaw`，建议采用：

- **借流程骨架，不整包照搬**
- **借角色分工，不生搬宿主机制**
- **借 review / verification 纪律，不照抄平台工具名**
- **围绕护士站场景重新命名、重写、收紧**

---

## 3. `superpowers` 的核心设计精髓

## 3.1 过程门禁先于代码执行

在 `superpowers` 中，常见主链是：

`brainstorming -> writing-plans -> subagent/executing -> verification -> finishing`

这背后的精髓是：

1. 不允许需求还模糊时直接开始编码
2. 不允许计划缺失时直接下放执行
3. 不允许执行者自报完成就算完成
4. 不允许没有验证就进入收尾

这套纪律非常适合当前护士站专项开发框架。

## 3.2 skill 不是知识库，而是流程规约

`superpowers` 的 skill 不是“告诉 agent 一些建议”，而是：

- 什么情况下必须进入该 skill
- 进入后必须按什么顺序做
- 哪些行为是禁止的
- 哪些产物必须落地

这点对本地 `OpenClaw` 很关键：后续 skill 要承载的是**流程约束**，不是“说明文档”。

## 3.3 子代理设计的精髓不在“多”，而在“隔离 + 审查顺序”

`subagent-driven-development` 真正强的地方在于：

- 每个任务一个 fresh subagent
- 主控给完整任务文本，不让子代理自己乱读全局上下文
- 每个任务后做两阶段 review：
  - 先 `spec compliance`
  - 再 `code quality`
- review 不通过就回环，不进入下一步

这比“多 agent 并行很酷”更有价值。

## 3.4 技能本身可测试、可迭代

`superpowers` 附带：

- prompt 模板
- review 模板
- 集成测试
- 设计稿 / 计划稿 / 迭代记录

说明它把“技能资产本身也当工程对象维护”。

这意味着本地 skill 体系后续也不应只写 `SKILL.md`，还要有：

- supporting references
- prompt 模板
- 触发示例
- 反模式清单
- 使用后回写改进

---

## 4. 与今天 `1543024` MVP 的映射关系

## 4.1 今天已经自然跑出的链路

围绕 `1543024`，今天实际跑出的流程是：

1. 用 `tfs2018-integration` 取回需求与产品分析线索
2. 结合护士站框架文档，判断这不是“只查单”，而是要跑一条真实 MVP
3. 做需求澄清：
   - 保留“类型切换 + 日期范围”交互
   - 只在“已出院”场景显示
4. 用 `opencode + glm-5` 在指定仓库定位实现入口
5. 收敛为明确改动面：
   - `homeHeader.vue`
   - `searchComp.vue`
6. 抽象出主控 / 定位 / 实现 / 验证四类角色

这条链路说明，本地框架已经有雏形，只是还没被写成正式可复用 skill。

## 4.2 今天暴露出的短板

今天这条 MVP 也明确暴露了当前还缺的东西：

1. 缺正式的“需求准入”技能与统一输出格式
2. 缺正式的“实现任务拆解”技能
3. 缺主控如何给 executor 下发任务的标准模板
4. 缺“定位结果 -> 实现任务 -> 验证任务”的标准衔接协议
5. 缺本地 reviewer / verifier 的独立技能
6. 缺对 skill 本身的测试与验收方式

---

## 5. `superpowers` 到 `OpenClaw` 的映射表

| `superpowers` 能力 | 核心价值 | 当前 OpenClaw 对应方式 | 本地化建议 |
|---|---|---|---|
| `using-superpowers` | 强制先选流程 | 当前靠系统规则 +人工判断 | 不直接照搬，融入主控默认工作法 |
| `brainstorming` | 需求澄清、先设计后执行 | 当前靠主会话临时收口 | 落为 `nurse-station-brainstorming` |
| `writing-plans` | 输出可执行计划 | 当前靠聊天中临时拆解 | 落为 `nurse-station-writing-plans` |
| `subagent-driven-development` | 主控-执行-复核编排 | 当前 `main -> executor/opencode` 半手工 | 落为 `nurse-station-subagent-execution` |
| `verification-before-completion` | 防止假完成 | 当前靠主会话人工把关 | 落为 `nurse-station-verification` |
| `requesting-code-review` | 独立 code review 纪律 | 当前还未固化 | 后续补 `nurse-station-review-gate` |
| `systematic-debugging` | 根因导向排障 | 当前已有可直接借用 | 与本地护士站技能配合使用 |
| `finishing-a-development-branch` | 收尾和分支整理 | 当前还没进入该层 | 先不引入，等开发闭环成熟后再补 |

---

## 6. 已落地的本地技能骨架

本次已在 `C:\Users\pc\.openclaw\workspace\skills` 下新增第一批本地化 skill：

1. `nurse-station-brainstorming`
   - 用于需求准入、边界澄清、成功标准收口
2. `nurse-station-writing-plans`
   - 用于把已澄清事项转成实现计划
3. `nurse-station-subagent-execution`
   - 用于主控如何下发定位 / 实现 / 验证任务
4. `nurse-station-verification`
   - 用于检查结果是否真的符合需求

这 4 个 skill 组成了第一版最小骨架，已经足以承接类似 `1543024` 的 MVP 流。

---

## 7. 为什么不建议整包复制 `superpowers`

## 7.1 宿主差异

`superpowers` 的很多描述是围绕 Claude Code / Codex / OpenCode 插件生态写的。

而当前本地 `OpenClaw`：

- 主控是 chat 会话
- 执行依赖 `exec`
- subagent 能力与 `superpowers` 设定不完全同构
- 真实现状是 `main + executor` 更接近“人工编排的专业 Agent”

所以整包复制会产生大量宿主错配。

## 7.2 场景差异

`superpowers` 面向通用软件开发。

你这里要做的是：

- 护士站专项开发框架
- 以稳定性、效率、流程规范、成果复用为目标
- 要能承接 TFS 需求、历史问题治理、专项复盘

因此必须做场景本地化。

## 7.3 认知负担差异

如果整包搬入，技能库会瞬间变大，但当前真正高频使用的核心技能其实只有少数几类。

优先做“小而硬”的技能，比“多而散”的技能更有价值。

---

## 8. 还缺什么

当前只是第一版骨架，离“真正可长期复用的护士站框架 skill 库”还缺以下关键资产。

## 8.1 还缺的 skill

### A. `nurse-station-review-gate`

建议新增。

职责：
- 将 review 明确拆成两层：
  - 需求符合性 / 方案符合性
  - 代码质量 / 风险质量
- 明确 reviewer 不信 implementer 自报
- 要求 reviewer 读真实代码 / 真实变更，而非只看摘要

### B. `nurse-station-locator`

建议新增。

职责：
- 专门负责仓库入口定位
- 输出：入口文件、关键组件、参数链路、风险点、待确认点
- 不做实现

今天 `1543024` 的“用 opencode 做代码定位”已经证明这个角色单独存在很有价值。

### C. `nurse-station-implementer`

建议新增。

职责：
- 只接受已明确的实现任务
- 必须报告改了什么、没改什么、验证了什么、还有什么不确定
- 不负责做需求澄清和大范围探索

### D. `nurse-station-mvp-retrospective`

建议新增。

职责：
- 每次完整任务后，把真实过程回写成框架资产
- 特别记录：
  - 哪些信息是进入执行前必须有的
  - 哪些问题反复造成返工
  - 哪些 Agent 边界最有效

## 8.2 还缺的 supporting docs / prompt 模板

建议每个关键技能继续补：

1. `references/trigger-examples.md`
2. `references/output-template.md`
3. `references/anti-patterns.md`
4. `prompts/locator-prompt.md`
5. `prompts/implementer-prompt.md`
6. `prompts/reviewer-prompt.md`
7. `prompts/verifier-prompt.md`

当前只写 `SKILL.md` 还不够，后续需要这些 supporting assets 才能把调度真正稳定下来。

## 8.3 还缺的工作流载体

建议在 `work-system/templates/` 下补：

1. `nurse-station-requirement-intake-template.md`
2. `nurse-station-implementation-plan-template.md`
3. `nurse-station-agent-handoff-template.md`
4. `nurse-station-verification-template.md`
5. `nurse-station-mvp-retrospective-template.md`

这样 skill 输出就能稳定落到工作系统，而不是只停在聊天里。

## 8.4 还缺的测试与验证机制

建议后续补一套轻量验证法，至少验证：

1. 需求澄清 skill 是否真的能把模糊需求收口
2. 计划 skill 是否真的能产出可执行任务单
3. 执行 skill 是否真的能把任务明确发给 executor
4. 验证 skill 是否真的能发现“执行者说完成但其实没完成”的情况

也就是说：**要开始测试 skill，而不只是使用 skill。**

---

## 9. 后续补强路线

建议按以下顺序增强。

### 第一阶段：把最小骨架补完整

目标：让类似 `1543024` 的需求可以稳定跑完一整条开发链。

动作：
1. 新增 `nurse-station-review-gate`
2. 新增 `nurse-station-locator`
3. 新增 `nurse-station-implementer`
4. 为现有 4 个 skill 补充输出模板和反模式说明

### 第二阶段：把技能和工作系统打通

目标：不只是“会执行”，而是“会沉淀”。

动作：
1. 在 `work-system/templates/` 增加标准模板
2. 让 skill 输出直接落到模板文件
3. 用真实任务持续修正模板

### 第三阶段：把角色编排固定下来

目标：把“主控不承担全部执行逻辑”落到稳定机制。

动作：
1. 明确四类核心角色：Controller / Locator / Implementer / Verifier
2. 定义角色之间的 handoff 契约
3. 明确何时串行、何时可并行
4. 明确什么信息必须由 Controller 保留，什么可以传给子角色

### 第四阶段：建立 skill 自己的反馈闭环

目标：让技能资产持续进化。

动作：
1. 每次完整 MVP 后做 retrospective
2. 把踩坑写回 skill 或 references
3. 形成“真实任务 -> 技能改进 -> 下次更稳”的循环

---

## 10. 当前最重要的判断

对于你现在的阶段，最重要的不是“把 superpowers 装进来”，而是：

**把今天已经证明有效的开发链，提炼成可复用的本地 skill 体系。**

换句话说：

- `superpowers` 是高质量参考源
- `OpenClaw + 本地 skills + work-system` 才是你真正的本地底座
- 先把护士站专项框架本地化跑通，再考虑是否吸收更多通用 skill

---

## 11. 建议的下一步

建议下一步立即做这三件事：

1. 围绕 `1543024` 产出第一份正式的本地实现计划文档
2. 基于今天的定位结果，生成第一版 `locator / implementer / verifier` handoff 模板
3. 继续补 `nurse-station-review-gate`、`nurse-station-locator`、`nurse-station-implementer`

当这三步完成后，这套框架就会从“已经有方向”进入“已经有最小工程化闭环”。

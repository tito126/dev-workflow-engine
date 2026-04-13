# nurse-station-* 技能可落地优化方向（2026-04-13）

## 一、目标

把本轮 `1516840` 暴露出来的问题，沉淀成对 `nurse-station-*` 技能可复用、可执行、可阻断的优化规则，减少后续对个人记忆和临场判断的依赖。

---

## 二、优化方向总览

### 方向 1：把“扫哪里”从记忆变成显式配置
**问题来源**：过去多仓扫描路径容易依赖历史经验和个人记忆。

**可落地优化**：
1. 引入工作区 YAML：`work-system/config/nurse-station-repo-routing.yaml`
2. 引入模板文件：`skills/nurse-station-orchestrator/references/nurse-station-repo-routing.template.yaml`
3. `orchestrator` 在 YAML 缺失时自动创建 `draft` 模板，然后立即阻断
4. `locator / implementer / writing-plans` 统一要求 YAML 必须 `ready`
5. `findings.md` 强制记录首扫根、扩扫根、扩扫原因、排除根

**已落地内容**：
- YAML 模板已创建
- orchestrator / locator / writing-plans / implementer 已加入阻断规则

**后续建议**：
- 再补一个“从模板复制到工作区”的更明确操作示例
- 在 planner / findings 模板里固化 scan log 章节

---

### 方向 2：把“文案能不能改”从默认自由发挥，变成显式约束
**问题来源**：`1516840` 中，位置被产品接受，但改写后的文案未被接受。

**可落地优化**：
1. 在 `brainstorming` 阶段新增“文案 / 提示类任务额外检查点”
2. 明确判断：
   - 当前文案是否已有正式原文
   - 是否允许改写
   - 验收是否拆成“位置通过 / 文案通过”两层
3. 在 `writing-plans` 中新增字段：
   - `受保护文案：有/无`
   - `是否允许改写文案：是/否`
4. 在 `implementer` 中加入“文案保护规则”

**已落地内容**：
- brainstorming 已补“正式原文默认受保护”规则
- writing-plans 已补“受保护文案 / 是否允许改写”字段
- implementer 已补“默认不允许改写产品原文”规则

**后续建议**：
- 给 implementer 增加“如果原文已给出，优先直接复制原文，不要自行转写”的执行模板
- 如后续涉及多语言或 i18n，补“原文与 key 管理”约束

---

### 方向 3：把“位置通过”和“文案通过”拆开验收
**问题来源**：如果只看承载位置，会误判任务已基本完成。

**可落地优化**：
1. 在 `verification` 中把以下维度拆开：
   - 位置 / 承载方式是否通过
   - 文案内容是否按原文落地
   - 示例 / 编号 / 条目是否完整
   - 是否出现“位置通过但文案不通过”
2. 在 `review-gate` 中把位置验收和文案验收视为两道独立子检查
3. 一旦产品给了标准案例，不允许用概括性示例替代

**已落地内容**：
- verification 已补“位置通过 / 文案通过 / 示例完整性”拆分规则
- review-gate 已补“位置对了但原文被改写仍算不通过”的检查要求

**后续建议**：
- 未来可以把 verification 的输出模板进一步固定成“位置 / 文案 / 示例 / 运行态”四段

---

### 方向 4：把“draft 只能停”变成绝对硬规则
**问题来源**：如果 skill 在 YAML 为 draft 时还能继续，规则就会再次被记忆和经验绕开。

**可落地优化**：
1. orchestrator 明确：YAML 缺失时自动创建模板，但创建后必须停
2. locator 明确：draft 不允许“先扫一个仓看看”
3. writing-plans 明确：draft 只能输出“先维护 YAML”的阻断结论
4. implementer 明确：不能以“仓库都知道了”为理由继续

**已落地内容**：
- 4 个关键技能都已加入 draft 硬阻断规则

**后续建议**：
- 如果未来增加 subagent-execution，也应显式继承相同阻断逻辑

---

## 三、针对 1516840 直接提炼出的规则

1. 文案类需求默认不改写产品原文
2. 位置验收与文案验收必须分开
3. 产品给了编号案例时，不能压缩成概括性示例
4. YAML draft 只能停，不能继续多仓推进
5. 即使方案方向正确，只要文案边界被破坏，也不能算需求完成

---

## 四、建议的下一轮落地顺序

### 第一批（已经开始 / 已完成）
- YAML 模板
- orchestrator 自动创建模板 + 阻断
- locator / writing-plans / implementer 的 YAML 阻断
- brainstorming / implementer / verification / review-gate 的文案保护规则

### 第二批（建议后续继续做）
1. 给 `plan.md`、`findings.md`、`verification-evidence.md` 增加更固定的字段模板
2. 给 `subagent-execution` 也补 YAML 阻断与受保护文案规则
3. 在 orchestrator 增加“任务类型识别”分支：
   - 页面/文案类
   - 配置/规则类
   - SQL/性能类
   - 纯定位类
4. 如果后续真实使用人变多，再把 YAML 校验做成更结构化的 checklist

---

## 五、当前结论

这轮复盘后，`nurse-station-*` 技能的可落地方向已经比较明确：
- 用 YAML 管“扫哪里”
- 用 brainstorming / plans / implementer 管“能不能改写”
- 用 verification / review-gate 管“怎么验收文案与位置”

这样后续就不再依赖“我记得”、“这次先跑一下”、“意思差不多”这种不稳定路径。
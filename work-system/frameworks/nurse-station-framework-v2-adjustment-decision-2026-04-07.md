# 护士站框架 v2 调整决议（2026-04-07）

## 1. 这份决议解决什么问题

截至今天上午，护士站框架已经完成一轮集中诊断，产出了三份上层文档：

- `nurse-station-framework-execution-chain-diagnosis-2026-04-07.md`
- `nurse-station-task-routing-spec-2026-04-07.md`
- `nurse-station-requirement-fit-checkpoint-spec-2026-04-07.md`

随后又继续把部分结论正式回写到了 skill 层。

这份文档的作用不是重复分析，而是形成一份**正式拍板口径**，明确：

1. 今天到底已经决定了什么
2. 哪些内容已经进入 skill 改造
3. 哪些内容还没落地
4. 下一步应该怎样继续推进，而不是再散着扩写

---

## 2. v2 的总判断

本轮调整后的护士站框架，不再应被理解为：

- 一条固定顺序的重执行链
- 所有任务默认都走同样的阶段组合
- coding 之后再靠 review / verification 去兜底需求不清

而应被正式改写为：

> **一个按任务分级自适应分流、在 coding 前显式检查 requirement-fit、在中重任务中优先使用 wrapper-based 外部执行器、并用分层 review / verification 控制风险的执行框架。**

---

## 3. 本轮正式拍板的四条核心决议

## 3.1 决议一：任务必须先分级，再进入执行链

后续护士站任务默认不再直接进入完整流程，而必须先做：

- `light`
- `medium`
- `heavy`

三档判断。

### 含义
- `light`：默认不走重链
- `medium`：默认走 requirement-fit + minimal planning + narrow execution
- `heavy`：默认走 runtime + planning + formal review / verification / retrospective

### 结果
护士站框架从“固定流程”升级为“带路由的状态机”。

---

## 3.2 决议二：coding 前必须有 requirement-fit checkpoint

后续不得再默认认为“需求大概清楚了就可以开始改”。

进入 coding 前，至少要明确：
- 场景
- 模块 / 页面
- in-scope / out-of-scope
- 验收观察点

对 UI / 交互类任务，还必须尽量显性化：
- 控件 / 行为对象
- 插入位置 / 相对顺序
- 显隐规则
- 旧行为是否保留 / 去重

### 结果
没有 requirement-fit checkpoint，就不应进入 implementer。

---

## 3.3 决议三：`opencode` 在中重任务中默认走 wrapper 路径

后续如果护士站任务使用 `opencode` 作为外部执行器：

- `light`：默认不触发 wrapper
- `medium`：默认优先考虑 wrapper
- `heavy`：默认必须走 wrapper

这里的 wrapper 指当前已产出的最小链路：
- `start-opencode-task.ps1`
- `opencode-run.ps1`
- `get-opencode-task.ps1`
- `stop-opencode-task.ps1`

### 含义
后续不再把裸 `exec + poll` 当成 `medium / heavy` 任务的默认 `opencode` 路线。

---

## 3.4 决议四：review / verification 不再只做后置兜底

后续 review-gate 正式升级为三段：
- Gate 0：pre-code requirement-fit mini gate
- Gate 1：post-implementation requirement/spec fit
- Gate 2：post-implementation code quality/risk

verification 则正式承担：
- 检查 requirement / scene / technical fit
- 检查 acceptance anchors 是否存在
- 若前置验收锚点缺失，不得判完成

### 结果
后段门禁不再只是“最后看一眼”，而是和前段 requirement-fit 形成闭环。

---

## 4. 本轮已完成的 skill 改造

## 4.1 已改造完成

### `skills/nurse-station-brainstorming/SKILL.md`
已补：
- task level
- suggested route
- wrapper execution recommendation
- medium / heavy + opencode 时偏向 wrapper 路由

### `skills/nurse-station-writing-plans/SKILL.md`
已补：
- execution carrier
- minimal plan 倾向
- medium / heavy + opencode 默认走 `start-opencode-task.ps1`

### `skills/nurse-station-subagent-execution/SKILL.md`
已补：
- wrapper-based `opencode` 路由
- bare `exec + poll` 不再作为默认长任务执行方式
- dispatch payload 中加入 task level / execution carrier

### `skills/nurse-station-review-gate/SKILL.md`
已补：
- Gate 0 pre-code requirement-fit mini gate
- wrapper 产物 (`status.json` / `result.md`) 作为 review evidence

### `skills/nurse-station-verification/SKILL.md`
已补：
- 没有前置验收锚点不得判完成
- acceptance anchors reviewed / missing acceptance anchors
- 缺锚点时回退到 requirement-fit / planning，而不是只怪实现层

---

## 4.2 当前相对稳定、暂不优先大改

### `skills/nurse-station-locator/SKILL.md`
当前方向基本合理，问题更多在调用时机，而不是 skill 本体。

### `skills/nurse-station-implementer/SKILL.md`
当前不是主要故障源，后续只需在更强的 phase contract 下继续观察是否还需要进一步收紧。

### `skills/nurse-station-mvp-retrospective/SKILL.md`
当前定位正确，后续应继续承担“真实 run 反哺框架”的角色。

### `skills/planning-runtime/SKILL.md`
当前不急着继续扩写，下一步更重要的是在真实任务里验证它与 v2 路由的配合效果。

---

## 5. 当前还没完成的部分

## 5.1 还未形成单独 skill / 模板的 requirement-fit 节点

虽然规范已经产出、部分 skill 也已吸收，但 requirement-fit checkpoint 目前仍主要是：
- 规范文档
- skill 中的规则吸收

还没有变成一个完全独立的模板化执行资产。

### 当前判断
暂时可以不急着单独再造 skill；优先让它先在现有链路里跑出真实效果。

---

## 5.2 还未完成 v2 链路的真实样本验证

目前是：
- 规则已成形
- skill 已局部改造
- `opencode wrapper` 基础设施已补齐

但还没有正式拿一个 v2 样本完整跑一遍，去验证：
- requirement-fit 是否真能减少 drift
- medium 任务走 wrapper 是否真降低 poll 摩擦
- Gate 0 是否真能拦住不该直接 coding 的任务

---

## 5.3 wrapper 已进入路由规则，但尚未形成平台级全自动拦截

当前已完成的是：
- skill 层接入
- 主控可按这套规则执行

当前还没完成的是：
- 更底层的平台级“凡是 opencode 都自动重写到 wrapper”

### 当前判断
这一点先不着急下沉到底层；当前阶段先让框架层真正用起来更重要。

---

## 6. v2 之后的推荐继续顺序

## 第一阶段：先做真实验证，不再横向扩写

下一步不应再继续横向增加文档或 skill，而应优先挑一个真实任务，按 v2 路由完整跑一遍。

### 推荐样本
- `1543024`

但它的身份要调整为：
- **v2 中任务验证样本**
- 而不是“普通前端需求实现任务”

### 验证重点
不是“做没做完”本身，而是：
- 路由是否更准确
- requirement-fit 是否更充分
- wrapper 是否降低了 poll 摩擦
- Gate 0 / Gate 1 / Gate 2 是否真的各司其职

---

## 第二阶段：基于真实样本再决定是否增设独立模板/skill

只有在 v2 样本跑过之后，再决定：
- requirement-fit checkpoint 是否值得单独模板化
- runtime 是否需要轻运行态版本
- implementer / locator 是否还要继续收紧

也就是说：

> 现在该从“继续设计框架”切到“拿真实任务验证框架”。

---

## 7. 一句话结论

护士站框架 v2 今天已经正式完成了一次方向性调整：

> 从“默认重链 + 后置兜底”转向“任务分级分流 + coding 前 requirement-fit + medium/heavy wrapper execution + 分层门禁 review/verification”。

下一步最应该做的，不是继续扩文档，而是拿一个真实中任务去验证这套新链路是否真正降低执行跑偏。 

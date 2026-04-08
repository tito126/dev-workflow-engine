# 护士站框架执行链路诊断与 Skill 设计问题清单（2026-04-07）

## 1. 这份诊断的目标

这份文档不再围绕某个单一需求做局部修补，而是回到你最初的核心诉求：

> 构建一套成熟、通用、可适配不同任务类型的护士站执行框架。

因此，这里重点回答四个问题：

1. 当前执行链路真正出问题的环节在哪里。
2. 哪些问题是流程层问题，哪些问题是 Skill 设计问题。
3. 哪些 Skill 当前设计不合理，为什么不合理。
4. 后续框架优化应该先调哪里，再调哪里。

---

## 2. 先给总体判断

当前护士站框架并不是“方向错了”，而是处于一个典型的**结构已搭起、调度逻辑仍未稳定**的阶段。

也就是说：

- 角色拆分方向是对的
- `brainstorming → planning → locate → implement → review → verify → retrospective` 这个主链条也是对的
- runtime / evidence / retrospective 的方向也对

但现在的关键问题是：

> **框架的阶段节点已经有了，阶段之间的“准入条件、放行条件、回退条件”还不够硬。**

于是表面上像是有完整流程，实际上却容易发生：

- 任务该不该进某阶段，没有硬判断
- 进了某阶段后，如果前提不成立，也没有被及时拦下
- skill 虽然各有职责，但主控还缺少一套更明确的路由纪律

所以当前最需要的，不是继续补“更多 skill”，而是排查并修正执行链中的**四个关键失稳点**。

---

## 3. 当前执行链的四个关键失稳点

## 3.1 失稳点一：准入阶段只判断“清不清楚”，没有判断“该走哪条链”

当前 `nurse-station-brainstorming` 更像一个需求澄清器，它会判断：
- 业务目标是否清楚
- 模块是否清楚
- 成功标准是否初步存在

这没问题，但还不够。

它缺少一个更关键的判断：

- 这是轻任务 / 中任务 / 重任务？
- 是否需要 runtime？
- 是否需要 planning？
- 是否可以跳过部分阶段直接进入窄实现？
- 是否必须先补 requirement-fit artifact？

结果就是：

> 现在的准入阶段更像“能不能做”，而不是“应该怎么做”。

这是第一处结构性问题。

### 本质
不是 intake 不存在，而是 intake 的输出维度不够。

### 框架后果
会导致不同复杂度任务被不加区分地送入近似同一条执行链，只是“走得快一点”或“走得慢一点”，而不是根本上分流。

---

## 3.2 失稳点二：需求与验证之间没有前置锚点，导致 implementer 和 verifier 都容易靠猜

这是你刚才强调得最准确的一点。

当前很多链路问题，表面看发生在 implementation 或 review，其实源头更早：

- 需求分析阶段没有显性记录 UI / 参数 / 场景的关键验证点
- planning 阶段没有把这些验证点转成 implementer 可执行、verifier 可复核的条目
- verification 阶段自然就没有稳定参照物

于是会出现三种典型失真：

1. implementer 在补空白
2. review 在事后猜 intent
3. verification 在判断“像不像”而不是“是不是”

### 本质
框架里已经有“需求澄清”和“最终验证”，但还缺一个：

> **编码前的 requirement-fit checkpoint**

这不是 review 的替代，而是 review 之前的前置闸门。

### 框架后果
如果这层缺失，那么后面的 implement / review / verify 再怎么加厚，仍然会持续吸收上游未澄清的不确定性。

---

## 3.3 失稳点三：执行阶段角色虽然拆了，但执行合同还不够硬

`locator`、`implementer`、`review-gate`、`verification` 这几个角色的方向是对的。

问题不在于“有没有拆角色”，而在于：

- handoff contract 还不够硬
- stop condition 还不够硬
- 回退规则虽然已有文档，但还没有上升成默认纪律

例如当前 implementer skill 虽然写了：
- 不要 silent scope expansion
- 如果不清楚就停
- 做 scoped code changes

但这些还更像“行为建议”，不是“调度系统的硬门禁”。

### 本质
skill 有职责说明，但主控层还没有一套足够强的**phase contract enforcement**。

### 框架后果
角色会名义上分开，实际却可能重新滑回“一个执行者兼做定位、判断、实现、局部设计”。

---

## 3.4 失稳点四：runtime 的使用条件与收益边界还没真正收稳

`planning-runtime` 的方向是对的，但当前问题不在 skill 本身，而在它和护士站链路之间的调用边界尚未收稳。

当前 runtime 在设计上承担的是：
- 复杂任务执行容器
- 证据链容器
- 多轮续接容器
- retrospective 证据源

这些都成立。

但现在还缺：

- runtime 什么时候必须启用
- runtime 什么时候不该启用
- 中任务如何选择“轻运行态”还是“完整运行态”
- runtime 的最低维护成本应该是多少

### 本质
当前 runtime 更像“复杂任务推荐项”，但还没被纳入清晰路由规则。

### 框架后果
会造成两种摇摆：
- 该用的时候担心太重，不敢用
- 不该用的时候为了样板验证而提前启用，造成摩擦感

---

## 4. Skill 设计问题清单：哪些 Skill 当前不合理

下面不是说这些 skill 没用，而是指出它们当前最需要修的地方。

## 4.1 `nurse-station-brainstorming`

### 当前优点
- 能做需求澄清
- 能做 readiness 判断
- 已有 runtime recommended 之类的意识

### 当前问题
它仍然把“是否清楚”当成主问题，但没有把“该走哪条链”变成结构化输出。

### 不合理点
- 缺少任务分级输出（light / medium / heavy）
- 缺少 route recommendation
- 缺少 requirement-fit artifact readiness 判断
- 缺少 UI / 参数 / 场景类需求的前置验证锚点检查

### 结论
这是当前最优先要改的 skill 之一。

因为如果第一个 skill 不负责把任务正确送到正确链路，后面所有 skill 都会被迫承接前置判断缺失的成本。

---

## 4.2 `nurse-station-writing-plans`

### 当前优点
- 对复杂任务计划化能力较强
- 对 repo / module / file / agent split 的表达清楚

### 当前问题
它默认假设任务已经准备好进入完整计划化分解。

### 不合理点
- 对 light / medium 任务偏重
- 缺少“最小计划模式”
- 缺少 pre-code confirmation checklist
- 容易让 plan 继续沿用重任务结构，而不是根据任务级别裁剪

### 结论
它不是错，而是太偏向重任务模板，需要增加“分级计划模式”。

---

## 4.3 `nurse-station-subagent-execution`

### 当前优点
- 角色边界定义得比较好
- dispatch payload 规范是有价值的
- 适合复杂任务

### 当前问题
它太像一个默认上场的调度中枢，但其实只适合中重任务中的特定场景。

### 不合理点
- 缺少“哪些任务根本不该进入 subagent execution”的硬规则
- 容易把 controller 自己能直接承接的轻任务，也送去做多角色分发
- 对 runtime path 的强调是对的，但没有和任务分级绑定

### 结论
这个 skill 需要明确降级为：

> 不是默认执行总线，而是中重任务的专用调度器。

---

## 4.4 `nurse-station-verification`

### 当前优点
- 强调 requirement fit / scene fit / technical fit
- 已有 completion honesty 的意识

### 当前问题
它假定“前面已经准备好了足够的验收锚点”，但现实上经常没有。

### 不合理点
- 没有把“缺少前置验收物时必须拒绝通过”写成硬规则
- 对 UI / 交互类需求缺少具体检查模板
- 更像一个结果校验器，而不是一个能识别‘上游证据不足’的守门员

### 结论
verification 需要从“只看结果”升级为“也检查验收依据是否存在”。

---

## 4.5 `planning-runtime`

### 当前优点
- 作为运行态容器方向明确
- 文件分层合理
- 与 retrospective 的连接有价值

### 当前问题
它本身并不坏，但现在被放在了一个还没有成熟分流规则的体系里。

### 不合理点
- 启用规则仍偏泛
- 没有区分“轻 runtime / 完整 runtime”
- 对 controller 来说仍像一个额外操作，而不是自然路由结果

### 结论
`planning-runtime` 现在不是先要大改内容，而是要先被纳入更清楚的任务分级体系里。

---

## 4.6 `nurse-station-review-gate`

### 当前优点
- requirement fit 与 code quality 双 gate 的设计是对的
- 回环机制本身非常重要

### 当前问题
它仍然更偏“实现后门禁”，而不是“执行前后联动门禁”。

### 不合理点
- Gate 1 触发得偏晚
- 没有和 requirement-fit mini gate 前置联动
- 对中轻任务来说可能仍显得偏重

### 结论
review-gate 不该被削掉，而该被拆成：
- pre-code mini gate
- post-implementation full gate

---

## 5. 哪些 Skill 现在反而基本合理

## 5.1 `nurse-station-locator`

这个 skill 当前相对健康。

原因：
- 目标清楚
- 不做实现
- 强调定位证据
- 反模式明确

它的问题不是 skill 本身，而是：
- 何时该调用它
- 定位结果如何被下游正确消费

所以 locator 当前不算优先大改项。

## 5.2 `nurse-station-implementer`

这个 skill 也不是最核心的问题源。

它的问题主要是被喂给它的任务边界常常还不够稳，而不是 skill 自己完全失控。

所以 implementer 需要收紧 contract，但不是当前第一优先级改造对象。

## 5.3 `nurse-station-mvp-retrospective`

这个 skill 的定位其实很对：
- 它是把真实 run 转化为框架资产的必要层
- 当前阶段恰恰需要它

所以 retrospective 应该保留，并且在框架优化中扮演“故障归因器”的角色。

---

## 6. 现在应如何重构整个执行链

## 6.1 新链路原则

当前最需要的不是继续加技能，而是把整条链从“顺序流程”升级为“带路由的状态机”。

### 当前偏像
`brainstorming → planning → locate → implement → review → verify`

### 未来应像
`intake → task-level routing → requirement-fit checkpoint → execution path selection → phased delivery → verification / retrospective`

也就是说，真正要新增的，不是再加一个后段 skill，而是前段增加两层控制：

1. **Task-level routing**
2. **Requirement-fit checkpoint**

---

## 6.2 建议的框架级重构顺序

### 第一优先级：重写前段路由逻辑
先改：
- `nurse-station-brainstorming`
- 补一份正式的 task routing spec

目标：
- 明确 light / medium / heavy
- 明确谁进 runtime，谁不进
- 明确谁可以跳过 planning，谁不能
- 明确谁必须先补 requirement-fit artifact

### 第二优先级：补 requirement-fit checkpoint
不一定先做成新 skill，也可以先做成正式 spec / template。

目标：
- 在 coding 前锁定验证锚点
- 让 implementer 和 verifier 都有统一参照

### 第三优先级：改 `writing-plans` 和 `subagent-execution`
目标：
- 让它们服从 task-level routing
- 不再默认按重任务结构展开

### 第四优先级：再调 `verification` 与 `review-gate`
目标：
- 让它们从“后段检查器”变成“前后联动的门禁系统”

### 第五优先级：最后再精修 runtime 形态
目标：
- 区分轻运行态与完整运行态
- 降低中任务的使用摩擦

---

## 7. 最终判断：当前框架最该修的不是“实现层”，而是“调度层”

这是这轮诊断最重要的结论。

如果继续只盯 implementer、review、verification 做局部修补，问题会反复出现。

因为当前真正的主问题不是：
- implementer 不会改
- verifier 不会看

而是：

> **调度层没有在正确时机，把任务送入正确复杂度的路径，也没有在编码前确认“这件事已经具备可稳定实现、可稳定验收的条件”。**

所以本轮框架优化的主战场应该是：

- task routing
- requirement-fit checkpoint
- phase contract enforcement

而不是继续围绕某一个需求做局部技巧增强。

---

## 8. 一句话总结

当前护士站框架的问题，不是 skill 太少，也不是某个需求太特殊，而是：

> 已经搭起了一套“看起来完整”的阶段链，但前段路由与准入闸门不够硬，导致不同复杂度任务被送入不匹配的执行路径；真正需要优先重构的是调度层，而不是只修实现层。 

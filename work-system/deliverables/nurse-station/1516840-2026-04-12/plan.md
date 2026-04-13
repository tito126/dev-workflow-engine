# 执行计划 - 1516840

- Item: `1516840`
- Task level: `medium`
- Execution carrier: `ACP opencode`（若 ACP 不可用则降级 `exec opencode`）
- Goal: 在住院护士站配置页的 `长期医嘱首日设置` 处补足一段可直接理解的参数说明，让用户明确“首日”标识的含义、作用范围、与医嘱物资流向配置的联动关系，以及典型示例，降低误配置和理解偏差
- Repo: `E:\winning-code\akso5\winning-nis-ward`（按当前护士站默认仓库预估）
- Module: 护士站配置 / 长期医嘱首日设置 / 参数说明承载区块（具体入口待 locator 落证）
- In scope:
  - 定位 `长期医嘱首日设置` 对应的前端配置入口、展示组件、文案来源与可能的后端配置元数据
  - 明确当前页面如何承载说明文案（静态说明、tooltip、帮助区块、富文本区域等）
  - 在不改变业务算法的前提下，落地说明内容及必要的轻量展示优化
  - 核对说明文案是否准确映射到 `基础配置 -> 公共配置 -> 医嘱流向配置 -> 住院 -> 药品 -> 物资流向`
- Out of scope:
  - 改造长期医嘱首日规则本身
  - 改造医嘱流向引擎、接口协议、数据库对象
  - 做跨产品线配置整合
  - 默认新增自动校验、自动联动跳转或配置向导
- Allowed change levels:
  - 允许：页面说明文案、帮助提示、说明承载区块、必要的前端展示优化
  - 谨慎允许：与说明展示直接相关的配置项元数据、渲染方式、文案映射
  - 禁止：首日规则算法、流向规则引擎、接口协议、数据库结构、跨模块重构
- Shared context summary:
  - TFS `1516840`，项目 `WiNEX-Inpatient-2`
  - 需求标题：`【参数优化】长期医嘱首日说明优化`
  - 当前已完成 brainstorming，并已落地 `requirement-summary.md`
  - 当前关键判断：本轮核心不是改业务规则，而是把“首日”标识的意义、边界、联动配置位置和案例讲清楚
  - 用户当前已明确：本轮不再额外停在“是否采用这版说明口径”的确认点，可直接进入下一阶段推进
- Success anchors:
  - 找到 `长期医嘱首日设置` 的真实实现入口与说明承载点
  - 明确说明文案来自哪里，需改静态页面、配置元数据还是组件渲染
  - 最终展示内容覆盖“含义、作用范围、联动配置位置、示例”四类信息
  - 说明文案明确表达“首日标识只影响执行计划赋标，不等于直接完成流向控制”
  - 若需要额外去物资流向配置补齐业务效果，页面说明能让用户读懂并找到这层关系
- Acceptance:
  - 代码完成：说明内容已落到对应配置入口，展示正常，未破坏原配置交互
  - 需求完成：说明完整覆盖业务意义、范围、联动位置、示例，并与现有业务规则一致
  - 效果已验证：需业务 / 产品或现场确认，用户不再因“只配参数、不配流向”产生理解偏差
- Evidence expectation:
  - `findings.md`：入口文件、数据流、承载方式、可能改动文件、风险
  - `implementation-result.md`：实际改动文件、说明落点、未决点
  - `verification-evidence.md`：对 success anchors 的逐条核对
  - `review-conclusion.md`：需求匹配与代码质量评审结论
- Runtime path: `work-system/deliverables/nurse-station/1516840-2026-04-12/`
- Phases to mirror in later artifacts:
  - `findings.md`
  - `implementation-result.md`
  - `verification-evidence.md`
  - `review-conclusion.md`
- Expected findings capture:
  - `长期医嘱首日设置` 页面 / 组件入口
  - 说明文案当前是否已有占位、帮助提示或配置元数据
  - 文案是前端静态写死、后端返回、字典配置还是参数项 schema 驱动
  - 与 `医嘱流向配置` 相关的提示是否已有现成文案或跳转能力
  - 最小可改方案对应的文件清单
- Expected progress updates:
  - 完成入口定位
  - 完成说明承载方式判断
  - 完成最小改动面收敛
  - 完成实现与验证收口
- Pre-code confirmation items:
  - 默认按当前 TFS 草案与 requirement summary 的口径推进，不再额外等待一轮“是否可继续”的确认
  - 若 locator 发现现网实现口径与 TFS 草案明显冲突，再回退并单独确认
  - 若产品侧后续补充更正式文案，可在实现阶段替换，不阻塞当前定位与实现准备
- Analysis-to-user confirmation gate:
  - 本任务不是 SQL / 性能优化任务，无强制用户确认闸门
  - 但若定位发现存在医院特化口径或页面已绑定定制文案，需回问“按标准产品口径还是项目定制口径落地”
- Sections to rewrite first if scope changes:
  - `Shared context summary`
  - `Success anchors`
  - `Allowed change levels`
  - `Acceptance`

## Agent 分工

- Controller:
  - 维护阶段推进与边界
  - 基于 `requirement-summary.md` 和 `findings.md` 判断是否可直接进入 implementer
  - 在发现标准口径与现网实现冲突时，及时拉回确认
- Locator / Analyst:
  - 在目标仓库内定位配置页面、参数 schema、帮助提示、说明承载点
  - 说明当前页面如何拼装参数项与说明文案
  - 输出可能改动文件、风险和未解决问题
- Implementer:
  - 在 locator 明确的文件边界内落地说明文案与必要展示优化
  - 不越界改业务规则、接口或数据库层
  - 产出结构化实现报告
- Verifier / Reviewer:
  - 对照 success anchors 检查说明是否讲清四类关键信息
  - 检查改动是否越界、是否引入新的歧义或 UI 退化

## 任务

- Task 1:
  - Purpose: 定位 `长期医嘱首日设置` 的实现入口、参数来源与说明承载方式
  - Inputs: `requirement-summary.md`
  - Likely files:
    - 护士站配置页相关前端页面 / 组件
    - 长期医嘱首日设置对应的参数 schema / 常量 / 字典文件
    - 若存在，相关后端参数定义或接口返回结构
  - Output: 入口文件、当前行为拼装方式、可能改动文件、风险清单
  - Should persist as: `findings.md`
  - Verification: 能明确回答“这段说明该改在哪里、通过什么方式展示”

- Task 2:
  - Purpose: 基于定位结果收敛最小实现方案
  - Inputs: `findings.md`、`requirement-summary.md`
  - Likely files:
    - Task 1 确认出的页面 / 组件 / schema 文件
  - Output: 最小改动方案、说明承载方式决策、是否需要补充帮助提示或示例
  - Should persist as: `implementation-result.md`（实现前先形成方案骨架）
  - Verification: 改动面清晰，implementer 无需再从聊天回捞背景

- Task 3:
  - Purpose: 实现说明文案与必要展示优化
  - Inputs: Task 2 结果
  - Likely files:
    - 由 Task 1 / 2 最终收敛出的目标文件
  - Output: 代码改动与实现报告
  - Should persist as: `implementation-result.md`
  - Verification: 页面说明能完整表达“意义、范围、联动位置、示例”四类信息

- Task 4:
  - Purpose: 做实现后验证与评审收口
  - Inputs: `implementation-result.md`
  - Likely files:
    - `verification-evidence.md`
    - `review-conclusion.md`
  - Output: 验证结论、未验证点、需求匹配与代码质量结论
  - Should persist as: `verification-evidence.md`、`review-conclusion.md`
  - Verification: 明确区分代码完成 / 需求完成 / 效果已验证三种状态

## 风险

- 当前尚未落到真实文件证据，页面入口和说明承载方式仍存在不确定性
- 若现网已有医院定制文案或特殊交互，标准说明可能不能直接平移
- 若页面由通用参数渲染引擎驱动，文案改动可能不只在单一页面文件内
- 若说明区域空间受限，可能需要在“内联说明”和“帮助提示”之间做折中

## 执行就绪度

- Can enter coding now: `no`
- Missing prerequisite:
  - 先完成 locator，确认真实入口文件、参数流与最小改动边界
  - 若定位后发现标准产品口径与现网实现冲突，再补一次范围确认

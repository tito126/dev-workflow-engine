# 执行计划 - 1540718

- Item: `1540718`
- Task level: `medium`
- Execution carrier: `ACP opencode`（若 ACP 不可用则降级 `exec opencode`）
- Goal: 在第三方主体未明确期间，为 `4199-2017-02` 住院医嘱执行查询接口提供系统侧最小兜底方案，优先降低 2 天检索场景下的明显超时风险，同时保持后续可在第三方明确后收缩或回退
- Repo: `E:\winning-code\akso5\winning-nis-ward`
- Module: `ward.order` / `execution_aggregate` 相关链路
- In scope:
  - 复核现有 `queryOrderExecPlanResults` 调用链与昨天已落改动
  - 判断现有改动中哪些符合“系统兜底”目标，哪些存在语义或分页风险
  - 优先收敛数据库侧分页、查询结构优化等最小兜底手段
  - 为“第三方后续明确”预留收缩 / 回退条件
- Out of scope:
  - 把本次兜底默认固化为长期最优架构
  - 直接修改数据库表结构或上线新索引
  - 在语义未确认前直接把 `UNION ALL` 作为最终结论收口
  - 扩展到无关接口或前端调用链
- Shared context summary:
  - TFS `1540718`，WINNING-6.0，项目 `WiNEX-Inpatient-2`
  - 慢接口：`/api/v1/execution_aggregate/ipt/cli_order_exec_result/query/by_example`
  - 代码入口：`com.winning.ward.order.api.rest.ExecPlanRestImpl#queryOrderExecPlanResults`
  - 当前新增澄清：第三方主体尚未明确，但在未明确期间系统侧仍需承担兜底责任
  - 昨天仓库内已出现一版实现主线：分页参数下沉、补 count 查询、`UNION` 改 `UNION ALL`
  - 这版实现不能默认直接收口，需重新对照“系统兜底”目标审视语义和风险
- Success anchors:
  - 明确这次要交付的是“第三方未明确期间的系统侧兜底”，而不是长期重方案
  - 识别现有代码改动里哪些可保留、哪些需回调、哪些需补验证
  - 接口在 2 天查询条件下性能显著改善，且结果语义不变
  - 分页总数、分页数据、空页行为一致，不引入新的统计错误
  - 为后续第三方明确后的收缩 / 回退保留清晰条件
- Runtime path: `work-system/deliverables/nurse-station/1540718-2026-04-09/`
- Phases to mirror in later artifacts:
  - `findings.md`
  - `implementation-result.md`
  - `verification-evidence.md`
  - `review-conclusion.md`
- Expected findings capture:
  - 当前已改文件与改动点清单
  - 数据库侧分页是否真正替代了内存分页
  - `count` 逻辑是否与分页结果一致
  - `UNION ALL` 是否存在重复语义风险
  - 哪些改动属于“当前兜底有效”，哪些属于“长期仍待确认”
- Expected progress updates:
  - 完成现有 diff 复核
  - 完成兜底方案保留 / 回调项划分
  - 完成最小改动方案收敛
  - 完成验证锚点重写
- Pre-code confirmation items:
  - 是否接受本轮以“系统兜底优先”而非“长期最优”作为目标
  - 对空页、总数、重复数据的语义要求是否必须完全与旧行为一致
  - 若第三方后续明确，是否允许届时回收部分系统侧兜底改动

## Agent 分工

- Controller:
  - 维护阶段推进
  - 维护“系统兜底”边界，防止重新滑回长期重方案
  - 基于 requirement summary 与现有 diff 决定是否直接进入 implementer
- Locator / Analyst:
  - 复核当前接口调用链、分页路径、SQL 组织方式
  - 输出“现有改动是否匹配兜底目标”的判断
  - 如有必要，补充 `findings.md`
- Implementer:
  - 在现有改动基础上做最小修正或回调
  - 优先保留数据库侧分页等低侵入收益项
  - 对 `UNION ALL`、count、空页行为等高风险点做修正
- Verifier / Reviewer:
  - 对照 success anchors 验证语义一致性、兜底效果、回退边界是否清晰

## 任务

- Task 1:
  - Purpose: 复核昨天已落改动是否符合“系统兜底”目标
  - Inputs: `requirement-summary.md`、当前仓库 diff
  - Likely files:
    - `ExeOrderExecuteQueryServiceImpl`
    - `ExecPlanRepositoryImpl`
    - 相关 repository / service 接口与 BO
  - Output: 保留项 / 回调项 / 待验证项清单
  - Should persist as: `findings.md` 或 `implementation-result.md`
  - Verification: 能明确回答“昨天那版哪些改动现在仍成立”

- Task 2:
  - Purpose: 收敛最小兜底实现方案
  - Inputs: Task 1 结果、`requirement-summary.md`
  - Likely files:
    - 同上
  - Output:
    - 推荐保留：数据库侧分页或其他低侵入优化
    - 待修正：count 逻辑 / 空页行为 / 重复语义风险
    - 谨慎项：`UNION ALL` 是否回退或增加保护
  - Should persist as: `implementation-result.md`
  - Verification: 方案能支撑“2 天检索下系统兜底”且不过度绑定长期前提

- Task 3:
  - Purpose: 执行最小范围代码修正
  - Inputs: Task 2 结果
  - Likely files:
    - `ExeOrderExecuteQueryServiceImpl`
    - `ExecPlanRepositoryImpl`
    - 必要时相关接口 / DTO / BO
  - Output: 兜底版实现落地
  - Should persist as: `implementation-result.md`
  - Verification: 改动点与兜底目标逐项对应

- Task 4:
  - Purpose: 为后续验证准备明确锚点
  - Inputs: Task 3 结果
  - Likely files:
    - `verification-evidence.md`
    - 需要时补 `findings.md`
  - Output: 验证项清单，至少覆盖分页总数、空页、重复语义、性能改善
  - Should persist as: `verification-evidence.md`
  - Verification: 后续 verification 无需再从聊天回捞判断口径

## 风险

- 当前没有真实执行计划，仍可能误判根因与收益占比
- `UNION ALL` 若不满足去重语义，可能带来重复数据或重复计数
- 仅做系统兜底时，要防止实现过深，导致未来第三方明确后难以回收
- 现有分页 total 与 data 的一致性需要重点核查，否则容易出现空页返回总数 0 等行为偏差

## 执行就绪度

- Can enter coding now: `yes`
- Missing prerequisite:
  - 不再需要重新做大范围 locator，但 implementer 第一跳必须先复核现有 diff 与语义风险
  - 若能补充数据库执行计划或慢 SQL 证据更好，但不是进入兜底修正的硬阻塞

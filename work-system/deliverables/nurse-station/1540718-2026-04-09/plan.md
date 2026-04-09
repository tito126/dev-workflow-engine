# 执行计划 - 1540718

- Item: `1540718`
- Task level: `medium`
- Execution carrier: `ACP opencode`（若 ACP 不可用则降级 `exec opencode`）
- Goal: 明确 `4199-2017-02` 住院医嘱执行查询接口的真实性能瓶颈，并基于证据选择最合适的优化方案，而不是预设“时间分批并发”一定落地
- Repo: `E:\winning-code\akso5\winning-nis-ward`
- Module: `ward.order` / `execution_aggregate` 相关链路
- In scope:
  - 定位 `ExecPlanRestImpl#queryOrderExecPlanResults` 的完整调用链
  - 还原完整 SQL / ORM 条件拼装逻辑
  - 分析 `EXEC_FLOW_ID` 与 `GOODS_FLOW_ID` 两个分支的执行特征
  - 评估 `UNION`、索引匹配、分页/时间范围处理方式
  - 在证据基础上给出优化方案优先级
- Out of scope:
  - 直接修改数据库表结构或上线新索引
  - 还未证实瓶颈前直接落地线程分批并发
  - 扩展到无关接口或前端调用链
- Shared context summary:
  - TFS `1540718`，WINNING-6.0，项目 `WiNEX-Inpatient-2`
  - 慢接口：`/api/v1/execution_aggregate/ipt/cli_order_exec_result/query/by_example`
  - 代码入口：`com.winning.ward.order.api.rest.ExecPlanRestImpl#queryOrderExecPlanResults`
  - 已知 SQL 片段对 `EXEC_PLAN` 进行了两支查询后 `UNION`
  - 已补充索引信息：`EXEC_FLOW_ID` 分支有部分匹配索引；`GOODS_FLOW_ID` 未见对应索引；但 DBA 不建议继续新增索引
- Success anchors:
  - 明确瓶颈是在 `EXEC_FLOW_ID` 分支、`GOODS_FLOW_ID` 分支、`UNION` 去重，还是上层代码逻辑
  - 输出至少 2 到 3 个优化方向，并按推荐优先级排序
  - 若进入实现，保证接口结果语义不变
  - 若采用并发方案，明确其触发条件与不适用条件
- Runtime path: `work-system/deliverables/nurse-station/1540718-2026-04-09/`
- Phases to mirror in later artifacts:
  - `findings.md`
  - `implementation-result.md`
  - `verification-evidence.md`
  - `review-conclusion.md`
- Expected findings capture:
  - 控制层 → 服务层 → DAO / Mapper 调用链
  - 完整 SQL 及参数来源
  - 分页、时间范围、医院过滤、流程号过滤的实际拼装方式
  - `UNION` 是否可改 `UNION ALL`
  - `GOODS_FLOW_ID` 是否确实无索引覆盖
- Expected progress updates:
  - 完成代码入口定位
  - 完成 SQL 与 mapper 定位
  - 完成瓶颈候选排序
  - 完成优化建议收敛
- Pre-code confirmation items:
  - 是否已有数据库执行计划截图或慢 SQL 证据
  - 是否允许后续建议新增索引，但先不落地
  - 若最后并发方案成立，是否有线程池/超时治理约束

## Agent 分工

- Controller:
  - 维护阶段推进
  - 汇总 TFS、需求澄清、索引判断
  - 决定是否从 locator 进入 implementer
- Locator / Analyst:
  - 在仓库中定位调用链、SQL、Mapper、DTO 条件来源
  - 分析现有实现与数据库访问模式
  - 输出 `findings.md`
- Implementer:
  - 仅在方案收敛后执行最小范围改动
  - 优先落地 SQL/查询结构优化，再考虑应用层并发拆分
- Verifier / Reviewer:
  - 对照 success anchors 验证行为一致性、性能收益、风险控制

## 任务

- Task 1:
  - Purpose: 定位接口完整调用链与条件拼装入口
  - Inputs: `requirement-summary.md`、TFS `1540718`
  - Likely files:
    - `ExecPlanRestImpl`
    - 对应 service / facade / query service
    - mapper / repository / xml / SQL builder
  - Output: 入口到 SQL 的链路图 + 关键方法清单
  - Should persist as: `findings.md`
  - Verification: 能明确回答“完整 SQL 从哪里生成”

- Task 2:
  - Purpose: 分析 SQL 结构与索引匹配关系
  - Inputs: 代码定位结果、已知索引列表
  - Likely files:
    - mapper XML
    - repository / DAO
    - query DTO / example builder
  - Output: 慢点候选排序（`GOODS_FLOW_ID` / `UNION` / 时间范围 / 其他）
  - Should persist as: `findings.md`
  - Verification: 能明确回答“为什么当前并发分批不是默认首选”

- Task 3:
  - Purpose: 收敛优化路线并给出实现建议
  - Inputs: Task 1~2 结果
  - Likely files:
    - 同上，必要时补看测试或调用方代码
  - Output:
    - 推荐方案 A：SQL / 查询结构优化
    - 备选方案 B：结果去重语义允许时调整 `UNION` 组织方式
    - 条件成立时的方案 C：应用层时间切片并发
  - Should persist as: `findings.md`
  - Verification: 方案间有清晰的适用条件与风险比较

- Task 4:
  - Purpose: 若用户确认方案，进入实现准备
  - Inputs: `findings.md`
  - Likely files: 待 locator 确认
  - Output: 实现范围与改动点清单
  - Should persist as: `implementation-result.md`（实现后）
  - Verification: 改动点与推荐方案一一对应

## 风险

- 当前只有索引定义，没有真实执行计划，仍可能误判瓶颈
- 如果 `GOODS_FLOW_ID` 的数据分布极不均匀，单看索引名仍不够
- 若 `UNION` 改 `UNION ALL`，必须先确认结果去重语义
- 由于 DBA 不建议继续加索引，后续优化路线应优先集中在 SQL 结构、条件组织、调用方式与应用层拆分

## 执行就绪度

- Can enter coding now: `no`
- Missing prerequisite:
  - 需要先完成 locator，确认完整调用链、SQL 与执行特征
  - 最好补一份数据库执行计划或慢 SQL 证据

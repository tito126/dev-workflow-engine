# 需求澄清 - 1540718

> 来源：TFS 1540718 | 集合：WINNING-6.0 | 项目：WiNEX-Inpatient-2
> 状态：已分析 | 分配：未分配
> 澄清时间：2026-04-09 14:13

---

## 需求澄清

### 类型
**性能优化** — 稳定性/效率类，属于债务治理 + 效率提升

### 背景
- 病区护士站网关接口 `4199-2017-02`（住院医嘱执行查询）响应耗时超过 3 秒
- API 入口：`/api/v1/execution_aggregate/ipt/cli_order_exec_result/query/by_example`
- 代码入口：`com.winning.ward.order.api.rest.ExecPlanRestImpl#queryOrderExecPlanResults`
- 慢查询根因：三方调用时查询时间跨度为 2 天，SQL 对 EXEC_PLAN 表做 UNION 查询（分别查 EXEC_FLOW_ID 和 GOODS_FLOW_ID），数据量大时耗时显著

### 当前补充判断（基于索引）
- 现有索引中，`IDX_EXEC_PLN_FLOW_ID_DEL_AT (IS_DEL, PLANNED_EXEC_AT, EXEC_FLOW_ID)` 对 `EXEC_FLOW_ID` 分支**部分匹配**，但对 `HOSPITAL_SOID` 过滤不友好，且键顺序不利于先按 `EXEC_FLOW_ID` 精确收敛
- 当前提供的索引里**没有看到 `GOODS_FLOW_ID` 相关索引**，这意味着 `GOODS_FLOW_ID` 分支大概率才是慢查询的重要来源之一
- 已补充约束：`EXEC_PLAN` 已有 8 个索引，**DBA 不建议再增加索引**
- 因此，**按时间分批并发执行不一定是最优首选**。如果瓶颈在于单条 SQL 走不到合适索引，并发只是在放大低效查询，可能把数据库压力打得更高
- 在没有执行计划前，更稳妥的优先级应是：**先确认 SQL 实际走法，再决定是否需要并发拆分**

### 目标
- 将该接口响应时间从 3s+ 降到可接受范围（建议 <1s，具体标准待确认）
- 在不改变接口行为的前提下，找到最合适的优化路径，分批并发只是候选方案之一

### 非目标
- 不改变接口入参出参协议
- 不直接预设“线程分批”一定落地
- 不把“新增索引”作为本次默认优化路径
- 不改变前端调用逻辑

### 范围
- **受影响模块**：winning-nis-ward（病区护士站）后端，具体为 `ward.order` 模块
- **受影响接口**：`queryOrderExecPlanResults`（可能涉及底层 DAO/SQL）
- **仓库**：`E:\winning-code\akso5\winning-nis-ward`

### 成功标准
1. 接口响应时间在 2 天查询条件下显著下降（建议 <1s，需确认目标值）
2. 功能行为不变（查询结果与优化前一致）
3. 若采用并发方案，不引入并发安全问题，也不明显放大数据库压力
4. 优化方案对 `EXEC_FLOW_ID` 与 `GOODS_FLOW_ID` 两个分支都成立，而不是只优化一半

### 风险 / 模糊点
1. ⚠️ **优化目标未量化**：需求只说"需要优化"，未明确目标响应时间
2. ⚠️ **真正瓶颈未证实**：目前只有 SQL 片段和索引信息，还没有执行计划/实际慢点证据
3. ⚠️ **GOODS_FLOW_ID 可能缺索引，但当前不可默认走补索引**：DBA 已明确不建议继续增加索引
4. ⚠️ **分批策略未具体化**：按时间分批的粒度？按天？按小时？是否需要动态调整？
5. ⚠️ **并发线程数未定义**：线程池大小、最大并发数未明确
6. ⚠️ **UNION 是否必要**：若两支结果天然不重叠，`UNION ALL` 可能优于 `UNION`，但需要语义确认

### 当前建议的优化优先级
1. **先做 locator + SQL/执行计划分析**
   - 确认完整 SQL、参数拼装逻辑、是否分页
   - 拿到数据库执行计划，确认慢在 `EXEC_FLOW_ID` 分支、`GOODS_FLOW_ID` 分支，还是 `UNION` 去重
2. **优先评估 SQL / 查询结构优化**
   - 重点检查 `GOODS_FLOW_ID` 分支是否存在可改写空间
   - 评估现有过滤条件顺序、SQL 组织方式、是否存在多余扫描
   - 评估 `UNION` 是否可安全改为 `UNION ALL`
3. **最后再评估应用层并发分批**
   - 只有在单条 SQL 已较优、但 2 天窗口数据量仍大时，再考虑时间切片并发

---

## 连续执行判断

### 任务级别
**medium** — 边界可控，单一接口优化，需要定位 + 窄范围实现 + 验证

### 是否值得进入持续工作流
**是** — 涉及代码定位、SQL 分析、优化方案判断、实现和验证，需要多步协作

### 推荐执行路径
```
brainstorming（本阶段 ✓）
  → writing-plans
  → locator（定位当前实现、完整 SQL、执行计划、数据量）
  → implementer（按证据选择 SQL/索引优化 or 应用层分批优化）
  → verification
  → review-gate
  → done
```

### 是否建议使用外部执行器
**是** — 需要在 winning-nis-ward 仓库中定位和修改代码

### 首选外部执行路径
**ACP opencode** — 降级方案：exec opencode

### 建议后续沉淀资产
- `plan.md` — 执行计划
- `findings.md` — 代码定位结果
- `implementation-result.md` — 实现报告
- `verification-evidence.md` — 验证证据

### 建议任务标识
`1540718-2026-04-09`

### 是否可进入计划
**是** — 目标问题可理解，受影响模块已知，当前已具备做实现前方案收敛的条件

### 是否可进入执行
**否** — 尚需 locator 阶段确认当前实现细节和 SQL / 执行计划证据

### 下一步所需动作
1. 进入 `writing-plans` 阶段，明确“先证实瓶颈，再定优化路线”
2. 用 locator 定位 `ExecPlanRestImpl#queryOrderExecPlanResults` 的完整调用链和 SQL
3. 补充执行计划或数据库慢点证据，优先判断 `GOODS_FLOW_ID` 分支与 `UNION` 去重成本

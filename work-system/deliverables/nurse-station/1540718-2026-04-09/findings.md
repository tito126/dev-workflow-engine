# Locator Findings - 1540718

> 来源：ACP opencode locator run
> 任务：`nurse-station-locator-1540718-run`
> 完成时间：2026-04-09 15:21

---

## 1. 调用链

根据 ACP locator 返回结果，当前接口调用链为：

```text
ExecPlanRestImpl#queryOrderExecPlanResults
→ ExeOrderExecuteQueryServiceImpl#queryOrderExecPlanResults
→ nestInputParamData() 参数组装
→ ExeOrderExecuteQueryManager / DAO / Mapper 查询链路
```

> 当前系统事件里已明确给出前 3 层；后续若需要做 implementer，可再回仓库补精确文件与行号。

## 2. 当前确认的关键观察

### 2.1 SQL 结构层面
- 目标查询对 `EXEC_PLAN` 存在两支主查询：
  - `EXEC_FLOW_ID` 分支
  - `GOODS_FLOW_ID` 分支
- 两支结果通过 `UNION` 合并
- 当前查询时间跨度为 2 天，导致扫描范围较大

### 2.2 性能瓶颈排序（来自 ACP locator）
1. **`GOODS_FLOW_ID` 分支无索引**
   - 被判断为当前最慢分支
   - 高概率导致 `EXEC_PLAN` 大范围扫描甚至全表扫描
2. **`UNION` 导致两次扫描 / 去重成本**
   - 两支查询都要执行，再做合并去重
3. **内存分页**
   - 需先加载全部结果到内存，再分页
   - 数据量大时存在 OOM 风险，也会放大整体耗时
4. **其他关联查询**
   - `ExecOrder`、`ExecOrderItem`、`ExecPlanResult` 等关联查询在结果量大时继续放大耗时

## 3. 对当前方案判断的影响

### 3.1 为什么“时间分批并发”不是默认首选
- 当前慢点首先落在 `GOODS_FLOW_ID` 分支与 `UNION` 结构上
- 如果直接做时间切片并发，相当于把低效查询切成多份并发执行
- 在数据库层面，这更可能放大扫描压力，而不是从根因上降耗

### 3.2 为什么“新增索引”也不能作为默认答案
- 虽然 ACP 返回的瓶颈第一位是 `GOODS_FLOW_ID` 无索引
- 但当前已知业务约束是：`EXEC_PLAN` 已有 8 个索引，且 DBA 不建议继续新增
- 因此 implementer 阶段应优先寻找 **不依赖新增索引** 的优化路径

## 4. 推荐后续实现优先级

### 优先级 A：SQL / 查询结构优化
- 优先确认 `UNION` 是否有必要保留去重语义
- 如果两支结果天然不重叠，优先评估改写为 `UNION ALL`
- 评估是否能提前缩小 `GOODS_FLOW_ID` 分支的数据范围
- 评估是否能重组过滤条件与查询路径，减少无效扫描

### 优先级 B：分页策略优化
- 确认当前是否先全量查出结果再内存分页
- 如果属实，优先改为数据库侧分页或更早截断结果集

### 优先级 C：应用层时间切片并发（条件成立时）
- 只有在 SQL 结构已尽量收敛后，2 天窗口仍然导致单次查询过重，才考虑时间切片并发
- 若采用，必须同时评估线程数、超时、数据库压力与结果合并成本

## 5. 当前建议的 implementer 任务方向

1. 精确定位 `queryOrderExecPlanResults` 对应的 service、manager、mapper / xml
2. 还原完整 SQL 与分页逻辑
3. 先判断：
   - `UNION` 能否改 `UNION ALL`
   - 是否存在“先查全量再内存分页”
   - `GOODS_FLOW_ID` 分支是否能通过业务条件提前收敛
4. 在不新增索引的前提下，给出最小改动实现方案

## 6. 未确认点

- 还缺 ACP 原始 findings 中的精确文件路径和行号
- 还未看到数据库执行计划截图或实际 SQL plan
- `UNION ALL` 是否成立，取决于结果去重语义，需要结合代码与业务确认
- 内存分页的具体实现位置仍需 implementer / locator 再补精确文件信息

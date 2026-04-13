# Locator Findings - 1554774

> 任务：TFS 1554774
> 日期：2026-04-13
> 说明：ACP 未拿到有效回传后，经用户确认，已降级到 `exec opencode` 做定向定位

---

## 定位结果

- 仓库：`E:\winning-code\akso5\winning-nis-ward`
- 模块：`winning-ward-execution-order`
- YAML 路由文件：`work-system/config/nurse-station-repo-routing.yaml`
- 首扫根：`E:\winning-code\akso5\winning-nis-ward`
- 首扫根来源（用户 / YAML）：YAML
- 实际扫描根：`E:\winning-code\akso5\winning-nis-ward`
- 被排除的根：`E:\winning-code\work`、`E:\winning-code\ai`
- 扩扫触发原因：无
- 运行时路径：`ExecPlanRestImpl#queryOrderExecPlanResults -> ExeOrderExecuteQueryServiceImpl#queryOrderExecPlanResults -> ExeOrderExecuteQueryServiceImpl#queryExecPlanResultList -> ExecPlanRepositoryImpl#queryExecPlanByConditions`
- 可能入口文件：
  - `winning-ward-execution-order/winning-ward-execution-order-api/src/main/java/com/winning/ward/order/api/rest/ExecPlanRestImpl.java`
  - `winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/service/execorder/impl/ExeOrderExecuteQueryServiceImpl.java`
  - `winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/repository/execplan/impl/ExecPlanRepositoryImpl.java`
- 关键关联文件：
  - `docs/exec_plan_union_vs_or_benchmark.py`
  - `winning-ward-model/src/main/java/com/winning/ward/entity/order/ExecPlan.java`
- 当前行为拼装方式：查询 SQL 不是 Mapper/XML，而是在 `ExecPlanRepositoryImpl#queryExecPlanByConditions` 中用 `StringBuilder` 直接拼原生 SQL；当前做法是把 `EXEC_FLOW_ID` 和 `GOODS_FLOW_ID` 两支条件拆成两个 `select`，中间用 `union all` 拼接
- 可能改动文件：
  1. **高概率**：`ExecPlanRepositoryImpl.java`（若把 `union all` 改成 `or`，主改动在这里）
  2. **低概率**：若需要补注释或联动说明，可能涉及同文件附近逻辑
  3. **数据库脚本**：仓内未发现现成 `sql` / `ddl` / `upgrade` 目录可直接承接索引脚本
- 风险：
  1. 把两支查询合并成 `or` 后，可能失去当前“拆分条件以利用索引”的设计意图，性能不一定更好
  2. 当前 `union all` 允许重复行，`or` 单条查询天然不会重复，结果集语义可能变化
  3. 仓内没有现成索引脚本承接位置，如果本轮要落索引，需要额外明确脚本规范或落点
- 未解决问题：
  1. 1554774 是否明确要求覆盖 1540718 的现有 `union all` 实现
  2. 本轮是否真的要一并落索引，而不是只调整 Java 查询结构
- 需要向用户确认的问题：
  1. 本轮是否明确以 1554774 为准，把现有 `union all` 改成单条 SQL 的 `or` 条件
  2. 索引是否要在本轮一并落地；如果要，仓内暂无现成脚本落点，是否接受我按当前仓库结构新建承接位置

---

## 代码证据

### 1. 1540718 的改动仍然存在
- 文件：`winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/repository/execplan/impl/ExecPlanRepositoryImpl.java`
- 位置：约第 230-235 行
- 证据：
```java
if (CollectionUtils.isNotEmpty(input.getExecDeptIdList())) {
    sqlQuery.append(" and (a.EXEC_FLOW_ID in :execFlowId)");
}
//性能优化，利用索引，or 改成 union all 查询（不去重，减少成本）
sqlQuery.append(" union all ");
sqlQuery.append(" select a.* from EXEC_PLAN a ");
```

### 2. 第二支查询走 `GOODS_FLOW_ID`
- 文件：同上
- 位置：约第 259-261 行
- 证据：
```java
if (CollectionUtils.isNotEmpty(input.getExecDeptIdList())) {
    sqlQuery.append(" and ( a.GOODS_FLOW_ID in :execFlowId)");
}
```
说明：当前真实结构是两条几乎相同的 SQL，分别筛 `EXEC_FLOW_ID` 与 `GOODS_FLOW_ID`，再 `union all` 合并。

### 3. 查询入口与调用链证据
- REST 入口：`winning-ward-execution-order/.../api/rest/ExecPlanRestImpl.java` 约第 112-115 行
```java
public WinRpcResponse<List<ExecPlanResultOutputDTO>> queryOrderExecPlanResults(@RequestBody QueryCliOrderExecPlanResultInputDTO inputDTO) {
    QueryCliOrderExecPlanResultInputBO input = BeanMapper.map(inputDTO, QueryCliOrderExecPlanResultInputBO.class);
    WinPagedList<ExecPlanResultByEncounterOutputBO> pagedList = exeOrderExecuteQueryService.queryOrderExecPlanResults(input);
```
- Service 调用：`winning-ward-execution-order/.../service/execorder/impl/ExeOrderExecuteQueryServiceImpl.java` 约第 380-392 行
```java
public WinPagedList<ExecPlanResultByEncounterOutputBO> queryOrderExecPlanResults(QueryCliOrderExecPlanResultInputBO inputDTO) {
    ...
    ExecOrderPlanInputBO execOrderPlanInputDTO = this.nestInputParamData(inputDTO);
    List<QueryClicOrderExecPlanResultOutputBO> clicOrderExecPlanResultOutputDtos = exeOrderExecuteQueryService.queryExecPlanResultList(execOrderPlanInputDTO);
```
- Repository 调用：`.../ExeOrderExecuteQueryServiceImpl.java` 约第 123-137 行
```java
public List<QueryClicOrderExecPlanResultOutputBO> queryExecPlanResultList(ExecOrderPlanInputBO input) {
    ...
    execPlanVoList.addAll(execPlanRepository.queryExecPlanByConditions(inputVo));
}
```

### 4. SQL 位于 Java 原生拼接，不在 Mapper/XML
- 在 `winning-ward-execution-order` 下未找到 `ExecPlan*.xml`
- 未找到与本查询对应的 Mapper/XML 定义
- 结论：若改 `union all -> or`，主改动点就是 `ExecPlanRepositoryImpl.java`

### 5. 仓内未发现现成索引脚本承接位置
- 未找到 `**/sql/**/*.sql`、`**/db/**/*.sql`、`**/upgrade/**`、`**/*ddl*` 等与本需求直接对应的脚本目录
- `IDX_EXEC_PLN_FLOW_ID_DEL_AT` 在代码仓内没有现成命中
- 当前唯一明显相关命中是 `docs/exec_plan_union_vs_or_benchmark.py` 中的本地基准脚本和模拟索引，不是正式生产 DDL 落点

### 6. 关于 `or` 风险的直接代码证据
- `docs/exec_plan_union_vs_or_benchmark.py` 文件头明确写道：生产仓当前之所以把
  - `a.EXEC_FLOW_ID in (...)`
  - `a.GOODS_FLOW_ID in (...)`
  拆成两支再 `UNION`
  是为了“让每个分支使用各自索引”
- 这说明从仓内已有辅助文档看，**拆分查询本身就是经过性能考量的设计**，因此直接改成 `or` 的主要风险不是代码难改，而是**执行计划和性能方向可能反转**

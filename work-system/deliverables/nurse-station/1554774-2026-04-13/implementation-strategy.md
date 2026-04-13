# 1554774 实施建议

> 事项：TFS 1554774
> 日期：2026-04-13
> 目的：沉淀当前对 SQL 改法、空条件处理、索引方案与适用边界的最终建议

---

## 1. 结论先行

结合新增前提：
- 后续主战场不是 MySQL，而是 Oracle / MSSQL / 国产数据库
- 大多数场景下 `execDeptIdList` 为空
- 本需求会同步补两条 flow 相关联合索引

当前更推荐的最终方向调整为：

1. **默认走单条基础查询**，当 `execDeptId` 与 `execDeptIdList` 都为空时，不拼 `OR`，也不拼 `UNION`
2. **仅在存在 flow 条件时，走双分支 `UNION` 查询**
3. **不使用 `UNION ALL`**，避免两支结果重叠时产生重复记录
4. **索引按 `EXEC_FLOW_ID` / `GOODS_FLOW_ID` 两条路径分别设计**，与 `UNION` 双分支一一对应

简化表达就是：

- **无 flow 条件时**：走基础单查询
- **有 flow 条件时**：走 `UNION`
- **不推荐最终保留 `OR`**，因为当前索引设计和查询路径更适配“两支各走各的”

---

## 2. 为什么不建议继续保留 `union all`

当前代码位置：
`winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/repository/execplan/impl/ExecPlanRepositoryImpl.java`

现状是：
- 第一支按 `EXEC_FLOW_ID` 查询
- 第二支按 `GOODS_FLOW_ID` 查询
- 两支之间用 `union all` 拼接

### 主要问题

#### 2.1 结果重复风险
如果同一条 `EXEC_PLAN` 同时满足：
- `EXEC_FLOW_ID in (...)`
- `GOODS_FLOW_ID in (...)`

那么 `union all` 会把这条记录返回两次。

这不是纯理论风险。仓库内的辅助脚本 `docs/exec_plan_union_vs_or_benchmark.py` 里专门统计了 overlap，说明设计者自己也知道两支条件存在交叠可能。

#### 2.2 空 flow 条件时结构更脆
当前代码里 `union all` 是直接拼接的，不依赖 `execDeptIdList` 是否为空。

这意味着如果没有 flow 条件：
- 两支 SQL 会变得几乎相同
- 相当于把同一批数据查两遍再拼起来

这类结构问题，比“索引会不会浪费”更值得优先修。

#### 2.3 `union all` 更像性能兜底，不像最终语义
如果业务语义本来就是“满足左边或右边即可”，那么单条 `OR` 查询更自然，也更接近需求表达。

---

## 3. 推荐 SQL 改法

### 3.1 推荐结构

#### 场景 A：无 flow 条件
当 `execDeptId` 与 `execDeptIdList` 都为空时：
- 只走基础单查询
- 不拼 `OR`
- 不拼 `UNION`

#### 场景 B：有 flow 条件
当存在 `execDeptId` 或 `execDeptIdList` 时：
- 先沿用现有补齐逻辑，把 `execDeptId` 补到 `execDeptIdList`
- 然后使用双分支 `UNION`

推荐结构：

```sql
select a.* from EXEC_PLAN a
...
where ...
  and a.EXEC_FLOW_ID in (:execFlowId)

union

select a.* from EXEC_PLAN a
...
where ...
  and a.GOODS_FLOW_ID in (:execFlowId)
```

### 3.2 推荐伪代码

```java
if (input.getExecDeptId() != null) {
    if (CollectionUtils.isEmpty(input.getExecDeptIdList())) {
        List<Long> deptList = new ArrayList<>();
        deptList.add(input.getExecDeptId());
        input.setExecDeptIdList(deptList);
    } else {
        input.getExecDeptIdList().add(input.getExecDeptId());
    }
}

sqlQuery.append(" select a.* from EXEC_PLAN a ");
...
sqlQuery.append(" where a.IS_DEL = 0 and a.HOSPITAL_SOID in :hospitalSOID ");
...
if (CollectionUtils.isNotEmpty(input.getExecDeptIdList())) {
    sqlQuery.append(" and (a.EXEC_FLOW_ID in :execFlowId)");
    sqlQuery.append(" union ");
    sqlQuery.append(" select a.* from EXEC_PLAN a ");
    ...
    sqlQuery.append(" and (a.GOODS_FLOW_ID in :execFlowId)");
}
```

### 3.3 要点

- **大多数无 flow 条件的请求**，不应承担双分支查询成本
- **少数有 flow 条件的请求**，才走 `UNION`
- **不使用 `UNION ALL`**，防止重复记录
- 当前索引思路与 `UNION` 双分支更匹配

---

## 4. 空 `execDeptIdList` 场景应该怎么处理

### 推荐原则

#### 场景 A：`execDeptId` 有值，`execDeptIdList` 为空
这不是问题。

当前代码已经有补齐逻辑：
- 如果 `execDeptId` 有值
- 且 `execDeptIdList` 为空
- 就把 `execDeptId` 塞进列表

这种情况下，推荐继续沿用补齐逻辑，然后拼 `OR` 条件。

#### 场景 B：`execDeptId` 和 `execDeptIdList` 都为空
这时不应该再做任何 flow 条件过滤。

推荐行为：
- 不拼 `EXEC_FLOW_ID in (...)`
- 不拼 `GOODS_FLOW_ID in (...)`
- 不拼 `union`
- 不拼 `union all`
- 直接走基础查询条件

### 结论

空 `execDeptIdList` 本身不是问题，**真正的问题是“无 flow 条件时还继续走双分支查询”**。

---

## 5. 索引建议

### 5.1 当前更推荐的两条索引最终版

```sql
CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_GOODS_FLOW
ON EXEC_PLAN (
    IS_DEL ASC,
    HOSPITAL_SOID ASC,
    GOODS_FLOW_ID ASC,
    PLANNED_EXEC_AT ASC
);

CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_EXEC_FLOW
ON EXEC_PLAN (
    IS_DEL ASC,
    HOSPITAL_SOID ASC,
    EXEC_FLOW_ID ASC,
    PLANNED_EXEC_AT ASC
);
```

### 5.2 为什么是这版顺序
这条查询的核心过滤结构是：
- `IS_DEL = ?`
- `HOSPITAL_SOID in / = ?`
- `EXEC_FLOW_ID in (...)` 或 `GOODS_FLOW_ID in (...)`
- `PLANNED_EXEC_AT between ...`

因此更自然的顺序是：
1. 先放等值过滤 `IS_DEL`
2. 再放等值过滤 `HOSPITAL_SOID`
3. 再放 flow 字段（`EXEC_FLOW_ID` / `GOODS_FLOW_ID`）
4. 最后放范围列 `PLANNED_EXEC_AT`

### 5.3 为什么这版更适配 `UNION`
因为 `UNION` 本质是两条独立查询路径：
- 第一支吃 `IDX_EXEC_PLN_EXEC_FLOW`
- 第二支吃 `IDX_EXEC_PLN_GOODS_FLOW`

与其把两列揉成一条 `OR` 让优化器决定，不如显式拆成两支，让每条支路各走各自索引。

---

## 6. 这两个索引会不会浪费

### 结论
**会不会浪费，不取决于字段是否存在，而取决于现场是否高频走 flow 过滤。**

### 6.1 什么情况下不浪费
如果真实慢查询大多满足：
- 带 `execDeptId` / `execDeptIdList`
- 时间范围较大
- `EXEC_FLOW_ID` / `GOODS_FLOW_ID` 经常参与过滤

那么这两条索引就有意义。

### 6.2 什么情况下收益不高
如果大多数请求里：
- `execDeptIdList` 经常为空
- 也没有 `execDeptId`
- 实际慢点主要不在 flow 过滤，而在别的条件

那么这两条索引对这批请求就没什么帮助。

### 6.3 额外代价
新增索引的固定代价包括：
- 存储占用
- 写入维护成本
- 表上索引数量继续增加

因此，不建议在缺少现场证据时默认新增。

---

## 7. 最稳的实施顺序

### 方案一：当前最终推荐
1. 保留“无 flow 条件时走单条基础查询”的保护
2. 将“有 flow 条件时”的查询结构调整为 `UNION`
3. 同步补两条 flow 索引
4. 在目标数据库上观察执行计划与耗时

### 方案二：保留 `OR`
1. 保持单条 `OR` 查询
2. 同步补两条 flow 索引
3. 再观察目标数据库优化器是否稳定吃到理想执行计划

### 当前建议
更建议走 **方案一**。

原因：
- 大多数请求本来就没有 flow 条件，不应该承担双分支成本
- 少数有 flow 条件的慢场景，更适合拆成两支显式吃索引
- 你当前准备新增的两条索引，也更匹配 `UNION` 而不是 `OR`

---

## 8. 最终建议

### 推荐最终改法

#### SQL
- **无 flow 条件时**：保持单条基础查询
- **有 flow 条件时**：使用 `UNION` 双分支
- **不要 `UNION ALL`**

#### 空条件保护
- `execDeptId` 有值但 `execDeptIdList` 空：补齐后再查
- `execDeptId` 和 `execDeptIdList` 都空：只走基础查询，不拼 flow 分支

#### 索引
最终建议与 SQL 双分支对应：

```sql
CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_GOODS_FLOW
ON EXEC_PLAN (IS_DEL ASC, HOSPITAL_SOID ASC, GOODS_FLOW_ID ASC, PLANNED_EXEC_AT ASC);

CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_EXEC_FLOW
ON EXEC_PLAN (IS_DEL ASC, HOSPITAL_SOID ASC, EXEC_FLOW_ID ASC, PLANNED_EXEC_AT ASC);
```

### 一句话版本

**大多数无 flow 条件的请求走单条基础查询，少数有 flow 条件的慢场景走 `UNION` 双分支，并分别命中 `EXEC_FLOW` / `GOODS_FLOW` 两条联合索引。**

# 1554774 实施建议

> 事项：TFS 1554774
> 日期：2026-04-13
> 目的：沉淀当前对 SQL 改法、空条件处理、索引方案与适用边界的最终建议

---

## 1. 结论先行

当前更推荐的最终方向不是继续保留 `union all`，而是：

1. **将双分支 SQL 改成单条 SQL + `OR` 条件**
2. **补上空 `execDeptIdList` / 空 `execDeptId` 场景的保护**
3. **只有在现场确认“按执行科室 / 物资流向过滤”是高频慢点时，才考虑新增两条分支索引**
4. **如果不能确认高频命中场景，就先改 SQL 结构，不急着上索引**

简化表达就是：

- **有 flow 条件时**：走 `OR`
- **没有 flow 条件时**：走基础查询，不拼 `OR`，更不要拼 `union` / `union all`
- **索引是否要建**：取决于现场真实命中频率与执行计划，不应只因为“字段存在”就默认落地

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

当存在 `execDeptId` 或 `execDeptIdList` 时，推荐改成：

```sql
and (
    a.EXEC_FLOW_ID in (:execFlowId)
    or a.GOODS_FLOW_ID in (:execFlowId)
)
```

### 3.2 推荐伪代码

```java
boolean hasExecDeptFilter = CollectionUtils.isNotEmpty(input.getExecDeptIdList())
        || input.getExecDeptId() != null;

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
    sqlQuery.append(" and (a.EXEC_FLOW_ID in :execFlowId or a.GOODS_FLOW_ID in :execFlowId)");
}
```

### 3.3 要点

- **有 flow 条件时**，才拼 `OR`
- **没有 flow 条件时**，只走基础查询
- 不再用 `union`
- 不再用 `union all`

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

### 5.1 当前更合理的两条索引

```sql
CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_EXEC_FLOW
ON EXEC_PLAN (
    IS_DEL ASC,
    EXEC_FLOW_ID ASC,
    PLANNED_EXEC_AT ASC
);

CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_GOODS_FLOW
ON EXEC_PLAN (
    IS_DEL ASC,
    GOODS_FLOW_ID ASC,
    PLANNED_EXEC_AT ASC
);
```

### 5.2 为什么拆成两条更合理
因为查询本质上是两条不同过滤路径：
- 一条围绕 `EXEC_FLOW_ID`
- 一条围绕 `GOODS_FLOW_ID`

如果希望数据库在 `OR` 场景下也能分别命中索引，更合理的做法是：
- 左边条件有自己的前导列索引
- 右边条件也有自己的前导列索引

而不是做一条把两个 flow 字段混在一起的复合索引。

### 5.3 为什么不推荐把两个 flow 字段塞进同一条混合索引
像下面这种思路：

```sql
(IS_DEL, GOODS_FLOW_ID, PLANNED_EXEC_AT, EXEC_FLOW_ID)
```

问题是：
- 对 `GOODS_FLOW_ID` 分支友好
- 但对 `EXEC_FLOW_ID` 分支不够对称
- 不像真正的“双路优化”

因此，它不太像该查询的最优索引表达。

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

### 方案一：偏稳，推荐优先
1. 先改 SQL 结构：`union all` → 单条 `OR`
2. 补空 flow 条件保护
3. 先不上索引
4. 观察真实环境执行计划与耗时
5. 若仍慢，再补两条索引

### 方案二：偏激进
1. 改 SQL 结构：`OR`
2. 补空 flow 条件保护
3. 同步新增两条分支索引
4. 由 DBA / 现场再验证执行计划与收益

### 当前建议
更建议先走 **方案一**。

原因：
- 先把当前 `union all` 的结构性问题修掉
- 先保证结果语义更稳
- 索引是否新增，留给真实执行计划来决定

---

## 8. 最终建议

### 推荐最终改法

#### SQL
- 改成单条查询
- 只在 flow 条件存在时拼：

```sql
and (
    a.EXEC_FLOW_ID in (:execFlowId)
    or a.GOODS_FLOW_ID in (:execFlowId)
)
```

#### 空条件保护
- `execDeptId` 有值但 `execDeptIdList` 空：补齐后再查
- `execDeptId` 和 `execDeptIdList` 都空：不拼 flow 条件

#### 索引
如确认现场高频需要 flow 过滤，再考虑：

```sql
CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_EXEC_FLOW
ON EXEC_PLAN (IS_DEL ASC, EXEC_FLOW_ID ASC, PLANNED_EXEC_AT ASC);

CREATE NONCLUSTERED INDEX IDX_EXEC_PLN_GOODS_FLOW
ON EXEC_PLAN (IS_DEL ASC, GOODS_FLOW_ID ASC, PLANNED_EXEC_AT ASC);
```

### 一句话版本

**先把 SQL 改对，再决定要不要建索引；当前最该先修的，不是索引本身，而是 `union all` 和空 flow 条件下的查询结构问题。**

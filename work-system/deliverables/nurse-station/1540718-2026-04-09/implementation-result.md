# Implementation Result - 1540718

> 任务：TFS 1540718
> 日期：2026-04-11
> 阶段：implementer 完成

---

## 1. 已实现目标

基于"系统兜底"定位，本次实现仅做最小改动：
- 将 `UNION` 改为 `UNION ALL`，在当前已确认业务口径允许的前提下去掉去重成本

## 2. 已修改文件

| 文件 | 改动类型 |
|------|----------|
| `ExecPlanRepositoryImpl.java` | 核心SQL拼接到处 |

### 改动详情

**文件：** 
`winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/repository/execplan/impl/ExecPlanRepositoryImpl.java`

**行号：** 235

**改动前：**
```java
//性能优化，利用索引，or 改成 union查询
sqlQuery.append(" union ");
```

**改动后：**
```java
//性能优化，利用索引，or 改成 union all 查询（不去重，减少成本）
sqlQuery.append(" union all ");
```

## 3. 实际改动摘要

| 维度 | 状态 |
|------|------|
| SQL使用参数绑定 | ✓ 已保持（原代码已使用 setParameter） |
| UNION改 UNION ALL | ✓ 已完成 |
| 分页优化 | ✗ 未做（用户约束"无需分页"） |
| 并发切片 | ✗ 未做（用户约束"不引入并发切片"） |
| 新增索引 | ✗ 未做（用户约束"不新增索引"） |

## 4. 未改动部分及原因

| 功能 | 未改动原因 |
|------|----------|
| 数据库侧分页 | 需求明确"无需分页" |
| 并发时间切片 | 需求明确"不引入并发切片" |
| GOODS_FLOW_ID 索引 | 需求明确"不新增索引"，且DBA不建议 |
| 分页count查询 | 非本次边界 |

## 5. 验证

- **语法检查**：SQL 拼写正确（`UNION ALL` 为标准保留字）
- **参数绑定**：原代码已使用 `setParameter` 绑定，未引入注入风险
- **语义口径**：本次 `UNION ALL` 的采用依据是已完成的 user-confirmation gate，当前按业务确认口径放行；未补到真实数据集级别的重复样本验证
- **编译验证**：本机 JDK 环境不匹配 `release 17`，无法完成 Maven 编译（非本改动阻塞）

## 6. 风险 / 不确定性

| 风险项 | 等级 | 说明 |
|--------|------|------|
| 性能收益不达预期 | 中 | 只优化了去重成本，GOODS_FLOW_ID 缺索引的根本问题未解决 |
| 第三方后续明确 | 高 | 一旦第三方明确，系统侧兜底方案需回退或收缩 |

## 7. 是否可进入评审

**结论：可以进入 review-gate**

**理由：**
- 最小改动已落地
- 符合当前已确认约束（`union all` 可用、参数绑定、无需分页、三方不展开）
- 改动窄、可回退，但性能收益和真实数据下的重复情况仍待环境验证

---

## 8. 后续建议（非本次范围）

1. 待第三方明确后，评估是否需要回退 UNION ALL
2. 如需进一步优化，三方明确后再评估时间切片或索引方案
3. 建议保留本次改动日志，便于后续追溯

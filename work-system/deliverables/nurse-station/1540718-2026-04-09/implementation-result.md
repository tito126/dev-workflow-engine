# Implementation Result - 1540718

> 阶段：implementer
> 时间：2026-04-10 15:xx
> 目标口径：第三方未明确期间的系统侧最小兜底

## 已实现目标
- 将 1540718 的实现目标从“长期正式优化”收敛为“第三方未明确期间的系统侧兜底”。
- 对昨天已落代码做了第一轮风险修正，优先处理两类高风险问题：
  1. `UNION ALL` 可能带来的重复语义 / 重复计数风险
  2. 分页场景下空页直接返回 `count=0` 的错误风险

## 运行时路径
- `work-system/deliverables/nurse-station/1540718-2026-04-09/`

## 是否需要过程更新
- 是。当前已完成最小代码修正，正在跑定向编译确认。

## 需要沉淀的错误
- 原实现把分页参数下沉后，如果当前页查不到数据，可能直接返回 `WinPagedList(0L, [])`，这会把“空页”误报成“总数为 0”。
- 在未完成语义确认前，直接把 `UNION` 改成 `UNION ALL`，会把性能优化和结果语义变更绑在一起，风险过高。

## 已修改文件
- `winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/service/execorder/impl/ExeOrderExecuteQueryServiceImpl.java`
- `winning-ward-execution-order/winning-ward-execution-order-application/src/main/java/com/winning/ward/order/application/repository/execplan/impl/ExecPlanRepositoryImpl.java`

## 实际改动摘要
1. `ExeOrderExecuteQueryServiceImpl`
   - 保留分页场景下独立 count 查询的能力
   - 调整分页分支逻辑：即使当前页数据为空，也先返回真实 totalCount，再返回空列表
   - 非分页分支仍保持原有空结果快速返回逻辑

2. `ExecPlanRepositoryImpl`
   - 保留数据库侧分页能力
   - 将查询和 count 里的 `union all` 回退为 `union`
   - 目的不是否定性能优化，而是在系统兜底阶段先守住结果语义，避免重复数据与重复计数风险

## 未改动部分及原因
- 没有新增索引，因为当前已知 DBA 不建议继续加索引
- 没有引入并发切片，因为当前目标是最小兜底，且尚无充分证据证明应优先并发
- 没有继续深改排序 / 更大范围 SQL 重构，因为这已经超出“最小兜底修正”的边界

## 已执行验证
- 已完成代码级 diff 复核，确认修正点与当前 fallback 目标一致
- 已执行定向编译：
  - `mvn -pl winning-ward-execution-order/winning-ward-execution-order-application -am -DskipTests compile`
- 编译未通过，但当前失败点是**环境问题**而非本次改动直接报错：
  - `winning-ward-common` 编译阶段失败
  - Maven 编译器报错：`Fatal error compiling: 无效的目标发行版: 17`
- 该结果说明当前机器 / Maven 使用的 JDK 版本与项目 `release 17` 要求不匹配，因此这次未完成模块级编译验证

## 风险 / 不确定性
- 目前尚未拿到“代码层面编译通过”的最终结论，原因是本机 JDK / Maven 环境不满足 `release 17`
- `union` 回退后，性能收益可能低于昨天那版激进实现，但语义安全性更稳
- 仍缺数据库执行计划，无法精确量化本轮兜底收益上限
- 若后续第三方明确并改为 1 天检索，需要再评估这轮系统兜底改动是否保留或收缩

## 是否可进入评审
- 可进入代码评审 / verification 准备，但需明确：当前缺少基于本机的编译通过证据，阻塞点是环境而不是已知业务逻辑错误

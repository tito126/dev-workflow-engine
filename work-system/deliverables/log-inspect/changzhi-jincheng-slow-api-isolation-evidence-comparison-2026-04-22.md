# 长治 + 晋城高危慢接口事件对照分析（支撑三方服务隔离方案）

## 1. 目的

把长治（2026-04-21）与晋城（2026-04-15）两批 `slow_api` 证据收口成一版可直接支撑后续护士站“三方服务隔离方案”设计的对照稿。

本稿重点回答三件事：
1. 慢接口是否已经不是单点慢，而是结构性风险。
2. 哪些链路最值得优先做隔离。
3. 后续隔离方案应该按什么维度拆。

---

## 2. 输入材料

### 长治
- digest: `D:\现场支持\长治\ms_all_changzhi_9_digest_traces.json`
- log: `D:\现场支持\长治\ms_all.log.2026-04-21.9`
- 本轮产物：
  - `work-system/deliverables/log-inspect/changzhi-2026-04-21-slow-api-trace-ids.txt`
  - `work-system/deliverables/log-inspect/changzhi-2026-04-21-slow-api-summary.md`
  - `work-system/deliverables/log-inspect/changzhi-2026-04-21-slow-api-full-chains.log`

### 晋城
- digest: `D:\现场支持\晋城\ms_all_digest.json.2026-04-15_traces.json`
- log: `D:\现场支持\晋城\ms_all.log.2026-04-15.54`
- 本轮产物：
  - `work-system/deliverables/log-inspect/jincheng-2026-04-15-slow-api-trace-ids.txt`
  - `work-system/deliverables/log-inspect/jincheng-2026-04-15-slow-api-summary.md`
  - `work-system/deliverables/log-inspect/jincheng-2026-04-15-slow-api-full-chains.log`
- 既有补充证据：
  - `work-system/deliverables/log-inspect/log-inspect-slow-api-stack-evidence-2026-04-16.md`

---

## 3. 总体判断

两地证据已经可以共同支撑以下判断：

1. **这不是单个 SQL 或单个接口偶发变慢。**
   已经表现为“核心查询链路 + 三方依赖 + 执行校验链路 + 异常/通知侧链路”交织的结构性风险。

2. **慢链路已经具备拖垮节点的能力。**
   长治和晋城都出现了 `Java heap space`；晋城还出现了分钟级慢链路与大批量执行计划处理，说明风险不是普通性能抖动，而是会进一步演化成节点稳定性问题。

3. **后续方案不能只做‘接口优化’，而要做‘链路隔离’。**
   至少要区分：
   - 核心读链路
   - 三方费用/人域/病案增强链路
   - 执行计划库存/单位换算链路
   - WebSocket / 通知异常链路

---

## 4. 最支撑隔离方案的核心证据对照表

| 场景 | trace_id | 主要慢接口 | 关键证据 | 支撑的隔离判断 |
|---|---|---|---|---|
| 长治 | `9DE9C8B48F2C424F54BCF30D8136485F` | `/api/v1/app_inpatient_encounter/patient_list/query/by_example` `153993ms` | `Jetty-Worker_9380-Thread-28` 上出现 `Java heap space`，并带完整异常堆栈 | 患者列表主读链路已能直接把请求线程拖到 OOM，核心列表查询必须与重增强逻辑隔离 |
| 长治 | `63D9731F635A67DB2F09ACE35ECB196F` | `/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id` `141860ms` | `FinanceHelperImpl -> MedicalRecordAmtsRpcService -> HIS DataCenterSqlEngine`，报 `FIN-INP-0056` / `SQL路径:<DataBase>`，异常回到 `BannerInfoService` | Banner 费用增强链路依赖三方财务/HIS，且异常会直接打回主线程，必须单独隔离并支持 fail-open |
| 长治 | `DB22DCD8E7804F46E594DF32801C3245` | `/api/v1/app_inpatient_encounter/encounter_info/private/get/by_encounter_id` `142293ms` | 私有就诊信息读取同样到 142s，无单独堆栈也说明读链路整体被拖住 | 不只是费用接口，Banner/就诊相关读取整体存在被共性依赖拖慢的迹象 |
| 长治 | `68A3489F3C8F699ED1B1EC9A0483C2EF` | `/api/v1/app_inpatient_encounter/banner_person/query/by_id` `142114ms` | Banner 人域侧接口同量级慢 | 患者 Banner 信息应拆分核心字段与增强字段，避免一起被拖挂 |
| 晋城 | `0fb18dbda0ce42d081f1462d9083f9cc` | `/api/v1/app_inpatient_encounter/patient_list/query/by_example` `530768ms` | `Jetty-Worker_9380-Thread-145` 上出现 `Java heap space`，且耗时已到 530s | 列表主链路已经达到节点级风险，必须优先做核心链路瘦身与隔离 |
| 晋城 | `0f3cee3422a64ae6beeae9745fbbb3db` | `/api/v1/nis/exec_order_plan/advance_apply/by_end_time` `493986ms` | `VerifyMaterialService` 在 `exe-182` 中对大批执行计划逐项做库存/单位换算/系数匹配；既有证据还显示同窗口伴随 WebSocket 异常与 Hystrix 调用 | 执行计划校验链路是独立的重处理链，应与主读链路、通知链路、远程依赖链路分池隔离 |
| 晋城 | `b54e0bf4c468483a82c72bf5153a34b1` | `/api/v1/nis/exec_order/check/by_exec_order_ids` `525587ms` | 命中日志行 485，续行堆栈 516，说明执行单检查链路异常和处理量都很重 | 执行单检查不应与床旁高频读接口共用同类资源池 |
| 晋城 | `57af47aa45a54692b72e1e6695f7b75b` | `/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id` `374486ms` | Banner 费用接口再次落入高危慢链路 | Banner 费用增强是跨场景重复风险点，适合优先独立隔离 |
| 晋城 | `1fb099b5fcd645cd9fe35c533f78f38a` | `/api/v1/app_inpatient_encounter/encounter_info/private/get/by_encounter_id` `374701ms` | 私有就诊信息读取伴随 256 行续行堆栈 | 读链路不只是“慢”，而且会携带较重异常/附加处理，需分层 |
| 晋城 | `552483a4795f4a2eb9df1a2bd3038ba5` | `/api/v1/app_inpatient_encounter/inpat_basics_expense/query/by_encounter_id` `347488ms` | 费用基础信息链路同样带续行堆栈 | 费用与主信息读取不应继续强耦合同步返回 |

---

## 5. 四类归因收口

### A. 业务线程长时间占用

**晋城最典型。**

`0f3cee3422a64ae6beeae9745fbbb3db` 里，`VerifyMaterialService` 在单个 trace 内处理大量执行计划，并持续做：
- 药品库存查询
- 单位换算
- 剂量系数匹配
- 逐计划库存扣减演算

这说明链路不是“等一个外部接口回来”，而是**业务线程自己就在做高密度串行计算 + 远程依赖交叉处理**。

**对隔离方案的意义：**
- 执行计划库存校验链路要独立于床旁主读链路
- 同一业务动作内部也要区分“核心校验”和“增强校验”
- 能批量化、缓存化、异步化的部分不要继续逐计划同步执行

### B. Jetty Worker / 请求线程被拖住

长治和晋城都出现了 `patient_list/query/by_example` 上的 `Java heap space`。

这说明：
- 风险已经不只是“后台慢”，而是**请求处理线程本身被拖到不可恢复状态**
- 一旦并发叠加，节点会更容易出现线程池拥塞、GC 压力和整体雪崩

**对隔离方案的意义：**
- 列表/就诊信息/Banner 这类高频入口必须优先瘦身
- 入口接口默认只保留核心字段，增强信息延后、降级或异步补齐
- 重对象拼装、批量患者扩展字段、复杂列表增强不能继续压在主返回链路上

### C. 三方依赖 / SQL 侧链路直接拖挂主流程

长治的 `63D973...` 很典型：
- `FinanceHelperImpl.customQueryByEncounterId`
- `MedicalRecordAmtsRpcService.customQueryByEncounterId`
- HIS DataCenter `SQL路径:<DataBase>`
- 最终异常抛回 `BannerInfoService.queryInpatBannerBasicsExpense`

这条证据说明：
**三方费用/HIS 数据链路现在是同步强依赖，失败时会直接把 Banner 费用链路打穿。**

**对隔离方案的意义：**
- 费用、病案、人域、三方配置等增强项必须拆成独立依赖组
- 每组需要自己的超时、熔断、线程池/连接池边界
- 非核心增强字段允许返回空或占位，不应阻断主查询成功返回

### D. 异常 / 通知链路反向放大主链路风险

晋城既有证据已经证明：
- `ClosedChannelException` 在 `Jetty-Worker` 线程中沿 `SessionUtils.sendMessage -> OrderChangeWebSocketHandler` 展开完整堆栈
- 同一时间窗口又有多个 `hystrix-*` 远程依赖线程池调用

这说明系统不仅有主业务慢，还有**通知/推送异常链路反向消耗 Jetty Worker** 的问题。

**对隔离方案的意义：**
- WebSocket 推送失败要低成本处理，不再打完整错误堆栈
- 无效 session 要快速清理，避免继续发送
- 通知链路不能和高频查询请求线程抢同一类资源

---

## 6. 方案设计建议, 按隔离层次拆

### 第一层：核心读链路与增强链路分离

优先把以下接口从“全量同步拼装”改成“核心先返回，增强后补齐/可降级”：
- `/api/v1/app_inpatient_encounter/patient_list/query/by_example`
- `/api/v1/app_inpatient_encounter/encounter_info/private/get/by_encounter_id`
- `/api/v1/app_inpatient_encounter/banner_person/query/by_id`
- `/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id`
- `/api/v1/app_inpatient_encounter/inpat_basics_expense/query/by_encounter_id`

### 第二层：三方依赖按领域拆隔离池

至少拆成：
1. 财务 / 病案费用链路
2. HIS DataCenter / SQL 链路
3. 人域 / 标签 / 基础主数据链路
4. 物资 / 库存 / 药品信息链路

每一组都要有：
- 单独超时
- 单独线程池 / Bulkhead
- 单独降级策略
- 单独监控维度

### 第三层：执行计划重处理链路单独隔离

对以下链路单独做治理：
- `/api/v1/nis/exec_order_plan/advance_apply/by_end_time`
- `/api/v1/nis/exec_order/check/by_exec_order_ids`

建议优先动作：
- 对执行计划库存校验做批量预取 / 结果缓存
- 将单位换算、库存演算、非关键增强校验拆出主流程
- 对非关键校验支持异步 fail-open

### 第四层：异常通知链路降成本

- `ClosedChannelException` 不再完整打栈
- WebSocket 失败快速清理 session
- 通知推送与主查询解耦
- 补 Jetty Worker / Hystrix / 业务 executor 的活跃线程、队列、拒绝、耗时指标

---

## 7. 我建议的优先级

### P0, 先止血
1. Banner / 患者列表主链路去增强化, 只保核心字段
2. 费用 / 病案 / 三方读取链路独立超时 + fail-open
3. 执行计划库存校验链路从主高频请求中隔离出来
4. WebSocket 异常降成本, 避免继续吃 Jetty Worker

### P1, 再做结构优化
1. 药品库存 / 单位换算批量化、缓存化
2. 各类三方依赖按领域分池
3. 主查询与增强查询彻底拆线程模型

### P2, 最后补闭环
1. 补分段耗时埋点
2. 补线程池监控
3. 补降级命中率 / 超时率 / 堆栈密度指标
4. 把慢接口报告升级为“链路隔离风险报告”

---

## 8. 一句话结论

**长治和晋城两批证据已经足够支撑后续把问题定义从“高危慢接口”升级为“护士站核心读链路与三方增强链路、执行校验链路、异常通知链路缺少隔离，已具备拖垮节点的结构性风险”。**

后续方案重点不应只盯某一个慢接口，而应按“核心读链路 / 三方增强链路 / 执行重处理链路 / 通知异常链路”四层去做隔离设计。

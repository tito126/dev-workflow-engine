# 中江病区护士站慢接口分析报告

- 日期：2026-03-31
- 所属专项：日志猎人（`P-2026-02`）
- 子任务：中江病区护士站节点 down 事件——慢接口与三方服务隔离优化
- 执行方式：`executor -> acp -> Codex`
- 当前阶段：分析 / 方案草案
- 结论属性：基于源码静态分析，未改代码，未做运行时验证

## 1. 这轮做了什么
- 触发 `acp -> Codex`，对 `winning-nis-ward` 进行多文件调用链分析。
- 定位目标接口从 API 常量、Controller、Service 到 finance / tripartite / basicdata 的完整路径。
- 收口三类问题：同步串行远程调用、过度取数、缺少隔离与超时治理。
- 形成一版“小改动大收益”优先的隔离优化方案草案。

## 2. 当前结论
- 可疑接口确认为 `/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id`。
- 主路径为：`BannerInfoController` → `BannerInfoService.queryInpatBannerBasicsExpense()`。
- 主方法内当前串行执行 3 段关键远程调用：
  1. `expenseBaseService.queryByEncounterId()`：核心余额 / 基础费用查询
  2. `expenseBaseService.queryByEncounterIds()`：病案费用汇总 / treatment fee
  3. `financeHelper.customQueryByEncounterId()`：中医补充明细
- 三段之间没有强数据依赖，理论上都可以拆分为核心 + 增强并行执行。
- 当前代码中没有看到显式的超时、重试、熔断、Bulkhead 隔离；主要依赖底层 RPC / 网关默认行为。
- 按源码静态判断，节点 down 更像“慢外部依赖拖住请求线程 / 连接池”的级联问题，而不是本地 CPU 计算瓶颈。

## 3. 关键代码路径
- 接口路径常量：`winning-ward-banner/winning-ward-banner-api/src/main/java/com/winning/ward/banner/api/constant/bannerApiPathConstants.java:68`
- Controller：`winning-ward-banner/winning-ward-banner-api/src/main/java/com/winning/ward/banner/api/controller/BannerInfoController.java:200`
- Service 主方法：`winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoService.java:436`
- 第一段调用：`winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoService.java:444`
- 第二段调用：`winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoService.java:478`
- 第三段调用：`winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoService.java:510`
- Expense bridge：`winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/bridge/impl/ExpenseBaseServiceImpl.java:84`
- Expense bridge：`winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/bridge/impl/ExpenseBaseServiceImpl.java:91`
- Query application：`winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/query/QueryBillApplicationService.java:264`
- Query application：`winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/query/QueryBillApplicationService.java:1157`
- 策略路由：`winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/utils/StrategyUtil.java:43`
- WHTTP 路由配置查询：`winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/WHttpHelperImpl.java:53`
- WHTTP 实际远程发送：`winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/WHttpHelperImpl.java:92`
- 通用 RPC 包装：`winning-ward-common/src/main/java/com/winning/ward/common/util/WinRpcTemplate.java:14`
- 中医补充入口：`winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/FinanceHelperImpl.java:1271`

## 4. 三方服务依赖图谱
### 4.1 路由配置依赖
- `SubscriberRpcService.queryFhirTransaction`
- 落点：`winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/WHttpHelperImpl.java:53`
- 风险：每次选路都查，当前接口至少会多打 2 次配置查询。

### 4.2 第一段：核心余额查询
- 60 分支：`QueryBill60ServiceImpl.java:199` → `FinanceHelperImpl.java:296` → `basicsExpenseRpcService.queryByEncounterId`
- HTTP 分支：`QueryBillHttpServiceImpl.java:315` → `QueryBillHttpServiceImpl.java:871` → `WHttpHelperImpl.send()` → `wHttpGatewayRpcService.allInOne`
- FHIR 分支：`QueryBillFhirServiceImpl.java:87` → `FinanceHelperImpl.java:698` → `basicsExpenseApi.queryByEncounterId`

### 4.3 第二段：病案费用汇总
- 60 分支：`QueryBill60ServiceImpl.java:3719` → `FinanceHelperImpl.java:577` → `inpatientBillBMTSRpcService.queryInpatientBillDetailByEncIds`
- HTTP 分支：`QueryBillHttpServiceImpl.java:2202` → `WHttpHelperImpl.send()` → HIS，再经 `QueryBillHttpServiceImpl.java:2211` 做 MDM 码表转换
- FHIR 分支：`QueryBillFhirServiceImpl.java:424` → `FinanceHelperImpl.java:747` → `inpatientMedicalRecordApi.queryFee`

### 4.4 第三段：中医补充明细
- 固定直连 RPC，不走动态路由
- 路径：`FinanceHelperImpl.java:1275` → `medicalRecordAmtsRpcService.customQueryByEncounterId`
- 风险：注释提示依赖中心侧 SQL 配置，既慢又脆弱，适合优先隔离。

### 4.5 HTTP 分支额外隐含依赖
- 欠费额度 RPC：`winning-ward-basicdata/winning-ward-basicdata-application/src/main/java/com/winning/ward/basicdata/application/helper/FinanceMdmRpcHelper.java:158`
- 药占比查询：`winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/query/impl/QueryBillHttpServiceImpl.java:331`
- 床位 / 欠费额度 / 住院次数等通用附加查询

## 5. 瓶颈与风险分析
### 5.1 串行阻塞
- `BannerInfoService` 当前把 3 次远程查询串行执行。
- 三段间没有强依赖，却直接叠加 RT。
- 这是最直接的慢点和线程占用放大点。

### 5.2 过度取数
- 当前接口实际只消费余额相关字段。
- 但通用费用查询链路仍额外拉：住院次数、床位、欠费额度、药占比等。
- 特别是 HTTP 分支 `QueryBillHttpServiceImpl.java:331` 到 `QueryBillHttpServiceImpl.java:333` 的药占比调用，对当前接口是纯额外成本，因为 `BannerInfoService` 不消费 `medicinalScale`。

### 5.3 路由配置查询无缓存
- `SubscriberRpcService.queryFhirTransaction` 至少被调用 2 次。
- 这会把配置查询延迟直接叠加到用户请求。

### 5.4 HTTP 分支风险最高
- 静态估算：HTTP 分支每次请求大约 7~8 次远程依赖，再叠加约 4 次本地 DB 查询。
- 60 / FHIR 分支大约 5 次远程依赖。
- 所以如果中江当前走 HTTP，风险会明显更高。

### 5.5 本地 DB 重复查询
- 同一个 encounter 在 HTTP 分支被重复查询多次。
- 代表点：`QueryBillHttpServiceImpl.java:317`、`QueryBillHttpServiceImpl.java:350`、`QueryBillHttpServiceImpl.java:790`、`QueryBillHttpServiceImpl.java:2194`
- 单次不重，但高并发下会放大数据库压力。

### 5.6 非核心依赖拖垮核心路径
- HTTP 分支欠费额度查询返回 `null` 时，后续直接使用可能触发 NPE。
- 底层：`FinanceMdmRpcHelper.java:162` 异常时返回 `null`。
- 这意味着一个非核心配置服务有机会拖挂核心余额查询。

### 5.7 失败可观测性差
- 当前是“大 try/catch 包全段”。
- 结果常常不是明确失败，而是 200 + 部分字段为空。
- 容易掩盖故障，也不利于后续归因。

### 5.8 失败传播现状
- 第一段失败：几乎空结果。
- 第二段失败：保留余额字段，但直接跳过第三段。
- 第三段失败：只丢失 `tcm*` 字段。
- 这说明第二、三段天然适合改成增强型依赖并 fail-open。

## 6. 隔离优化方案草案
### 6.1 Phase 1：小改动大收益，优先止血
1. **第二段 + 第三段异步化并 fail-open**
   - 保留第一段核心余额同步等待。
   - 第二段病案费用汇总、第三段中医补充改为 `CompletableFutureBuilder` 并行执行。
   - 同模块已有现成用法：`winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoFromThirdPartyService.java:130`

2. **按子调用设置独立超时预算**
   - 核心余额：600~800ms
   - 病案费用：300~500ms
   - 中医补充：300~500ms
   - 路由配置查询：100~200ms
   - 不建议对重查询做业务层多次重试。

3. **拆分核心字段与增强字段**
   - 核心字段：`accountBalance`、`advancePaymentAmount`、`expenseAmount`、`advancePaymentBalance`、`guaranteedAmount`、`medInsurPayCost`、`personPayCost`
   - 增强字段：`chineseTreatmentFee`、`treatmentFee`、`chineseTreatmentPercent`、`tcmChineseTreatmentFee`、`tcmChineseTreatmentPercent`、`tcmHerbalMedicineFee`、`tcmPatentMedicineFee`
   - 原则：增强字段超时 / 失败直接置空，不阻断核心返回。

4. **给集成方式查询加本地缓存**
   - 缓存 key：`(hospitalSOID, transCode)`
   - TTL：5~10 分钟
   - 落点：`WHttpHelperImpl.queryFhirTransaction` / `getIntegrateTypeCode`
   - 直接收益：减少 2 次配置 RPC。

5. **跳过当前接口不消费的附加查询**
   - 优先跳过 HTTP 分支药占比查询：`QueryBillHttpServiceImpl.java:331`
   - 再评估床位、欠费额度、住院次数等通用附加查询是否可在 Banner 专用路径下跳过。
   - 如果不想新建接口，可先加内部标志：`fastMode` / `skipExtraFields`。

6. **非核心空值兜底**
   - 对欠费额度返回 `null` 的情况做空值兜底，默认欠费额度为 0。
   - 目标：避免一个配置类 RPC 导致核心查询 NPE。

### 6.2 Phase 2：中期稳定性治理
1. **统一熔断 / 超时收口**
   - WHTTP/HIS：优先挂在 `WHttpHelperImpl.send`
   - 普通 RPC：优先挂在 FinanceHelper / Bridge 层，而不是散落到各业务 Service

2. **按依赖组拆断路器**
   - 路由配置查询
   - 核心余额查询
   - 病案费用汇总
   - 中医补充明细
   - 原则：非核心依赖熔断时不影响核心余额。

3. **线程 / 连接池隔离**
   - 核心查询和增强查询不要共用同一批异步资源。
   - 防止增强调用反压核心路径。

4. **补子调用可观测性**
   - 当前只有总耗时日志：`winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoService.java:517`
   - 建议补：3 个子调用耗时、超时次数、降级次数、熔断状态。

## 7. 稳定判断
- **高置信判断**
  - 主因不是单点代码 bug，而是“同步串行外部依赖 + 过度取数 + 无显式隔离治理”的组合问题。
  - 第二段和第三段适合优先做增强依赖隔离。
  - 给路由配置加缓存、跳过药占比等无用查询，属于“小改动大收益”。

- **中置信判断**
  - 如果中江当前走 HTTP 分支，则这条链路是最像“节点 down 诱因放大器”的路径。

- **低置信 / 待运行时验证**
  - 中江当前到底走 60 / HTTP / FHIR 哪条分支。
  - 真实线上慢点中，三段调用的耗时占比具体是多少。

## 8. 风险与未定项
- 仓库代码无法直接确认“中江”当前的实际集成方式。
- 本轮仅做静态源码分析，未验证运行时耗时占比。
- 是否已有底层 RPC / 网关默认超时，需要运行环境补证。
- 第二段失败后是否还有业务上必须保底的字段，需再和业务使用方对齐。

## 9. 建议下一步
1. 到运行环境确认中江当前两个交易码的实际分支：
   - `399564662`：基础费用查询
   - `399626902`：病案费用分支选择
2. 补一条真实慢请求的分段耗时：
   - 路由配置查询
   - 第一段余额查询
   - 第二段病案汇总
   - 第三段中医补充
3. 若以最快止血为目标，优先级建议：
   - P0：第二段 + 第三段异步 fail-open
   - P0：集成方式缓存
   - P1：跳过 HTTP 分支药占比等无用附加查询
   - P2：统一熔断 / 超时治理
4. 若需要进入实施准备，下一轮可继续整理成 `P0/P1/P2` 的改造任务拆解清单。

## 10. executor-handoff-template
- 日期：2026-03-31
- 所属专项：日志猎人
- 子任务：中江病区护士站节点 down 事件——慢接口与三方服务隔离优化
- 当前阶段：方案
- 承接载体：executor + Codex

### 这轮为什么切给 executor
- 需要跨 `banner / finance / tripartite / basicdata / common` 多模块连续追踪。
- 需要从代码证据而不是口头猜测，收口问题特征与优化方向。
- 留在 `main` 容易停留在抽象讨论，难以拿到可执行的代码路径证据。

### 已确认结论
- 目标接口与主调用链已定位。
- 3 段关键远程调用当前串行执行。
- 当前缺少显式超时 / 熔断 / Bulkhead。
- 存在明显过度取数和配置查询无缓存问题。

### 本轮目标
- 收口关键代码路径
- 明确三方依赖与瓶颈位置
- 形成隔离优化方案草案

### 重点关注对象
- 关键接口：`/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id`
- 关键模块：`winning-ward-banner`、`winning-ward-finance`、`winning-ward-tripartite`、`winning-ward-basicdata`
- 关键文件：`BannerInfoService.java`、`QueryBillHttpServiceImpl.java`、`WHttpHelperImpl.java`、`FinanceHelperImpl.java`
- 关键现象：同步阻塞、过度取数、配置查询叠加、无隔离治理

### 希望 executor 回来时至少带回什么
- 当前结论
- 关键代码路径
- 可行方案草案
- 风险与待确认
- 建议下一步

## 11. execution-feedback-template
- 日期：2026-03-31
- 所属专项：日志猎人
- 执行载体：executor + `acp -> Codex`
- 任务类型：隔离改造方案分析

### 任务背景
- 中江病区护士站节点 down 事件继续挂在日志猎人专项下推进。
- 当前可疑接口已收敛到 banner 费用基础信息查询接口。

### 执行内容
- 通过 `acp -> Codex` 做深度代码阅读，追踪调用链与依赖。
- 识别同步串行依赖、过度取数、缓存缺失和非核心依赖拖挂风险。
- 形成以“并行化 + fail-open + 缓存 + 精简查询路径”为主的优化草案。

### 当前结果
- 已拿到可回收的分析报告。
- 已明确优先止血方向和实施顺序。
- 尚未进入代码修改和运行时验证阶段。

### 有效原因
- 任务满足 `executor / Codex` 适用条件：跨模块、多文件、强代码上下文。
- 现有代码中已存在 `CompletableFutureBuilder` 异步模式，可降低方案落地风险。

### 风险 / 不足
- 未确认中江当前运行分支。
- 未补真实慢请求的分段耗时。
- 仍需业务确认哪些字段允许降级。

### 可迁移经验
- 这类事故驱动分析，优先把依赖拆成“核心 / 增强”。
- 先找“同步串行 + 过度取数 + 配置查询无缓存”这三类问题，往往比一开始讨论熔断框架更有产出。
- 对护士站高频刷新接口，短 TTL 缓存和 fail-open 往往比重试更值。

### 对降本增效的影响判断
- 可显著减少事故排查时间。
- 可减少因非核心依赖拖垮主路径带来的节点风险。
- 可降低后续实施时的试错范围与沟通轮次。

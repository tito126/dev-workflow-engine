# 日志猎人

- 专项编号: P-2026-02
- 状态: 推进中
- 专项类型: 开发/落地类专项
- 健康度: 绿
- 优先级: 高
- 负责人: 第别
- 协同方: 工具组, 运维平台, 相关医院环境
- 开始时间: 2026-03-05 之前已启动
- 目标时间: 持续推进中

## 背景
"日志猎人"是用于日志巡检、异常分析和报告输出的持续型项目,面向不同医院环境提供日志拉取、异常分类、慢接口分析和 HTML 报告能力,同时兼顾 K8s 环境和传统服务器环境。

## 目标
形成可演示、可复用、可持续扩展的日志巡检能力,支持从日志获取到分析报告输出的完整链路,并具备面向真实医院环境的落地能力。

## 要解决的问题
- 手工排查日志效率低,难以快速定位异常和慢接口
- 不同医院环境差异较大,处理路径不统一
- 需要一套可展示成果、可支撑答辩和汇报的完整方案
- 阶段成果较多,如果不专项化记录,后续演进容易零散

## 价值
- 提高日志排障效率
- 提升异常分析和问题定位能力
- 降低人工整理报告成本
- 支持答辩、汇报、演示和后续推广复用

## 当前进度
根据既有沉淀,当前已完成核心能力搭建,并打通 K8s 与 tool_api 两条主要业务线。项目已形成流程文档、分析报告、关键脚本和多轮联调结论。答辩材料方面,已完成从 `v11` 到 `v12` 的一轮集中收敛,已围绕"问题驱动、持续优化、验证闭环"重新校正文案主线,并纠正了"健壮性"表述偏差,当前阶段可视为答辩材料暂告一段落,后续重心转向抽时间持续补强验证闭环。

围绕真实事故样例“中江病区护士站节点 down 事件”,当前也已完成一轮基于 `executor -> acp -> Codex` 的源码分析收口: 已确认目标接口、关键代码路径、三方依赖结构、主要瓶颈与隔离优化草案,并已回写正式分析报告,可作为后续技术评审和实施拆解的共同底稿。

今天又继续把高危慢接口证据从“已有判断”推进到“跨现场可对照的结构化证据底稿”：已分别完成长治（2026-04-21）与晋城（2026-04-15）两批 `slow_api` trace 的全量提取、完整异常链路回捞与摘要化整理，并进一步合成为一版可直接支撑“护士站三方服务隔离方案”设计的对照分析稿。当前这条线的阶段状态，已经从“继续补日志证据”推进为“足以支撑设计澄清 / 方案分层”的程度，但仍未进入正式实施阶段。

## 核心成果
- 两阶段日志拉取与完整链路补强
- 四级分组、代表 trace、调用方识别、慢接口分析
- HTML 报告输出能力
- K8s 路线流程沉淀
- tool_api 测试环境联调打通
- 多医院/多环境适配经验沉淀

## 当前答辩准备
- 场景: AI 技术大赛汇报演示 PPT
- 截止: 2026-03-22
- 当前状态: 本轮答辩材料已阶段性收口,后续以小幅微调和现场使用为主
- 当前版本: `work-system/deliverables/log-hunter-ai-presentation-2026-03-21-v12-notes.pptx`
- 配套脚本: `work-system/deliverables/build_log_hunter_ppt_v12_notes.py`
- 配套答辩稿: `work-system/deliverables/log-hunter-ai-presentation-2026-03-21-v12-speech.md`
- 口语版答辩稿: `work-system/deliverables/log-hunter-ai-presentation-2026-03-21-v12-speech-colloquial.md`
- Q&A 模板: `work-system/deliverables/log-hunter-ai-presentation-2026-03-21-v11-qa.md`
- 队伍名称: 日志猎人
- PPT 模板: `D:\WXWork\1688852666741352\Cache\File\2026-03\【 汇报序号+ 参数项目分类 +队名队长姓名 工号 +队伍名称】AI技术大赛汇报演示PPT模板.pptx`
- 模板结构: 封面 -> 团队介绍 -> 汇报目录 -> 项目背景与目标 -> 技术原理与实现 -> 算法/能力亮点 -> 成果展示与前景 -> 总结展望 -> 收获 -> 未来规划 -> Q&A
- 本轮已完成调整:
  - 解决 `P1` 与 `P3` 职责重复问题,强化页面分工
  - 根据用户反馈削弱"技术炫技感",将中段重心收回到"事后响应痛点、持续优化方向、验证闭环机制"
  - 将后续思考重新纳入答辩表达,包括系统健壮性提升、性能优化、日志质量分析增强、日志反哺建议等方向
  - 补齐并迭代演讲者备注,形成 `v12-notes`
  - 重排 `P9-P10` 成果展示页,更突出报告结果和定位价值
  - 纠正"健壮性"表述使用偏差,统一回到"支撑系统健壮性提升"的表达框架
- 当前记录方式: 将"答辩 PPT 准备"作为本专项下的当前阶段任务管理,不单独拆成新专项;时间节点由提醒区承接,材料内容由本专项档案承接

## 里程碑
- [x] 完成核心日志巡检能力搭建
- [x] 完成 K8s 路线主要流程沉淀
- [x] 完成 tool_api 测试环境联调打通
- [x] 完成答辩 PPT 材料梳理
- [x] 完成答辩 PPT 初版(v8)
- [x] 完成带演讲者备注的答辩 PPT 精修版(v9-notes)
- [x] 完成按 15 分钟答辩节奏收敛的 v10-notes 和配套答辩稿
- [x] 完成更适合直接照读的 v11-notes 和 v11 答辩稿
- [x] 完成基于表述纠偏后的 `v12-notes`、正式稿和口语稿
- [x] 完成本轮答辩 PPT 阶段性定稿

## 风险与待确认
- 传统服务器生产环境验证仍待后续推进
- 答辩材料虽然已阶段性收口,但验证闭环目前仍主要停留在答辩表达层,后续还需要继续沉淀成可复用的执行路径
- 现有成果较多,后续若继续扩展内容,仍需要控制重点,避免重新回到信息堆积
- 中江病区护士站慢接口问题当前仍停留在静态源码分析阶段,尚未补齐运行时分段耗时与实际集成方式证据
- 中江当前到底走 `60 / HTTP / FHIR` 哪条分支尚未确认; 若实际走 HTTP, 风险等级预计更高
- 2026-04-07 乐山、2026-04-15 晋城、2026-04-21 长治三批高危性能场景已共同呈现“系统被拖垮”或具备拖垮节点能力的信号,问题已从一般慢接口进一步升级为跨现场重复出现的结构性风险
- 当前已能看到三类重复模式: 核心读链路被重增强逻辑拖挂、执行计划/库存/单位换算链路在业务线程内高密度串行处理、以及异常通知/三方依赖链路反向放大线程资源消耗
- 虽然证据已足以支撑方案设计,但“隔离方案”本身仍未落到具体任务号、目标仓与实施边界,若后续不及时承接到护士站设计/研发主线,日志猎人的价值仍可能停留在发现问题而不是推动治理

## 下一步动作
- **中江病区护士站慢接口优化**：基于 Codex 分析结果，推进隔离优化方案（详见 deliverables/zhongjiang-2026-03-31-slow-api-analysis.md）
- **长治 / 晋城高危慢接口治理**：把现有对照证据正式承接到“护士站三方服务隔离方案”设计阶段,优先明确核心读链路、三方增强链路、执行校验链路、异常通知链路四层隔离边界
- 基于 `work-system/deliverables/log-inspect/changzhi-jincheng-slow-api-isolation-evidence-comparison-2026-04-22.md`，继续压缩出可对外同步的简版口径,并在合适时机转成 `nurse-station` 的 `brainstorming / planning` 输入
- 若继续推进实施,优先补齐任务号、目标仓、代码基线和设计边界,避免证据已齐但无法进入研发执行
- 基于 `main / executor / Codex` 联调实际进展，继续把这条链路从"可用验证"推进到"可复用工作法"
- 抽时间继续补强"发现问题 - 生成建议 - 推动整改 - 回看验证"的验证闭环
- 将答辩阶段形成的表达、材料和后续验证动作继续沉淀为专项可复用资产
- 结合后续真实场景，继续推进传统服务器生产环境验证和闭环佐证

## 最近更新
- 2026-04-22: 围绕长治（2026-04-21）与晋城（2026-04-15）两批高危慢接口事件,已分别完成 `slow_api` trace 全量提取、原始日志完整异常链路回捞和摘要表整理,并进一步合成为一版面向“三方服务隔离方案”设计的对照分析稿。当前已可共同支撑以下判断: 一是 `patient_list/query/by_example` 在长治、晋城均已出现 `Java heap space`,说明核心读链路具备直接拖垮请求线程的能力; 二是 `inpat_banner_basics_expense/query/by_id` 在长治、晋城均反复落入高危慢链路,且长治已明确暴露 `FinanceHelperImpl -> MedicalRecordAmtsRpcService -> HIS DataCenterSqlEngine` 的同步强依赖异常链; 三是晋城 `VerifyMaterialService` 在 `exe-*` 业务线程内对大量执行计划做库存/单位换算/系数匹配,说明执行校验链路本身就是独立重处理链。对照稿已落到 `work-system/deliverables/log-inspect/changzhi-jincheng-slow-api-isolation-evidence-comparison-2026-04-22.md`, 当前阶段判断已从“补证据”推进为“足以支撑护士站三方服务隔离设计澄清”。
- 2026-04-16: 围绕 2026-04-07 乐山与 2026-04-15 晋城两次高危性能场景,开始基于 `slow_api` 代表 trace 提炼详细链路与堆栈证据。当前已确认晋城侧存在三类可支撑治理的关键信号: 一是 `VerifyMaterialService` 在业务线程内对执行计划做大量串行药品校验 / 库存 / 单位换算处理; 二是 `OrderChangeWebSocketHandler -> SessionUtils.sendMessage` 链路在 `Jetty-Worker` 线程内因 `ClosedChannelException` 展开完整 WebSocket 异常堆栈; 三是同一时间窗口内混有多个 `hystrix-*` 远程依赖线程池调用。当前判断已可初步支撑“慢接口 + 异常通知链路 + 远程依赖交织,缺少有效隔离机制,具备拖垮节点的结构性风险”这一问题定义,初稿已落到 `work-system/deliverables/log-inspect-slow-api-stack-evidence-2026-04-16.md`。

## 中江子任务快照
- 子任务: 中江病区护士站节点 down 事件——慢接口与三方服务隔离优化
- 当前状态: 已完成静态源码分析与方案草案,未进入实施
- 当前结论:
  - 目标接口: `/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id`
  - 主调用链: `BannerInfoController.java:200` → `BannerInfoService.java:436`
  - 主问题: 3 段远程依赖串行执行 + 通用查询链路过度取数 + 集成方式查询无缓存 + 缺少显式超时/隔离治理
- 关键代码路径:
  - `winning-ward-banner/winning-ward-banner-api/src/main/java/com/winning/ward/banner/api/controller/BannerInfoController.java:200`
  - `winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoService.java:436`
  - `winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/WHttpHelperImpl.java:53`
  - `winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/WHttpHelperImpl.java:92`
  - `winning-ward-tripartite/winning-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/FinanceHelperImpl.java:1271`
  - `winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/query/impl/QueryBillHttpServiceImpl.java:315`
  - `winning-ward-finance/winning-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/query/impl/QueryBillHttpServiceImpl.java:2202`
- 优化方案草案:
  - `P0`: 第二段 / 第三段异步 fail-open
  - `P0`: `(hospitalSOID, transCode)` 集成方式查询加 5~10 分钟缓存
  - `P1`: 跳过 HTTP 分支药占比等当前接口未消费的附加查询
  - `P2`: 统一熔断 / 超时 / 线程隔离治理
- 风险与待确认:
  - 未确认中江当前实际走 `60 / HTTP / FHIR` 哪条分支
  - 未补真实慢请求的分段耗时证据
  - 尚需业务确认哪些增强字段允许降级为空
- 下一步:
  - 先补运行环境分支证据和分段耗时
  - 再决定是先止血优化还是直接进入中期治理

## 更新记录
- 2026-04-22: 把长治 / 晋城两批高危慢接口证据推进到可直接支撑“护士站三方服务隔离方案”设计的阶段,新增 trace 清单、完整异常链路、摘要表和对照分析稿,并明确当前更适合作为 `nurse-station` 的 `brainstorming / planning` 启动输入,而非直接进实现阶段。
- 2026-03-31: 补充记录"昨天通过 `APC` 联调 `Codex` 已有实际进展"这一新状态。当前判断不再停留在工具尝鲜,而是已经出现方法论价值:一方面说明 `Codex` 适合承接部分事故驱动、探索性强、需要文件/代码上下文的执行任务;另一方面也暴露出一个管理要求--这类新进展如果不及时写入项目 `Latest Update / Next Action`,第二天的 `Daily Focus` 容易漏抬头。后续应把这类"昨天刚发生、今天值得继续推进"的进展,作为 `Daily Focus` 的显式提取信号。
- 2026-03-30: 围绕中江病区护士站节点 down 事件,确认可疑接口 `/api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id` 继续作为本专项的真实落地样例推进;今天同时完成 `Codex` 链路关键验证,并形成 `main / executor / Codex` 的最小协作工作法。
- 2026-03-22: 基于用户反馈,纠正答辩材料中"健壮性"表述偏差,生成 `log-hunter-ai-presentation-2026-03-21-v12-notes.pptx`、`build_log_hunter_ppt_v12_notes.py` 及配套讲稿,并将当前阶段状态更新为"答辩材料暂告一段落,后续持续补强验证闭环"。
- 2026-03-21: 根据最新反馈,将中段内容从偏技术路径改回"问题驱动 + 持续优化 + 闭环验证"导向,产出 `log-hunter-ai-presentation-2026-03-21-v9-notes.pptx` 和 `build_log_hunter_ppt_v9_notes.py`。
- 2026-03-21: 根据用户反馈重写 `P4-P7` 主线,优化 `P9-P10` 成果展示页,并产出 `log-hunter-ai-presentation-2026-03-21-v8.pptx`。
- 2026-03-19: 用户确认参赛名称使用"日志猎人"。
- 2026-03-19: 将答辩 PPT 准备作为当前阶段重点任务纳入专项档案。

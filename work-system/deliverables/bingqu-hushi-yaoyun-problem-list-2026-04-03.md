# 病区护士（姚云）问题清单

- 来源：`E:\winning-code\ai\temp\【内部】临床&医管高危代码修复计划.xlsx`
- 工作表：`病区护士（姚云）`
- 原始问题数：`103`
- 收编时间：`2026-04-03 15:56`

## 扫描要求
- 代码高危漏洞扫描要求
- 1、每周至少扫描一次，优先在公版分支执行；特性分支待公版验证修复后再合并。
- 2、高危漏洞本周必须处理，其他等级漏洞排期修复，无需处理的备注原因。
- 3、漏洞修复后需复测，扫描及处理结果留存归档。

## 原始问题台账

| 代码扫描时间 | 问题描述 | 危险等级 | git分支 | 涉及文件 / 范围 | 计划修复时间 | 责任人 | 实际修复时间 | 扫描工具 | 改造建议链接地址 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-27 00:00:00 | RPC调用未配置超时时间 | 高 | sr-next | winning-ward-bedcard/winning-ward-bedcard-application/src/main/java/com/winning/ward/bedcard/application/service/BedCardService.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | Redis缓存键未设置过期时间 | 高 | sr-next | winning-ward-bedcard/winning-ward-bedcard-application/src/main/java/com/winning/ward/bedcard/application/service/BedCardService.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 单次接口可能存在多次SQL调用 | 高 | sr-next | winning-ward-bedcard/winning-ward-bedcard-application/src/main/java/com/winning/ward/bedcard/application/service/BedCardService.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用Redis危险命令，未设置过期时间 | 高 | sr-next | winning-ward-bedcard/winning-ward-bedcard-application/src/main/java/com/winning/ward/bedcard/application/service/InpatientEncounterController.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | Redis查询操作未设置键过期时间 | 高 | sr-next | winning-ward-bedcard/winning-ward-bedcard-application/src/main/java/com/winning/ward/bedcard/application/utils/TagUtil.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 循环中存在数据库查询风险 | 高 | sr-next | winning-ward-allergy/winning-ward-allergy-application/src/main/java/com/winning/ward/allergy/application/service/InpatientEncounterService.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异常处理中未包含具体错误信息 | 高 | sr-next | winning-ward-allergy/winning-ward-allergy-application/src/main/java/com/winning/ward/allergy/application/service/CoordinatorRpcService.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能存在频繁的RPC调用 | 高 | sr-next | winning-ward-banner/winning-ward-banner-application/src/main/java/com/winning/ward/banner/application/service/BannerInfoFromThirdPartyService.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | HTTP连接和读取超时未配置 | 高 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/http/client/core/httpurl/UnifiedHttpURLClient.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能使用IP直接调用第三方接口 | 低 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/http/client/core/httpurl/UnifiedHttpURLClient.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用LOGGER.error记录异常，但未完全确保资源释放 | 高 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/http/client/core/httpurl/UnifiedHttpURLClient.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 多线程共享变量未使用volatile | 高 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/PageUtil.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 单接口RPC调用次数可能超过100 | 高 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/RpcUtil.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 未确保子线程正确传递上下文 | 高 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/RpcUtil.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 导入了未使用的ConvertUtil和ListUtil | 高 | sr-next | winning-ward-common/src/main/java/com/winning/ward/common/util/PageUtil.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能存在字符串拼接SQL | 高 | sr-next | winning-ward-config/winning-ward-config-application/src/main/java/com/winning/ward/config/application/repository/encounter/jpa/BedRelatedChargeSvcJpa.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用select new语法 | 高 | sr-next | winning-ward-config/winning-ward-config-application/src/main/java/com/winning/ward/config/application/repository/encounter/jpa/BedRelatedChargeSvcJpa.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | JPQL查询中存在字符串拼接 | 高 | sr-next | winning-ward-config/winning-ward-config-application/src/main/java/com/winning/ward/config/application/repository/encounter/jpa/BedRelatedChargeSvcJpa.java | 2026-04-10 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | JPQL查询中使用了别名b，但在where条件中使用了a.isDel | 高 | sr-next | winning-ward-config/winning-ward-config-application/src/main/java/com/winning/ward/config/application/repository/encounter/jpa/BedRelatedChargeSvcJpa.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-finance/win-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/rule/ConstraintRuleApplicationService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-finance/win-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/template/BillTemplateApplicationService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-finance/win-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/template/BillTemplateApplicationService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-finance/win-ward-finance-application/src/main/java/com/winning/ward/finance/application/service/wardbill/WardBillApplicationService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在多表JOIN操作 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/repository/request/DispenseRequestDomainService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/repository/request/impl/InpMedDispenseRequestHqlRepositoryImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能存在SQL注入风险 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/repository/request/impl/InpMedDispenseRequestHqlRepositoryImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/repository/request/impl/InpMedDispenseRequestHqlRepositoryImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/repository/stock/PatientMedStockDomainService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/fhir/InpDispenseRequestFhirService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/request/InpMedDispenseRequestOperateService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/request/InpMedDispenseRequestOperateService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/request/InpMedDispenseRequestService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/request/InpMedDispenseRequestService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/specialmed/InpMedSpecialMedService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/specialmed/InpMedSpecialMedService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-material/win-ward-material-application/src/main/java/com/winning/ward/material/application/service/specialmed/InpMedSpecialMedService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-newborn/win-ward-newborn-application/src/main/java/com/winning/ward/newborn/application/repository/InpatEncMaternityDomainRepository.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-plugin/win-ward-plugin-application/src/main/java/com/winning/ward/plugin/application/service/ExecBizNurseMessageService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-plugin/win-ward-plugin-application/src/main/java/com/winning/ward/plugin/application/service/exec/CliOrderRevokedPostServiceImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-plugin/win-ward-plugin-application/src/main/java/com/winning/ward/plugin/application/service/exec/CliOrderSignOffPostServiceImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-plugin/win-ward-plugin-application/src/main/java/com/winning/ward/plugin/application/service/fhir/PlanStateChangeRevokedFhirServiceImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/bo/order/ExecCliOrderDocDetailDisplayOutputBO.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/repository/material/InpMedDispenseRequestHqlRepository.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能存在SQL注入风险 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/repository/material/InpMedDispenseRequestHqlRepository.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能存在SQL注入风险 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/repository/material/InpMedReturnRequestDomainRepository.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/encounter/PrintEncounterService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/encounter/PrintEncounterService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/material/PrintMedReturnRequestService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/material/PrintMedReturnRequestService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintCliOrderDocDefService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintCliOrderDocDefService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintCliOrderDocDefService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintCliOrderDocService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintCliOrderDocService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintCliOrderDocService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintExecDefinitionService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintExecDefinitionService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintExecPlanService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintExecPlanService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderChangeService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderChangeService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderChangeService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderMainService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderMainService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderRequisitionService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintOrderRequisitionService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintWardExecDefinitionDocService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 存在线程安全问题 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintWardExecDefinitionDocService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/PrintWardExecDefinitionDocService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/changeBiz/BizExecChangeOrderPrintService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-print/win-ward-print-application/src/main/java/com/winning/ward/print/application/service/order/changeBiz/BizExecChangeOrderPrintService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 异步上下文传递不完整 | 高 | sr-next | winning-ward-tags/win-ward-tags-application/src/main/java/com/winning/ward/tags/application/service/EncounterTagDataService.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-tripartite/win-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/ChartHelperImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-tripartite/win-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/OrderExecHelperImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-tripartite/win-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/impl/TaikangBzHelperImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 可能存在SQL注入风险 | 高 | sr-next | winning-ward-tripartite/win-ward-tripartite-application/src/main/java/com/winning/ward/tripartite/application/repository/CliDiagnosisQueryRepository.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 下游调用未配置超时时间 | 高 | sr-next | winning-ward-work-log/win-ward-work-log-application/src/main/java/com/winning/ward/work/log/application/repository/impl/InpatWardWorkDomainRepositoryImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 事务中可能包含RPC调用 | 高 | sr-next | winning-ward-work-log/win-ward-work-log-application/src/main/java/com/winning/ward/work/log/application/repository/impl/InpatWardWorkDomainRepositoryImpl.java | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用window.eval()执行动态代码存在安全风险 | 高 | sr-next | winning-webui-admin-execution-inpatient/src/pages/EncounterMain/patientConsultation/bedcardSetting2/async-component/src/getComponent.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用window.eval()执行动态代码存在安全风险 | 高 | sr-next | winning-webui-admin-execution-inpatient/src/pages/EncounterMain/patientConsultation/bedcardSetting2/async-component/src/getComponent.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象注入dispatchWinningEvent方法 | 高 | sr-next | winning-web-carnation/src/system/index.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象添加loadMore属性 | 高 | sr-next | winning-webui-admin-execution-inpatient/src/directive/load-more/index.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象添加loadMore属性 | 高 | sr-next | winning-webui-admin-execution-inpatient/src/directive/load-moreTable/index.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象添加winning属性 | 高 | sr-next | winning-webui-admin-execution-inpatient/src/app.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象注入selfwinning属性 | 高 | sr-next | winning-webui-inpatient-bedcard/src/components/personDrawer/utils/mywinning.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用了动态require | 高 | sr-next | winning-web-carnation/.sparkrc.ts | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用动态fetch加载远程组件 | 高 | sr-next | winning-webui-admin-execution-inpatient/src/pages/EncounterMain/patientConsultation/bedcardSetting2/async-component/src/getComponent.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用动态require或import | 高 | sr-next | winning-webui-inpatient-nursingtask/src/pages/order-task-new/dialog/asyncImport.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用动态require或import | 高 | sr-next | winning-webui-inpatient-costcheck/src/pages/supplementBookkeeping-entire/asyncImport.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用动态require或import | 高 | sr-next | winning-webui-admin-execution-inpatient/src/router/routes.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用原生fetch而非@winex-plugin/win-request | 高 | sr-next | winning-web-carnation/src/api/dataBase.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用axios而非@winex-plugin/win-request | 高 | sr-next | winning-webui-admin-execution-inpatient/src/service/axios.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用非规范的请求库 | 高 | sr-next | winning-webui-inpatient-nursingtask/src/pages/order-task-new/index.vue | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用非规范的请求库 | 高 | sr-next | winning-webui-inpatient-costcheck/src/utils/request.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 70个文件使用lodash而非lodash-es | 高 | sr-next | 多个文件 | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 直接监听store的state对象 | 低 | sr-next | winning-webui-admin-execution-inpatient/src/pages/CriticalSet/mixin.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | methods后面缺少逗号 | 低 | sr-next | winning-webui-admin-execution-inpatient/src/pages/404.vue | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象注入属性 | 高 | sr-next | winning-webui-inpatient-nursingtask/src/lib/umy-ui/index.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 向window对象注入属性 | 高 | sr-next | winning-webui-inpatient-bedcard/src/app.js | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 45个文件使用动态require | 高 | sr-next | 多个路由文件 | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用lodash而非lodash-es | 高 | sr-next | winning-webui-inpatient-nursingtask/src/pages/plan-apply/component/chooseTable.vue | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 使用lodash而非lodash-es | 高 | sr-next | winning-webui-inpatient-dischargeoutarea/src/pages/dischargeOutArea/components/DischargeCheckNew.vue | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |
| 2026-03-27 00:00:00 | 69个文件使用watch需检查 | 低 | sr-next | 多个Vue文件 | 2026-04-15 00:00:00 |  |  | openclaw+glm4.7 |  |  |

## AI 预整理
- 总问题数：`103`
- 分支：`sr-next`
- 扫描工具：`openclaw+glm4.7`
- 计划修复时间范围：`2026-04-10 00:00:00` ~ `2026-04-15 00:00:00`
- 危险等级分布：`高` 95条，`低` 8条

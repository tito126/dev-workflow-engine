# 执行计划 - 1554774

## 计划头
- 事项标识：`1554774-2026-04-13`
- 任务级别：`medium`
- 执行载体：`ACP opencode` 优先
- 目标：确认 1554774 对 1540718 的补充改动点，并在前置允许时直接落地最小代码修改
- 仓库：`E:\winning-code\akso5\winning-nis-ward`
- 模块：住院护士站后端执行计划查询链
- YAML 路由文件：`work-system/config/nurse-station-repo-routing.yaml`
- 首扫根：`E:\winning-code\akso5\winning-nis-ward`
- 候选扩扫根：无，当前不计划跨仓
- 禁止扫描根：`E:\winning-code\work`、`E:\winning-code\ai`
- 受保护文案：无
- 是否允许改写文案：否
- 范围内：接口 `queryOrderExecPlanResults` 相关 service / repository / SQL 拼接
- 范围外：前端、无关模块、接口协议调整、大范围数据库治理
- 允许改动层级：SQL 结构、小范围查询逻辑；索引脚本待确认
- 共享上下文摘要：1554774 是 1540718 的补充，TFS 当前口径从 `UNION ALL` 倾向转向 `OR + 索引`
- 成功锚点：
  1. 找到当前实现与 1540718 已落地改动
  2. 确认 1554774 补充点会影响哪些文件和语义
  3. 明确是否允许 `OR`、是否允许新增索引
  4. 若放行则完成最小改动并给出验证证据
- 验收方式：代码证据为主，真实性能效果待环境验证
- 证据预期：findings、implementation-result、verification-evidence
- 运行时路径：本轮先用一次性 ACP run
- 后续阶段需镜像的产物：`findings.md`、`implementation-result.md`、`verification-evidence.md`
- 预期 findings 捕获：现状 SQL、1540718 已改位置、1554774 影响点、是否涉及索引脚本
- 编码前确认项：是否以 1554774 补充口径覆盖 1540718；是否允许新增索引
- 分析后用户确认闸门：`UNION ALL -> OR` 是否放行；索引是否由本轮一并处理
- 若范围后续变化，需优先重写的段落：目标、允许改动层级、成功锚点、编码前确认项

## 角色分工
- 主控：整理 TFS / 1540718 上下文，维护产物，吸收定位和实现结果
- 定位 / 分析：定位当前代码、核对上一轮改动、识别补充需求影响点
- 实现执行：在确认放行后做最小改动
- 验证 / 评审：核对代码完成、需求完成、效果验证边界

## 任务
- 任务 1：补充需求定位
  - 目的：确认 1554774 对现有实现的真实影响
  - 输入：TFS 1554774、1540718 产物、当前仓库代码
  - 可能文件：`ExecPlanRestImpl`、`ExeOrderExecuteQueryServiceImpl`、`ExecPlanRepositoryImpl`、相关 mapper/xml、索引脚本目录
  - 输出：结构化 findings
  - 应沉淀为：`findings.md`
  - 验证方式：能明确文件、SQL、差异点、待确认问题
- 任务 2：最小实现
  - 目的：在确认口径后直接编码
  - 输入：findings + 用户确认
  - 可能文件：定位阶段收窄后的后端文件
  - 输出：补丁与实现报告
  - 应沉淀为：`implementation-result.md`
  - 验证方式：代码 diff、定向检查、必要时编译/测试

## 风险
- SQL / 性能优化任务存在语义变化风险，不能跳过分析后确认闸门
- 索引策略可能与上一轮约束冲突
- 若 ACP 阻塞，需先汇报，再等第别决定是否降级

## 执行就绪度
- 是否可进入编码：否
- 缺失前提：补充需求的代码定位结果 + `OR/索引` 放行确认

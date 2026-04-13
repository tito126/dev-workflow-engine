# 定位结果 - 1516840

- 仓库：
  - 后端主根：`backend_main -> E:\winning-code\akso5\winning-nis-ward`
  - 前端主根：`frontend_main -> E:\winning-code\frontend\webui-next`
  - 本轮实际命中的前端子项目：`E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient`
- 模块：
  - 前端页面：`LongOrderFirstMedicineExecRules`
  - 前端 store / API 配置：同名模块
  - 后端对外入口：`winning-ward-execution-order-api` 的首日规则接口
  - 后端配置域入口：`winning-ward-config-api` 的 MAS 首日规则接口
  - 下游业务关联：执行计划拆分 / 首日标识 / 物资流向相关逻辑
- YAML 路由文件：`work-system/config/nurse-station-repo-routing.yaml`
- 首扫根：`backend_main -> E:\winning-code\akso5\winning-nis-ward`
- 首扫根来源：历史本轮用户给定仓库
- 实际扫描根：
  - `E:\winning-code\akso5\winning-nis-ward`
  - `E:\winning-code\frontend\webui-next`
- 被排除的根：
  - `E:\winning-code\work`
  - `E:\winning-code\ai`
- 扩扫触发原因：首扫根内只命中后端规则链，未命中页面实现；结合“页面/文案类需求”特征，向前端主根定向收窄后命中实际子项目
- 需要更新的发现章节：`findings.md`

## 可能入口文件

### 前端页面真实入口
1. `E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient\src\pages\LongOrderFirstMedicineExecRules\Index.vue`
   - 页面名就是“长期医嘱首日用药执行规则”
   - 当前页面是左右布局，左侧规则列表，右侧规则详情与编辑区
   - 已检索到：当前页面里没有现成的 `el-alert` / `tooltip` / `popover` / “说明” / “提示” 区块，说明文案大概率需要直接补在这个页面里

2. `E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient\src\store\modules\LongOrderFirstMedicineExecRules\index.js`
   - 页面通过 store action 拉取列表、详情、保存、启停、删除、排序等行为
   - 如果说明文案只是静态页面说明，这个文件大概率不用改
   - 如果说明文案要来自接口返回或配置元数据，这里要跟着加取数 / 映射

3. `E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient\src\api\api-config\LongOrderFirstMedicineExecRules.js`
   - 定义首日规则页面调用的 API 路径
   - 当前已经有 search / detail / save / update / enabled / delete / seq_no 等接口映射
   - 如果后端新增“说明文案”字段并从现有接口返回，这个文件大概率不需要单独加新接口；如果要独立说明接口，则需要改这里

### 后端页面接口入口
4. `E:\winning-code\akso5\winning-nis-ward\winning-ward-execution-order\winning-ward-execution-order-api\src\main\java\com\winning\ward\order\api\controller\ExecFirstDayMedicationRuleController.java`
   - 前端更可能直接打到这组 `api/v1/.../exec_first_day_medication_rule/...` 接口
   - 提供列表、详情、保存、启停、删除、修改、排序

5. `E:\winning-code\akso5\winning-nis-ward\winning-ward-config\winning-ward-config-api\src\main\java\com\winning\ward\config\api\controller\firstday\ExecFirstDayMedicationRuleMasController.java`
   - 配置域 / MAS 侧也有同表接口
   - 如果前端走的是 config 域代理，也可能从这边透出；但从页面 API 命名看，更优先怀疑前端直连的是 execution-order-api 暴露的首日规则接口

## 关键关联文件

### 前端关联
- `src\api\index.js`
  - 能搜到 `LongOrderFirstMedicineExecRules` 模块注册
- `src\router\modules\execution.js`
  - 有执行域相关路由，说明页面挂在执行域前端里
- 物资流向相关前端页面 / API 配置
  - 已定位到 `DoctorAdviceDirection` 相关页面与 API 配置
  - 若说明文案里需要放“去哪里配置医嘱物资流向”的明确路径，这组页面是后续需要联动核对的前端落点

### 后端首日规则数据链
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\service\execrule\impl\ExecFirstDayMedicationRuleServiceImpl.java`
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\repository\execrule\impl\ExecFirstDayMedicationRuleRepositoryImpl.java`
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\bo\execdef\ExecFirstDayMedicationRuleBO.java`
- `winning-ward-execution-order-api\src\main\java\com\winning\ward\order\api\dto\execdef\ExecFirstDayMedicationRuleDTO.java`
- `winning-ward-config-application\src\main\java\com\winning\ward\config\application\service\rules\impl\ExecFirstDayMedicationRuleServiceImpl.java`
- `winning-ward-config-api\src\main\java\com\winning\ward\config\api\dto\firstday\response\ExecFirstDayMedicationRuleDTO.java`
- `winning-ward-model\src\main\java\com\winning\ward\entity\order\ExecFirstDayMedicationRule.java`
- `winning-ward-model\src\main\java\com\winning\ward\entity\rules\firstday\MdsExecFirstDayMedicationRule.java`

### 与“首日标识影响执行计划 / 物资流向”有关的下游业务文件
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\service\execplan\impl\ExecOrderPlanServiceImpl.java`
  - 能看到“长期输液医嘱默认病区配液规则 all / firstDay”
  - 能看到 `EX025`、`EXEC_REQ_002` 等与首日 / 流向药房相关的参数读取
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\common\constants\RuleCodeConst.java`
  - 有 `LONG_ORDER_WARD_DISPENSING`、`LONG_ORDER_FIRST_NOT_EXEC`、`FIRST_TIME_RULE_DATE`、`FIRST_TIME_RULE_TIME`、`OPEN_PHARMACY`
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\common\constants\CliSettingNoConst.java`
  - 有 `EXEC_REQ_002`，语义是“输液新开医嘱首日与次日执行流向药房分开”
- `winning-ward-execution-order-application\src\main\java\com\winning\ward\order\application\common\constants\WardOrderCommonConst.java`
  - 有 `EX025`，语义是“非静配药品领药药房流向配置”

## 当前行为拼装方式

### 前端层
- 页面主入口已经明确在前端仓 `LongOrderFirstMedicineExecRules/Index.vue`
- 页面通过同名 store 模块调 API 配置里的首日规则接口
- 当前页面是“规则列表 + 详情编辑”的配置页形态
- 当前没有现成说明区 / 帮助区 / tooltip 组件，说明文本如果要直接让用户看见，最自然的落点是：
  1. 页面头部标题下方增加静态说明区
  2. 右侧规则详情头部增加说明区
  3. 若希望更轻，可在表单顶部增加说明块

### 后端层
- execution-order-api 暴露前端可用的首日规则 CRUD 接口
- execution-order-application / config-application 都映射到 `EXEC_FIRST_DAY_MEDICATION_RULE` 表
- 当前实体 / DTO / BO 字段基本只覆盖：规则名、条件、开始时间类型、截止类型、截止时间、启停、排序等
- **没有看到现成“说明文案 / 帮助文案 / 提示文案 / remark / memo / description”这类业务字段**
- 这说明如果需求是“页面展示一段参数说明”，更像是**前端静态说明文案需求**，而不是现成后端字段改个映射就完事

### 业务关联层
- 首日规则本身在首日配置表里维护
- 执行计划拆分、首日标识、病区配液、首日药房、物资流向等效果，分散在执行计划生成 / 流向判断逻辑里
- 这与 requirement-summary 里的判断一致：
  - “首日”不是直接等于流向控制
  - 还需要与医嘱物资流向配置结合才会体现最终业务效果

## 可能改动文件

### 如果采用“前端静态说明文案”方案，最小改动面优先是
1. `E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient\src\pages\LongOrderFirstMedicineExecRules\Index.vue`
   - 直接补说明块
   - 大概率是本轮最小、最稳的实现入口

### 如果采用“后端返回说明字段，前端渲染”方案，则可能扩展到
2. 前端：
   - `src\pages\LongOrderFirstMedicineExecRules\Index.vue`
   - `src\store\modules\LongOrderFirstMedicineExecRules\index.js`
3. execution-order-api / application：
   - `ExecFirstDayMedicationRuleDTO.java`
   - `ExecFirstDayMedicationRuleBO.java`
   - `ExecFirstDayMedicationRuleRepositoryImpl.java`
   - `ExecFirstDayMedicationRuleController.java`
4. config-api / application：
   - `ExecFirstDayMedicationRuleDTO.java`
   - `ExecFirstDayMedicationRuleOutputBO.java`
   - `ExecFirstDayMedicationRuleServiceImpl.java`
5. model：
   - `ExecFirstDayMedicationRule.java`
   - `MdsExecFirstDayMedicationRule.java`

### 如果说明里需要可点击跳转 / 路径联动，还可能涉及
6. 医嘱流向配置相关前端页面 / 路由 / 菜单文件

## 风险

1. **真实可交付入口不在原默认后端仓单独完成**
   - 这次需求是页面说明展示，真正 UI 入口在前端仓，不是只在 `winning-nis-ward` 里改 Java 就能完成

2. **当前数据模型没有说明字段**
   - 如果坚持做成后端配置化说明，而不是前端静态说明，改动面会从单页文案扩大到 DTO / BO / entity / 表结构或配置来源，复杂度明显上升

3. **需求标题和页面现名存在口径差异**
   - TFS 说的是“长期医嘱首日说明优化”
   - 页面现名更像“长期医嘱首日用药执行规则”
   - 需要实现时确认：说明是放整个页面头部，还是放某个具体参数项附近

4. **“医嘱物资流向配置路径”在当前页不是天然同域内容**
   - 如果文案写得太重，可能会把本页变成半个操作手册
   - 需要控制说明颗粒度，避免页面拥挤

5. **存在历史复制痕迹 / 命名债务**
   - 首日规则 DTO / BO 的 `ApiModel` 描述里仍写着“药房科室关系表”，说明该模块本身有复制残留
   - 实现时要防止继续沿用错误文案

## 未解决问题

1. 当前最终产品口径是否就是“在页面固定展示一段说明文案”，还是要做成可配置说明
2. 说明文案需要放：
   - 页面头部
   - 右侧详情顶部
   - 某个具体字段旁边
   - 还是弹层 / tooltip
3. 说明里是否要加入“去医嘱流向配置页”的跳转入口，还是只写文字路径
4. 物资流向配置对应的前端页面与菜单文案，是否与 TFS 草案中的路径命名完全一致，实施前还应再核一遍

## 需向用户确认的问题

当前只建议保留一个真正有价值的问题：

- **本轮你更倾向于哪种实现口径？**
  1. **最小方案**：只在前端页面 `Index.vue` 加静态说明块
  2. **配置化方案**：说明文案走后端字段 / 配置返回，再由前端渲染

如果没有额外要求，我建议默认走 **方案 1**，因为它最符合“参数说明优化”的轻量目标，也最贴近当前代码结构。

## 明确建议写入 findings.md 的内容

建议后续 implementer 直接复用以下结论：

1. 真实 UI 入口已定位到前端仓：
   - `winning-webui-admin-execution-inpatient/src/pages/LongOrderFirstMedicineExecRules/Index.vue`
2. 当前页面没有现成说明区 / tooltip / alert，可直接在页面层补静态说明块
3. 当前后端首日规则数据链没有“说明文案”字段，若走配置化方案会扩大改动面
4. 业务口径上，“首日”与“物资流向配置”确实是有关联但不等价的两层配置，requirement-summary 的方向成立
5. 若目标只是“让用户看懂”，推荐 implementer 优先做前端静态说明，不建议先动表结构或接口字段

## 当前阶段结论

- 是否已支持 implementer 进入窄范围实现：**是，但前提是实现仓库切到 `frontend_main` 下的目标子项目**
- 推荐下一步：
  1. 默认按“前端静态说明块”进入 implementer
  2. 实现仓库切到：`E:\winning-code\frontend\webui-next\winning-webui-admin-execution-inpatient`
  3. 以 `LongOrderFirstMedicineExecRules/Index.vue` 为主文件开始实现

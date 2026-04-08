# MEMORY.md - 长期记忆

## 日志巡检工具（log-inspect）

### 项目概况
- **位置**：`C:\Users\pc\.openclaw\workspace\skills\log-inspect\`
- **用途**：从 Loki/工具组API 拉取日志，分析ERROR/WARN/慢接口，生成HTML报告
- **医院**：乐山市人民医院、桐乡市卫生健康局等
- **服务**：病区护士站（winning-winex-ipt-ward-pbc）

### 核心功能（2026-03-12 完成）
1. **四级分组**：按 `category:root_class:api_entry:caller_service` 分组
2. **调用方识别**：区分本服务/跨服务调用/异步任务/RPC
3. **代表trace优先**：每个分组优先显示拉取了完整链路的代表trace
4. **效率优化**：代表trace从148个降至51个，拉取时间从10分钟降至5分钟
5. **报告增强**：显示调用方、线程、影响级别、拉取时间范围、拉取耗时

### 关键文件
- `log_inspect_main.py` - 入口脚本，支持自然语言和命令行参数
- `loki_fetcher.py` - 两阶段拉取（ERROR/WARN + 完整链路）
- `preprocess.py` - 日志分析，四级分组，代表trace优先
- `generate_html_report_v2.py` - HTML报告生成

### 重要事件

#### 2026-03-12：代码丢失
- **原因**：OpenClaw 升级（v2026.2.25 → v2026.3.11）后，workspace 文件被覆盖
- **丢失内容**：
  - 四级分组功能
  - 调用方服务显示
  - 线程信息显示
  - 影响级别显示
  - 慢接口详情渲染
  - 代表trace优先逻辑
  - 效率优化（按root_class分组）
- **保留内容**：
  - 基本信息中的拉取时间范围和拉取耗时（当天新加的）
- **参考资料**：
  - 工作版本报告：`logs_20260312_145058_默认集群_report.html`（14:50生成）
  - 工作版本digest：`logs_20260312_145058_默认集群_digest.json`
  - 详细记录：`memory/2026-03-12-code-lost.md`
- **恢复进度**（2026-03-13 00:46 完成）：
  - ✅ generate_html_report_v2.py - error 详情显示（调用方、线程、影响级别）
  - ✅ generate_html_report_v2.py - 慢接口详情渲染（时间间隔分析）
  - ✅ generate_html_report_v2.py - 日志质量分析（500条样本统计）
  - ✅ generate_html_report_v2.py - 左侧导航栏
  - ✅ preprocess.py - 四级分组和 caller_service 提取
  - ✅ 基本信息优化（拉取时间范围、拉取耗时、友好时间格式）
  - ✅ loki_fetcher.py - 两阶段拉取功能（已完成）
  - ✅ log_inspect_main.py - 分阶段执行（--stage fetch/fetch2/analyze/report）
  - ✅ log_inspect_main.py - 两阶段拉取集成进 run() 方法
  - ✅ generate_html_report_v2.py - 完整链路日志展示（替代优化建议）
  - ✅ 关键字高亮：traceId 黄色，error 红色，.winning. 黄色

#### 2026-03-13：分阶段执行 + 完整链路日志展示
- **分阶段调用**：`--stage fetch/fetch2/analyze/report`，支持阶段间发消息通知
- **默认 level**：改为 `ERROR|业务处理耗时`
- **两阶段拉取**：集成进 `run()` 方法
- **测试结果**（乐山 2026-03-12）：总计 32,027 条日志，总耗时 40.9秒

### tool_api 联调进度
- 测试环境全流程已打通（2026-03-18）
- **待办**：工具组部署生产后，需集成 wxp-tunnel 验证

### 操作规范
- **桐乡市卫生健康局**：多集群（第一/第二/第三），拉日志前必须询问用户要哪个集群

### 经验教训
1. yieldMs=10000 必须加
2. subprocess.run 不要用 capture_output=True
3. 分组逻辑必须一致
4. 升级前要备份
5. workspace 才是工作目录
6. f-string 中的 CSS 的 `{` 需要转义
7. PowerShell 参数传递用文件方式
8. 两阶段拉取时间窗口默认 ±60s

## 协作目标判断
- 第别对这套机制半年后是否"成功"的判断，已进一步收敛为两个结果导向：**降低运维成本**、**提升开发效率**。
- 第别明确要求：后续在复盘、总结时，需要主动提醒其不仅关注目标是否明确，也要检查衡量标准是否明确。
- 第别进一步明确要求：后续在立项时，也要主动追问目标、成功标准和衡量口径。
- AI 分享主题方向：`从消息流到工作流：AI 如何把零散协作变成持续推进`。

## memory_search 的定位
- 核心价值是作为访问长期记忆的语义检索系统
- 三层价值：**找得到**、**少漏**、**接得上**

## ACP 执行基础设施（2026-04-08 打通）
- OpenClaw ACP 连 opencode 已从 `backend unavailable` 修复为正式可用
- 依赖两处 Windows 手动补丁（详见 TOOLS.md），升级后需重新打
- 执行载体优先级：`ACP opencode` > `exec opencode` > `wrapper opencode`（禁止）
- ACP 的核心价值：减少上下文重复灌输、支撑中任务连续推进、利用持续会话能力

## 护士站执行框架（2026-04-08 重构）
- 统一入口：`skills/nurse-station-orchestrator/SKILL.md`
- 三条路径：light（直接改） / medium（planning + ACP 执行 + 验证） / heavy（完整六段 + retrospective）
- 产物落地：`work-system/deliverables/nurse-station/{task-id}/`
- 阶段衔接靠共享产物文件流转，不靠聊天回捞
- subagent-execution 定位为"派发层规则"，当前单执行器环境，多 agent 预留但暂不拆
- 首次真实验证任务：TFS 1540718（2026-04-09）

## Codex 调用规范
- **必须显式传 cwd**：调用 Codex 时，必须指定工作目录 `E:\winning-code\akso5\winning-nis-ward`
- 推荐用 `exec` 直接调 codex CLI，ACP 方式当前不稳定

## OpenCode 调用
- ACP 方式（2026-04-08 打通）：`sessions_spawn runtime=acp agentId=opencode` — **已验证可用**
- exec 降级方式：`npx -y opencode-ai run -m <model>` — 已验证可用
- 当前默认走 ACP，exec 作为降级方案
- OpenCode 支持通过 `-m` 指定模型（已验证 glm-5）

## 用户信息
- **姓名**：第别
- **公司**：卫宁健康
- **机器**：LAPTOP-2STTCK0U
- **时区**：Asia/Shanghai (GMT+8)

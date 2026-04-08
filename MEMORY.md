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
  - fetch 输出 `RESULT_GRAFANA_URL/DATASOURCE_ID/APP_NAME` 供 fetch2 使用
  - analyze 支持 `--fetch-start/end/duration` 跨进程传递元数据
- **默认 level**：改为 `ERROR|业务处理耗时`（argparse 和 parse_natural_language 均已修改）
- **两阶段拉取**：集成进 `run()` 方法，分阶段流程：fetch → analyze → fetch2 → analyze → report
- **完整链路日志展示**：详细异常分析中"优化建议"改为完整链路日志，按时间正序排序
- **关键字高亮**：traceId 黄色，error 红色，`(?<=\.)winning(?=\.)` 黄色
- **内容截断修复**：去掉 content[:200]/[:500]/[:100] 截断，显示完整内容
- **时间间隔分析**：前一条/后一条内容改用 textarea（60px 高，可拖拽）
- **导航子项**：详细异常分析、慢接口 Trace 详情加子导航，默认折叠，点击展开
- **Windows 编码**：log_inspect_main.py 开头加 stdout.reconfigure(utf-8)，修复 emoji 报错
- **generate_report 修复**：参数改为 `--hospital/--service` 标志形式
- **实现内容**：
  - 第一阶段：拉取 `ERROR | 业务处理耗时` 日志（不再是 ERROR | WARN）
  - 第二阶段：拉取代表 traces 的完整链路（包括 INFO 等所有日志）
  - 异常类：每个四级分组的第一个 traceId（22 个）
  - 慢接口：top 10 的最慢 traceId（10 个）
- **新增文件**：
  - `two_stage_fetch.py` - 一键两阶段拉取脚本
  - `*_traces.json` - 代表 traces 列表（供第二阶段使用）
- **测试结果**（乐山 2026-03-12 23:42:46 ~ 23:52:46）：
  - 第一阶段：20,059 条日志，耗时 17.1秒
  - 第二阶段：32 个 traces，11,966 条日志，耗时 21.0秒
  - 总计：32,027 条日志，总耗时 40.9秒
- **使用方法**：
  ```bash
  python two_stage_fetch.py \
    --grafana "http://127.0.0.1:14828" \
    --datasource 2 \
    --app "winning-winex-ipt-ward-pbc" \
    --start "2026-03-13 00:00:00" \
    --end "2026-03-13 00:10:00" \
    --output logs.log
  ```
- **下一步**：
  - ~~明天和工具组调接口（集成到工具组 API）~~ → 2026-03-14 已完成联调
  - 等工具组修复 endTime bug 后完整验证
  - 可能需要优化四级分组的准确性（用户提到"命中率不高"）

### tool_api 联调进度
- 测试环境全流程已打通（2026-03-18）
- 属于传统服务器模式，不走 Grafana/Loki
- **待办**：工具组部署生产后，需集成 wxp-tunnel 验证（打通道 → 拉日志）

### 操作规范
- **桐乡市卫生健康局**：多集群（第一/第二/第三），拉日志前必须询问用户要哪个集群

- `config/environments.json` - 医院环境配置（Grafana地址、服务映射、集群配置）

### 经验教训
1. **yieldMs=10000 必须加**：否则 exec 会 hang 住
2. **subprocess.run 不要用 capture_output=True**：会吞掉子进程输出
3. **分组逻辑必须一致**：loki_fetcher.py 和 preprocess.py 的分组键要匹配
4. **升级前要备份**：npm upgrade 会覆盖 node_modules 里的文件
5. **workspace 才是工作目录**：修改应该在 workspace 里，不是 node_modules
6. **f-string 中的 CSS**：CSS 的 `{` 需要转义为 `{{`，或者在 f-string 外部定义
7. **PowerShell 参数传递**：复杂命令用文件方式，避免引号和特殊字符问题
8. **记录拉取耗时**：用 PowerShell 的 `$start = Get-Date` 和 `($end - $start).TotalSeconds`
9. **Windows 控制台编码**：避免使用 emoji，会导致 UnicodeEncodeError
10. **两阶段拉取时间窗口**：默认 ±60s；`be25d207c0c04053a3a54d7df3cc271c` 已验证 ±30s 会少 2 条，±60s 可补齐，可根据 trace 复杂度继续调整

### 报告功能清单（2026-03-13 00:46）
- ✅ 左侧导航栏（固定位置，快速跳转）
- ✅ 基本信息（医院、服务、拉取时间范围、拉取耗时、日志量、阈值）
- ✅ 日志质量分析（缺少API入口、null异常、影响级别分布）
- ✅ 异常统计概览（Top 3 错误类型卡片）
- ✅ 详细异常分析（四级分组、调用方、线程、影响级别、代表trace）
- ✅ 日志反哺建议（不明确的日志分类）
- ✅ 慢接口 Trace 详情（调用次数、最大/平均耗时、时间间隔分析）
- ✅ 慢接口完整链路（两阶段拉取已完成）

## 协作目标判断
- 第别对这套机制半年后是否“成功”的判断，已进一步收敛为两个结果导向：**降低运维成本**、**提升开发效率**。这比“系统是否完整”更重要，应作为后续专项跟踪、复盘和 cognition 沉淀的上层标准。
- 对 cognition 的预期也进一步明确：不仅记录专项结论，还要持续提炼哪些做法真正带来了降本增效，哪些失败案例说明了什么边界条件；重点沉淀成功/失败背后的因果解释与可迁移规则。
- 第别明确要求：后续在复盘、总结时，需要主动提醒其不仅关注目标是否明确，也要检查衡量标准是否明确；若只有目标、没有判据，要把补齐衡量口径作为复盘的一部分。
- 第别进一步明确要求：后续在立项时，也要主动追问目标、成功标准和衡量口径；如果这些内容说不清，不直接判定项目必败，但要视为高风险信号，并优先考虑先按探索题/试验项而非正式专项推进。
- 第别周四的 AI 分享，已初步收敛为偏实践分享路线，时长约 20-30 分钟；当前最匹配的主题方向是：`从消息流到工作流：AI 如何把零散协作变成持续推进`。这类分享应坚持“真实案例 + 可运行机制 + 边界反思”风格，不走过虚的概念化表达。
- 第别明确偏好：对这类有明确时间点但未必已形成完整材料的事项，不建议依赖 `cron` 或孤立的 `reminders` 机制；更合适的做法是在前一天或更早的“今日总结”中主动提醒临近事项，并在当天/前一天的 `Daily Focus` 中显性抬头，帮助其提前感知时间节点和准备压力。
- 当前这次 AI 分享已延期到 `2026-04-02 17:00`，后续应按“前一天总结提醒 + 当天聚焦显性列出”的方式处理。
- 那些天然服务护士站降本增效的专项，应持续跟踪、试验、复盘并反哺；过程中穿插的其他任务，也尽量提炼出与降本增效有关的经验。

## memory_search 的定位
- `memory_search` 的核心价值不是“更快找到文件”，而是作为访问长期记忆的“语义检索系统”：先从历史记录里捞出最可能相关的片段，再据此恢复上下文连续性并作答。
- 其价值可稳定分成三层：**找得到**（换个说法也可能命中）、**少漏**（同一主题散落在多天记录里也能一起捞出）、**接得上**（跨天、跨会话时把先前的决策、偏好和进展续起来）。
- 因此，`memory_search` 解决的重点不是单纯检索速度，而是减少漏记、误判和“记忆文件明明在那儿却没及时捞对”的断片感。
- 没有 `memory_search` 并不等于完全失忆；仍可手工读文件。但回答会更容易停留在“帮助我查记忆文件”这种空泛层面，难以区分工作流层、项目运行层、长期记忆层之间的差异，也更难判断召回失败究竟是未写入记忆还是检索失效。

## Codex 调用规范
- **必须显式传 cwd**：调用 Codex 时，必须指定工作目录 `E:\winning-code\akso5\winning-nis-ward`
- 如果不传 cwd，Codex 找不到项目文件，可能乱扫描全盘
- **提示词示例**：`派 Codex 去 E:\winning-code\akso5\winning-nis-ward 做 xxx`
- **用户没指定仓库时必须提醒**：如果用户让 Codex 干活但没说在哪个项目/目录，必须先问清楚，禁止让 Codex 全盘扫描

### 调用方式选择
| 方式 | 稳定性 | 推荐 |
|------|--------|------|
| `exec` 直接调 codex CLI | ✅ 稳定 | **推荐** |
| `sessions_spawn` (ACP) | ❌ 不稳定 | 不推荐 |

**推荐用法**（exec 直接调）：
```
exec: cd E:\winning-code\akso5\winning-nis-ward && codex exec "你的任务"
```
- 能拿到完整输出
- 执行时间约 20-30 秒
- 需要设置足够的 timeout（`yieldMs: 60000`）

**ACP 方式的已知问题**（2026-04-03 测试）：
- Prompt 可能发不出去（只有初始化日志）
- 完成通知丢失（Codex 完成了但 OpenClaw 不触发事件）
- 搜索关键词：`OpenClaw ACP acpx sessions_spawn prompt not sent`

## OpenCode exec 调用
| 方式 | 命令 | 稡型支持 | 结果 |
|------|------|----------|------|
| exec | `npx -y opencode-ai run -m <model>` | ✅ 支持 | ✅ 成功获取响应 |

**测试结果（2026-04-04 01:52）**：
- ✅ **成功**：`npx -y opencode-ai run -m "zhipuai-coding-plan/glm-5" "Say hello..."` 
- ✅ **响应内容**：OpenCode 成功识别并使用了智谱 glm-5 模型
 
**结论**：OpenCode 的 `run` 子命令 + `-m` 参数可以成功指定模型并获取响应。 检查状态，或者用轮询代替 yield

## 用户信息
- **姓名**：第别
- **公司**：卫宁健康
- **机器**：LAPTOP-2STTCK0U
- **时区**：Asia/Shanghai (GMT+8)

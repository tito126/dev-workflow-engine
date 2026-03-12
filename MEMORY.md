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
  - ⏳ log_inspect_main.py - 实时输出和时间记录（待恢复）

#### 2026-03-13：两阶段拉取功能完成
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
  - 明天和工具组调接口（集成到工具组 API）
  - 可能需要优化四级分组的准确性（用户提到"命中率不高"）

### 配置文件
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
10. **两阶段拉取时间窗口**：默认 ±30s，可根据 trace 复杂度调整

### 报告功能清单（2026-03-13 00:46）
- ✅ 左侧导航栏（固定位置，快速跳转）
- ✅ 基本信息（医院、服务、拉取时间范围、拉取耗时、日志量、阈值）
- ✅ 日志质量分析（缺少API入口、null异常、影响级别分布）
- ✅ 异常统计概览（Top 3 错误类型卡片）
- ✅ 详细异常分析（四级分组、调用方、线程、影响级别、代表trace）
- ✅ 日志反哺建议（不明确的日志分类）
- ✅ 慢接口 Trace 详情（调用次数、最大/平均耗时、时间间隔分析）
- ✅ 慢接口完整链路（两阶段拉取已完成）

## 用户信息
- **姓名**：第别
- **公司**：卫宁健康
- **机器**：LAPTOP-2STTCK0U
- **时区**：Asia/Shanghai (GMT+8)

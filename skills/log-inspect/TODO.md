# 日志巡检工具 - 完整待办清单

## 已完成 ✅

### 1. 四级分组功能
- 按 `category:root_class:api_entry:caller_service` 四级分组
- 报告显示调用方服务、线程信息、影响级别

### 2. 效率优化
- 统一 loki_fetcher.py 和 preprocess.py 的分组逻辑
- 代表trace从148个降至51个
- 拉取时间从10分钟降至5分钟

### 3. 基本信息增强 ✅ 刚完成
- 报告中显示拉取时间范围（开始~结束）
- 显示拉取耗时（秒）
- 修改文件：
  - log_inspect_main.py - 记录拉取开始/结束时间
  - preprocess.py - 接收并写入 meta.fetch_range
  - generate_html_report_v2.py - 在基本信息表格显示

## 待办事项 🔴

### 1. 代表trace命中率优化 🟡 中优先级
**现状**：
- loki_fetcher.py识别51个分组
- preprocess.py识别27个分组
- 命中率33.3%（9/27）

**问题根源**：
- loki_fetcher.py从ERROR行提取API → 大多数得到`N/A`
- preprocess.py从WARN行提取API → 得到实际路径
- 分组键不匹配

**可选方案**：
- 方案A：让loki_fetcher.py也按trace聚合WARN日志提取API（复杂度高）
- 方案B：接受现状（效率已提升50%，命中率33%可接受）

**建议**：方案B，接受现状

### 2. 第二阶段统计信息显示 🟢 低优先级
**需求**：在报告中显示第二阶段的统计信息
- 拉取了多少个trace的完整链路
- 完整调用链日志量
- 去重后总计

**涉及文件**：
- loki_fetcher.py - 输出统计信息到日志文件头部
- preprocess.py - 读取并写入 meta
- generate_html_report_v2.py - 在报告中显示

### 3. 日志输出编码优化 🟢 低优先级
**问题**：Windows GBK编码不支持特殊Unicode字符（如✓✗、emoji）

**现状**：
- 已将✓✗改为[OK]/[FAIL]
- 但emoji仍会报错（不影响功能）

**可选方案**：
- 方案A：所有输出避免使用emoji和特殊字符
- 方案B：设置环境变量 `PYTHONIOENCODING=utf-8`
- 方案C：接受现状（只是打印错误，不影响报告生成）

**建议**：方案C，接受现状

### 4. 统一分组逻辑（长期优化）🟢 低优先级
**目标**：让loki_fetcher.py和preprocess.py使用完全一致的分组逻辑

**现状**：
- 已统一为按root_class分组
- 但API提取方式不同（ERROR行 vs WARN行）

**长期方案**：
- 让loki_fetcher.py在第一阶段就按trace聚合ERROR+WARN
- 从WARN行提取API，从ERROR行提取类名
- 这样分组键就完全一致了

**优先级**：低（当前效率已可接受）

## 优先级排序

1. ✅ 基本信息增强（已完成）
2. 🟡 代表trace命中率优化（建议接受现状）
3. 🟢 第二阶段统计信息显示（可选）
4. 🟢 日志输出编码优化（可选）
5. 🟢 统一分组逻辑（长期优化）

## 建议

当前工具已基本可用，核心功能完善。建议：
1. 先使用一段时间，收集实际使用反馈
2. 根据反馈决定是否需要进一步优化命中率
3. 第二阶段统计信息和编码优化都是锦上添花，不影响核心功能

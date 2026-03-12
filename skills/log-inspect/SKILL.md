# Log Inspect Skill

日志巡检技能 - 分析微服务日志，生成巡检报告。

## 使用场景

- 分析指定时间段的生产日志
- 提取 ERROR/WARN 级别异常
- 识别慢接口（响应时间 > 阈值）
- 生成 HTML 格式巡检报告

## 文件结构

```
log-inspect/
├── SKILL.md                    # 本文件
├── log_inspect_main.py         # 🆕 统一入口脚本（推荐使用）
├── loki_fetcher.py             # Loki 日志拉取（K8s 环境）
├── preprocess.py               # 日志预处理脚本
├── generate_html_report.py     # HTML 报告生成
└── config/
    └── environments.json       # 环境配置
```

## 完整工作流程

### 🚀 方式一：统一入口脚本（推荐）

使用 `log_inspect_main.py` 一键完成所有步骤：

```bash
# 自然语言查询
python log_inspect_main.py "帮我分析桐乡病区护士站今天上午8-10点的日志"

# 指定参数
python log_inspect_main.py \
  --hospital 桐乡市卫生健康局 \
  --service 病区护士站 \
  --start "2026-03-03 08:00" \
  --end "2026-03-03 10:00"

# 推送到飞书
python log_inspect_main.py "分析桐乡病区护士站昨天的日志" --push
```

**功能特性**：
- ✅ 自然语言参数解析（支持"今天"、"昨天"、"上午8-10点"等）
- ✅ 自动查找环境配置
- ✅ 封装完整流程（拉取 → 分析 → 报告）
- ✅ 进度反馈和异常处理
- ✅ 支持推送到飞书（可选）

---

### 📋 方式二：分步执行（高级用户）

如果需要更精细的控制，可以分步执行：

### 1. 拉取日志（K8s 环境）

使用 `loki_fetcher.py` 从 Loki 拉取日志：

```bash
python loki_fetcher.py \
  --grafana http://127.0.0.1:16291 \
  --datasource 1 \
  --app winning-winex-ward-akso5-pbc \
  --start "2026-03-02 08:00" \
  --end "2026-03-02 10:00" \
  --level "ERROR|WARN" \
  --chunk 30 \
  --limit 5000 \
  --output logs.log
```

**参数说明**：
- `--grafana`: Grafana 地址
- `--datasource`: Loki 数据源 ID（通常是 1 或 2）
- `--app`: 应用名称（app label）
- `--start` / `--end`: 时间范围（YYYY-MM-DD HH:MM）
- `--level`: 日志级别过滤（默认 "ERROR|WARN"，设为空则不过滤）
- `--chunk`: 分批查询时间跨度（分钟），默认 30
- `--limit`: 每批查询行数限制，默认 5000

**注意**：
- Loki 通常有 `max_entries_limit_per_query` 限制（如 5000 条）
- 使用 `--chunk` 参数分批查询可以获取更多数据
- 使用 `--level` 过滤可以减少数据量，聚焦关键日志

### 2. 预处理分析

使用 `preprocess.py` 分析日志：

```bash
python preprocess.py logs.log \
  -o digest.json \
  -t 1000
```

**参数说明**：
- 第一个参数：输入日志文件（或目录）
- `-o` / `--output`: 输出 digest 文件路径
- `-t` / `--threshold`: 慢接口阈值（毫秒），默认 1000
- `-s` / `--start`: 开始时间（可选）
- `-e` / `--end`: 结束时间（可选）

**输出**：
生成 `digest.json`，包含：
- 基本统计（总行数、ERROR/WARN 数量）
- 错误分类及频次
- 慢接口列表
- 样本日志（带 TraceID）

### 3. 生成 HTML 报告

使用 `generate_html_report.py` 生成可视化报告：

```bash
python generate_html_report.py \
  digest.json \
  report.html \
  "医院名称" \
  "服务名称"
```

**参数说明**：
1. digest.json 文件路径
2. 输出 HTML 文件路径
3. 医院名称（可选）
4. 服务名称（可选）

**输出**：
生成美观的 HTML 报告，包含：
- 概览统计卡片
- 错误分类表格
- 错误详情（带示例和 TraceID）
- 慢接口列表
- 分析建议

## 一键执行示例

```bash
# 1. 拉取日志
python loki_fetcher.py \
  --grafana http://127.0.0.1:16291 \
  --datasource 1 \
  --app winning-winex-ward-akso5-pbc \
  --start "2026-03-02 08:00" \
  --end "2026-03-02 10:00" \
  --level "ERROR|WARN" \
  --chunk 30 \
  --output txwsjkj.log

# 2. 预处理
python preprocess.py txwsjkj.log -o txwsjkj_digest.json -t 1000

# 3. 生成报告
python generate_html_report.py \
  txwsjkj_digest.json \
  txwsjkj_report.html \
  "桐乡市卫生健康局健康云" \
  "病区护士站"
```

## 环境配置

`config/environments.json` 用于配置不同医院的环境信息：

```json
{
  "桐乡市卫生健康局": {
    "name": "桐乡市卫生健康局健康云",
    "type": "k8s",
    "grafana": {
      "url": "http://127.0.0.1:16291",
      "datasource_id": 1
    },
    "services": {
      "病区护士站": "winning-winex-ward-akso5-pbc"
    }
  }
}
```

## 技术说明

### Loki 查询限制

大多数 Loki 部署都有 `max_entries_limit_per_query` 限制（通常是 5000 条）。对于日志量大的服务：

1. **分批查询**：使用 `--chunk` 参数，将长时间段分成多个小时间段
2. **过滤条件**：使用 `--level "ERROR|WARN"` 只拉取关键日志
3. **组合使用**：分批 + 过滤可以获取更完整的数据

示例：查询 2 小时数据，分 4 批，每批最多 5000 条，总计可获取 20000 条。

### 日志格式

支持的日志格式：
- 标准 Java 日志（带时间戳、级别、类名）
- 包含 TraceID 的分布式追踪日志
- gz 压缩日志文件

### 慢接口识别

通过正则匹配日志中的"业务处理耗时"关键字，提取接口响应时间。

## 常见问题

**Q: Loki 查询返回 "max entries limit exceeded" 错误？**  
A: 减小 `--limit` 参数（不超过 5000），或使用 `--chunk` 分批查询。

**Q: 如何只拉取 ERROR 级别的日志？**  
A: 使用 `--level "ERROR"`。

**Q: 如何拉取所有级别的日志？**  
A: 不使用 `--level` 参数，或设置为空字符串（但可能受限于数据量）。

**Q: 报告中的 TraceID 有什么用？**  
A: 可以用于追踪完整的调用链，排查分布式系统中的问题。

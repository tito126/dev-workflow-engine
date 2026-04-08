# Excel 报告模板结构

本模板定义 Excel 报告的三个 Sheet 结构，按规则分组展示问题。

## 报告命名规则（强制）

- 格式：`{仓库名称}_{时间}.{扩展名}`
- 示例：`winning-dtc-Knowledge_202602121501.md` 或 `winning-dtc-Knowledge_202602121501.xlsx`
- 时间格式：`YYYYMMDDHHmm`（如：202602121501 表示 2026年2月12日15:01）

---

## Sheet 1: 扫描概览

### 标题行
| 列名 | 说明 |
|------|------|
| 仓库 | {{repo_name}} |
Git URL | {{git_url}} |
| 分支 | {{git_branch}} |
| 批次进度 | {{batch_progress}} |
| 已扫描文件 | {{scanned_files}} / {{total_files}} ({{progress}}%) |
| 耗时 | {{elapsed}} 秒 |
| Token 消耗 | {{tokens}} |

### 统计表格
| 严重级别 | 数量 |
|---------|------|
| 严重 | {{critical_count}} |
| 警告 | {{warning_count}} |
| **合计** | **{{total_count}}** |

### 分类统计
| 类别 | 数量 |
|------|------|
| 性能 | {{category_performance}} |
| 安全 | {{category_security}} |
| 业务 | {{category_business}} |
| 框架 | {{category_framework}} |
| 架构 | {{category_architecture}} |
| 质量 | {{category_quality}} |
| 语法 | {{category_syntax}} |
| 工程 | {{category_engineering}} |

---

## Sheet 2: 问题清单（按规则分组）

### 表头

| 列名 | 说明 | 示例 |
|------|------|------|
| 规则编号 | PERF-B007、QUAL-B011 等 | PERF-B007 |
| 风险等级 | high/medium | 🔴 high / 🟡 medium |
| 问题类别 | 性能/安全/业务/代码质量等 | 性能规范 |
| 规则名称 | 规则的完整名称 | 下游调用超时配置规范 |
| 影响范围 | 该规则命中的问题行号总数（必与涉及文件行号数量一致） | 7 处 |
| 涉及文件 | 文件路径及行号列表 | `path/to/Service.java`: 第 45, 67, 89 行 |
| 修复建议 | 修复建议内容 | 为 RPC 调用配置超时时间... |
| 原理说明 | 问题描述和影响 | 下游接口调用必须设置合理的超时时间... |

### 数据行生成
{{#each issues_by_rule}}
| {{rule_code}} | {{risk_level}} | {{category}} | {{rule_name}} | {{impact_count}} | {{files_summary}} | {{suggestion}} | {{description}} |
{{/each}}

#### 涉及文件格式示例
```
winning-log-main/src/main/java/com/winning/mis/tasks/CleanLogDataTaskRunner.java: 第 81, 83, 85, 106, 108 行
winning-log-main/src/main/java/com/winning/mis/service/MgrLogServiceImpl.java: 第 74, 118 行
```

#### 影响范围计算规则（重要）
- **影响范围 = 涉及文件中所有行号的总数量**
- 示例：如果涉及文件为 `Service.java: 第 81, 83, 85 行` 和 `Controller.java: 第 45, 67 行`，则影响范围为 **5 处**（而非 2 个文件）

---

## Sheet 3: 问题明细（展开形式）

### 表头

| 列名 | 说明 |
|------|------|
| 规则编号 | 如 PERF-B007 |
| 风险等级 | 🔴 high / 🟡 medium |
| 问题类别 | 性能/安全/业务/代码质量等 |
| 文件路径 | src/main/java/com/example/Service.java |
| 行号 | 123 |
| 问题描述 | 循环内调用数据库查询单条记录 |
| 修复建议 | 使用批量查询替代循环查询 |

### 数据行结构
{{#each issues_expanded}}
| {{rule_code}} | {{risk_level}} | {{category}} | {{file_path}} | {{line}} | {{description}} | {{suggestion}} |
{{/each}}

**说明**: 此 Sheet 将每个规则下的每个文件位置展开为独立行，便于筛选和排序。

---

## 样式说明

### Sheet 1 - 概览
- 标题行：深蓝色背景，白色字体，16号加粗
- 统计表格：边框，居中对齐，数字右对齐
- 分类统计：交替行颜色（浅灰色）
- 仓库名称：14号加粗

### Sheet 2 - 问题清单（按规则分组）
- 表头：深蓝色背景，白色字体，12号加粗
- 规则编号列：加粗，左对齐
- 风险等级列：
  - 🔴 high：红色字体
  - 🟡 medium：橙色字体
- 冻结首行和前三列（规则编号、风险等级、问题类别）
- 自动筛选
- 行高：自动调整，涉及文件列设置自动换行

### Sheet 3 - 问题明细
- 表头：深蓝色背景，白色字体
- 规则编号列：加粗
- 风险等级列：颜色标识（high=红色，medium=橙色）
- 冻结首行和前两列
- 自动筛选
- 所有列：自动调整宽度

---

## 数据结构说明

### issues_by_rule 数据结构
```json
{
  "issues_by_rule": [
    {
      "rule_code": "PERF-B007",
      "risk_level": "🔴 high",
      "category": "性能规范",
      "rule_name": "下游调用超时配置规范",
      "impact_count": 7,
      "files_summary": "文件1: 第 81, 83 行\n文件2: 第 74, 118 行",
      "suggestion": "为 RPC 调用配置超时时间...",
      "description": "下游接口调用必须设置合理的超时时间，避免长时间等待和资源浪费"
    }
  ]
}
```

### issues_expanded 数据结构
```json
{
  "issues_expanded": [
    {
      "rule_code": "PERF-B007",
      "risk_level": "🔴 high",
      "category": "性能规范",
      "file_path": "src/main/java/com/example/Service.java",
      "line": 81,
      "description": "下游接口调用必须设置合理的超时时间",
      "suggestion": "使用 @Reference(timeout = 5000) 配置超时时间"
    },
    {
      "rule_code": "PERF-B007",
      "risk_level": "🔴 high",
      "category": "性能规范",
      "file_path": "src/main/java/com/example/Service.java",
      "line": 83,
      "description": "下游接口调用必须设置合理的超时时间",
      "suggestion": "使用 @Reference(timeout = 5000) 配置超时时间"
    }
  ]
}
```

---

## 生成示例

### Sheet 1 - 扫描概览示例

| 项目 | 值 |
|------|-----|
| 仓库 | winning-dtc-Knowledge |
Git URL | http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0/WiNEX_WXP/_git/winning-dtc-Knowledge |
| 分支 | 4.0.0-SNAPSHOT |
| 批次进度 | 5/8 批 (用户提前终止) |
| 已扫描文件 | 500 / 767 (65.2%) |
| 耗时 | 207 秒 |
| Token 消耗 | 138,784 |

| 严重程度 | 数量 |
|----------|------|
| 严重 | 15 |
| 警告 | 36 |
| **合计** | **51** |

### Sheet 2 - 问题清单示例

| 规则编号 | 风险等级 | 问题类别 | 规则名称 | 影响范围 | 涉及文件 | 修复建议 | 原理说明 |
|----------|----------|----------|----------|----------|----------|----------|----------|
| PERF-B007 | 🔴 high | 性能规范 | 下游调用超时配置规范 | 7 处 | `Service.java`: 第 81, 83, 85 行<br>`Controller.java`: 第 45, 67 行 | 使用 @Reference(timeout = 5000) 配置超时时间 | 下游接口调用必须设置合理的超时时间，避免长时间等待和资源浪费 |
| QUAL-B011 | 🔴 high | 代码质量 | 异常处理机制完整性 | 12 处 | `Mapper.java`: 第 74, 118 行<br>`Dao.java`: 第 23, 56 行 | 捕获具体异常而非通用Exception，异常信息需包含关键上下文 | 对可能返回null的方法调用添加完整异常处理 |

### Sheet 3 - 问题明细示例

| 规则编号 | 风险等级 | 问题类别 | 文件路径 | 行号 | 问题描述 | 修复建议 |
|----------|----------|----------|----------|------|----------|----------|
| PERF-B007 | 🔴 high | 性能规范 | Service.java | 81 | 下游接口调用未配置超时时间 | 使用 @Reference(timeout = 5000) 配置超时时间 |
| PERF-B007 | 🔴 high | 性能规范 | Service.java | 83 | 下游接口调用未配置超时时间 | 使用 @Reference(timeout = 5000) 配置超时时间 |
| PERF-B007 | 🔴 high | 性能规范 | Controller.java | 45 | 下游接口调用未配置超时时间 | 使用 @Reference(timeout = 5000) 配置超时时间 |
| QUAL-B011 | 🔴 high | 代码质量 | Mapper.java | 74 | 捕获了通用Exception但未进行适当的异常处理 | 捕获具体异常而非通用Exception |

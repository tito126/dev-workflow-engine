# Templates 目录

本目录包含代码扫描报告的输出模板。

## 模板文件

### report-markdown.md
Markdown 格式的扫描报告模板。使用 Handlebars 风格的占位符：
- `{{module_name}}` - 扫描模块名称
- `{{scan_time}}` - 扫描时间
- `{{scanned_files}}` - 扫描文件数
- `{{scan_mode}}` - 扫描方式（全库扫描/增量扫描/快速抽检）
- `{{repo_path}}` - 仓库路径

### report-json.json
JSON 格式的扫描报告模板，用于程序化处理和数据交换。

### report-excel.md
Excel 报告的结构说明模板，定义三个 Sheet 的列结构和样式。

### report-console.txt
控制台输出的报告模板，用于扫描完成后的终端显示。

## 占位符说明

### 基本信息
| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{module_name}}` | 扫描模块名称 | winning-opt-basicdata |
| `{{scan_time}}` | 扫描时间 | 2026-02-11 14:30:00 |
| `{{scanned_files}}` | 扫描文件数 | 1,156 |
| `{{scan_mode}}` | 扫描方式 | 全库扫描 |
| `{{repo_path}}` | 仓库路径 | /path/to/repo |
| `{{report_path}}` | 报告路径 | /tmp/basicdata-scan-report.md |
| `{{scan_duration}}` | 扫描耗时 | 约 5 分钟 |
| `{{report_generated_at}}` | 报告生成时间 | 2026-02-11 14:35:00 |

### 统计信息
| 占位符 | 说明 |
|--------|------|
| `{{total_count}}` | 问题总数 |
| `{{critical_count}}` | 严重问题数 |
| `{{warning_count}}` | 警告问题数 |
| `{{info_count}}` | 提示问题数 |
| `{{critical_percent}}` | 严重问题占比 |
| `{{warning_percent}}` | 警告问题占比 |
| `{{info_percent}}` | 提示问题占比 |

### 分类统计
| 占位符 | 说明 |
|--------|------|
| `{{category_performance}}` | 性能问题数 |
| `{{category_security}}` | 安全问题数 |
| `{{category_business}}` | 业务问题数 |
| `{{category_framework}}` | 框架问题数 |
| `{{category_architecture}}` | 架构问题数 |
| `{{category_quality}}` | 质量问题数 |
| `{{category_syntax}}` | 语法问题数 |

### 问题数据
| 占位符 | 说明 |
|--------|------|
| `{{#each issues}}...{{/each}}` | 问题列表循环 |
| `{{rule_code}}` | 规则编号 |
| `{{rule_name}}` | 规则名称 |
| `{{severity}}` | 严重程度 |
| `{{category}}` | 类别 |
| `{{file}}` | 文件路径 |
| `{{line}}` | 行号 |
| `{{code_snippet}}` | 代码片段 |
| `{{code_snippet_json}}` | JSON 转义后的代码片段 |
| `{{description}}` | 问题描述 |
| `{{suggestion}}` | 修复建议 |

### 按规则分组
| 占位符 | 说明 |
|--------|------|
| `{{#each issues_by_rule}}...{{/each}}` | 按规则分组循环 |
| `{{file_count}}` | 该规则影响的文件数 |
| `{{#each occurrences}}...{{/each}}` | 该规则的所有问题位置 |

### 按文件分组
| 占位符 | 说明 |
|--------|------|
| `{{#each issues_by_file}}...{{/each}}` | 按文件分组循环 |
| `{{issue_count}}` | 该文件的问题数 |
| `{{#each issues}}...{{/each}}` | 该文件的所有问题 |

### 条件渲染
| 占位符 | 说明 |
|--------|------|
| `{{#if has_issues}}...{{/if}}` | 有问题时显示 |
| `{{#unless has_issues}}...{{/unless}}` | 无问题时显示 |
| `{{#if has_critical_issues}}...{{/if}}` | 有严重问题时显示 |

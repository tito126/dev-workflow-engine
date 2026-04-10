---
name: win-code-scanner
description: 代码扫描与评审技能，支持前端(Vue/JS/TS)和后端(Java/SQL/YAML)项目的智能代码审查。扫描规则覆盖：前端12条（性能1条、框架2条、工程3条、安全2条、语法4条）、后端36条（性能17条、安全3条、业务3条、工程3条、语法6条、框架1条、架构2条、质量1条）。当用户需要进行代码扫描、代码评审、检查代码问题，或需要基于高危代码修复台账 Excel（含“行号 / 是否需要修复 / 备注”等列）过滤后再复扫，或需要用知识库对扫描结果做误报分流/增强报告时使用。
---

# Code Scanner - 代码扫描技能

## 外部调用模式

当通过 Skill 工具调用并传入 JSON 格式参数时，按以下流程执行：

### 参数格式

```json
{
  "files": ["/absolute/path/to/file1.java", "/absolute/path/to/file2.vue"],
  "severity_filter": ["严重"]
}
```

**参数说明：**
- `files`: 文件绝对路径列表（必填）
- `severity_filter`: 严重级别过滤（可选，默认全部）

### 执行流程

收到外部调用参数后，首先打印日志：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  win-code-scanner 外部调用
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

收到参数: {"files": [...], "severity_filter": ["严重"]}
文件数量: X 个
严重级别过滤: 严重

解析文件列表...
  - /path/to/file1.java (后端)
  - /path/to/file2.vue (前端)
  ...

加载规则文件...
  - 后端规则: X 条
  - 前端规则: X 条

执行扫描...
  - 扫描文件: X 个
  - 发现问题: X 个

生成报告完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

然后执行以下步骤：

1. **解析参数**：解析 JSON 获取文件列表和过滤条件，打印日志
2. **读取文件**：遍历文件列表，读取每个文件的完整内容
3. **识别类型**：根据文件扩展名判断前端/后端，选择对应规则
4. **执行扫描**：加载规则文件，对代码进行扫描分析
5. **输出报告**：输出 Markdown 格式的扫描报告

### 输出格式

```markdown
# 代码扫描报告

## 扫描统计

| 项目 | 数量 |
|------|------|
| 扫描文件 | {数量} |
| 问题总数 | {数量} |
| 严重 | {数量} |
| 警告 | {数量} |
| 提示 | {数量} |

## 问题列表

### {规则代码} - {规则名称}

- **严重程度**: {严重/警告/提示}
- **文件**: {文件路径}:{行号}
- **描述**: {问题描述}
- **建议**: {修复建议}

...
```

### 注意事项

- 文件路径必须是绝对路径
- 跳过不存在或无法读取的文件
- 按 severity_filter 过滤输出的问题

---

## 配置文件

代码扫描支持通过配置文件指定默认搜索路径和报告输出路径，便于通过自然语言描述仓库名称进行扫描。

**配置文件路径**: `~/.cache/skills/win-code-scanner/config.json`

**配置文件格式**:
```json
{
  "default_scan_path": "/winning/winex-repo/storage/repos",
  "report_output_path": "/winning/winex-repo/storage/repos/reports/code-scan",
  "report_base_url": "http://172.17.1.173/repos/reports/code-scan"
}
```

**配置项说明**:
| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `default_scan_path` | 仓库搜索的默认根路径 | 无（必须配置） |
| `report_output_path` | 扫描报告输出目录 | `/tmp/` |
| `report_base_url` | 报告下载的基础 URL | 无 |

**说明**:
- 配置文件不存在时，走原有流程（分析当前工作目录），报告输出到 `/tmp/`
- 配置文件存在时，在 `default_scan_path` 下搜索匹配的仓库
- 报告将保存到 `report_output_path` 目录，如未配置则使用 `/tmp/`

---

## 修复台账过滤模式（Excel / 工作表回扫）

当输入不是“直接扫仓库”，而是**基于高危代码修复台账回扫/复扫**时，先进入本模式，再决定后续扫描范围。

### 触发条件

满足任一情况就启用：
- 用户提供 `.xlsx` 台账，并明确说是高危代码修复计划、修复清单、回扫清单、复核清单
- 用户提到工作表里已经维护了 `行号`、`是否需要修复`、`备注` 等列
- 用户要求“跳过已标记无需修复的记录”“不要重复扫描已确认无需修复项”

### 必做规则

1. **先过滤，后扫描**，不要直接把整张表重新展开成待扫文件列表
2. 对于 `是否需要修复` 列，默认按以下规则处理：
   - **跳过**：`不需要修复`、`无需修复`、`不修复`、`否`、`skip` 等明确否定值
   - **保留**：`需要修复`、`待修复`、`待确认`、空白值、其他未识别值
3. 如果同一文件里同时存在“无需修复”和“需要修复”记录，**只围绕保留记录对应的问题描述 / 行号复核**，不要因为文件重复出现就把已跳过项重新纳入
4. 若工作表存在 `备注` 列，输出过滤结果时要保留备注，便于解释为什么被跳过或继续保留

### 执行方式

优先使用脚本：`scripts/filter_repair_targets.py`

```bash
python scripts/filter_repair_targets.py "E:\\winning-code\\ai\\temp\\【内部】临床&医管高危代码修复计划.xlsx" --sheet "病区护士（姚云）" --format text
```

脚本能力：
- 自动识别表头行
- 自动识别关键列：`问题描述`、`涉及文件 / 范围`、`行号/行数`、`是否需要修复`、`备注`、`git分支`
- 自动跳过已标记“无需修复”的记录
- 输出保留记录、跳过记录、待确认记录和唯一文件列表

### 后续扫描要求

过滤完成后：
1. 只基于 `selected_records` / `selected_files` 继续扫描
2. 向用户汇报过滤摘要：总记录数、保留数、跳过数、待确认数
3. 如果用户本意是“整改跟踪”，优先做**定点复核**（按文件 + 行号 + 问题描述），不要退化成全库通扫
4. 只有用户明确要求“重新全量扫描仓库”时，才回到常规仓库扫描流程

---

## 知识库增强模式（误报分流 / 报告增强）

### 目标

第一阶段目标不是改写扫描器原始结论，而是**保留原始扫描结果**，再通过知识库补充一层解释和分流，降低重复解释成本，并把高噪音问题从“直接高危”调整为“降级”或“人工确认”。

### 关键原则

1. **原始扫描结果保持不变**，不要因为知识库命中就直接删除 issue
2. 知识库优先用于报告增强和结果分层，不要一上来就把它当全局 suppress 开关
3. **不要依赖行号** 作为知识匹配主键。代码始终按最新版本扫描时，行号会漂移
4. 真正稳定的匹配依据应围绕：`规则编号 + 文件/路径特征 + 代码片段特征 + 问题描述特征 + 人工结论原因`
5. 人工复核结果是知识来源，不是自动生效的最终真理。先沉淀为候选规则，再人工启用

### 知识库文件

默认知识库：`references/false-positive-kb.json`

用途：
- 维护知识库增强规则
- 约定报告新增列
- 保存禁用中的候选规则样例

每条知识建议至少包含：
- `id`
- `enabled`
- `title`
- `rule_codes`
- `match`
- `decision`
- `reason`
- `feature_summary`
- `source`

### 知识库动作

推荐动作只用以下四类：
- `保留`：未命中或不做特殊处理
- `downgrade`：保留问题，但建议在报告中降级展示
- `manual_review`：转为人工确认项
- `known_false_positive`：已知误报，但第一阶段仍保留原始结果，只在增强列中标明

### 后处理脚本

优先使用：`scripts/annotate_scan_results.py`

```bash
python scripts/annotate_scan_results.py scan-results.json --output annotated-results.json --format text
```

脚本行为：
- 读取原始扫描结果（`issues` 数组）
- 读取 `false-positive-kb.json`
- 对每条 issue 追加知识库增强字段
- 输出增强后的 JSON，保留原始字段不变

新增字段：
- `kb_match_status`
- `kb_action`
- `kb_rule_id`
- `kb_rule_title`
- `kb_reason`
- `kb_feature_summary`
- `kb_confidence`
- `kb_requires_human_review`
- `kb_target_severity`

### 报告导出脚本

当需要把增强结果真正写入 Excel / Markdown 报告产物时，使用：`scripts/export_annotated_report.py`

```bash
python scripts/export_annotated_report.py annotated-results.json \
  --xlsx-out report.xlsx \
  --md-out report.md \
  --repo-name winning-demo \
  --git-url http://example/repo \
  --git-branch sr-next
```

脚本行为：
- 读取带 `kb_*` 字段的扫描结果
- 导出 Excel 三个 Sheet：`扫描概览`、`问题清单`、`问题明细`
- 导出 Markdown 报告，并按 `建议处理动作` 分层展示
- **原始扫描字段保留不变**，新增知识库增强列写入报告

### 报告新增列（Excel / 表格 / JSON 均适用）

在原始扫描字段后，追加以下增强列：
- `知识库匹配状态`
- `建议处理动作`
- `知识库规则ID`
- `知识库判断原因`
- `匹配特征摘要`
- `置信度`
- `是否需人工复核`

### 一键后处理脚本（推荐）

当你已经拿到原始扫描 JSON，希望最少手工步骤完成“知识库增强 + 正式报告导出”时，优先使用：`scripts/build_enhanced_report.py`

```bash
python scripts/build_enhanced_report.py scan-results.json \
  --repo-name winning-demo \
  --git-url http://example/repo \
  --git-branch sr-next
```

默认产物：
- `scan-results.annotated.json`
- `scan-results.knowledge.xlsx`
- `scan-results.knowledge.md`

可选参数：
- `--kb`：指定知识库文件
- `--output-dir`：指定输出目录
- `--base-name`：指定输出基础名
- `--annotated-json` / `--xlsx-out` / `--md-out`：显式指定各产物路径

### 推荐产物流水线

```bash
# 单命令后处理（推荐）
python scripts/build_enhanced_report.py scan-results.json --repo-name winning-demo --git-branch sr-next

# 若需要拆步排查，再分别执行：
python scripts/annotate_scan_results.py scan-results.json --output annotated-results.json
python scripts/export_annotated_report.py annotated-results.json --xlsx-out report.xlsx --md-out report.md
```

### 报告分层规则

后续输出报告时，优先按 `建议处理动作` 分层：
1. **需优先处理**：未命中知识库，或知识库仍建议保留
2. **待人工确认**：命中 `manual_review`
3. **可降级/已知模式**：命中 `downgrade` 或 `known_false_positive`

注意：
- 这只是展示分层，**不是删除原始 issue**
- 用户仍应能看到原始命中内容和增强判断内容

### 人工反哺流程

当用户像今天一样给出人工复核结果时，按以下方式使用：
1. 先把人工结论保留在台账 / 报告里
2. 再从中提炼出：
   - 规则编号（如暂缺，则先记问题类型）
   - 代码/路径模式
   - 适用边界
   - 为什么是误报 / 降级 / 人工确认
3. 默认先写成 **`enabled=false` 的候选知识**
4. 经人工确认后，再改为 `enabled=true`

优先收集的反哺字段：
- 规则编号
- 文件路径
- 命中代码片段或上下文
- 人工最终结论
- 原因说明
- 是否具有普遍性

---

## 扫描流程

### 步骤 0: 仓库路径确定

#### 检查配置文件

首先检查配置文件 `~/.cache/skills/win-code-scanner/config.json` 是否存在：

```bash
# 读取配置文件中的默认路径
DEFAULT_PATH=$(./scripts/read-config.sh default_scan_path)
```

#### 配置文件存在时的流程

如果配置文件存在且有 `default_scan_path`：

1. **解析用户输入**: 从用户描述中提取仓库名称关键词
2. **搜索仓库**: 在默认路径下递归搜索匹配的 git 仓库

```bash
# 搜索匹配的仓库
./scripts/find-repo.sh "{关键词}" "{默认路径}"
```

3. **显示搜索结果**:

**找到 1 个匹配时**:
```
找到仓库
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

仓库名称: {仓库名}
仓库路径: {仓库路径}
Git URL: {Git URL}

确认扫描此仓库？
  - 是 - 开始扫描
  - 否 - 手动指定路径
```

**找到多个匹配时**:
```
找到 {N} 个匹配的仓库
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. {仓库名1}
     路径: {路径1}

  2. {仓库名2}
     路径: {路径2}

  ...

请选择要扫描的仓库 (输入序号):
```

使用 `AskUserQuestion` 工具让用户选择。

**未找到匹配时**:
```
未找到匹配的仓库
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

搜索路径: {默认路径}
搜索关键词: {关键词}

请检查仓库名称是否正确，或手动指定仓库路径。
```

4. **确定仓库路径**: 根据用户选择确定最终的 `repo_path`
5. **继续后续步骤**: 进入步骤 1 进行仓库类型识别

#### 配置文件不存在时的流程

直接进入步骤 1，分析当前工作目录。

---

### 步骤 1: 智能识别仓库类型

AI 自动分析仓库类型并展示结果，用户可确认或纠正：

```
正在分析仓库类型...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

检测到项目类型: 前端项目

分析依据:
  - 发现 156 个 Vue 文件 (.vue)
  - 发现 423 个 JavaScript/TypeScript 文件 (.js, .ts)
  - 发现 package.json 配置文件
  - 检测到 Vue/Element UI 技术栈

适用扫描规则: 13 条 (性能、框架、工程、安全、语法规范)
```

#### AI 分析逻辑

1. **文件类型统计**: 扫描项目目录，统计各类文件数量
2. **配置文件检测**: 检测是否存在特征配置文件
3. **技术栈识别**: 根据文件和配置判断技术栈
4. **类型判定**: 综合判断项目类型

**判定规则**：

| 类型 | 判定依据 | 目标扩展名 |
|------|----------|------------|
| **前端** | Vue/JS/TS 文件占比 > 50% 或存在 package.json | `.vue`, `.js`, `.ts`, `.jsx`, `.tsx` |
| **后端** | Java/Python/Groovy 文件占比 > 50% 或存在 pom.xml/build.gradle | `.java`, `.py`, `.groovy` |

#### 用户说明

AI 分析完成后直接使用识别结果继续扫描。如果识别有误，用户可以随时终止并重新指定类型。

### 步骤 2: 统计仓库信息

扫描项目目录，统计文件数量并显示：

```
仓库信息统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
仓库路径: /path/to/repo
总文件数: 1,156

子模块统计:
  - winning-opt-basicdata-api: 423 文件
  - winning-opt-basicdata-application: 715 文件
  - winning-opt-basicdata-rpc: 18 文件
```

**注意**：
- 对于后端项目，如果检测到子模块（Maven多模块），需显示每个子模块的文件数
- 使用 `find` 命令按扩展名过滤统计

### 步骤 2.5: 排除低价值文件

为加快扫描速度，减少低价值文件扫描，自动排除以下文件类型：

#### 后端项目排除规则

```
排除低价值文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

原始文件数: 1,156 个
排除后文件数: 892 个
排除文件数: 264 个 (22.8%)

排除类型:
  - DTO/VO/BO/PO/DO/Entity/Model 等数据模型类
  - 文件名包含: InputDTO, OutputDTO, Dto, Bo, Vo, Po, Do 等
  - 注释类: Configuration/Config/Constants/Enum 等纯说明性质的类
```

**后端排除后缀列表**：
```python
backend_exclude_suffixes = [
    # 数据模型类
    "DTO.java", "InputDTO.java", "OutputDTO.java",
    "BO.java", "VO.java", "PO.java", "DO.java",
    "Entity.java", "Model.java",
    "Dto.java", "Bo.java", "Vo.java", "Po.java", "Do.java",
    # 注释类（纯说明性质，不包含业务逻辑）
    "Configuration.java", "Config.java",
    "Constants.java", "Constant.java",
    "Enum.java", "Enums.java"
]
```

#### 前端项目排除规则

```
排除低价值文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

原始文件数: 523 个
排除后文件数: 341 个
排除文件数: 182 个 (34.8%)

排除类型:
  - 目录: node_modules/, dist/, build/, coverage/, .next/, .vite/, __tests__/
  - 文件后缀: .d.ts, .css, .scss, .less, .sass, .png, .jpg, .svg, .spec.ts, .test.ts
  - 文件名: types.ts, interface.ts, constants.ts, enums.ts
```

**前端排除规则**：
```python
frontend_exclude = {
    "exclude_dirs": [
        "node_modules/", "dist/", "build/", "coverage/",
        ".next/", ".vite/", "__tests__/"
    ],
    "exclude_suffixes": [
        ".d.ts", ".css", ".scss", ".less", ".sass", ".module.css",
        ".png", ".jpg", ".svg",
        ".spec.ts", ".test.ts"
    ],
    "exclude_file_names": [
        "types.ts", "interface.ts", "constants.ts", "enums.ts"
    ]
}
```

#### 排除实现方式

**后端排除示例**：
```bash
# 使用 grep 排除低价值文件（数据模型类 + 注释类）
find . -name "*.java" | grep -v -E "(DTO|InputDTO|OutputDTO|BO|VO|PO|DO|Entity|Model|Dto|Bo|Vo|Po|Do|Configuration|Config|Constants|Constant|Enum|Enums)\.java$"
```

**前端排除示例**：
```bash
# 排除目录
find . -name "*.vue" -o -name "*.ts" -o -name "*.js" | \
  grep -v -E "(node_modules/|dist/|build/|coverage/|\.next/|\.vite/|__tests__/)"

# 排除后缀
find . -name "*.vue" -o -name "*.ts" -o -name "*.js" | \
  grep -v -E "\.(d\.ts|css|scss|less|sass|png|jpg|svg|spec\.ts|test\.ts)$"

# 排除特定文件名
find . -name "*.ts" | \
  grep -v -E "(types\.ts|interface\.ts|constants\.ts|enums\.ts)$"
```

#### 排除确认

排除完成后显示最终文件列表：
```
排除完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
待扫描文件数: 892 个
已排除低价值文件: 264 个

是否继续使用此文件列表进行扫描？
  - 是 - 继续扫描
  - 否 - 返回重新选择
```

### 步骤 3: 选择扫描方式

使用 `AskUserQuestion` 工具询问：
- **问题**: 请选择扫描方式
- **选项**:
  - 增量扫描 - 扫描最近修改的文件
  - 全库扫描 - 扫描所有文件
  - 抽样扫描 - 按范围或采样率扫描(适用大型仓库)
  - 返回上一步 - 重新分析仓库类型

#### 3A. 增量扫描

使用 `AskUserQuestion` 工具询问：
- **问题**: 请选择时间范围
- **选项**:
  - 最近 3 天
  - 最近 10 天
  - 最近 15 天
  - 返回上一步 - 重新选择扫描方式

使用 `scripts/get-changed-files.sh` 脚本获取指定时间范围内修改的文件：

```bash
# 进入仓库目录
cd {仓库路径}

# 调用脚本获取修改的文件
./script/get-changed-files.sh {天数} "{扩展名}"

# 前端项目示例
./script/get-changed-files.sh 3 "vue js ts jsx tsx"

# 后端项目示例
./script/get-changed-files.sh 3 "java groovy py"

# 读取临时文件中的文件列表
cat /tmp/changed_files_{天数}days.txt
```

**脚本输出示例**：
```
=== 增量扫描文件获取工具 ===

仓库路径: /path/to/repo
时间范围: 最近 3 天
扫描时间: 2026-02-11 10:30:00

找到 25 个修改的文件

文件类型统计:
  java: 18 个
  xml: 5 个
  properties: 2 个

=== 修改的文件列表 ===
src/main/java/com/example/Service.java
src/main/java/com/example/Controller.java
...

文件列表已保存到: /tmp/changed_files_3days.txt

=== 验证文件存在性 ===
存在: 24 个
缺失: 1 个
✗ src/main/java/com/example/DeletedClass.java (不存在)
```

#### 3B. 全库扫描

扫描所有目标文件，无需额外选择。

#### 3C. 抽样扫描

使用 `AskUserQuestion` 工具询问：
- **问题**: 请选择抽样方式
- **选项**:
  - 按目录扫描 - 指定扫描的子目录
  - 按采样率扫描 - 设置采样比例 (0.1-1.0)
  - 返回上一步 - 重新选择扫描方式

##### 3C-1. 按目录扫描

**先展示可用的子目录列表**，然后使用 `AskUserQuestion` 工具询问：

```
可用子目录列表：
  1. winning-opt-basicdata-api (423 文件)
  2. winning-opt-basicdata-application (715 文件)
  3. winning-opt-basicdata-rpc (18 文件)
```

- **问题**: 请输入要扫描的目录路径（支持相对路径，如：./module-name 或 module-name/src）
- **选项**:
  - 扫描全部子目录 - 扫描所有列出的子目录
  - 返回上一步 - 重新选择抽样方式

**用户输入处理**：
- 支持相对路径：`./module-name` 或 `module-name/src/main/java`
- 支持通配符：`**/*Controller.java`（扫描所有 Controller）
- 输入为空时，提示用户重新输入

**验证目录有效性**：
```bash
# 检查目录是否存在
ls -la {用户输入的目录}

# 统计该目录下的目标文件数
find {用户输入的目录} -name "*.java" -o -name "*.vue" | wc -l
```

##### 3C-2. 按采样率扫描

使用 `AskUserQuestion` 工具询问：
- **问题**: 请输入采样比例 (0.1-1.0)，0.1 表示扫描 10% 的文件
- **选项**:
  - 0.1 (10%) - 快速抽样
  - 0.3 (30%) - 中等抽样
  - 0.5 (50%) - 半量抽样
  - 1.0 (100%) - 全量扫描
  - 自定义输入 - 输入其他采样比例
  - 返回上一步 - 重新选择抽样方式

### 步骤 3.5: 处理大量文件（必须执行）

**⚠️ 重要：当待扫描文件数超过 150 个时，必须执行此步骤**

**原因**：文件数量过多会超过上下文 token 限制，导致扫描异常或失败。必须采用分批扫描模式。

使用 `AskUserQuestion` 工具询问：
- **问题**: 文件数量较多 ({N}个)，超过单次扫描阈值(150个)，必须分批处理以避免 token 超限。请选择处理方式
- **选项**:
  - 分批串行扫描（推荐） - 每批 100 个，串行扫描，批间询问是否继续，**稳定性最高**
  - 分批并发扫描 - 每批 100 个，批次内最多3个agent并发，**禁止连续启动多个批次**，批次间必须串行
  - 继续全量扫描 - 一次性扫描所有文件(⚠️ 警告：可能导致 token 超限失败)
  - 调整扫描范围 - 返回上一步重新选择扫描方式

**⭐ 推荐：分批串行扫描模式**
- 优点：稳定性高，token消耗可控，批间可灵活调整
- 适合：大多数场景，尤其是需要精确扫描或中途可能需要调整的情况

#### 3.5A. 分批串行扫描模式（推荐）

配置：
- 每批文件数: 100
- 扫描方式: 串行扫描（稳定性最高，token消耗可控）
- **增量报告**: 每批扫描完成后自动增量更新报告文件
- 每批扫描完成后使用 `AskUserQuestion` 工具询问：
  - **问题**: 第 {批次数}/{总批次数} 批扫描完成，已扫描 {已扫描数} 个文件，发现问题 {问题数} 个，预计剩余 {剩余批次数} 批 (约 {剩余时间})。**报告已增量更新**。请选择
  - **选项**:
    - 继续下一批
    - 停止扫描（当前报告已保存）
    - 继续剩余所有批次
    - 返回上一步 - 重新选择处理方式

#### 3.5B. 分批并发扫描模式（不推荐）

配置：
- 每批文件数: 100
- 每批并发数: 最多 3 个 Explore agent（**严格控制不能超过3个**）
- 扫描方式: **批次间必须串行，禁止连续启动多个批次**，批次内最多3个并发
- **增量报告**: 每批扫描完成后自动增量更新报告文件

**⚠️ 注意事项**：
- 虽然速度更快，但稳定性较低
- 批次内并发可能导致token超限
- 仅在时间紧迫且文件量很大时考虑使用

```
分批并发扫描配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总文件数: 500
批次大小: 100
总批次数: 5 批
每批并发数: 3 个 agent
每批文件数: 34 个

预计耗时: 约 15-20 分钟
  - 单线程: 50 分钟
  - 分批串行: 50 分钟
  - 分批并发: 15-20 分钟（更稳定）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第 1/5 批 (100 文件) - 正在扫描...

  Agent 1: ████████████████████ 100% (34/34)
  Agent 2: ████████████████████ 100% (33/33)
  Agent 3: ████████████████████ 100% (33/33)

本批完成: 扫描 100 个文件，发现问题 8 个
报告已增量更新: /tmp/仓库名称_202602111802.md
```

**实现方式**：

详见 `scripts/batch_scan.py`，核心逻辑：

```python
from scripts.batch_scan import BatchScanner

# 推荐配置：串行扫描模式（稳定性最高）
scanner = BatchScanner(
    files=files_list,
    batch_size=100,
    max_concurrent=1,  # 串行扫描
    report_path="/tmp/仓库名称_202602111802.md"
)

# 并发扫描模式（不推荐，仅时间紧迫时使用）
scanner_concurrent = BatchScanner(
    files=files_list,
    batch_size=100,
    max_concurrent=3,  # 批次内最多3个并发
    report_path="/tmp/仓库名称_202602111802.md"
)

def scan_batch(batch_files):
    """扫描单个批次"""
    # 串行模式：单个agent处理整批
    result = scan_files_serial(batch_files)
    return result

    # 并发模式：将批次分成3个chunk，并发处理
    tasks = []
    chunks = [batch_files[i::3] for i in range(min(3, len(batch_files)))]

    for i, chunk in enumerate(chunks):
        task = Task(
            description=f"批次-Agent{i+1}",
            prompt=f"扫描以下文件: {chunk}",
            subagent_type="Explore"
        )
        tasks.append(task)

    results = wait_for_all(tasks)
    return merge_results(results)

def ask_continue(batch_idx, total_batches):
    """询问用户是否继续"""
    # 使用 AskUserQuestion 工具
    return user_choice

# 执行扫描
results = scanner.scan(scan_func=scan_batch, ask_user_func=ask_continue)
```

**进度显示**：
```
正在扫描 [分批并发模式]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

批次进度: ████████░░░░░░░░░░░░ 2/5 批 (40%)
文件进度: ████████░░░░░░░░░░░░ 200/500 (40%)
发现问题: 16 个
报告状态: 已增量更新 2/5 批次

当前批次:
  Agent 1: ████████████████████ 100% (34/34) ✓
  Agent 2: ████████████████████ 100% (33/33) ✓
  Agent 3: ████████████████░░░░ 80% (26/33) ⏳

预估剩余: 3 批 (约 10 分钟)
```

### 步骤 4: 执行扫描

使用大模型进行代码扫描，**只显示进度条，不展示详细过程**：

```
正在扫描...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  45% (85/188)

已扫描: 85 个文件
待扫描: 103 个文件
```

**扫描提示词模板**：

```
你是一个专业的代码审查专家。请根据以下规则对代码进行扫描分析。

【扫描规则】
{从 references/ 读取的规则内容}

【待扫描文件】
{文件内容，包含文件路径和行号}

【输出要求】
请以纯JSON格式输出扫描结果：

{
  "issues": [
    {
      "rule_code": "规则编号",
      "rule_name": "规则名称",
      "severity": "严重/警告",
      "category": "性能/安全/业务/框架/架构/质量/语法",
      "file": "文件相对路径",
      "line": 行号,
      "code_snippet": "问题代码（前后各2行上下文）",
      "description": "问题描述",
      "suggestion": "修复建议"
    }
  ],
  "summary": {
    "total": 问题总数,
    "critical": 严重问题数,
    "warning": 警告问题数
  },
  "scanned_files": 扫描文件数
}
```

### 步骤 5: 选择报告格式

扫描完成后，使用 `AskUserQuestion` 工具询问：
- **问题**: 扫描完成！发现 {问题数} 个问题。请选择报告格式
- **选项**:
  - Markdown (.md)
  - Excel (.xlsx)

### 步骤 6: 生成报告文件

根据用户选择生成报告，并**必须**在控制台输出以下格式的下载信息：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 报告下载

报告路径: /winning/winex-repo/storage/repos/reports/code-scan/winning-dtc-Knowledge_202602121501.md
下载地址: http://172.17.1.173/repos/reports/code-scan/winning-dtc-Knowledge_202602121501.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**⚠️ 强制要求**：扫描完成后**必须**输出以上格式的报告下载信息，包含：
1. 报告路径（本地文件系统路径）
2. 下载地址（HTTP URL）

**下载地址生成逻辑**:
- 如果配置了 `report_base_url`，则下载地址为 `{report_base_url}/{报告文件名}`
- 如果未配置 `report_base_url`，则只显示报告路径，不显示下载地址

**⚠️ 报告内容要求（重要）**：

1. **报告命名规则（强制）**
   - 格式：`{仓库名称}_{时间}.{扩展名}`
   - 示例：`winning-dtc-Knowledge_202602121501.md` 或 `winning-dtc-Knowledge_202602121501.xlsx`
   - 时间格式：`YYYYMMDDHHmm`（如：202602121501 表示 2026年2月12日15:01）

2. **报告扫描概要（必含字段）**
   | 字段 | 说明 | 示例 |
   |------|------|------|
   | 仓库地址 | Git 仓库完整 URL | http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0/WiNEX_WXP/_git/winning-dtc-Knowledge |
   | 扫描分支 | 当前扫描的 Git 分支 | 4.0.0-SNAPSHOT |
   | 批次进度 | 扫描批次进度 | 5/8 批 (用户提前终止) |
   | 已扫描文件 | 已扫描文件数/总文件数 | 500 / 767 (65.2%) |
   | 耗时 | 扫描耗时 | 207 秒 |
   | Token 消耗 | Token 消耗量 | 138,784 |

3. **按规则分组展示问题**
   - 每个规则为一个独立的问题条目
   - 同规则的所有问题合并到一个条目中
   - 每批次扫描完成后，命中同规则的问题文件累加到"涉及文件"列表

4. **每个规则条目必须包含以下字段**：
   | 字段 | 说明 | 示例 |
   |------|------|------|
   | 规则编号 | 如 QUAL-B011 | QUAL-B011 |
   | 风险等级 | high/medium | 🔴 high / 🟡 medium |
   | 问题类别 | 性能/安全/业务/代码质量等 | 代码质量 |
   | 影响范围 | 该规则命中的问题行号总数（必与涉及文件行号数量一致） | 7 处 |
   | 涉及文件 | 文件路径及行号列表（支持累加） | `path/to/file.java`: 第 81, 83, 85 行 |
   | 修复步骤 | 1/2/3步修复指南 | - |
   | 代码示例 | 修改前/修改后对比 | - |
   | 原理说明 | 问题产生原因和影响 | - |

5. **影响范围计算规则（重要）**
   - **影响范围 = 涉及文件中所有行号的总数量**
   - 示例：如果涉及文件为 `Service.java: 第 81, 83, 85 行` 和 `Controller.java: 第 45, 67 行`，则影响范围为 **5 处**（而非 2 个文件）

6. **报告格式（参照 demo-markdown.md）**：

```markdown
# 仓库名称 代码扫描报告

## 📋 扫描概览

| 项目 | 值 |
|------|----|
| 仓库 | 仓库名称 |
Git URL | http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0/WiNEX_WXP/_git/仓库名称 |
| 分支 | 4.0.0-SNAPSHOT |
| 批次进度 | 5/8 批 (用户提前终止) |
| 已扫描文件 | 500 / 767 (65.2%) |
| 耗时 | 207 秒 |
| Token 消耗 | 138,784 |


## 问题统计

| 严重程度 | 数量 |
|----------|------|
| 严重 | 1 |
| 警告 | 45 |
| **总计** | **46** |


## 完整问题列表

### QUAL-B011

**风险等级**: 🔴 high

**问题类别**: 代码质量

**影响范围**: 7 处

**涉及文件**:
- `winning-log-main/src/main/java/com/winning/mis/tasks/CleanLogDataTaskRunner.java`: 第 81, 83, 85, 106, 108 行
- `winning-log-main/src/main/java/com/winning/mis/service/MgrLogServiceImpl.java`: 第 74, 118 行

**修复步骤**:
1. 识别并定位所有触发 QUAL-B011 规则的代码
2. 根据修复建议进行修改（见代码示例）
3. 添加必要的单元测试验证修复

**代码示例**:

❌ **修改前**:
\`\`\`java
72: return new String(Files.readAllBytes(Paths.get(mgrLogParam.getFilePath())), StandardCharsets.UTF_8);
73: } catch (IOException e) {
>>> 74: e.printStackTrace();
75: }
\`\`\`

✅ **修改后**:
\`\`\`java
使用printStackTrace打印异常堆栈,高并发环境下会影响IO性能,且不利于日志集中管理
\`\`\`

**原理说明**: 使用printStackTrace打印异常堆栈,高并发环境下会影响IO性能,且不利于日志集中管理

---

### PERF-B007

**风险等级**: 🔴 high

**问题类别**: 性能规范

**影响范围**: 3 处

**涉及文件**:
- `path/to/Service.java`: 第 45, 67 行
- `path/to/Controller.java`: 第 23 行

...
```

4. **增量报告更新规则**：
   - 每批次扫描完成后，按规则分组统计问题
   - 同规则的问题文件行号累加到现有条目
   - 新规则则创建新条目
   - 实时更新报告文件

5. **报告不应包含**：
   - 修复优先级建议（如 P0/P1/P2 分级）
   - 主观的修复建议排序
   - 让用户根据自身业务情况判断修复优先级

### 步骤 7: 完成扫描

```
代码扫描完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
扫描模块: winning-opt-basicdata
扫描文件: 1156 个
发现问题: 21 个
报告路径: /tmp/仓库名称_202602111802.md

扫描耗时: 约 5 分钟
```

---

## 扫描规则文件

规则文件存储在 `references/` 目录，采用索引+完整规则的双文件结构：

### 前端规则 (12条)
- `frontend_rules_index.json` - 精简索引，包含规则概要
- `frontend_rules.json` - 完整规则，包含所有检查点

### 后端规则 (36条)
- `backend_rules_index.json` - 精简索引，包含规则概要
- `backend_rules.json` - 完整规则，包含所有检查点

### 规则使用策略

**优先使用索引文件**：索引文件包含规则的核心信息（code, name, severity, description, checkpoints数量），token消耗更少。

**按需加载完整规则**：当需要详细检查点时，才从完整规则文件中读取对应规则的 checkpoints。

**规则匹配逻辑**：
1. 首先读取对应的 index 文件，获取规则列表
2. 根据文件扩展名从 `applicable_extensions` 字段筛选适用规则
3. 对于需要详细检查的规则，再从完整规则文件中读取 checkpoints

扫描前先读取对应的规则索引文件，但**不需要向用户展示规则详情**。

---

## 工作目录

扫描过程中产生的临时文件和报告保存在 `/tmp/` 目录：
- 临时文件列表: `/tmp/[module-name]_files.txt`
- 扫描报告: `/tmp/[仓库名称]_[YYYYMMDDHHmm].md`（如：`winning-code-scan-tool_202602111802.md`）

---

## 注意事项

1. **⚠️ Token 限制（最重要）**：当待扫描文件数超过 **150 个**时，必须触发步骤 3.5 的分批处理流程，否则会导致上下文 token 超限而失败
2. **⚠️ 完整问题列表（重要）**：报告必须包含所有扫描到的问题，不能只显示部分示例。每个问题必须包含：规则编号、严重程度、文件路径、行号、问题描述
3. **⚠️ 增量报告（重要）**：分批扫描时，**每批次完成后必须立即增量更新报告文件**，确保中途停止或失败时，已完成批次的报告已保存
4. **只显示进度条**：扫描过程中不要展示每个文件的扫描详情
5. **先统计后扫描**：确保用户知道要扫描多少文件
6. **子模块支持**：后端项目需正确识别和统计子模块
7. **git增量扫描**：正确使用git命令获取时间范围内的文件
8. **⚠️ 报告下载地址（重要）**：扫描完成后**必须**在控制台输出以下信息：
   - 报告路径（本地文件路径）
   - 下载地址（HTTP URL，格式：`{report_base_url}/{报告文件名}`）

   示例输出：
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📥 报告下载

   报告路径: /winning/winex-repo/storage/repos/reports/code-scan/winning-dtc-Knowledge_202602121501.md
   下载地址: http://172.17.1.173/repos/reports/code-scan/winning-dtc-Knowledge_202602121501.md
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```
9. **⭐ 推荐分批串行扫描模式（重要）**：对于大多数场景，推荐使用分批串行扫描而非并发扫描：
   - 优点：稳定性最高，token消耗可控，批间可灵活调整，便于调试
   - 并发扫描仅推荐在时间紧迫且文件量极大时使用
10. **分批扫描交互**：每批扫描完成后必须询问用户是否继续（每批 100 个文件）
11. **并发扫描限制**：严格控制并发任务数不超过 3 个，避免资源占用过高

12. **⚠️ 批次失败处理（重要）**：当某个批次因 token 限制失败时：
    - **失败重试**：自动重试失败的批次（最多3次）
    - **保留已成功结果**：失败批次不影响已完成批次的报告
    - **继续后续批次**：跳过失败批次，继续扫描剩余批次
    - **失败标记**：在报告中标记哪些批次扫描失败/重试成功

13. **配置文件路径**: 用户需手动创建 `~/.cache/skills/win-code-scanner/config.json` 文件，参考 `config/config.example.json` 示例

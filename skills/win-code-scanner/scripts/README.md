# Script 目录

此目录包含代码扫描工具使用的辅助脚本。

## 脚本列表

### exclude_low_value_files.py

低价值文件排除工具 - 在代码扫描前自动排除低价值文件，加快扫描速度。

#### 功能特性

- **后端排除**：排除 DTO/VO/BO/PO/DO/Entity/Model 等数据模型类
- **前端排除**：排除 node_modules、dist、测试文件、样式文件等
- **灵活输入**：支持从文件或 stdin 读取文件列表
- **统计摘要**：显示排除前后的文件数量统计

#### 使用方法

```bash
# 从文件读取
python scripts/exclude_low_value_files.py backend files.txt

# 从 stdin 读取
find . -name "*.java" | python scripts/exclude_low_value_files.py backend --stdin

# 前端项目
find . -name "*.vue" -o -name "*.ts" | python scripts/exclude_low_value_files.py frontend --stdin
```

#### 后端排除规则

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

#### 前端排除规则

```python
frontend_exclude = {
    "exclude_dirs": [
        "node_modules/", "dist/", "build/", "coverage/",
        ".next/", ".vite/", "__tests__/"
    ],
    "exclude_suffixes": [
        ".d.ts", ".css", ".scss", ".less", ".sass", ".module.css",
        ".png", ".jpg", ".jpeg", ".svg", ".gif", ".ico",
        ".spec.ts", ".test.ts", ".spec.js", ".test.js"
    ],
    "exclude_file_names": [
        "types.ts", "interface.ts", "interfaces.ts",
        "constants.ts", "enums.ts", "enum.ts"
    ]
}
```

#### 输出示例

```
排除低价值文件
==================================================
原始文件数: 1,156 个
排除后文件数: 892 个
排除文件数: 264 个 (22.8%)

排除类型:
  - DTO/VO/BO/PO/DO/Entity/Model 等数据模型类
  - 注释类: Configuration/Config/Constants/Enum 等纯说明性质的类

==================================================
src/main/java/com/example/UserService.java
src/main/java/com/example/UserController.java
...

过滤后的文件列表已保存到: /tmp/filtered_backend_files.txt
```

---

### optimize_rules.py

扫描规则优化工具 - 支持新的索引+规则双文件结构，减少 token 消耗。

#### 功能特性

- **规则验证**：检查规则文件是否已优化（检查 `_optimized` 标记和冗余字段）
- **规则索引生成**：生成按类别组织的索引文件
- **规则优化**：删除冗余字段，只保留核心扫描字段
- **Token 优化**：使用索引可减少约 40-60% 的 prompt token

#### 使用方法

```bash
# 验证所有规则文件
python scripts/optimize_rules.py --validate

# 优化所有规则文件
python scripts/optimize_rules.py --optimize

# 只处理后端规则
python scripts/optimize_rules.py --type backend --optimize

# 只处理前端规则
python scripts/optimize_rules.py --type frontend --optimize
```

#### 输出示例

```
==================================================
处理 backend 规则
==================================================
✓ 规则文件已优化，格式正确

正在生成规则索引...
规则索引已生成: .../references/backend_rules_index.json
  分类数: 7
  总规则数: 36

==================================================
处理 frontend 规则
==================================================
✓ 规则文件已优化，格式正确

正在生成规则索引...
规则索引已生成: .../references/frontend_rules_index.json
  分类数: 5
  总规则数: 12
```

#### 文件结构

```
references/
├── backend_rules.json          # 后端完整规则（已优化）
├── backend_rules_index.json    # 后端规则索引
├── frontend_rules.json        # 前端完整规则（已优化）
└── frontend_rules_index.json  # 前端规则索引
```

#### 索引文件格式

索引文件采用嵌套结构，按类别组织规则：

```json
{
  "性能规范": {
    "PERF-B007": {
      "name": "下游调用超时配置规范",
      "severity": "严重",
      "description": "下游接口调用必须设置合理的超时时间...",
      "checkpoints": 3
    },
    ...
  },
  "安全规范": {
    "SEC-B003": {
      "name": "SQL注入防护",
      "severity": "严重",
      "description": "禁止字符串拼接SQL语句...",
      "checkpoints": 5
    },
    ...
  }
}
```

---

### get_scan_prompt.py

扫描提示词生成脚本 - 支持索引+规则双文件结构。

#### 功能特性

- **智能加载**：优先使用索引文件（token消耗少），按需加载完整规则
- **扩展名筛选**：根据文件扩展名自动筛选适用的规则
- **规则指定**：支持指定特定规则代码进行扫描
- **Token 优化**：相比完整规则可节省 40-60% token

#### 使用方法

```bash
# 后端扫描提示词
python scripts/get_scan_prompt.py backend

# 前端扫描提示词
python scripts/get_scan_prompt.py frontend

# 指定规则代码（逗号分隔）
python scripts/get_scan_prompt.py backend PERF-B001,SEC-B003
```

#### API 用法

```python
from scripts.get_scan_prompt import (
    generate_scan_prompt,
    get_applicable_rules,
    get_rule_summary
)

# 生成扫描提示词
prompt = generate_scan_prompt(
    file_type='backend',
    file_extensions=['.java', '.sql'],
    use_index=True  # 优先使用索引
)

# 获取适用的规则
rules = get_applicable_rules('backend', ['.java'])

# 获取规则统计摘要
summary = get_rule_summary('backend')
# {'total': 36, 'by_category': {...}, 'by_severity': {...}}
```

#### 输出格式

提示词包含：
- 规则索引（精简格式，包含核心信息）
- 扫描要求（输出格式、字段说明）
- JSON 输出格式定义

#### Token 节省对比

| 方式 | Token 消耗 (后端) | Token 消耗 (前端) | 节省比例 |
|------|-------------------|-------------------|----------|
| 完整规则 | ~15000 tokens | ~5000 tokens | - |
| 规则索引 | ~6000 tokens | ~2000 tokens | 60% |
| 按扩展名筛选 | ~3000 tokens | ~1000 tokens | 80%+ |

---

### batch_scan.py

分批并发扫描实现，用于处理大量文件的代码扫描，避免 token 超限。

#### 功能特性

- 分批处理：将大量文件分成多个批次，每批默认 100 个文件
- 并发控制：批次内最多 3 个并发 agent（严格控制）
- 增量报告：每批次完成后立即更新报告，确保中途停止时已完成批次的报告已保存
- 批次间串行：禁止连续启动多个批次

#### 核心类

```python
import datetime
from scripts.batch_scan import BatchScanner

repo_name = "winning-code-scan-tool"  # 从 git 仓库名获取
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
report_path = f"/tmp/{repo_name}_{timestamp}.md"

scanner = BatchScanner(
    files=files_list,          # 待扫描的文件列表
    batch_size=100,             # 每批处理的文件数
    max_concurrent=3,           # 批次内最大并发数（不超过3）
    report_path=report_path      # 报告文件路径
)

# 执行扫描
results = scanner.scan(scan_func=scan_batch, ask_user_func=ask_continue)
```

#### 方法说明

- `init_report(total_files, total_batches)` - 初始化报告文件
- `update_report_incremental(...)` - 增量更新报告
- `scan(scan_func, ask_user_func)` - 执行分批扫描
- `format_progress(...)` - 格式化进度显示

#### 输出内容

1. **增量报告**：每批次完成后追加到报告文件
2. **进度信息**：格式化的批次进度、文件进度、问题统计

---

### get-changed-files.sh

获取指定天数内修改的文件列表，用于增量扫描。

#### 用法

```bash
# 获取最近 3 天修改的所有文件
./get-changed-files.sh 3

# 获取最近 10 天修改的 Java 和 Vue 文件
./get-changed-files.sh 10 "java vue js ts"

# 获取最近 30 天修改的所有文件
./get-changed-files.sh 30
```

#### 输出内容

1. **控制台输出**：
   - 仓库路径
   - 时间范围
   - 扫描时间
   - 文件类型统计
   - 修改的文件列表
   - 文件存在性验证

2. **临时文件**：
   - `/tmp/changed_files_{天数}days.txt` - 包含所有修改的文件列表

#### 返回值

- 脚本会将修改的文件列表输出到 stdout 和临时文件
- 退出码：
  - `0` - 成功
  - `1` - 错误（非 git 仓库等）

## 在 Skills 中使用

### Bash 工具调用示例

```bash
# 获取最近 3 天修改的 Java 文件
cd /path/to/repo && /path/to/get-changed-files.sh 3 "java"

# 读取临时文件中的文件列表
cat /tmp/changed_files_3days.txt
```

### Python 调用示例

```python
import subprocess

def get_changed_files(days=3, extensions=None):
    """获取指定天数内修改的文件"""
    cmd = ["/path/to/get-changed-files.sh", str(days)]
    if extensions:
        cmd.append(" ".join(extensions))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        # 从输出中解析文件列表
        files = [f for f in result.stdout.split('\n') if f and not f.startswith('=')]
        return files
    return []
```

## 规则文件更新流程

当规则需要更新时：

1. **更新完整规则**：修改 `backend_rules.json` 或 `frontend_rules.json`
2. **运行优化脚本**：`python scripts/optimize_rules.py --optimize`
3. **自动生成索引**：脚本会自动更新对应的 `_index.json` 文件

## Git 命令参考

脚本使用的核心 Git 命令：

```bash
# 获取已提交的修改文件
git log --name-only --since="3 days ago" --pretty=format: | sort | uniq

# 获取未提交的修改文件
git diff --name-only HEAD

# 获取指定日期范围的修改文件
git diff --name-only HEAD@{3.days.ago} HEAD
```

### find-repo.sh

在默认路径下递归搜索匹配的 git 仓库。

**用法**:
```bash
./find-repo.sh <关键词> <默认路径>
```

**参数**:
- `关键词`: 仓库名称匹配关键词（不区分大小写）
- `默认路径`: 搜索的根目录路径

**输出格式**:
```
FOUND_REPO:/path/to/repo|reponame|git_url
```

**示例**:
```bash
./find-repo.sh "winning-dtc" "/winning/winex-repo/storage/repos"
```

### read-config.sh

读取代码扫描配置文件。

**用法**:
```bash
./read-config.sh [配置项名称]
```

**参数**:
- `配置项名称`: 可选，默认为 `default_scan_path`

**返回值**:
- 配置项的值
- 如果配置文件不存在，返回空

**示例**:
```bash
./read-config.sh default_scan_path
# 输出: /winning/winex-repo/storage/repos
```

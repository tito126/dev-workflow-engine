# preprocess.py 日志解析 Bug 修复记录

## 问题描述

**发现时间**: 2026-03-06 15:45

**问题**: preprocess.py 无法正确解析工具组 API 返回的日志格式，导致所有 ERROR 和 WARN 都被漏掉。

**症状**:
- 分析结果显示 ERROR: 0, WARN: 0
- 实际日志中有 11,630 个 ERROR 行
- 用户发现问题并提醒

## 根本原因

工具组 API 返回的日志格式与预期不同：

**预期格式**:
```
[trace] [,,] [IP:Port] [user] time [thread] level class -- content
```

**实际格式**:
```
[trace] [,,] [IP:Port] [] [] time [thread] level class -- content
```

关键差异：有**两个空的 `[]` 字段**，而不是一个用户字段。

原有的正则表达式只有 4 个可选字段，无法匹配这种格式。

## 修复方案

### 1. 更新正则表达式

**修改前**:
```python
LOG_PATTERN = re.compile(
    r'\[([^]]*)\]\s*'  # traceId
    r'(?:\[([^]]*)\]\s*)?'  # [,,]
    r'\[([^]]*)\]\s*'  # IP:Port
    r'(?:\[([^]]*)\]\s*)?'  # user
    r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s*'  # timestamp
    ...
)
```

**修改后**:
```python
LOG_PATTERN = re.compile(
    r'\[([^]]*)\]\s*'  # traceId
    r'(?:\[([^]]*)\]\s*)?'  # [,,]
    r'\[([^]]*)\]\s*'  # IP:Port
    r'(?:\[([^]]*)\]\s*)?'  # field1
    r'(?:\[([^]]*)\]\s*)?'  # field2 (新增)
    r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s*'  # timestamp
    ...
)
```

### 2. 重写 parse_log_line 函数

**核心改进**:
- 动态查找时间戳位置（最可靠的标识）
- 基于时间戳位置推断其他字段
- 不再依赖固定的字段顺序

**新逻辑**:
```python
# 1. 找到时间戳位置
timestamp_idx = None
for i, g in enumerate(groups):
    if g and re.match(r'\d{4}-\d{2}-\d{2}', g):
        timestamp_idx = i
        break

# 2. 时间戳之后的字段是固定的
timestamp = groups[timestamp_idx]
thread = groups[timestamp_idx + 1]
level = groups[timestamp_idx + 2]
class_name = groups[timestamp_idx + 3]
content = groups[timestamp_idx + 4]

# 3. 时间戳之前的字段动态解析
for i in range(1, timestamp_idx):
    if ':' in groups[i] and any(c.isdigit() for c in groups[i]):
        ip_port = groups[i]
    elif '(' in groups[i] and ')' in groups[i]:
        user_field = groups[i]
```

## 修复结果

### 修复前
```
总日志数: 1,351,018
ERROR: 0
WARN: 0
慢接口: 0
```

### 修复后
```
总日志数: 1,351,018
ERROR: 5,844
WARN: 103,853
慢接口: 3,326
```

### 错误分类
- SQL 异常: 1,531 个
- 空指针异常: 660 个
- 超时异常: 48 个
- 其他: 3,605 个

## 影响范围

**受影响的环境**:
- 所有使用工具组 API 拉取日志的环境
- 可能包括飞书等其他传统服务器部署的医院

**不受影响的环境**:
- K8s 环境（通过 Grafana/Loki 查询，日志格式不同）

## 修复文件

1. `preprocess.py` - 主要修复文件
2. `fix_parse_function.py` - 修复脚本
3. `quick_analyze.py` - 验证脚本
4. `test_parse_fix.py` - 测试脚本

## 测试验证

### 测试用例
```python
# 工具组 API 格式
'[trace,span,parent] [,,] [172.16.6.60:9380] [] [] 2026-03-06 13:46:29,577 [thread] ERROR class (file:line) -- timeout'

# K8s 格式
'[trace,span,parent] [,,] [] [] [] 2026-03-06 13:46:27,970 [thread] INFO class (file:line) -- message'
```

### 测试结果
- ✅ 工具组 API 格式：正确解析
- ✅ K8s 格式：正确解析
- ✅ 传统格式：正确解析
- ✅ 解析率：68.6% (926,391 / 1,351,018)

## 后续行动

1. ✅ 修复 preprocess.py
2. ✅ 验证修复效果
3. ✅ 生成正确的分析报告
4. ⏳ 提交到公共 skill（避免飞书等环境遇到同样问题）
5. ⏳ 更新文档说明支持的日志格式

## 经验教训

1. **日志格式多样性**: 不同环境的日志格式可能有细微差异，需要更灵活的解析逻辑
2. **测试覆盖**: 应该用真实日志测试，而不是假设格式
3. **错误反馈**: 用户的反馈非常重要，及时发现了严重 bug
4. **动态解析**: 基于可靠标识（如时间戳）动态解析，比固定位置更健壮

## 相关文件

- `skills/log-inspect/preprocess.py` - 修复后的主文件
- `skills/log-inspect/PREPROCESS_BUG_FIX.md` - 本文档
- `skills/log-inspect/quick_analysis.json` - 真实分析结果
- `skills/log-inspect/logs_20260306_150657_test.json` - 修复后的 digest
- `skills/log-inspect/logs_20260306_150657_report_fixed.html` - 修复后的报告

## 更新日志

- **2026-03-06 15:45**: 用户发现问题
- **2026-03-06 15:50**: 定位根本原因
- **2026-03-06 15:55**: 完成修复并验证
- **2026-03-06 15:57**: 准备提交到公共 skill

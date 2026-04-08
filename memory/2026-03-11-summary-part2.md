# 2026-03-11 日志巡检工具优化总结（第二部分）

## 今天完成的工作（22:32 - 01:23）

### 1. API入口提取优化 ✅

**问题**：06b37820368c41d6ab2156592c778fcc 有API入口但没显示
**修复**：优先从WARN日志中提取API入口，如果没有WARN再从最后一条日志提取
**文件**：`D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py`

### 2. 高优先级优化（全部完成）✅

#### 2.1 慢接口优化

- 每个慢接口只取最慢的1个trace（从最多50个减到10个）
- 修改：`preprocess.py` line 716

#### 2.2 异常分类代表trace拉完整链路

- 为异常分类的代表traceId拉取完整链路
- 慢接口10个 + 异常分类代表，共拉取完整链路
- 修改：`preprocess.py` line 1168-1293
- **注意**：这个实现有问题，是从原始日志文件中提取，而不是从Loki拉取

#### 2.3 异常影响级别分析

- 新增函数：`analyze_impact_level(trace_logs)` - 基于线程类型判断影响级别
- 判断逻辑：
  - 🔴 high - HTTP请求线程（Jetty-Worker）
  - 🟡 medium - RPC调用线程（rpc-exec）
  - 🟢 low - 异步任务线程（exe, enc）
- 修改：`preprocess.py` line 152-180, `generate_html_report_v2.py` line 156-169

#### 2.4 日志质量分析章节

- 统计：缺少API入口、只有null、影响级别分布
- 修改：`preprocess.py` line 1296-1312, `generate_html_report_v2.py` line 152-203

### 3. 第二阶段拉取问题修复 ✅

#### 问题发现（00:16）

用户发现：06b37820368c41d6ab2156592c778fcc 在Loki中有21行日志，但我们只拉了2行

#### 原因分析

1. 第一阶段：拉取ERROR和"业务处理耗时"（WARN）
2. 第二阶段：loki_fetcher.py的 `extract_error_representatives`函数按category分组，每个分类只选1个代表
3. 问题：同一分类（如sql_error）可能有多个不同的错误，只选1个代表会漏掉其他错误

#### 解决方案A：三级分组（00:41）

- 按 `category:api_entry:error_signature` 三级分组
- `error_signature`：错误特征码（如 ORA-00904, ORA-01400）
- 修改：`loki_fetcher.py` line 169-268
- 效果：06b37820368c41d6ab2156592c778fcc 拉取了20行（接近21行）✅

#### 支持多种数据库（00:54）

用户指出：ORA-xxxxx是Oracle特有的，其他医院换数据库就识别不到了

- 增加支持：MySQL (Error 1054), PostgreSQL (ERROR: xxx), SQL Server (Msg 207)
- 增加通用SQL错误类型：DUPLICATE_KEY, FOREIGN_KEY, NOT_NULL, CONSTRAINT等
- 修改：`loki_fetcher.py` line 195-240

### 4. 四级分组优化 ✅（部分完成）

#### 用户需求（00:59）

用户发现：

1. 0e23dd93ce484aa0a952e81ffbb04dff - 调用方是winning-winex-ipt-charting-pbc（护理文书）
2. 3460f17311ff4438a1b968c431eb3438 - 调用方是winning-winex-ipt-pbc（医生站）
3. 这些是其他服务调用产生的异常，对当前服务（护士站）影响不大

用户建议：在分组时加入"调用方"信息

#### 实施方案：四级分组

- 按 `category:api_entry:caller_service:error_signature` 四级分组
- `caller_service`：从线程名提取调用方服务
  - `winning-winex-ipt-charting-pbc_Jetty-Worker` → `winning-winex-ipt-charting-pbc`
  - `Jetty-Worker_xxx` → `SELF`（本服务）
  - `exe-xxx`, `enc-xxx` → `ASYNC`（异步任务）
  - `rpc-exec-xxx` → `RPC`
- 修改：`loki_fetcher.py` line 169-330
- 效果：医生站的异常拉取了343行完整链路，护理文书的异常只有8行 ✅

### 5. 发现的问题 ❌（未完成）

#### 问题1：慢接口数量统计错误

- 用户指出：慢接口固定拉Top 10，为什么说拉了24个？
- 原因：我统计的是digest中所有慢接口（24个），而不是第二阶段拉取的数量（10个）
- 实际：第二阶段拉取 10个慢接口 + 20个异常分类 = 30个trace

#### 问题2：报告中看不到新功能 ❌

用户指出：新的报告和老的没区别，看不到异常级别、服务名、线程等信息

**根本原因**：

- 我只修改了 `loki_fetcher.py`（用四级分组选择代表trace）
- 但没有修改 `preprocess.py`（还是用旧的三级分组分析）
- 也没有修改 `generate_html_report_v2.py`（没有显示caller_service）

**数据流**：

1. loki_fetcher.py：拉取日志 → 写入log文件
2. preprocess.py：读取log文件 → 分析 → 生成digest
3. generate_html_report_v2.py：读取digest → 生成HTML报告

**问题**：

- loki_fetcher.py用四级分组选择代表trace ✅
- preprocess.py还是用旧的三级分组 ❌
- generate_html_report_v2.py没有显示caller_service ❌

## 待办事项（明天继续）

### 高优先级

1. **修改preprocess.py**：

   - 提取caller_service（从线程名）
   - 按四级分组：`category:api_entry:caller_service:error_signature`
   - 在error_line中保存caller_service和thread信息
   - 已完成：在trace_logs中保存thread信息
2. **修改generate_html_report_v2.py**：

   - 在"详细异常分析"中显示caller_service
   - 显示线程信息
   - 区分本服务异常 vs 其他服务调用产生的异常
3. **验证完整效果**：

   - 拉取最新日志
   - 验证报告中能看到caller_service、线程信息
   - 验证四级分组的效果

### 中优先级

4. 多样本迭代优化异常分类
5. 建立"其他异常"兜底类别
6. 从trace的其他日志中提取更多上下文

## 关键技术细节

### 修改的文件

1. `D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\loki_fetcher.py`

   - 三级分组 → 四级分组
   - 支持多种数据库错误码
   - 提取caller_service
2. `D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py`

   - 慢接口优化（每个取1个）
   - 异常影响级别分析
   - 日志质量统计
   - 在trace_logs中保存thread信息（已完成）
3. `D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\generate_html_report_v2.py`

   - 影响级别显示
   - 日志质量分析章节

### 四级分组逻辑（loki_fetcher.py）

```python
def extract_caller_service(line: str) -> str:
    """从线程名提取调用方服务"""
    # 跨服务调用：winning-winex-xxx_Jetty-Worker
    service_match = re.search(r'^(winning-winex-[a-z0-9-]+)_Jetty-Worker', thread)
    if service_match:
        return service_match.group(1)
  
    # 本服务调用：Jetty-Worker_xxx
    if thread.startswith('Jetty-Worker_'):
        return 'SELF'
  
    # 异步任务：exe-xxx, enc-xxx
    if re.match(r'^(exe|enc)-\d+$', thread):
        return 'ASYNC'
  
    # RPC调用：rpc-exec-xxx
    if thread.startswith('rpc-exec-'):
        return 'RPC'
  
    return 'UNKNOWN'

# 四级分组键
group_key = f"{matched_category}:{api_path}:{caller_service}:{error_sig}"
```

### 多数据库支持

```python
def extract_error_signature(line: str, category: str) -> str:
    if category == 'sql_error':
        # Oracle: ORA-00904
        ora_match = re.search(r'(ORA-\d+)', line)
        if ora_match:
            return ora_match.group(1)
      
        # MySQL: Error 1054
        mysql_match = re.search(r'Error\s+(\d+)', line, re.IGNORECASE)
        if mysql_match:
            return f'MySQL-{mysql_match.group(1)}'
      
        # PostgreSQL, SQL Server...
      
        # 通用SQL错误类型
        if 'duplicate' in line_lower or '重复' in line:
            return 'DUPLICATE_KEY'
        # ...
```

## 验证结果

### 最新生产日志（00:55~01:05）

- 总日志数：25,047
- ERROR：247
- WARN：17,231
- 慢接口：24个（digest中所有慢接口）
- 异常分类：20类
- 第二阶段拉取：10个慢接口 + 20个异常分类 = 30个trace
- 实际拉取完整链路：51个trace（有些trace既是慢接口又是异常代表）

### 四级分组效果

- 医生站（winning-winex-ipt-pbc）：343行完整链路 ✅
- 护理文书（winning-winex-ipt-charting-pbc）：8行（只有ERROR）✅
- 说明四级分组生效，不同服务的异常被正确分组

## 当前状态

### 已完成

- loki_fetcher.py：四级分组 ✅
- preprocess.py：部分修改（在trace_logs中保存thread信息）✅

### 未完成

- preprocess.py：提取caller_service，按四级分组 ❌
- generate_html_report_v2.py：显示caller_service、线程信息 ❌

### 用户反馈

- 报告中看不到新功能（caller_service、线程信息）
- 需要明天继续完善

## 下一步计划

1. 修改preprocess.py的categorize_trace函数，提取caller_service
2. 修改preprocess.py的aggregate_errors函数，按四级分组
3. 修改generate_html_report_v2.py，显示caller_service和线程信息
4. 重新拉取日志，验证完整效果
5. 生成最终报告，确认用户能看到所有新功能

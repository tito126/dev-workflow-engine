# 日志分析整改说明

## 整改内容

### 1. 改进错误分类逻辑

- 添加业务错误分类（最高优先级）
- 提取错误的真正原因（不只是关键词）
- 移除 'null' 关键词，避免误判

### 2. 过滤无意义错误

- 添加 --skip-no-trace 参数，过滤没有 traceId 的错误
- 这些错误通常是噪音（如 cookie 异常、认证过期等）

### 3. 错误详情展示

- 在报告中展示 error_reason（真正的错误原因）
- 展示操作人、具体参数等关键信息

### 4. 慢接口分析集成

- 在 preprocess.py 中集成 slow_interface_analyzer
- 在报告中展示调用链分析和瓶颈

## 具体修改

### preprocess.py

1. 添加 `extract_error_reason()` 函数
2. 改进 `categorize_error()` 函数
3. 添加 `--skip-no-trace` 参数
4. 集成慢接口深度分析

### generate_html_report_v2.py

1. 展示 error_reason
2. 展示慢接口的调用链分析
3. 展示瓶颈和优化建议

## 测试用例

### 用户提到的问题

1. **traceId: 12299d550a044038bf50c54af6d524dc**

   - 应该识别为：业务逻辑错误
   - 原因：批次冻结失败的药品库存：[]，操作人是：黄丽(440543600136155141)
2. **无 traceId 的噪音**

   - "处理soid值异常,当前cookie(winning_soid)值:null"
   - "认证过期,请重新刷新"
   - "initForceContextData"
   - 应该被过滤掉（使用 --skip-no-trace）
3. **traceId: C1EAF8C857A5FC2407A263124EB88DB3**

   - 应该识别为：业务逻辑错误（标签算法问题）
   - 不应该是：认证/权限问题
4. **traceId: 8eb56014bb8e40e0bd1d3ef65e17c7a2**

   - 应该识别为：业务逻辑错误
   - 原因：执行Fhir消息处理事件399202393，buildData失败
5. **慢接口分析**

   - 应该展示 traceId
   - 应该展示慢在什么地方（调用链分析）
   - 应该展示优化建议

## 实施计划

由于当前上下文较大，建议：

1. 创建新的优化版本文件
2. 测试验证
3. 替换旧版本

或者：

1. 直接修改关键函数
2. 增量测试

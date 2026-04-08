# 日志巡检工具 - 更新日志

## [2.0.0] - 2026-03-09

### 🎉 重大更新

#### 错误分类中文化和细化
- ✅ 所有错误分类改为中文名称（空指针异常、认证/权限问题等）
- ✅ 新增分类：插件配置问题、JSON解析错误、文件不存在等
- ✅ 每个分类都有具体的优化建议
- ✅ 消除了"Other"这种模糊分类

#### 统计逻辑优化
- ✅ 按 traceId 去重，避免重复统计
- ✅ 统计数量更加准确
- ✅ 支持没有 traceId 的日志

#### traceId 过滤功能（新增）
- ✅ 添加 `--filter-by-error-trace` 参数
- ✅ 两遍扫描：先找 ERROR/WARN 的 traceId，再过滤
- ✅ 只分析有问题的 traceId，保留完整上下文
- ✅ 解决 tool_api_fetcher 和 loki_fetcher 的对齐问题

#### 报告生成优化
- ✅ 新增 `generate_html_report_v2.py`
- ✅ 错误分类表格显示中文名称和优化建议
- ✅ 错误详情显示匹配的关键词
- ✅ 美观的可视化展示

### 📝 新增文件

- `generate_html_report_v2.py` - 优化后的报告生成器
- `ENHANCEMENT_PLAN.md` - 完整的增强方案文档
- `ALIGNMENT_AND_OPTIMIZATION.md` - 对齐和优化方案
- `OPTIMIZATION_SUMMARY.md` - 第一阶段总结
- `STAGE2_SUMMARY.md` - 第二阶段总结
- `test_optimization.py` - 测试脚本

### 🔧 修改文件

- `preprocess.py` - 核心分析逻辑
  - 更新 ERROR_CATEGORIES（中文化 + 细化）
  - 改进 categorize_error() 函数
  - 添加 traceId 去重逻辑
  - 新增 extract_error_trace_ids() 函数
  - 新增 process_file_with_filter() 函数
  - 添加 --filter-by-error-trace 参数

- `log_inspect_main.py` - 统一入口
  - 修改为使用 generate_html_report_v2.py

### 📊 效果对比

**优化前**:
```
异常统计：
- NullPointerException: 654
- Other: 3,272  ← 不清楚是什么
```

**优化后**:
```
异常统计：
- 空指针异常: 654 (11.2%)
  💡 检查对象是否为空，添加空值校验
  
- 认证/权限问题: 1,794 (30.7%)
  💡 检查token是否过期，确认用户权限配置
  
- 其他异常: 184 (3.1%)
  💡 需要查看详细日志进行分析
```

### 🚀 使用方式

#### 标准模式（分析所有日志）
```bash
python preprocess.py logs.log -o digest.json
```

#### 过滤模式（只分析有问题的 traceId）
```bash
python preprocess.py all_logs.log \
  --filter-by-error-trace \
  -o digest.json
```

### 🎯 下一步计划

- [ ] loki_fetcher 两阶段拉取（--with-context）
- [ ] 慢接口深度分析器
- [ ] 报告展示调用链和瓶颈
- [ ] 反馈收集功能

---

## [1.0.0] - 2026-03-06

### 初始版本

- ✅ K8s 环境支持（Loki）
- ✅ 传统服务器支持（工具组 API）
- ✅ Feishu 机器人集成
- ✅ 多集群选择
- ✅ 自然语言解析
- ✅ HTML 报告生成

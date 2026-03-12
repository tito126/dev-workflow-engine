# 日志巡检代码恢复计划

## 数据结构（从 logs_20260312_145058_默认集群_digest.json 反推）

### error 结构
```json
{
  "category": "标签配置问题",
  "class": "c.w.a.e.i.t.i.AutoTagAlgorithmServiceImpl",
  "api_entry": "/api/v1/encounter_inpatient/encounter_tag_data/refresh",
  "caller_service": "winning-winex-ipt-charting-pbc",
  "impact_level": "high",
  "count": 102,
  "samples": [
    {
      "trace_id": "00948907f36b457d95b595544423bcc9",
      "caller_service": "winning-winex-ipt-charting-pbc",
      "thread": "winning-winex-ipt-charting-pbc_Jetty-Worker_8080-Thread-611",
      "content": "没有获取到远程服务",
      ...
    }
  ]
}
```

### slow_api 结构
```json
{
  "api_path": "/api/v1/app_finance_fee_nurse/inpatient_bill/bill_by_encounter_id",
  "count": 56,
  "max_ms": 28188,
  "avg_ms": 10196,
  "representative_trace_id": "c6ac9bc837774a638ab31fc25baa9eb5",
  "representative_trace_logs": [...],  // 完整调用链
  "analysis": {
    "total_time": 28188,
    "steps": [...],
    "bottleneck": {...}
  }
}
```

## 恢复步骤

### 步骤1：恢复 generate_html_report_v2.py（最高优先级）
1. 恢复慢接口详情渲染（显示 representative_trace_logs 和 analysis）
2. 恢复 error 详情渲染（显示 caller_service、thread、impact_level）

### 步骤2：恢复 preprocess.py（高优先级）
1. 添加 extract_caller_service_from_thread 函数
2. 修改 categorize_trace 提取 caller_service
3. 修改 aggregate_errors 使用四级分组键
4. 添加代表trace优先逻辑

### 步骤3：恢复 loki_fetcher.py（中优先级）
1. 重写 extract_error_representatives（按 root_class 分组）
2. 写入代表trace列表到日志文件头部

### 步骤4：恢复 log_inspect_main.py（低优先级）
1. 去掉 capture_output=True
2. max-context-traces=100
3. 记录拉取时间

## 开始执行

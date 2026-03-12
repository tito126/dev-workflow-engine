# 日志巡检工具 - 快速上手（新session用）

## 当前状态（2026-03-11 23:47）

### 最新完成
✅ 4个高优先级优化全部上线：
1. 慢接口优化（每个取最慢的1个）
2. 异常分类代表trace拉完整链路
3. 异常影响级别分析（🔴高/🟡中/🟢低）
4. 日志质量分析章节

### 最新报告
- 文件：`C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_20260311_234639_默认集群_report.html`
- 时间：2026-03-11 23:36~23:46（最近10分钟）
- 医院：乐山市人民医院 - 病区护士站
- 数据：ERROR 179, WARN 22147, 慢接口 22

## 快速命令

### 拉取最新日志（乐山）
```bash
python "D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\log_inspect_main.py" \
  --hospital "乐山市人民医院" \
  --service "病区护士站" \
  --start "2026-03-12 00:00" \
  --end "2026-03-12 00:10"
```

### 拉取最新日志（桐乡）
```bash
python "D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\log_inspect_main.py" \
  --hospital "桐乡市第一人民医院" \
  --service "病区护士站" \
  --cluster "第二集群" \
  --start "2026-03-12 00:00" \
  --end "2026-03-12 00:10"
```

### 手动分析已有日志
```bash
python "D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py" \
  "C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_xxx.log" \
  -o "C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_xxx_analyzed" \
  -t 1000 \
  --service-name "winning-winex-ipt-ward-pbc"
```

### 生成HTML报告
```bash
python "D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\generate_html_report_v2.py" \
  "C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_xxx_analyzed" \
  "C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_xxx_report.html" \
  "乐山市人民医院" \
  "病区护士站" \
  "2026-03-12 00:00~00:10" \
  "C:\Users\pc\.openclaw\workspace\skills\log-inspect\logs_xxx.log"
```

## 待办事项（按优先级）

### 高优先级（已完成）
- [x] 慢接口优化
- [x] 异常分类代表trace拉完整链路
- [x] 异常影响级别分析
- [x] 日志质量分析章节

### 中优先级（下一步）
- [ ] 多样本迭代优化异常分类
- [ ] 建立"其他异常"兜底类别
- [ ] 从trace的其他日志中提取更多上下文
- [ ] 增加"来源类型"字段

### 长期优化
- [ ] 分类规则配置化
- [ ] 日志质量评分机制

## 关键文件位置

### 代码（全局目录）
- `D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\`
  - `log_inspect_main.py` - 统一入口脚本
  - `preprocess.py` - 日志分析核心
  - `generate_html_report_v2.py` - 报告生成
  - `loki_fetcher.py` - Loki日志拉取

### 输出（workspace）
- `C:\Users\pc\.openclaw\workspace\skills\log-inspect\`
  - `logs_*.log` - 原始日志
  - `logs_*_analyzed` - 分析结果（JSON）
  - `logs_*_report.html` - HTML报告

### 配置
- `D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\config.yaml`
  - 医院配置
  - Grafana连接信息
  - 服务映射

## 端口转发

### 乐山
```bash
# 需要用户手动打开
127.0.0.1:14828 -> Grafana
```

### 桐乡
```bash
# 需要用户手动打开
127.0.0.1:16291 -> Grafana
```

## 常见问题

### 1. gbk编码错误
- **现象**：`'gbk' codec can't encode character '\U0001f4c4'`
- **原因**：emoji在Windows控制台输出
- **影响**：不影响功能，报告已正常生成
- **解决**：忽略即可

### 2. 时间解析错误
- **现象**：时间范围解析为 01:00 ~ 00:00
- **原因**：自然语言解析失败
- **解决**：使用具体时间 `--start "2026-03-12 00:00" --end "2026-03-12 00:10"`

### 3. 端口连接失败
- **现象**：`连接失败: Connection refused`
- **原因**：端口转发未打开
- **解决**：提醒用户打开端口转发

## 下一步建议

1. **查看最新报告**：
   - 打开 `logs_20260311_234639_默认集群_report.html`
   - 验证4个高优先级优化的效果
   - 查看日志质量分析章节

2. **根据报告决定下一步**：
   - 如果"其他异常"占比高 → 完善分类规则
   - 如果日志质量问题严重 → 与研发沟通改进
   - 如果影响级别分布不合理 → 调整判断逻辑

3. **多样本验证**：
   - 拉取不同时间段的日志
   - 拉取不同医院的日志
   - 验证分类规则的通用性

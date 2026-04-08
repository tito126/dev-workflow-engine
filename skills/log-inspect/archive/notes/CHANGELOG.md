# Log Inspection Skill - 更新说明

## 版本: 2026-03-06

### 重要修复

#### 🐛 修复日志解析 Bug (Critical)

**问题**: preprocess.py 无法正确解析工具组 API 返回的日志格式，导致所有 ERROR 和 WARN 被漏掉。

**影响**: 
- 所有使用工具组 API 拉取日志的环境
- 可能影响飞书等传统服务器部署的医院

**修复内容**:
1. 更新 `LOG_PATTERN` 正则表达式，支持多个空字段
2. 重写 `parse_log_line()` 函数，使用动态解析逻辑
3. 基于时间戳位置推断其他字段，更加健壮

**修复效果**:
- 修复前: ERROR: 0, WARN: 0
- 修复后: ERROR: 5,844, WARN: 103,853

### 新功能

#### ✨ 工具组 API 支持

**新增文件**:
- `tool_api_fetcher.py` - 工具组 API 日志拉取器
- `TOOL_API_WORKFLOW.md` - 完整工作流程文档
- `PREPROCESS_BUG_FIX.md` - Bug 修复详细记录

**集成**:
- `log_inspect_main.py` 新增 `_fetch_from_tool_api()` 方法
- `environments.json` 支持 `tool_api` 类型环境

**功能**:
- 通过工具组 API 拉取传统服务器日志
- 自动下载、解压、合并多节点日志
- 无需开端口，直接通过 API 访问

### 配置示例

```json
{
  "测试医院": {
    "name": "测试医院（工具组测试环境）",
    "type": "tool_api",
    "description": "通过工具组 API 拉取日志，无需开端口",
    "toolApi": {
      "baseUrl": "http://172.16.9.87:8089",
      "appId": "9380",
      "envId": "14e48a6c43de4deeb42d1a3d4b2a2d7e",
      "nodeId": "1e211db4638244edbdb606da5c3107ac"
    },
    "services": {
      "病区护士站": "winning-winex-ipt-ward-pbc"
    }
  }
}
```

### 使用方法

```bash
# 自然语言方式
python log_inspect_main.py "分析测试医院病区护士站今天上午8-10点的日志"

# 参数方式
python log_inspect_main.py \
  --hospital "测试医院" \
  --service "病区护士站" \
  --start "2026-03-06 08:00:00" \
  --end "2026-03-06 10:00:00"
```

### 测试验证

- ✅ 工具组 API 日志拉取
- ✅ 日志解析（支持多种格式）
- ✅ 错误分类统计
- ✅ 慢接口识别
- ✅ HTML 报告生成
- ✅ 完整端到端流程

### 兼容性

- ✅ K8s 环境（Grafana/Loki）
- ✅ 传统服务器（工具组 API）
- ✅ 多种日志格式

### 文档

- `README.md` - 使用说明
- `TOOL_API_WORKFLOW.md` - 工具组 API 工作流程
- `PREPROCESS_BUG_FIX.md` - Bug 修复记录
- `INTEGRATION_SUMMARY.md` - 集成总结

### 后续计划

- [ ] 集成工具组 Skill（连接现场医院）
- [ ] 实现动态查询 envId 和 nodeId
- [ ] 支持多节点日志拉取
- [ ] 优化大文件处理性能

### 贡献者

- 第别 - 发现并报告 preprocess.py bug
- Kiro - 修复 bug 并集成工具组 API

---

**重要提示**: 如果你之前使用过 log-inspect skill 分析工具组 API 的日志，请重新分析以获取正确的结果。

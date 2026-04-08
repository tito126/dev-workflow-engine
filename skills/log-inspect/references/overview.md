# 日志巡检 Skill (Log Inspect)

智能日志分析工具，支持 K8s 和传统服务器环境，自动生成巡检报告。

## ✨ 特性

- 🔍 **智能解析**：支持自然语言查询（"分析昨天上午8-10点的日志"）
- 🎯 **多环境支持**：K8s (Loki) + 传统服务器（工具组 API）
- 📊 **可视化报告**：自动生成 HTML 格式巡检报告
- 🚀 **一键执行**：统一入口脚本，封装完整流程
- 💬 **飞书集成**：支持推送报告到飞书群

## 🚀 快速开始

### 安装

将此 skill 复制到你的 OpenClaw skills 目录：

```bash
# Windows
cp -r log-inspect %USERPROFILE%\.openclaw\skills\

# Linux/Mac
cp -r log-inspect ~/.openclaw/skills/
```

### 配置环境

编辑 `config/environments.json`，添加你的医院/项目配置：

```json
{
  "你的医院名称": {
    "name": "完整名称",
    "type": "k8s",
    "grafana": {
      "url": "http://your-grafana:3000",
      "datasource_id": 1
    },
    "services": {
      "服务名称": "app-label-name"
    }
  }
}
```

### 使用

```bash
# 自然语言查询
python log_inspect_main.py "帮我分析XX医院XX服务今天上午8-10点的日志"

# 指定参数
python log_inspect_main.py \
  --hospital 医院名称 \
  --service 服务名称 \
  --start "2026-03-09 08:00" \
  --end "2026-03-09 10:00"

# 推送到飞书
python log_inspect_main.py "分析昨天的日志" --push
```

## 📖 详细文档

查看 [SKILL.md](SKILL.md) 了解完整功能和高级用法。

## 🛠️ 依赖

- Python 3.7+
- requests
- 可选：OpenClaw (用于飞书推送)

## 📝 输出示例

- **digest.json**：结构化分析数据
- **report.html**：可视化巡检报告
- 包含：错误统计、慢接口、TraceID、优化建议

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可

MIT License

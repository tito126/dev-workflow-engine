# 工具组 API 日志巡检工作流程

## 概述

本文档描述了通过工具组 API 进行日志巡检的完整工作流程，适用于传统服务器部署的医院环境。

## 架构说明

### 当前实现（测试环境）

```
用户请求 → log_inspect_main.py → tool_api_fetcher.py → 工具组 API
                                                           ↓
                                                    下载日志压缩包
                                                           ↓
                                                    解压 + 合并日志
                                                           ↓
                                                    返回统一日志文件
                                                           ↓
                                    preprocess.py → 分析日志 → 生成报告
```

### 未来实现（现场医院）

```
用户请求 → log_inspect_main.py → 工具组 Skill（连接现场）
                                        ↓
                                  查询接口获取 envId、nodeId
                                        ↓
                                  调用 getServiceLogs API
                                        ↓
                                  tool_api_fetcher.py → 下载 + 处理
                                        ↓
                                  返回统一日志文件
                                        ↓
                                  分析 + 生成报告
```

## API 接口说明

### 1. 查询环境和节点信息（待实现）

**用途**: 获取指定医院的 envId 和 nodeId

**接口**: 待工具组提供

**参数**:
- `hospitalId`: 医院标识
- `appId`: 应用 ID
- 其他待定参数

**返回**:
```json
{
  "code": 20000,
  "message": "操作成功",
  "data": {
    "envId": "14e48a6c43de4deeb42d1a3d4b2a2d7e",
    "nodeId": "1e211db4638244edbdb606da5c3107ac"
  },
  "success": true
}
```

### 2. 获取服务日志

**接口**: `/api/v1/wincode/faultlocation/getServiceLogs`

**方法**: POST

**参数**:
```json
{
  "appId": "9380",
  "envId": "14e48a6c43de4deeb42d1a3d4b2a2d7e",
  "programName": "winning-winex-ipt-ward-pbc",
  "nodeId": "1e211db4638244edbdb606da5c3107ac",
  "startTime": "2026-03-06 12:00:00"
}
```

**返回**:
```json
{
  "code": 20000,
  "message": "操作成功",
  "data": "172.16.9.87:8089/cluster/action/copfile/localDown?filepath=...",
  "success": true
}
```

**说明**:
- `data` 字段返回的是日志下载地址（相对路径，需要添加 `http://` 前缀）
- 下载的文件是 zip 压缩包，包含多个节点的日志文件
- 日志文件可能是 `.log` 或 `.gz` 格式

## 环境配置

### 测试医院配置示例

在 `config/environments.json` 中添加：

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

### 现场医院配置示例（未来）

```json
{
  "某某医院": {
    "name": "某某医院",
    "type": "tool_api",
    "description": "通过工具组 API 拉取日志",
    "toolApi": {
      "baseUrl": "http://工具组API地址",
      "appId": "应用ID",
      "hospitalId": "医院标识",
      "queryEnvUrl": "/api/v1/query/env"
    },
    "services": {
      "病区护士站": "winning-winex-ipt-ward-pbc",
      "门诊医生站": "winning-winex-opd-doctor"
    }
  }
}
```

## 使用方法

### 命令行方式

```bash
# 测试医院（已配置 envId 和 nodeId）
python log_inspect_main.py "分析测试医院病区护士站今天上午8-10点的日志"

# 或使用参数方式
python log_inspect_main.py \
  --hospital "测试医院" \
  --service "病区护士站" \
  --start "2026-03-06 08:00:00" \
  --end "2026-03-06 10:00:00"
```

### 自然语言方式

```python
from log_inspect_main import LogInspector

inspector = LogInspector()

# 解析自然语言需求
params = inspector.parse_natural_language("分析测试医院病区护士站今天上午8-10点的日志")

# 执行完整流程
inspector.run(
    hospital=params['hospital'],
    service=params['service'],
    start_time=params['start_time'],
    end_time=params['end_time']
)
```

## 工作流程详解

### 1. 日志拉取阶段

**模块**: `tool_api_fetcher.py`

**步骤**:
1. 调用 API 获取下载地址
2. 下载日志压缩包（zip 格式）
3. 解压日志文件（支持 .log 和 .gz）
4. 合并多个节点的日志文件
5. 清理临时文件
6. 返回统一的日志文件路径

**输出**: `logs_YYYYMMDD_HHMMSS_程序名称.log`

### 2. 日志分析阶段

**模块**: `preprocess.py`

**步骤**:
1. 读取日志文件
2. 解析日志行（时间戳、级别、内容）
3. 统计错误和警告
4. 识别慢接口
5. 生成 digest.json

**输出**: `logs_YYYYMMDD_HHMMSS_程序名称_digest.json`

### 3. 报告生成阶段

**模块**: `generate_html_report.py`

**步骤**:
1. 读取 digest.json
2. 生成 HTML 报告
3. 包含统计图表和详细日志

**输出**: `logs_YYYYMMDD_HHMMSS_程序名称_report.html`

## 待实现功能

### 1. 动态查询 envId 和 nodeId

**需求**: 连接现场医院时，需要先查询环境和节点信息

**实现方案**:
```python
def _query_env_info(self, hospital_id: str, app_id: str) -> Dict:
    """查询环境和节点信息"""
    # 调用工具组提供的查询接口
    # 返回 envId 和 nodeId
    pass
```

### 2. 集成工具组 Skill

**需求**: 通过工具组的 Skill 连接现场医院

**实现方案**:
- 在 `log_inspect_main.py` 中集成工具组 Skill
- 使用 Skill 建立连接后，再调用 API

### 3. 多节点支持

**需求**: 支持查询多个节点的日志

**实现方案**:
- 修改 API 调用，支持传入多个 nodeId
- 或者循环调用 API，分别获取每个节点的日志
- 合并所有节点的日志

## 测试记录

### 2026-03-06 测试

**环境**: 工具组测试环境（http://172.16.9.87:8089）

**参数**:
- appId: "9380"
- envId: "14e48a6c43de4deeb42d1a3d4b2a2d7e"
- programName: "winning-winex-ipt-ward-pbc"
- nodeId: "1e211db4638244edbdb606da5c3107ac"
- startTime: "2026-03-06 12:00:00"

**结果**:
- ✅ API 调用成功
- ✅ 日志下载成功（52 MB）
- ✅ 解压成功（4 个文件：2 个 .log + 2 个 .gz）
- ✅ 合并成功
- ✅ 生成日志文件: `logs_20260306_150657_winning-winex-ipt-ward-pbc.log`

**日志文件结构**:
```
test-server-log.zip
├── 172.16.6.60/
│   ├── ms_all.log
│   └── ms_all.log.2026-03-06.0.gz
└── 172.16.7.106/
    ├── ms_all.log
    └── ms_all.log.2026-03-06.0.gz
```

## 注意事项

1. **时间格式**: API 要求的时间格式为 `YYYY-MM-DD HH:MM:SS`
2. **URL 处理**: API 返回的下载地址可能不包含协议前缀，需要添加 `http://`
3. **文件编码**: 日志文件使用 UTF-8 编码，解析时需要设置 `errors='ignore'` 避免编码错误
4. **临时文件**: 下载和解压过程会产生临时文件，处理完成后会自动清理
5. **网络超时**: 下载大文件时需要设置合理的超时时间（建议 300 秒）

## 相关文件

- `tool_api_fetcher.py`: 工具组 API 日志拉取器
- `log_inspect_main.py`: 日志巡检主入口
- `config/environments.json`: 环境配置文件
- `preprocess.py`: 日志分析脚本
- `generate_html_report.py`: 报告生成脚本

## 更新日志

- **2026-03-06**: 
  - 创建 `tool_api_fetcher.py` 模块
  - 在 `log_inspect_main.py` 中集成工具组 API 支持
  - 添加测试医院环境配置
  - 完成测试验证
  - 编写本文档

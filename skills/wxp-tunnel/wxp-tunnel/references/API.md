# Lockjaw 代理服务 API 文档

## 基础信息

- **服务地址**: `http://<host>:8765`
- **认证方式**: API Key (通过 `X-API-Key` 请求头)
- **IP 白名单**: 需要在配置的全局 IP 白名单内

## 认证

所有 API 请求需要在请求头中包含有效的 API Key：

```http
X-API-Key: your-api-key-here
```

## API 接口

### 1. 创建并启动通道

创建一个新的代理通道并自动启动。

**请求**

```http
POST /api/v1/lockjaw/channels HTTP/1.1
Host: <host>:8765
Content-Type: application/json
X-API-Key: your-api-key
```

**请求体**

```json
{
  "tenantName": "租户名称",
  "hostId": "主机标识",
  "userName": "用户名",
  "targetIp": "目标IP地址",
  "targetPort": 目标端口,
  "channelType": "TCP",
  "localPort": 本地监听端口(可选，不指定则自动分配),
  "description": "通道描述(可选)"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tenantName | String | 是 | 租户名称，用于多租户隔离 |
| hostId | String | 是 | 主机标识，同一租户+主机组合只会建立一个连接 |
| userName | String | 是 | 用户名 |
| targetIp | String | 是 | 目标服务器 IP 地址 |
| targetPort | Integer | 是 | 目标服务器端口 |
| channelType | String | 是 | 通道类型，目前支持 `TCP` |
| localPort | Integer | 否 | 本地监听端口，不指定则从 8000-9000 自动分配 |
| description | String | 否 | 通道描述信息 |

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "channelId": "租户名称-主机标识",
    "tenantName": "租户名称",
    "hostId": "主机标识",
    "userName": "用户名",
    "targetIp": "目标IP地址",
    "targetPort": 目标端口,
    "localPort": 本地监听端口,
    "channelType": "TCP",
    "status": "RUNNING",
    "description": "通道描述",
    "createTime": 1739200000000
  }
}
```

**cURL 示例**

```bash
curl -X POST http://localhost:8765/api/v1/lockjaw/channels \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-test-key-2024" \
  -d '{
    "tenantName": "txswsjkjjky",
    "hostId": "9-128-200-45-80",
    "userName": "admin",
    "targetIp": "9.128.200.45",
    "targetPort": 80,
    "channelType": "TCP"
  }'
```

---

### 2. 查询通道列表

获取所有通道的列表。

**请求**

```http
GET /api/v1/lockjaw/channels HTTP/1.1
Host: <host>:8765
X-API-Key: your-api-key
```

**响应**

```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "channelId": "xxxshsxhqdhyy-10-36-201-147-8089",
      "tenantName": "xxxshsxhqdhyy",
      "hostId": "10.36.201.147-8089",
      "userName": "8915",
      "channelType": "TCP",
      "localPort": 18003,
      "targetIp": "10.36.201.147",
      "targetPort": 8089,
      "status": "RUNNING",
      "description": "WXP Tunnel - 运维平台 (xxxshsxhqdhyy)",
      "createTime": 1772591664937,
      "lastUpdateTime": 1772591664937,
      "transferredBytes": 0,
      "connectionCount": 0,
      "errorCount": 0
    }
  ],
  "timestamp": 1772631259313
}
```

**cURL 示例**

```bash
curl http://localhost:8765/api/v1/lockjaw/channels \
  -H "X-API-Key: dev-test-key-2024"
```

---

### 3. 查询指定通道

根据通道 ID 查询通道详情。

**请求**

```http
GET /api/v1/lockjaw/channels/{channelId} HTTP/1.1
Host: <host>:8765
X-API-Key: your-api-key
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| channelId | String | 是 | 通道 ID |

**响应**

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "channelId": "shsxhqdhyyx-10-36-210-77-8089",
    "tenantName": "shsxhqdhyyx",
    "hostId": "10.36.210.77-8089",
    "userName": "8915",
    "channelType": "TCP",
    "localPort": 8015,
    "targetIp": "10.36.210.77",
    "targetPort": 8089,
    "status": "RUNNING",
    "description": "WXP Tunnel - 运维平台 (shsxhqdhyyx)",
    "createTime": 1772629905950,
    "lastUpdateTime": 1772629905950,
    "transferredBytes": 0,
    "connectionCount": 0,
    "errorCount": 0
  },
  "timestamp": 1772630774568
}
```

**cURL 示例**

```bash
curl http://localhost:8765/api/v1/lockjaw/channels/txswsjkjjky-9-128-200-45-80 \
  -H "X-API-Key: dev-test-key-2024"
```

---

### 4. 停止并删除通道

停止指定的通道并将其删除。

**请求**

```http
DELETE /api/v1/lockjaw/channels/{channelId} HTTP/1.1
Host: <host>:8765
X-API-Key: your-api-key
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| channelId | String | 是 | 通道 ID |

**响应**

```json
{
  "code": 200,
  "message": "通道已删除",
  "data": null
}
```

**cURL 示例**

```bash
curl -X DELETE http://localhost:8765/api/v1/lockjaw/channels/txswsjkjjky-9-128-200-45-80 \
  -H "X-API-Key: dev-test-key-2024"
```

---

### 5. 健康检查

检查服务健康状态。

**请求**

```http
GET /actuator/health HTTP/1.1
Host: <host>:8765
```

**响应**

```json
{
  "status": "UP"
}
```

**cURL 示例**

```bash
curl http://localhost:8765/actuator/health
```

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API Key 无效） |
| 403 | 禁止访问（IP 不在白名单内） |
| 404 | 资源不存在 |
| 409 | 资源冲突（如通道已存在） |
| 500 | 服务器内部错误 |

## 通道状态说明

| 状态 | 说明 |
|------|------|
| RUNNING | 运行中 |
| STOPPED | 已停止 |
| ERROR | 错误 |

## 错误响应格式

```json
{
  "code": 400,
  "message": "错误描述信息",
  "timestamp": "2026-02-10T16:00:00"
}
```

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8765"
API_KEY = "dev-test-key-2024"
HEADERS = {"X-API-Key": API_KEY}

# 创建通道
response = requests.post(
    f"{BASE_URL}/api/v1/lockjaw/channels",
    headers=HEADERS,
    json={
        "tenantName": "txswsjkjjky",
        "hostId": "9-128-200-45-80",
        "userName": "admin",
        "targetIp": "9.128.200.45",
        "targetPort": 80,
        "channelType": "TCP"
    }
)
print(response.json())

# 查询通道列表
response = requests.get(
    f"{BASE_URL}/api/v1/lockjaw/channels",
    headers=HEADERS
)
print(response.json())

# 删除通道
response = requests.delete(
    f"{BASE_URL}/api/v1/lockjaw/channels/txswsjkjjky-9-128-200-45-80",
    headers=HEADERS
)
print(response.json())
```

### Java 示例

```java
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

RestTemplate restTemplate = new RestTemplate();

String baseUrl = "http://localhost:8765";
String apiKey = "dev-test-key-2024";

// 设置请求头
HttpHeaders headers = new HttpHeaders();
headers.set("X-API-Key", apiKey);
headers.setContentType(MediaType.APPLICATION_JSON);

// 创建通道
String requestJson = """
    {
      "tenantName": "txswsjkjjky",
      "hostId": "9-128-200-45-80",
      "userName": "admin",
      "targetIp": "9.128.200.45",
      "targetPort": 80,
      "channelType": "TCP"
    }
    """;

HttpEntity<String> entity = new HttpEntity<>(requestJson, headers);
ResponseEntity<String> response = restTemplate.postForEntity(
    baseUrl + "/api/v1/lockjaw/channels",
    entity,
    String.class
);

System.out.println(response.getBody());
```

### JavaScript/Node.js 示例

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8765';
const API_KEY = 'dev-test-key-2024';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

// 创建通道
async function createChannel() {
  try {
    const response = await client.post('/api/v1/lockjaw/channels', {
      tenantName: 'txswsjkjjky',
      hostId: '9-128-200-45-80',
      userName: 'admin',
      targetIp: '9.128.200.45',
      targetPort: 80,
      channelType: 'TCP'
    });
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// 查询通道列表
async function getChannels() {
  try {
    const response = await client.get('/api/v1/lockjaw/channels');
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// 删除通道
async function deleteChannel(channelId) {
  try {
    const response = await client.delete(`/api/v1/lockjaw/channels/${channelId}`);
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}
```

## 注意事项

1. **多租户隔离**: 同一租户+主机组合只会建立一个连接，重复创建会返回错误
2. **端口池**: 本地监听端口从 8000-9000 范围内自动分配
3. **通道 ID**: 通道 ID 自动生成，格式为 `{tenantName}-{hostId}`
4. **NameNode 连接**: 服务启动时会自动连接到 NameNode，确保 NameNode 可访问

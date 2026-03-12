```mermaid
sequenceDiagram
    participant User as 👤 用户
    participant WeCom as 🏢 企微服务器
    participant Internet as 🌐 公网
    participant Server as 🖥️ 你的服务器<br/>(123.45.67.89)
    participant OpenClaw as 🦞 OpenClaw Gateway<br/>(端口 18789)
    participant Agent as 🤖 AI Agent

    Note over User,Agent: 场景：用户在企微发送消息

    User->>WeCom: 发送消息："帮我巡检日志"
    WeCom->>WeCom: 接收消息
    
    Note over WeCom,Server: 企微主动发起 HTTP POST 请求
    WeCom->>Internet: POST https://bot.example.com/webhook/wecom<br/>{msgtype: "text", content: "帮我巡检日志"}
    
    Internet->>Server: 请求到达服务器 (443端口)
    Server->>Server: Nginx 接收请求
    Server->>OpenClaw: 转发到 localhost:18789/webhook/wecom
    
    OpenClaw->>OpenClaw: 1. 验证签名<br/>2. 解析消息<br/>3. 提取用户ID和内容
    OpenClaw->>Agent: 转发消息给 Agent
    
    Agent->>Agent: 处理请求<br/>执行日志巡检
    Agent-->>OpenClaw: 返回结果
    
    OpenClaw->>WeCom: 调用企微 API 发送回复
    WeCom->>User: 推送结果消息
    
    Note over User,Agent: 用户收到巡检报告
```

# 图1: 企微 Webhook 完整流程

这个图展示了从用户发消息到收到回复的完整过程。

---

```mermaid
graph TB
    subgraph "🌐 公网"
        WeCom[企微服务器<br/>wecom.qq.com]
        Domain[你的域名<br/>bot.example.com]
    end
    
    subgraph "🖥️ 你的服务器 (123.45.67.89)"
        Nginx[Nginx<br/>端口 443/80<br/>SSL 证书]
        Gateway[OpenClaw Gateway<br/>端口 18789]
        Agent[AI Agent]
        Skills[日志巡检 Skill]
    end
    
    WeCom -->|HTTP POST| Domain
    Domain -->|DNS 解析| Nginx
    Nginx -->|反向代理| Gateway
    Gateway -->|调用| Agent
    Agent -->|执行| Skills
    
    Gateway -.->|调用 API 发送消息| WeCom
    
    style WeCom fill:#1aad19
    style Domain fill:#4a9eff
    style Nginx fill:#009639
    style Gateway fill:#ff6b6b
    style Agent fill:#ffd93d
```

# 图2: 服务器架构图

这个图展示了各个组件的关系和数据流向。

---

```mermaid
graph LR
    subgraph "方式A: 飞书长连接 (当前方案)"
        A1[你的电脑<br/>OpenClaw]
        A2[飞书服务器]
        A1 -->|主动连接<br/>WebSocket| A2
        A2 -.->|推送消息| A1
        
        Note1[✅ 不需要公网IP<br/>✅ 不需要 Webhook<br/>✅ 配置简单]
    end
    
    subgraph "方式B: 企微 Webhook (需要服务器)"
        B1[企微服务器]
        B2[你的服务器<br/>OpenClaw]
        B1 -->|HTTP POST<br/>Webhook| B2
        B2 -.->|调用API回复| B1
        
        Note2[❌ 需要公网IP<br/>❌ 需要配置 Webhook<br/>❌ 配置复杂]
    end
    
    style A1 fill:#95ec69
    style A2 fill:#95ec69
    style B1 fill:#ffd93d
    style B2 fill:#ffd93d
```

# 图3: 飞书 vs 企微 对比

这个图对比了两种方案的连接方式。

---

```mermaid
sequenceDiagram
    participant Admin as 👨‍💼 管理员
    participant WeCom as 🏢 企微管理后台
    participant Server as 🖥️ 你的服务器
    participant OpenClaw as 🦞 OpenClaw

    Note over Admin,OpenClaw: 场景：首次配置 Webhook

    Admin->>Server: 1. 启动 OpenClaw Gateway
    Server->>OpenClaw: openclaw gateway start
    OpenClaw->>OpenClaw: 监听端口 18789<br/>创建 /webhook/wecom 接口
    
    Admin->>WeCom: 2. 在企微后台配置
    Admin->>WeCom: 填入 Webhook URL:<br/>https://bot.example.com/webhook/wecom
    Admin->>WeCom: 填入 Token 和 EncodingAESKey
    Admin->>WeCom: 点击"保存"
    
    Note over WeCom,OpenClaw: 企微发起验证请求
    
    WeCom->>OpenClaw: GET /webhook/wecom?<br/>echostr=xxx&signature=yyy&timestamp=zzz
    OpenClaw->>OpenClaw: 验证签名
    OpenClaw->>WeCom: 返回 echostr
    
    WeCom->>WeCom: 验证成功 ✅
    WeCom->>Admin: 显示"配置成功"
    
    Note over Admin,OpenClaw: 配置完成，可以接收消息了
```

# 图4: Webhook 配置流程

这个图展示了如何配置企微 Webhook。

---

```mermaid
graph TB
    subgraph "Webhook URL 的组成"
        Protocol[协议<br/>https://]
        Domain[域名/IP<br/>bot.example.com]
        Port[端口<br/>:443]
        Path[路径<br/>/webhook/wecom]
        
        Protocol --> Domain
        Domain --> Port
        Port --> Path
        
        Full[完整 URL:<br/>https://bot.example.com:443/webhook/wecom]
    end
    
    subgraph "对应到服务器"
        DNS[DNS 解析]
        IP[服务器 IP<br/>123.45.67.89]
        Nginx[Nginx 监听<br/>443 端口]
        Proxy[反向代理到<br/>localhost:18789]
        Gateway[OpenClaw Gateway<br/>处理 /webhook/wecom]
        
        DNS --> IP
        IP --> Nginx
        Nginx --> Proxy
        Proxy --> Gateway
    end
    
    Full -.->|映射| DNS
    
    style Full fill:#4a9eff
    style Gateway fill:#ff6b6b
```

# 图5: Webhook URL 解析

这个图展示了 Webhook URL 的各个部分如何对应到服务器配置。

---

```mermaid
graph TB
    Start([用户问题:<br/>Webhook URL 怎么创建?])
    
    Q1{有公网服务器吗?}
    Start --> Q1
    
    Q1 -->|没有| NoServer[使用飞书长连接<br/>✅ 当前方案<br/>不需要 Webhook]
    Q1 -->|有| HasServer[可以配置企微 Webhook]
    
    HasServer --> Step1[1. 在服务器安装 OpenClaw]
    Step1 --> Step2[2. 启动 Gateway<br/>自动创建 /webhook/wecom 接口]
    Step2 --> Step3[3. 配置 Nginx 反向代理<br/>+ SSL 证书]
    Step3 --> Step4[4. 在企微后台填入<br/>Webhook URL]
    Step4 --> Done[✅ 配置完成]
    
    NoServer --> Happy[✅ 继续用飞书<br/>已经可以工作了]
    
    style Start fill:#4a9eff
    style NoServer fill:#95ec69
    style Happy fill:#95ec69
    style Done fill:#95ec69
```

# 图6: 决策流程

这个图帮助你理解什么时候需要 Webhook。


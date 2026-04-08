# Ideas Inbox

Use this file for ideas that are not yet formal projects.

## Idea Template

```md
### [I-YYYYMMDD-01] Idea title
- Created: YYYY-MM-DD HH:MM
- Related Project: none | <project name>
- Trigger: what led to the idea
- Idea: short description
- Potential Value: why it may matter
- Next Step: revisit / discuss / move to project / archive
- Status: open
```

## Open Ideas

### [I-20260319-01] 转写 skill：多源输入转成结构化文档
- Created: 2026-03-19 19:12
- Related Project: none
- Trigger: 需要接收视频、录音、会议纪要等输入，并转写成需要的文档
- Idea: 做一个转写 skill，能够接收会议录音、视频、纪要等素材，转成会议纪要、结构化摘要、行动项、专项上下文文档等输出
- Potential Value: 降低手工整理成本，让非结构化输入快速进入工作系统
- Next Step: 在后续某次每日总结中提醒回看，并在用户状态更清醒时先反问确认意图
- Status: open

### [I-20260319-02] 任务上下文机制：给 agent 持续喂上下文
- Created: 2026-03-19 19:12
- Related Project: none
- Trigger: 希望搭建一个任何任务都能给 agent 提供上下文的工作机制
- Idea: 建立统一上下文入口，允许从录音、录屏、会议纪要等来源提取信息，沉淀为 agent 可复用的任务上下文包
- Potential Value: 提高 agent 在复杂任务中的理解连续性，减少重复解释背景
- Next Step: 在后续某次每日总结中提醒回看，并在用户状态更清醒时先反问确认意图
- Status: open

### [I-20260319-03] Cherry Studio agent 壳对接多技能与工具
- Created: 2026-03-19 19:12
- Related Project: none
- Trigger: 想做一个 Cherry Studio agent 的壳，对接技能、MCP、工具、插件等
- Idea: 设计一个以 agent 为核心的壳层，统一对接不同技能、MCP、工具和插件，形成可扩展的工作入口
- Potential Value: 把不同能力统一封装，降低切换成本，便于后续扩展自动化工作流
- Next Step: 在后续某次每日总结中提醒回看，并在用户状态更清醒时先反问确认意图
- Status: open

### [I-20260319-04] 运维减负 skill：从高频问题识别到小范围治理闭环
- Created: 2026-03-19 22:13
- Related Project: none
- Trigger: 当前运维成本过高，值班人员每天焦头烂额、分身乏术，同质问题反复处理，且通常没有额外精力形成记录；2026-03-20 与领导沟通后，方向获得认可，但要求避免步子太大，优先从可落地切口切入
- Idea: 先不做大而全的运维知识库或完整 skill，而是先建立一个最小闭环：收集最近 1~2 个月的问题样本，识别高频高成本模块，区分 bug/历史重构遗留/需求改动破坏/环境配置/协作边界等问题类型；在此基础上只选 1 个模块，沉淀 2~3 条可执行的 review 或治理规则，验证是否能降低重复问题和运维成本
- Potential Value: 把“运维减负”从抽象方向收敛为可验证的小步快跑方案，先找到最值得动刀的模块和最可复制的 review/治理动作，降低重复劳动，提高重构延续性和跨部门协同效率
- Next Step: 第一步先收集最近 1~2 个月的问题样本，最少记录 `问题标题 / 所属模块 / 问题类型 / 是否重复` 四列；拿到样本后再一起判断高频模块，并决定是否转成正式专项或提醒事项
- Status: open

<!-- Add new ideas below this line -->

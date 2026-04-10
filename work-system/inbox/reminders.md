# Reminder Candidates

Use this file for reminders before they become a scheduled reminder or a tracked follow-up.

## Reminder Template

```md
### [R-YYYYMMDD-01] Reminder title
- Created: YYYY-MM-DD HH:MM
- Due: YYYY-MM-DD HH:MM | TBD
- Related Project: none | <project name>
- Reason: why this matters
- Status: pending
- Next Handling: schedule / follow manually / move to project / archive
```

## Open Reminders

### [R-20260319-01] 周日完成答辩PPT
- Created: 2026-03-19 16:44
- Due: 2026-03-22 18:00
- Related Project: none
- Reason: 本周日需要完成答辩 PPT，需提前开始准备材料，避免临近截止仓促整理。
- Status: pending
- Next Handling: schedule

### [R-20260319-02] 下周与产品沟通病区护士站专项细节
- Created: 2026-03-19 18:33
- Due: TBD（下周）
- Related Project: 病区护士站专项
- Reason: 与产品沟通病区护士站专项细节的时间已改到下周，需要下周继续跟进并在会前留出准备和对齐时间。
- Status: pending
- Next Handling: follow manually

### [R-20260406-01] 下周推进《病区护士（姚云）》高危代码修复清单
- Created: 2026-04-06 09:30
- Due: TBD
- Related Project: 病区护士高危问题治理
- Reason: 下周需要推进《病区护士（姚云）》高危代码修复清单，这项工作不应按一次性全修处理，而应先用 AI 做分类、聚类、批次拆分，并按长期跟踪台账持续维护，承接后续持续扫描新增问题。
- Status: in-progress
- Progress:
  - 2026-04-08: 已安排人完成一轮代码排查，发现很多记录不需要整改，属于误报或已处理
  - 后续需完善 `win-code-scanner` skill，优化扫描规则，避免重复扫描和误报
- Next Handling: follow manually（优先完善扫描规则，减少无效工作量）

### [R-20260406-02] 跟进主数据院端后台接口是否可封装前端接口
- Created: 2026-04-06 11:18
- Due: TBD
- Related Project: 病区护士相关事项
- Reason: 需确认主数据院端提供的后台接口是否可以进一步封装为前端接口，当前约定由姚云联系黄荣波沟通，后续需要跟进沟通结果与可行性判断。
- Status: pending
- Next Handling: follow manually

### [R-20260406-03] 跟进是否增加单独测试环境
- Created: 2026-04-06 11:18
- Due: TBD
- Related Project: 病区护士相关事项
- Reason: 需评估是否增加单独测试环境；如果 105 测试通过会到现场，担心存在兼容问题；如果 105 测试不通过，又会阻塞代码提交。当前约定由姚云联系李莺沟通，后续需要跟进结论与处理方案。
- Status: pending
- Next Handling: follow manually

### [R-20260410-01] 周末在家搭建微信集成“小龙虾”
- Created: 2026-04-10 14:55
- Due: TBD（本周末）
- Related Project: none
- Reason: 周末计划在家搭建微信集成“小龙虾”，为后续把微信消息直接记入 reminder 打通入口，减少从消息流转成待办记录的摩擦。
- Status: pending
- Next Handling: follow manually

### [R-20260410-02] 定位 ACP 子会话结果回传失败问题
- Created: 2026-04-10 19:21
- Due: TBD（本周内）
- Related Project: win-code-scanner
- Reason: 2026-04-10 实战发现 ACP child session 有扫描结果且已落盘，但主会话 completion event 收到的是空 result。根因在 OpenClaw ACP 回传链路，不是 opencode 本身。需要定位 relay 断点并修复。
- Status: pending
- Next Handling: 排查 OpenClaw ACP result relay 机制，确认是 gateway 层还是 session 层丢数据

### [R-20260410-03] 完善 win-code-scanner 人工反哺流程
- Created: 2026-04-10 19:21
- Due: TBD
- Related Project: win-code-scanner
- Reason: 第一阶段知识库增强框架已打通，但还缺最后一环：把人工复核结果自动沉淀为候选知识条目（enabled=false），减少手工整理成本。
- Status: pending
- Next Handling: 实现 extract_feedback_candidates.py 或等价功能
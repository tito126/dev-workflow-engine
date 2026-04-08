# 护士站 requirement-fit checkpoint 规范（2026-04-07）

## 1. 目标

这份规范用于填补护士站框架中“需求已讨论，但尚未达到可稳定编码、可稳定验收”的空档层。

它的作用不是替代需求分析，也不是替代最终 verification，而是作为进入 coding 前的硬闸门：

> 没有通过 requirement-fit checkpoint，就不应进入 implementer。

---

## 2. 它解决什么问题

当前框架里已经有：
- `brainstorming`：需求准入与澄清
- `verification`：最终验收

但实际链路中缺的，是一个编码前检查：
- implementer 是否已经拿到足够清晰、足够稳定的任务定义？
- verifier 未来是否有明确锚点可判断？

如果没有这层检查，就会出现：
- implementer 靠猜补空白
- review 事后猜 intent
- verification 只能判断像不像

---

## 3. 适用范围

优先适用于：
- UI / 前端需求
- 页面交互调整
- 显隐逻辑调整
- 参数映射变更
- 中轻量但容易因为描述模糊而返工的任务

对 Heavy 任务也适用，只是通常嵌在 planning / runtime 之前或之中。

---

## 4. checkpoint 必查项

## 4.1 通用项
- 目标问题是什么
- 目标场景是什么
- 不做什么（non-goals）
- 模块 / 页面 / 代码范围是否已知
- 成功标准是否可描述
- 验收时看什么现象

## 4.2 UI / 交互类任务专用项
- 页面：哪个页面 / 区域
- 控件：新增 / 移动 / 替换的是哪个控件
- 插入位置：放在什么位置
- 相邻关系：在谁前 / 在谁后 / 替换谁
- 场景限制：在哪些状态显示 / 不显示
- 交互约束：是否保留原交互
- 去重规则：旧入口是否保留
- 验收观察点：完成后页面应呈现什么结果

## 4.3 技术进入条件
- likely files 是否已知
- 是否还需要 locator
- validation 方法是否已知
- 是否存在必须先确认的风险点

---

## 5. 输出格式

建议固定输出：

### Requirement-fit checkpoint
- Task level:
- Route recommendation:
- Objective:
- Scene:
- In scope:
- Out of scope:
- Page / module:
- Control / object:
- Placement / relation:
- Visibility rule:
- Keep / remove old behavior:
- Acceptance checkpoints:
- Need locator first: yes/no
- Ready for coding: yes/no
- Missing prerequisite:

---

## 6. 放行规则

### 可放行到 coding
只有当以下条件全部成立：
- 目标行为可描述
- 页面 / 模块方向清楚
- 场景限制清楚
- 至少一个明确验收观察点存在
- implementer 不需要靠猜关键 UI / 参数 / 场景边界

### 不可放行
满足任一则不得进入 coding：
- 关键 UI 位置说不清
- 场景限制说不清
- 是否替换 / 去重旧行为说不清
- 验收观察点写不出来
- 代码范围仍完全未知且无 locator 安排

---

## 7. 与其他 Skill 的关系

## 7.1 与 `nurse-station-brainstorming`
- brainstorming 负责澄清问题
- checkpoint 负责判断是否已达到 coding-ready

## 7.2 与 `nurse-station-writing-plans`
- plan 只能建立在 checkpoint 已放行的基础上
- 若 checkpoint 未过，plan 只能先写 missing prerequisite

## 7.3 与 `nurse-station-review-gate`
- checkpoint 是 pre-code mini gate
- review-gate 是 post-implementation gate

## 7.4 与 `nurse-station-verification`
- verification 依赖 checkpoint 提供的验收锚点
- 若 checkpoint 没形成验收锚点，则 verification 默认不可判完成

---

## 8. 一句话执行纪律

后续护士站框架中的 coding 准入规则应改为：

> 没有 requirement-fit checkpoint，就没有稳定 coding；没有前置验收锚点，就没有可信 verification。 

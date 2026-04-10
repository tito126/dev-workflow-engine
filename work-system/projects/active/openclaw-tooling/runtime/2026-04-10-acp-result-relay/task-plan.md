# Task Plan

- Goal: 定位并修复“ACP child session 已产出结果，但主会话 completion/result 拿不到”的回传问题。
- Current phase: validated
- Runtime path: `work-system/projects/active/openclaw-tooling/runtime/2026-04-10-acp-result-relay/`

## Stage breakdown
1. 固化现象与关键证据
2. 检查 child session transcript、主会话事件与本地日志
3. 查 OpenClaw 文档与代码路径，定位 relay 断点
4. 形成问题判断与修复建议
5. 产出补丁并做正常 / gateway 重启场景验证

## Known facts
- child session `232633ae-bbda-4a85-aa20-e36a3cfd825b` 本地 transcript 已有结果
- 主会话收到的 completion event 为空结果或超时
- 问题更像 OpenClaw / ACP relay 链路问题，不是 opencode 未执行
- `pi-embedded-DWASRjxE.js` 已补上 transcript 磁盘 fallback
- 2026-04-11 已完成两类验证：正常 one-shot ACP 回传、spawn 后立即重启 gateway 的回传

## Decisions
- 先不猜，直接以 transcript、落盘产物、日志和代码为准
- 若 ACP 链路再次异常，按新规则立即中断并汇报
- 修复以“增加独立于 gateway RPC 的 transcript 磁盘结果来源”为主，不靠单纯延长等待时间掩盖问题

## Error log
- `openclaw gateway restart` 后短暂出现过 synthetic transcript repair 提示，但不影响最终回传验证结果

## Done definition
- 能明确说明断点更可能在 gateway、session relay、还是 completion 汇聚层
- 能给出可复现实证与下一步修复建议
- 已完成：问题定位、补丁固化、验证通过

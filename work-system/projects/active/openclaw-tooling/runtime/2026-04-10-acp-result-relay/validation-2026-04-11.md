# ACP Result Relay Validation - 2026-04-11

## Scope
验证 `pi-embedded-DWASRjxE.js` 中 ACP result relay 磁盘 fallback 补丁是否已在本机真实生效，并确认 `sessions_spawn runtime="acp" agentId="opencode" mode="run"` 不再出现“child 有结果但 parent 空回”的问题。

## Environment
- OpenClaw: `2026.4.5 (3e72c03)`
- OS: `Windows 10.0.26200`
- Node: `24.9.0`
- Agent: `executor`
- ACP target: `opencode`

## Scenario A: 正常 one-shot ACP 回传
### Spawn
- child session key: `agent:opencode:acp:02834858-a803-45f7-be05-6486d1383767`
- run id: `04fe5367-96fc-4854-a253-1f33d6d92460`
- stream log: `C:\Users\pc\.openclaw\agents\opencode\sessions\ce2507ce-b764-430e-ad6c-c0e089fa27e2.acp-stream.jsonl`
- transcript: `C:\Users\pc\.openclaw\agents\opencode\sessions\ce2507ce-b764-430e-ad6c-c0e089fa27e2.jsonl`

### Expected output
```text
ACP-RELAY-TEST-OK
child-visible-result
```

### Result
- stream log 已出现 `assistant_delta`
- child transcript 已写入同样 assistant 文本
- parent 成功看到明确 completion / progress 文本
- 结论：**正常回传通过**

## Scenario B: Spawn 后立即重启 gateway
### Spawn
- child session key: `agent:opencode:acp:68291ecb-e648-478c-890c-287fcdfd6511`
- run id: `50894643-75a5-4dbd-aacc-867bdea98877`
- stream log: `C:\Users\pc\.openclaw\agents\opencode\sessions\dcc9fc85-99ca-4f8b-8f2a-8a0e30014377.acp-stream.jsonl`
- transcript: `C:\Users\pc\.openclaw\agents\opencode\sessions\dcc9fc85-99ca-4f8b-8f2a-8a0e30014377.jsonl`

### Restart action
- 在 child 启动后执行：`openclaw gateway restart`

### Expected output
```text
ACP-RELAY-RESTART-TEST-OK
TOPLEVEL-COUNT=8
child-result-after-restart
```

### Result
- gateway 重启后，最终仍收到 child 输出
- stream log 中有 `assistant_delta`、`progress`、`done` 事件
- child transcript 与 stream log 内容一致
- 结论：**重启扰动下的结果回传通过**

## Overall conclusion
这处补丁已经通过本机真实验证，可判定为：
1. 能解决“child transcript 已有结果，但 parent 空 result / timeout / gateway closed”的核心问题
2. 正常路径行为未见异常
3. 至少在 `gateway restart` 扰动场景下，relay 已恢复可用

## Caveat
本次验证证明“结果已能稳定回传”，但没有额外加入埋点来确认每次实际命中的是哪一层 fallback。若后续要做更强证明，需要再加日志或临时 instrumentation。

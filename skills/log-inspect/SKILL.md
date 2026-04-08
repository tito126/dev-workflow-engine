---
name: log-inspect
description: Analyze microservice logs and produce inspection reports for hospital systems across K8s/Loki and traditional server environments. Use when the user asks to inspect logs, analyze ERROR/WARN or slow interfaces, pull logs for a hospital/service/time range, generate HTML inspection reports, or troubleshoot production incidents from log evidence.
---

# Log Inspect

Use this skill for log inspection work in hospital environments.

## Default workflow

Default to `log_inspect_main.py` first.

It is the preferred entry point when the user asks in natural language to:
- analyze logs for a hospital or service
- inspect a time range
- find ERROR / WARN patterns
- identify slow interfaces
- generate a report

Example:

```bash
python log_inspect_main.py "帮我分析桐乡病区护士站今天上午8-10点的日志"
```

## Core entry files

Keep these as the main execution path:
- `log_inspect_main.py` — unified entry
- `loki_fetcher.py` — Loki/K8s fetch path
- `tool_api_fetcher.py` — traditional server / tool API path
- `preprocess.py` — digest generation and grouping
- `generate_html_report_v2.py` — current HTML report generator
- `slow_interface_analyzer.py` — slow-interface analysis
- `two_stage_fetch.py` — representative-trace full-chain fetch flow
- `config/environments.json` — hospital and service mapping

## When to use which path

- If the user wants the standard end-to-end run, use `log_inspect_main.py`.
- If the environment is K8s / Loki, use the Loki route.
- If the environment is traditional server / tool group API, use the tool API route.
- If the task requires representative trace full-chain补强, use the two-stage flow.

## Important operating rules

- For `桐乡市卫生健康局`, ask which cluster to use before pulling logs.
- Prefer the current report path and current workflow; do not assume older scripts or notes are authoritative.
- Use archived files only as historical reference, not as the default operating path.

## Read these references as needed

- Read `references/overview.md` for general background and older usage notes.
- Read `archive/notes/TOOL_API_WORKFLOW.md` only when working on the traditional-server route.
- Read `archive/notes/LOG_INSPECT_WORKFLOW.md` only when you need historical workflow context.
- Read archived reports or digests only when the user asks for comparison, recovery, or historical verification.

## Directory intent

- root: active skill entry files only
- `references/`: lightweight docs worth reading when needed
- `scripts/dev/`: one-off helpers, checks, and dev utilities
- `archive/`: historical outputs, notes, and no-longer-primary materials

## Output expectation

Typical outputs are:
- digest JSON
- HTML inspection report
- structured findings on errors, slow interfaces, representative traces, and next-step suggestions

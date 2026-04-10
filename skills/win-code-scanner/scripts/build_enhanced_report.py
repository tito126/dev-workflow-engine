#!/usr/bin/env python3
"""
一键执行 win-code-scanner 的知识库增强后处理流水线。

流程：
1. 读取原始扫描 JSON
2. 使用 false-positive-kb.json 做增强标注
3. 输出 annotated JSON
4. 导出 Excel / Markdown 报告

示例：
    python scripts/build_enhanced_report.py scan-results.json --repo-name winning-demo --git-url http://example/repo --git-branch sr-next
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from annotate_scan_results import annotate_issue, load_issues as annotate_load_issues, load_json as annotate_load_json
from export_annotated_report import build_overview, export_markdown, export_xlsx, load_issues as export_load_issues, normalize_text, aggregate_rule_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="一键生成知识库增强版扫描报告")
    parser.add_argument("input_json", help="原始扫描结果 JSON")
    parser.add_argument("--kb", help="知识库 JSON 路径，默认 references/false-positive-kb.json")
    parser.add_argument("--output-dir", help="输出目录，默认与输入文件同目录")
    parser.add_argument("--base-name", help="输出文件基础名，默认使用输入文件名（不含扩展名）")
    parser.add_argument("--repo-name", default="code-scan", help="仓库名称")
    parser.add_argument("--git-url", default="", help="Git URL")
    parser.add_argument("--git-branch", default="", help="Git 分支")
    parser.add_argument("--annotated-json", help="增强后 JSON 输出路径")
    parser.add_argument("--xlsx-out", help="Excel 报告输出路径")
    parser.add_argument("--md-out", help="Markdown 报告输出路径")
    return parser


def load_kb(kb_path: Path) -> Dict[str, Any]:
    kb = annotate_load_json(kb_path)
    if not isinstance(kb, dict):
        raise ValueError("知识库文件必须是 JSON 对象")
    return kb


def default_output_paths(input_path: Path, output_dir: Path, base_name: str) -> Dict[str, Path]:
    return {
        "annotated_json": output_dir / f"{base_name}.annotated.json",
        "xlsx": output_dir / f"{base_name}.knowledge.xlsx",
        "md": output_dir / f"{base_name}.knowledge.md",
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input_json)
    if not input_path.exists():
        raise SystemExit(f"输入文件不存在: {input_path}")

    kb_path = Path(args.kb) if args.kb else Path(__file__).resolve().parents[1] / "references" / "false-positive-kb.json"
    if not kb_path.exists():
        raise SystemExit(f"知识库文件不存在: {kb_path}")

    output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = args.base_name or input_path.stem

    defaults = default_output_paths(input_path, output_dir, base_name)
    annotated_json_path = Path(args.annotated_json) if args.annotated_json else defaults["annotated_json"]
    xlsx_out = Path(args.xlsx_out) if args.xlsx_out else defaults["xlsx"]
    md_out = Path(args.md_out) if args.md_out else defaults["md"]

    payload = annotate_load_json(input_path)
    raw_issues = annotate_load_issues(payload)
    kb = load_kb(kb_path)
    entries = kb.get("entries", []) if isinstance(kb, dict) else []

    annotated_issues = [annotate_issue(issue, entries) for issue in raw_issues]
    annotated_payload: Dict[str, Any]
    if isinstance(payload, dict):
        annotated_payload = dict(payload)
        annotated_payload["issues"] = annotated_issues
        annotated_payload["kb_path"] = str(kb_path)
        annotated_payload["report_columns"] = kb.get("report_columns", [])
    else:
        annotated_payload = {
            "issues": annotated_issues,
            "kb_path": str(kb_path),
            "report_columns": kb.get("report_columns", []),
        }

    annotated_json_path.parent.mkdir(parents=True, exist_ok=True)
    annotated_json_path.write_text(json.dumps(annotated_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    issues_for_export, _ = export_load_issues(annotated_payload)
    overview = build_overview(args.repo_name, args.git_url, args.git_branch, issues_for_export)
    rule_rows = aggregate_rule_rows(issues_for_export)

    export_xlsx(xlsx_out, overview, rule_rows, issues_for_export)
    export_markdown(md_out, overview, rule_rows, issues_for_export)

    result = {
        "input_json": str(input_path),
        "kb": str(kb_path),
        "annotated_json": str(annotated_json_path),
        "xlsx_out": str(xlsx_out),
        "md_out": str(md_out),
        "repo_name": normalize_text(args.repo_name),
        "git_branch": normalize_text(args.git_branch),
        "total_issues": len(issues_for_export),
        "rule_rows": len(rule_rows),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

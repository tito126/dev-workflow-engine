#!/usr/bin/env python3
"""
对 win-code-scanner 的原始扫描结果进行知识库增强标注。

输入：
- 原始扫描 JSON（支持 {"issues": [...]} 或直接传列表）
- false-positive-kb.json

输出：
- 保留原始 issues 不变
- 为每条 issue 追加知识库增强字段：
  - kb_match_status
  - kb_action
  - kb_rule_id
  - kb_reason
  - kb_feature_summary
  - kb_confidence
  - kb_requires_human_review

示例：
    python scripts/annotate_scan_results.py scan.json --output annotated.json
    python scripts/annotate_scan_results.py scan.json --kb references/false-positive-kb.json --format text
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFAULT_COLUMNS = [
    "知识库匹配状态",
    "建议处理动作",
    "知识库规则ID",
    "知识库判断原因",
    "匹配特征摘要",
    "置信度",
    "是否需人工复核",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def lowered(value: Any) -> str:
    return normalize_text(value).lower()


def load_issues(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("issues"), list):
        return payload["issues"]
    if isinstance(payload, list):
        return payload
    raise ValueError("输入 JSON 必须是 issues 数组，或包含 issues 数组的对象")


def issue_file_path(issue: Dict[str, Any]) -> str:
    return normalize_text(issue.get("file") or issue.get("file_path") or issue.get("path"))


def issue_description(issue: Dict[str, Any]) -> str:
    return normalize_text(issue.get("description") or issue.get("issue_desc") or issue.get("message"))


def issue_code(issue: Dict[str, Any]) -> str:
    return normalize_text(issue.get("code_snippet") or issue.get("snippet") or issue.get("code"))


def issue_rule_code(issue: Dict[str, Any]) -> str:
    return normalize_text(issue.get("rule_code") or issue.get("rule") or issue.get("ruleId"))


def path_extension(path: str) -> str:
    return Path(path).suffix.lower()


def any_contains(haystack: str, needles: Iterable[str]) -> bool:
    values = [lowered(v) for v in needles if normalize_text(v)]
    if not values:
        return True
    target = lowered(haystack)
    return any(item in target for item in values)


def all_contains(haystack: str, needles: Iterable[str]) -> bool:
    values = [lowered(v) for v in needles if normalize_text(v)]
    if not values:
        return True
    target = lowered(haystack)
    return all(item in target for item in values)


def none_contains(haystack: str, needles: Iterable[str]) -> bool:
    values = [lowered(v) for v in needles if normalize_text(v)]
    if not values:
        return True
    target = lowered(haystack)
    return all(item not in target for item in values)


def regex_match_any(value: str, patterns: Iterable[str]) -> bool:
    patterns = [p for p in patterns if normalize_text(p)]
    if not patterns:
        return True
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def rule_code_match(issue_rule: str, entry_rule_codes: Iterable[str]) -> bool:
    codes = [normalize_text(v) for v in entry_rule_codes if normalize_text(v)]
    if not codes:
        return True
    return issue_rule in codes


def compute_match_score(issue: Dict[str, Any], entry: Dict[str, Any]) -> Tuple[bool, int, List[str]]:
    match = entry.get("match", {})
    file_path = issue_file_path(issue)
    extension = path_extension(file_path)
    description = issue_description(issue)
    code = issue_code(issue)
    rule_code = issue_rule_code(issue)

    if not rule_code_match(rule_code, entry.get("rule_codes", [])):
        return False, 0, []

    if not regex_match_any(file_path, match.get("file_path_regex", [])):
        return False, 0, []

    extensions = [lowered(v) for v in match.get("extensions", []) if normalize_text(v)]
    if extensions and lowered(extension) not in extensions:
        return False, 0, []

    if not any_contains(file_path, match.get("path_contains_any", [])):
        return False, 0, []

    if not any_contains(description, match.get("description_contains_any", [])):
        return False, 0, []

    if not all_contains(description, match.get("description_contains_all", [])):
        return False, 0, []

    if not none_contains(description, match.get("description_contains_none", [])):
        return False, 0, []

    if not any_contains(code, match.get("code_contains_any", [])):
        return False, 0, []

    if not all_contains(code, match.get("code_contains_all", [])):
        return False, 0, []

    if not none_contains(code, match.get("code_contains_none", [])):
        return False, 0, []

    matched_features: List[str] = []
    score = 0

    if rule_code:
        matched_features.append(f"规则={rule_code}")
        score += 2
    if extension:
        matched_features.append(f"后缀={extension}")
        score += 1
    for field_name, label, source in [
        ("path_contains_any", "路径", file_path),
        ("description_contains_any", "描述", description),
        ("code_contains_any", "代码", code),
    ]:
        for token in match.get(field_name, []):
            if lowered(token) in lowered(source):
                matched_features.append(f"{label}包含:{token}")
                score += 1

    if match.get("file_path_regex"):
        matched_features.append("命中路径正则")
        score += 1

    return True, score, matched_features


def pick_best_entry(issue: Dict[str, Any], entries: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    candidates: List[Tuple[int, Dict[str, Any], List[str]]] = []
    for entry in entries:
        if not entry.get("enabled", False):
            continue
        ok, score, features = compute_match_score(issue, entry)
        if ok:
            candidates.append((score, entry, features))

    if not candidates:
        return None, []

    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best_entry, features = candidates[0]
    if best_score >= 5:
        status = "已命中"
    else:
        status = "弱命中"
    return dict(best_entry, _matched_status=status), features


def annotate_issue(issue: Dict[str, Any], entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    annotated = deepcopy(issue)
    best_entry, features = pick_best_entry(issue, entries)

    if not best_entry:
        annotated.update({
            "kb_match_status": "未命中",
            "kb_action": "保留",
            "kb_rule_id": "",
            "kb_rule_title": "",
            "kb_reason": "",
            "kb_feature_summary": "",
            "kb_confidence": "",
            "kb_requires_human_review": True,
            "kb_target_severity": "",
        })
        return annotated

    decision = best_entry.get("decision", {})
    annotated.update({
        "kb_match_status": best_entry.get("_matched_status", "已命中"),
        "kb_action": normalize_text(decision.get("action")) or "人工确认",
        "kb_rule_id": normalize_text(best_entry.get("id")),
        "kb_rule_title": normalize_text(best_entry.get("title")),
        "kb_reason": normalize_text(best_entry.get("reason")),
        "kb_feature_summary": normalize_text(best_entry.get("feature_summary")) or "；".join(features),
        "kb_confidence": normalize_text(decision.get("confidence")) or "中",
        "kb_requires_human_review": bool(decision.get("requires_human_review", True)),
        "kb_target_severity": normalize_text(decision.get("target_severity")),
    })
    return annotated


def summarize(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = {
        "total": len(issues),
        "kb_matched": 0,
        "kb_weak_matched": 0,
        "actions": {},
    }
    for issue in issues:
        status = issue.get("kb_match_status")
        action = issue.get("kb_action") or "保留"
        if status == "已命中":
            summary["kb_matched"] += 1
        elif status == "弱命中":
            summary["kb_weak_matched"] += 1
        summary["actions"][action] = summary["actions"].get(action, 0) + 1
    return summary


def print_text_report(result: Dict[str, Any]) -> None:
    summary = result["summary"]
    print("知识库增强结果")
    print("=" * 60)
    print(f"总问题数: {summary['total']}")
    print(f"已命中: {summary['kb_matched']}")
    print(f"弱命中: {summary['kb_weak_matched']}")
    print(f"输出增强列: {', '.join(result['report_columns'])}")
    print("动作统计:")
    for action, count in sorted(summary["actions"].items()):
        print(f"- {action}: {count}")
    print("=" * 60)

    preview = result["issues"][:10]
    for item in preview:
        print(f"- {issue_rule_code(item)} | {issue_file_path(item)} | {item.get('kb_match_status')} | {item.get('kb_action')} | {item.get('kb_rule_id')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="对扫描结果追加知识库增强字段")
    parser.add_argument("input_json", help="原始扫描结果 JSON 路径")
    parser.add_argument("--kb", default=None, help="知识库 JSON 路径，默认使用 references/false-positive-kb.json")
    parser.add_argument("--output", help="输出 JSON 路径")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="stdout 输出格式")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input_json)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        return 1

    kb_path = Path(args.kb) if args.kb else Path(__file__).resolve().parents[1] / "references" / "false-positive-kb.json"
    if not kb_path.exists():
        print(f"错误: 知识库文件不存在: {kb_path}", file=sys.stderr)
        return 1

    try:
        payload = load_json(input_path)
        issues = load_issues(payload)
        kb = load_json(kb_path)
        entries = kb.get("entries", []) if isinstance(kb, dict) else []
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    annotated_issues = [annotate_issue(issue, entries) for issue in issues]
    result = {
        "issues": annotated_issues,
        "summary": summarize(annotated_issues),
        "report_columns": kb.get("report_columns", DEFAULT_COLUMNS),
        "kb_path": str(kb_path),
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.format == "text":
        print_text_report(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

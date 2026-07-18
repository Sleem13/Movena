"""Summarize privacy-safe internal pilot feedback and issue templates."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEEDBACK = ROOT / "data/processed/pilot/internal_pilot_feedback_template.csv"
DEFAULT_ISSUES = ROOT / "data/processed/pilot/internal_pilot_issue_log.csv"
DEFAULT_MARKDOWN = ROOT / "reports/pilot/internal_pilot_summary.md"
DEFAULT_CSV = ROOT / "reports/pilot/internal_pilot_summary.csv"

TRUE_VALUES = {"1", "true", "yes", "y", "passed", "success"}
SEVERE_LEVELS = {"blocker", "high"}
SAFETY_LEVEL = "safety_privacy"


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            normalized = {
                key: (value or "").strip()
                for key, value in row.items()
                if key is not None and isinstance(value, str)
            }
            if any(normalized.values()):
                rows.append(normalized)
        return rows


def _rate(rows: list[dict[str, str]], field: str) -> tuple[int, int, float | None]:
    values = [row.get(field, "").strip().lower() for row in rows if row.get(field, "").strip()]
    positive = sum(value in TRUE_VALUES for value in values)
    return positive, len(values), (positive / len(values) if values else None)


def _join_counts(counter: Counter[str]) -> str:
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common()) or "None recorded"


def summarize_feedback(feedback_rows: list[dict[str, str]], issue_rows: list[dict[str, str]]) -> dict[str, object]:
    testers = {row.get("tester_id_or_alias", "") for row in feedback_rows} - {""}
    devices = {
        (row.get("device_model", ""), row.get("os_version", ""))
        for row in feedback_rows
        if row.get("device_model") or row.get("os_version")
    }
    device_models = Counter(row.get("device_model", "") for row in feedback_rows if row.get("device_model"))
    exercises = Counter(row.get("exercise_tested", "") for row in feedback_rows if row.get("exercise_tested"))
    upload_yes, upload_total, upload_rate = _rate(feedback_rows, "upload_success")
    rejected_rows = [row for row in feedback_rows if row.get("analysis_status", "").lower() == "rejected"]
    clarity_yes, clarity_total, clarity_rate = _rate(rejected_rows, "rejected_result_clear")

    common_issues = Counter()
    common_issues.update(row.get("issue_type", "") for row in feedback_rows if row.get("issue_type"))
    common_issues.update(row.get("issue_category", "") for row in issue_rows if row.get("issue_category"))

    combined_severity = [
        (row.get("severity", "").lower(), row.get("issue_description", "")) for row in feedback_rows
    ] + [
        (row.get("severity", "").lower(), row.get("description", "")) for row in issue_rows
    ]
    blocker_high = [description or "Description not supplied" for severity, description in combined_severity if severity in SEVERE_LEVELS]
    safety_privacy = [description or "Description not supplied" for severity, description in combined_severity if severity == SAFETY_LEVEL]
    recommendations = [
        row.get("suggested_improvement", "") for row in feedback_rows if row.get("suggested_improvement")
    ]
    recommendations.extend(blocker_high)
    recommendations.extend(safety_privacy)
    recommendations = list(dict.fromkeys(item for item in recommendations if item))

    if not feedback_rows:
        recommendation = "NO-GO — no completed pilot feedback is available."
    elif safety_privacy or any(severity == "blocker" for severity, _ in combined_severity):
        recommendation = "NO-GO — stop and resolve blocker or safety/privacy issues before another build."
    elif blocker_high:
        recommendation = "CONDITIONAL — resolve high-severity issues before the next internal build."
    else:
        recommendation = "CONTINUE INTERNAL PILOT — review recorded medium/low issues before the next build."

    return {
        "number_of_testers": len(testers),
        "number_of_devices": len(devices),
        "number_of_sessions": len(feedback_rows),
        "devices_tested": _join_counts(device_models),
        "exercises_tested": _join_counts(exercises),
        "upload_success": f"{upload_yes}/{upload_total}",
        "upload_success_rate": upload_rate,
        "rejected_result_clarity": f"{clarity_yes}/{clarity_total}",
        "rejected_result_clarity_rate": clarity_rate,
        "common_issues": _join_counts(common_issues),
        "blocker_high_count": len(blocker_high),
        "safety_privacy_count": len(safety_privacy),
        "recommended_fixes": recommendations,
        "recommendation": recommendation,
    }


def _format_rate(value: object) -> str:
    return "Not measured" if value is None else f"{float(value):.1%}"


def write_summary(summary: dict[str, object], markdown_path: Path, csv_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fixes = summary["recommended_fixes"]
    fix_lines = "\n".join(f"- {item}" for item in fixes) if fixes else "- No fixes recorded; collect completed pilot feedback first."
    markdown_path.write_text(
        "# Internal Pilot Feedback Summary\n\n"
        "> Product QA evidence only. This report is not clinical validation and must contain no patient-identifiable data.\n\n"
        f"- Testers: {summary['number_of_testers']}\n"
        f"- Devices: {summary['number_of_devices']} ({summary['devices_tested']})\n"
        f"- Sessions: {summary['number_of_sessions']}\n"
        f"- Exercises: {summary['exercises_tested']}\n"
        f"- Upload success: {summary['upload_success']} ({_format_rate(summary['upload_success_rate'])})\n"
        f"- Rejected-result clarity: {summary['rejected_result_clarity']} ({_format_rate(summary['rejected_result_clarity_rate'])})\n"
        f"- Common issues: {summary['common_issues']}\n"
        f"- Blocker/high issues: {summary['blocker_high_count']}\n"
        f"- Safety/privacy issues: {summary['safety_privacy_count']}\n\n"
        "## Recommended fixes\n\n"
        f"{fix_lines}\n\n"
        "## Go/no-go recommendation\n\n"
        f"**{summary['recommendation']}**\n",
        encoding="utf-8",
    )
    rows = [
        ("number_of_testers", summary["number_of_testers"]),
        ("number_of_devices", summary["number_of_devices"]),
        ("number_of_sessions", summary["number_of_sessions"]),
        ("devices_tested", summary["devices_tested"]),
        ("exercises_tested", summary["exercises_tested"]),
        ("upload_success_rate", _format_rate(summary["upload_success_rate"])),
        ("rejected_result_clarity_rate", _format_rate(summary["rejected_result_clarity_rate"])),
        ("common_issues", summary["common_issues"]),
        ("blocker_high_count", summary["blocker_high_count"]),
        ("safety_privacy_count", summary["safety_privacy_count"]),
        ("recommendation", summary["recommendation"]),
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def run_summary(feedback_path: Path, issues_path: Path, markdown_path: Path, csv_path: Path) -> dict[str, object]:
    summary = summarize_feedback(_read_rows(feedback_path), _read_rows(issues_path))
    write_summary(summary, markdown_path, csv_path)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--issues", type=Path, default=DEFAULT_ISSUES)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    summary = run_summary(args.feedback, args.issues, args.markdown_output, args.csv_output)
    print(f"Pilot summary written: {args.markdown_output} ({summary['number_of_sessions']} session(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

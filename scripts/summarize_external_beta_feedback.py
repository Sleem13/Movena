"""Summarize privacy-safe external beta feedback, issues, builds, and optional QA data."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEEDBACK = ROOT / "data/processed/beta/external_beta_feedback_template.csv"
DEFAULT_ISSUES = ROOT / "data/processed/beta/external_beta_issue_log.csv"
DEFAULT_BUILDS = ROOT / "data/processed/beta/external_beta_build_registry.csv"
DEFAULT_QA_MATRIX = ROOT / "data/processed/beta/external_beta_qa_matrix.csv"
DEFAULT_INTERNAL_REVIEWER_QA = ROOT / "data/processed/beta/internal_reviewer_qa_log.csv"
DEFAULT_MARKDOWN = ROOT / "reports/beta/external_beta_summary.md"
DEFAULT_CSV = ROOT / "reports/beta/external_beta_summary.csv"

TRUE_VALUES = {"1", "true", "yes", "y", "passed", "success"}
SEVERE_LEVELS = {"blocker", "high"}
SAFETY_LEVEL = "safety_privacy"
SECOND_WAVE_VALUES = {"2", "second", "second_wave", "wave_2", "wave2"}


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows: list[dict[str, str]] = []
        for row in csv.DictReader(handle):
            normalized = {
                key: value.strip()
                for key, value in row.items()
                if key is not None and isinstance(value, str)
            }
            if any(normalized.values()):
                rows.append(normalized)
        return rows


def _is_true(value: str) -> bool:
    return value.strip().lower() in TRUE_VALUES


def _is_second_wave(row: dict[str, str]) -> bool:
    return row.get("beta_wave", "").strip().lower() in SECOND_WAVE_VALUES


def _rate(rows: list[dict[str, str]], field: str) -> tuple[int, int, float | None]:
    values = [row.get(field, "").strip().lower() for row in rows if row.get(field, "").strip()]
    positive = sum(value in TRUE_VALUES for value in values)
    return positive, len(values), positive / len(values) if values else None


def _join_counts(counter: Counter[str]) -> str:
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common()) or "None recorded"


def summarize_feedback(
    feedback_rows: list[dict[str, str]],
    issue_rows: list[dict[str, str]],
    build_rows: list[dict[str, str]] | None = None,
    qa_rows: list[dict[str, str]] | None = None,
    internal_reviewer_rows: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    build_rows = build_rows or []
    qa_rows = qa_rows or []
    internal_reviewer_rows = internal_reviewer_rows or []
    testers = ({row.get("tester_alias", "") for row in feedback_rows} | {
        row.get("reported_by_alias", "") for row in issue_rows
    }) - {""}
    devices = {
        (row.get("device_model", ""), row.get("os_version", ""))
        for row in feedback_rows
        if row.get("device_model") or row.get("os_version")
    }
    devices.update(
        (row.get("device_model", ""), "") for row in issue_rows if row.get("device_model")
    )
    device_models = Counter(row.get("device_model", "") for row in feedback_rows if row.get("device_model"))
    device_models.update(row.get("device_model", "") for row in issue_rows if row.get("device_model"))
    exercises = Counter(row.get("exercise_tested", "") for row in feedback_rows if row.get("exercise_tested"))
    exercises.update(row.get("exercise", "") for row in issue_rows if row.get("exercise"))
    upload_yes, upload_total, upload_rate = _rate(feedback_rows, "upload_success")
    rejected_rows = [row for row in feedback_rows if row.get("analysis_status", "").lower() == "rejected"]
    clarity_yes, clarity_total, clarity_rate = _rate(rejected_rows, "rejected_result_clear")

    common_issues: Counter[str] = Counter()
    common_issues.update(row.get("issue_type", "") for row in feedback_rows if row.get("issue_type"))
    common_issues.update(row.get("issue_category", "") for row in issue_rows if row.get("issue_category"))

    combined_severity = [
        (row.get("severity", "").lower(), row.get("issue_description", "")) for row in feedback_rows
    ] + [(row.get("severity", "").lower(), row.get("description", "")) for row in issue_rows]
    blocker_high = [
        description or "Description not supplied"
        for severity, description in combined_severity
        if severity in SEVERE_LEVELS
    ]
    safety_privacy = [
        row.get("issue_description", "") or "Privacy/safety concern not described"
        for row in feedback_rows
        if row.get("severity", "").lower() == SAFETY_LEVEL
        or _is_true(row.get("privacy_safety_concern", ""))
    ]
    safety_privacy.extend(
        row.get("description", "") or "Privacy/safety concern not described"
        for row in issue_rows
        if row.get("severity", "").lower() == SAFETY_LEVEL
        or _is_true(row.get("privacy_safety_related", ""))
    )
    safety_privacy = list(dict.fromkeys(safety_privacy))

    recommendations = [
        row.get("suggested_improvement", "") for row in feedback_rows if row.get("suggested_improvement")
    ]
    recommendations.extend(blocker_high)
    recommendations.extend(safety_privacy)
    recommendations = list(dict.fromkeys(item for item in recommendations if item))

    build_statuses = Counter(row.get("build_status", "") for row in build_rows if row.get("build_status"))
    blocked_builds = sum(
        "blocked" in row.get("build_status", "").lower()
        or "failed" in row.get("build_status", "").lower()
        or "not_submitted" in row.get("build_status", "").lower()
        for row in build_rows
    )
    latest_build = build_rows[-1] if build_rows else {}
    qa_statuses = Counter(row.get("status", "").lower() for row in qa_rows if row.get("status"))
    first_wave_feedback = sum(not _is_second_wave(row) for row in feedback_rows)
    second_wave_feedback = sum(_is_second_wave(row) for row in feedback_rows)
    first_wave_issues = sum(not _is_second_wave(row) for row in issue_rows)
    second_wave_issues = sum(_is_second_wave(row) for row in issue_rows)

    has_blocker = any(severity == "blocker" for severity, _ in combined_severity)
    if not feedback_rows:
        recommendation = "NO-GO — no completed external beta feedback is available."
    elif safety_privacy or has_blocker:
        recommendation = "NO-GO — resolve blocker or safety/privacy issues before another beta build."
    elif blocker_high:
        recommendation = "CONDITIONAL — resolve high-severity issues before another beta build."
    else:
        recommendation = "CONTINUE INVITE-ONLY BETA — review medium/low issues before another build."

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
        "builds_recorded": len(build_rows),
        "build_statuses": _join_counts(build_statuses),
        "blocked_build_count": blocked_builds,
        "latest_rc_version": latest_build.get("rc_version", "Not recorded"),
        "latest_build_status": latest_build.get("build_status", "Not recorded"),
        "qa_checks_recorded": len(qa_rows),
        "qa_pass_count": qa_statuses.get("pass", 0),
        "qa_fail_count": qa_statuses.get("fail", 0),
        "qa_blocked_count": qa_statuses.get("blocked", 0),
        "first_wave_feedback_records": first_wave_feedback,
        "first_wave_issue_records": first_wave_issues,
        "second_wave_feedback_records": second_wave_feedback,
        "second_wave_issue_records": second_wave_issues,
        "internal_reviewer_records": len(internal_reviewer_rows),
        "internal_pt_physical_device_reviews": sum(
            row.get("role", "").lower() == "physical_therapist_internal_reviewer"
            and row.get("test_type", "").lower() == "internal_physical_device_qa"
            for row in internal_reviewer_rows
        ),
        "recommended_fixes": recommendations,
        "recommendation": recommendation,
    }


def _format_rate(value: object) -> str:
    return "Not measured" if value is None else f"{float(value):.1%}"


def write_summary(summary: dict[str, object], markdown_path: Path, csv_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fixes = summary["recommended_fixes"]
    fix_lines = "\n".join(f"- {item}" for item in fixes) if fixes else "- Collect completed beta feedback before prioritizing fixes."
    evidence_note = (
        "Internal reviewer QA evidence exists, but no external beta feedback has been collected. Internal QA is not external beta evidence."
        if summary["number_of_sessions"] == 0 and summary["internal_reviewer_records"]
        else "No external beta feedback has been collected yet. Empty feedback is not evidence of safety, usability, or clinical validity."
        if summary["number_of_sessions"] == 0
        else "Feedback counts reflect submitted product-QA sessions only; they are not clinical validation."
    )
    markdown_path.write_text(
        "# External Closed Beta Feedback Summary\n\n"
        "> Product QA evidence only. This is not clinical validation. Do not enter patient-identifiable data.\n\n"
        f"- Testers: {summary['number_of_testers']}\n"
        f"- Devices: {summary['number_of_devices']} ({summary['devices_tested']})\n"
        f"- Sessions: {summary['number_of_sessions']}\n"
        f"- Exercises: {summary['exercises_tested']}\n"
        f"- Upload success: {summary['upload_success']} ({_format_rate(summary['upload_success_rate'])})\n"
        f"- Rejected-result clarity: {summary['rejected_result_clarity']} ({_format_rate(summary['rejected_result_clarity_rate'])})\n"
        f"- Common issues: {summary['common_issues']}\n"
        f"- Blocker/high issues: {summary['blocker_high_count']}\n"
        f"- Safety/privacy concerns: {summary['safety_privacy_count']}\n\n"
        "## Wave separation\n\n"
        f"- First-wave feedback / issues: {summary['first_wave_feedback_records']} / "
        f"{summary['first_wave_issue_records']}\n"
        f"- Second-wave feedback / issues: {summary['second_wave_feedback_records']} / "
        f"{summary['second_wave_issue_records']}\n\n"
        "## Internal reviewer evidence (not external beta)\n\n"
        f"- Internal reviewer records: {summary['internal_reviewer_records']}\n"
        f"- Internal PT physical-device QA records: {summary['internal_pt_physical_device_reviews']}\n\n"
        "## Release evidence\n\n"
        f"- Builds recorded: {summary['builds_recorded']} ({summary['build_statuses']})\n"
        f"- Latest RC: {summary['latest_rc_version']} — {summary['latest_build_status']}\n"
        f"- Blocked builds: {summary['blocked_build_count']}\n"
        f"- Machine-readable QA checks: {summary['qa_checks_recorded']} "
        f"(pass {summary['qa_pass_count']}, fail {summary['qa_fail_count']}, blocked {summary['qa_blocked_count']})\n\n"
        f"**Evidence note:** {evidence_note}\n\n"
        "## Recommended fixes\n\n"
        f"{fix_lines}\n\n"
        "## Go/no-go recommendation for the next beta build\n\n"
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
        ("builds_recorded", summary["builds_recorded"]),
        ("build_statuses", summary["build_statuses"]),
        ("blocked_build_count", summary["blocked_build_count"]),
        ("latest_rc_version", summary["latest_rc_version"]),
        ("latest_build_status", summary["latest_build_status"]),
        ("qa_checks_recorded", summary["qa_checks_recorded"]),
        ("qa_pass_count", summary["qa_pass_count"]),
        ("qa_fail_count", summary["qa_fail_count"]),
        ("qa_blocked_count", summary["qa_blocked_count"]),
        ("first_wave_feedback_records", summary["first_wave_feedback_records"]),
        ("first_wave_issue_records", summary["first_wave_issue_records"]),
        ("second_wave_feedback_records", summary["second_wave_feedback_records"]),
        ("second_wave_issue_records", summary["second_wave_issue_records"]),
        ("internal_reviewer_records", summary["internal_reviewer_records"]),
        ("internal_pt_physical_device_reviews", summary["internal_pt_physical_device_reviews"]),
        ("recommendation", summary["recommendation"]),
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def run_summary(
    feedback_path: Path,
    issues_path: Path,
    markdown_path: Path,
    csv_path: Path,
    build_registry_path: Path | None = None,
    qa_matrix_path: Path | None = None,
    internal_reviewer_qa_path: Path | None = None,
) -> dict[str, object]:
    summary = summarize_feedback(
        _read_rows(feedback_path),
        _read_rows(issues_path),
        _read_rows(build_registry_path) if build_registry_path else [],
        _read_rows(qa_matrix_path) if qa_matrix_path else [],
        _read_rows(internal_reviewer_qa_path) if internal_reviewer_qa_path else [],
    )
    write_summary(summary, markdown_path, csv_path)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--issues", type=Path, default=DEFAULT_ISSUES)
    parser.add_argument("--build-registry", type=Path, default=DEFAULT_BUILDS)
    parser.add_argument("--qa-matrix", type=Path, default=DEFAULT_QA_MATRIX)
    parser.add_argument("--internal-reviewer-qa", type=Path, default=DEFAULT_INTERNAL_REVIEWER_QA)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    summary = run_summary(
        args.feedback,
        args.issues,
        args.markdown_output,
        args.csv_output,
        args.build_registry,
        args.qa_matrix,
        args.internal_reviewer_qa,
    )
    print(f"External beta summary written: {args.markdown_output} ({summary['number_of_sessions']} session(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

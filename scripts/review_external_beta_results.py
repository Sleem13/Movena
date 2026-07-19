"""Review genuine invite-only external beta records without inventing results."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BETA_DIR = ROOT / "data/processed/beta"
DEFAULT_ROSTER = BETA_DIR / "external_beta_tester_roster.csv"
DEFAULT_CONSENT = BETA_DIR / "external_beta_consent_tracker.csv"
DEFAULT_ASSIGNMENTS = BETA_DIR / "external_beta_test_assignments.csv"
DEFAULT_FEEDBACK = BETA_DIR / "external_beta_feedback_template.csv"
DEFAULT_ISSUES = BETA_DIR / "external_beta_issue_log.csv"
DEFAULT_REVIEW_MD = ROOT / "reports/beta/external_beta_results_review.md"
DEFAULT_REVIEW_CSV = ROOT / "reports/beta/external_beta_results_review.csv"
DEFAULT_METRICS_MD = ROOT / "reports/beta/external_beta_metrics_summary.md"
DEFAULT_METRICS_CSV = BETA_DIR / "external_beta_metrics_summary.csv"

TRUE_VALUES = {"1", "true", "yes", "y", "pass", "passed", "success", "successful", "complete", "completed"}
BLOCKER_LEVELS = {"blocker", "critical", "p0"}
HIGH_LEVELS = {"high", "p1"}


def read_rows(path: Path) -> list[dict[str, str]]:
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


def is_true(value: str) -> bool:
    return value.strip().lower() in TRUE_VALUES


def rate(rows: list[dict[str, str]], field: str) -> tuple[int, int, float | None]:
    values = [row.get(field, "").strip() for row in rows if row.get(field, "").strip()]
    positives = sum(is_true(value) for value in values)
    return positives, len(values), positives / len(values) if values else None


def format_rate(value: object) -> str:
    return "not_available" if value is None else f"{float(value):.1%}"


def format_counts(values: Counter[str]) -> str:
    return ", ".join(f"{key} ({count})" for key, count in values.most_common()) or "none_recorded"


def build_review(
    roster: list[dict[str, str]],
    consent: list[dict[str, str]],
    assignments: list[dict[str, str]],
    feedback: list[dict[str, str]],
    issues: list[dict[str, str]],
) -> dict[str, object]:
    tester_ids = {row.get("tester_id", "") for row in roster if row.get("tester_id")}
    invited_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("invite_status", "").lower() in {"invited", "accepted", "declined", "removed"}
    }
    accepted_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("invite_status", "").lower() == "accepted"
    }
    active_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("testing_status", "").lower() in {"in_progress", "active"}
    }
    completed_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("testing_status", "").lower() == "completed"
    }
    consent_ids = {
        row.get("tester_id", "")
        for row in consent
        if row.get("tester_id")
        and is_true(row.get("consent_acknowledged", ""))
        and is_true(row.get("data_handling_acknowledged", ""))
        and is_true(row.get("no_real_patient_data_acknowledged", ""))
        and is_true(row.get("safety_limitations_acknowledged", ""))
        and not is_true(row.get("withdrawal_requested", ""))
    }
    consent_complete = len(accepted_ids & consent_ids)
    consent_rate = consent_complete / len(accepted_ids) if accepted_ids else None

    completed_assignments = [row for row in assignments if row.get("status", "").lower() == "completed"]
    exercises = Counter(row.get("exercise_tested", "") for row in feedback if row.get("exercise_tested"))
    exercises.update(row.get("exercise_id", "") for row in completed_assignments if row.get("exercise_id"))
    devices = {
        (row.get("device_model", ""), row.get("os_version", ""))
        for row in feedback
        if row.get("device_model") or row.get("os_version")
    }

    upload_yes, upload_total, upload_rate = rate(feedback, "upload_success")
    result_clarity_yes, result_clarity_total, result_clarity_rate = rate(feedback, "result_easy_to_understand")
    rejected = [row for row in feedback if row.get("analysis_status", "").lower() == "rejected"]
    clarity_yes, clarity_total, clarity_rate = rate(rejected, "rejected_result_clear")
    severities = Counter(row.get("severity", "").lower() for row in issues if row.get("severity"))
    severities.update(row.get("severity", "").lower() for row in feedback if row.get("severity"))
    blocker_count = sum(severities[level] for level in BLOCKER_LEVELS)
    high_count = sum(severities[level] for level in HIGH_LEVELS)
    safety_count = sum(is_true(row.get("safety_privacy_flag", "")) for row in roster)
    safety_count += sum(is_true(row.get("privacy_safety_concern", "")) for row in feedback)
    safety_count += sum(is_true(row.get("privacy_safety_related", "")) for row in issues)
    auth_token_count = sum(
        row.get("issue_category", "").lower() in {"auth", "authentication", "token"}
        for row in issues
    )
    network_count = sum(row.get("issue_category", "").lower() == "network" for row in issues)
    upload_issue_count = sum(row.get("issue_category", "").lower() == "upload" for row in issues)

    if not tester_ids:
        status = "blocked_no_beta_data"
        recommendation = "Continue Sprint 29B; do not start Sprint 30 review or expand the beta until genuine consented records exist."
    elif safety_count or blocker_count:
        status = "paused_for_safety_or_blocker_review"
        recommendation = "Pause the invite-only beta and resolve safety/privacy or blocker findings before resuming."
    elif not completed_ids or not feedback:
        status = "insufficient_beta_results"
        recommendation = "Continue the controlled Sprint 29B beta and collect genuine completed-session evidence before Sprint 30."
    else:
        status = "results_available_for_review"
        recommendation = "Review the recorded evidence and prioritize verified issues before any expansion decision."

    return {
        "review_status": status,
        "tester_records": len(tester_ids),
        "invited_testers": len(invited_ids),
        "accepted_testers": len(accepted_ids),
        "consent_complete_testers": consent_complete,
        "consent_completion_rate": consent_rate,
        "active_testers": len(active_ids),
        "completed_testers": len(completed_ids),
        "assignment_records": len(assignments),
        "completed_assignments": len(completed_assignments),
        "feedback_records": len(feedback),
        "issue_records": len(issues),
        "blocker_issue_count": blocker_count,
        "high_issue_count": high_count,
        "safety_privacy_issue_count": safety_count,
        "devices_tested_count": len(devices),
        "exercises_tested_count": len(exercises),
        "exercises_tested": format_counts(exercises),
        "upload_success_count": upload_yes,
        "upload_failure_count": upload_total - upload_yes,
        "upload_attempts_recorded": upload_total,
        "upload_success_rate": upload_rate,
        "result_clarity_positive": result_clarity_yes,
        "result_clarity_responses": result_clarity_total,
        "result_clarity_rate": result_clarity_rate,
        "rejected_clarity_positive": clarity_yes,
        "rejected_clarity_responses": clarity_total,
        "rejected_result_clarity_rate": clarity_rate,
        "upload_issue_count": upload_issue_count,
        "network_issue_count": network_count,
        "auth_token_issue_count": auth_token_count,
        "issue_severity_distribution": format_counts(severities),
        "recommendation": recommendation,
    }


def metric_rows(summary: dict[str, object]) -> list[tuple[str, object]]:
    mapping = (
        ("review_status", "review_status"), ("invited_testers", "invited_testers"),
        ("accepted_testers", "accepted_testers"), ("consent_rate", "consent_completion_rate"),
        ("active_testers", "active_testers"), ("completed_testers", "completed_testers"),
        ("feedback_count", "feedback_records"), ("issue_count", "issue_records"),
        ("blocker_issue_count", "blocker_issue_count"), ("high_issue_count", "high_issue_count"),
        ("safety_privacy_issue_count", "safety_privacy_issue_count"),
        ("exercises_tested_count", "exercises_tested_count"),
        ("upload_success_rate_if_available", "upload_success_rate"),
        ("rejected_result_clarity_rate_if_available", "rejected_result_clarity_rate"),
    )
    return [
        (output_key, format_rate(summary[source_key]) if output_key.endswith("rate") or "rate_if_available" in output_key else summary[source_key])
        for output_key, source_key in mapping
    ]


def write_outputs(
    summary: dict[str, object], review_md: Path, review_csv: Path, metrics_md: Path, metrics_csv: Path
) -> None:
    for path in (review_md, review_csv, metrics_md, metrics_csv):
        path.parent.mkdir(parents=True, exist_ok=True)
    evidence = (
        "All five beta inputs contain zero real rows. Zero is a record count, not evidence that the product is safe, reliable, clear, or clinically valid."
        if summary["tester_records"] == 0
        else "Only non-empty recorded beta rows are counted; this product-QA review is not clinical validation."
    )
    review_md.write_text(
        "# External Beta Results Review\n\n"
        "> Invite-only product QA only. No public release, real patient data, clinical use, diagnosis, or treatment claims.\n\n"
        f"**Review status:** `{summary['review_status']}`\n\n"
        f"**Evidence boundary:** {evidence}\n\n"
        "## Participation\n\n"
        f"- Tester records: {summary['tester_records']}\n"
        f"- Invited / accepted: {summary['invited_testers']} / {summary['accepted_testers']}\n"
        f"- Consent complete: {summary['consent_complete_testers']} ({format_rate(summary['consent_completion_rate'])})\n"
        f"- Active / completed: {summary['active_testers']} / {summary['completed_testers']}\n"
        f"- Assignments: {summary['assignment_records']} (completed {summary['completed_assignments']})\n\n"
        "## Product evidence\n\n"
        f"- Feedback / issues: {summary['feedback_records']} / {summary['issue_records']}\n"
        f"- Devices / exercises: {summary['devices_tested_count']} / {summary['exercises_tested_count']}\n"
        f"- Upload success: {summary['upload_success_count']}/{summary['upload_attempts_recorded']} ({format_rate(summary['upload_success_rate'])})\n"
        f"- Upload failures: {summary['upload_failure_count']}\n"
        f"- General result clarity: {summary['result_clarity_positive']}/{summary['result_clarity_responses']} ({format_rate(summary['result_clarity_rate'])})\n"
        f"- Rejected-result clarity: {summary['rejected_clarity_positive']}/{summary['rejected_clarity_responses']} ({format_rate(summary['rejected_result_clarity_rate'])})\n"
        f"- Issue severity: {summary['issue_severity_distribution']}\n"
        f"- Blocker / high / safety-privacy: {summary['blocker_issue_count']} / {summary['high_issue_count']} / {summary['safety_privacy_issue_count']}\n"
        f"- Upload / network / auth-token issues: {summary['upload_issue_count']} / {summary['network_issue_count']} / {summary['auth_token_issue_count']}\n\n"
        "## Decision\n\n"
        f"**{summary['recommendation']}**\n",
        encoding="utf-8",
    )
    with review_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in summary.items():
            writer.writerow([key, format_rate(value) if key.endswith("_rate") else value])
    rows = metric_rows(summary)
    with metrics_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)
    metrics_md.write_text(
        "# External Beta Metrics Summary\n\n"
        "> Product-QA metrics only; not clinical validation. `not_available` means no real denominator was recorded.\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in rows)
        + f"\n\n**Decision:** {summary['recommendation']}\n",
        encoding="utf-8",
    )


def run_review(
    roster_path: Path, consent_path: Path, assignments_path: Path, feedback_path: Path,
    issues_path: Path, review_md: Path, review_csv: Path, metrics_md: Path, metrics_csv: Path,
) -> dict[str, object]:
    summary = build_review(
        read_rows(roster_path), read_rows(consent_path), read_rows(assignments_path),
        read_rows(feedback_path), read_rows(issues_path),
    )
    write_outputs(summary, review_md, review_csv, metrics_md, metrics_csv)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--consent", type=Path, default=DEFAULT_CONSENT)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--issues", type=Path, default=DEFAULT_ISSUES)
    parser.add_argument("--review-markdown", type=Path, default=DEFAULT_REVIEW_MD)
    parser.add_argument("--review-csv", type=Path, default=DEFAULT_REVIEW_CSV)
    parser.add_argument("--metrics-markdown", type=Path, default=DEFAULT_METRICS_MD)
    parser.add_argument("--metrics-csv", type=Path, default=DEFAULT_METRICS_CSV)
    args = parser.parse_args()
    summary = run_review(
        args.roster, args.consent, args.assignments, args.feedback, args.issues,
        args.review_markdown, args.review_csv, args.metrics_markdown, args.metrics_csv,
    )
    print(f"External beta results review written: {args.review_markdown} (status={summary['review_status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

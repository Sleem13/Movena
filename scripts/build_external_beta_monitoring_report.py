"""Build a privacy-safe operational report for the invite-only external beta."""

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
DEFAULT_MARKDOWN = ROOT / "reports/beta/external_beta_monitoring_report.md"
DEFAULT_CSV = ROOT / "reports/beta/external_beta_monitoring_report.csv"

TRUE_VALUES = {"1", "true", "yes", "y", "passed", "complete", "completed"}
INVITED_STATES = {"invited", "accepted", "declined", "removed"}
SEVERE_STATES = {"blocker", "high"}


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


def format_rate(value: float | None) -> str:
    return "Not measured" if value is None else f"{value:.1%}"


def count_text(counter: Counter[str]) -> str:
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common()) or "None recorded"


def build_summary(
    roster: list[dict[str, str]],
    consent: list[dict[str, str]],
    assignments: list[dict[str, str]],
    feedback: list[dict[str, str]],
    issues: list[dict[str, str]],
) -> dict[str, object]:
    real_tester_ids = {row.get("tester_id", "") for row in roster if row.get("tester_id")}
    invited_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("invite_status", "").lower() in INVITED_STATES
    }
    accepted_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("invite_status", "").lower() == "accepted"
    }
    active_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("testing_status", "").lower() == "in_progress"
    }
    completed_ids = {
        row.get("tester_id", "")
        for row in roster
        if row.get("tester_id") and row.get("testing_status", "").lower() == "completed"
    }

    consent_complete_ids = {
        row.get("tester_id", "")
        for row in consent
        if row.get("tester_id")
        and is_true(row.get("consent_acknowledged", ""))
        and is_true(row.get("data_handling_acknowledged", ""))
        and is_true(row.get("no_real_patient_data_acknowledged", ""))
        and is_true(row.get("safety_limitations_acknowledged", ""))
        and not is_true(row.get("withdrawal_requested", ""))
    }
    accepted_consent = len(accepted_ids & consent_complete_ids)
    consent_rate = accepted_consent / len(accepted_ids) if accepted_ids else None

    completed_assignments = [row for row in assignments if row.get("status", "").lower() == "completed"]
    exercises = Counter(row.get("exercise_tested", "") for row in feedback if row.get("exercise_tested"))
    exercises.update(row.get("exercise_id", "") for row in completed_assignments if row.get("exercise_id"))

    issue_severity = Counter(row.get("severity", "").lower() for row in issues if row.get("severity"))
    roster_safety = sum(is_true(row.get("safety_privacy_flag", "")) for row in roster)
    feedback_safety = sum(is_true(row.get("privacy_safety_concern", "")) for row in feedback)
    issue_safety = sum(
        is_true(row.get("privacy_safety_related", ""))
        or row.get("severity", "").lower() in {"safety_privacy", "critical", "safety/privacy critical"}
        for row in issues
    )
    safety_flags = roster_safety + feedback_safety + issue_safety
    upload_issues = sum(row.get("issue_category", "").lower() == "upload" for row in issues)
    upload_issues += sum(row.get("issue_type", "").lower() == "upload" for row in feedback)

    rejected_rows = [row for row in feedback if row.get("analysis_status", "").lower() == "rejected"]
    clarity_values = [row.get("rejected_result_clear", "") for row in rejected_rows if row.get("rejected_result_clear")]
    clarity_positive = sum(is_true(value) for value in clarity_values)
    clarity_rate = clarity_positive / len(clarity_values) if clarity_values else None

    blocker_high = issue_severity.get("blocker", 0) + issue_severity.get("high", 0)
    if not real_tester_ids:
        beta_status = "not_started"
        alert = "NO-GO — beta has not started; no real tester records exist."
    elif safety_flags:
        beta_status = "paused"
        alert = "PAUSE — a safety/privacy flag requires immediate restricted review."
    elif not invited_ids:
        beta_status = "not_started"
        alert = "NO-GO — no tester invitation has been recorded."
    elif not accepted_ids:
        beta_status = "invitation_pending"
        alert = "NO-GO — no invited tester has accepted."
    elif accepted_consent < len(accepted_ids):
        beta_status = "blocked"
        alert = "NO-GO — accepted testers cannot proceed until all required acknowledgements are complete."
    elif blocker_high:
        beta_status = "paused"
        alert = "PAUSE — blocker/high issues must be resolved before continuing."
    elif active_ids:
        beta_status = "in_progress"
        alert = "CONTINUE INVITE-ONLY BETA — monitor issues and maintain stop criteria."
    elif completed_ids:
        beta_status = "completed_pending_review"
        alert = "REVIEW REQUIRED — evaluate feedback and issues before another build or wider pilot."
    else:
        beta_status = "ready_not_started"
        alert = "HOLD — consented testers exist, but execution has not started."

    return {
        "beta_status": beta_status,
        "tester_records": len(real_tester_ids),
        "invited_testers": len(invited_ids),
        "accepted_testers": len(accepted_ids),
        "consent_complete_testers": accepted_consent,
        "consent_completion_rate": consent_rate,
        "active_testers": len(active_ids),
        "completed_testers": len(completed_ids),
        "assignment_records": len(assignments),
        "completed_assignments": len(completed_assignments),
        "exercises_tested": count_text(exercises),
        "feedback_records": len(feedback),
        "feedback_submitted_flags": sum(is_true(row.get("feedback_submitted", "")) for row in roster),
        "issues_recorded": len(issues),
        "issues_by_severity": count_text(issue_severity),
        "blocker_high_issues": blocker_high,
        "safety_privacy_flags": safety_flags,
        "upload_related_issues": upload_issues,
        "rejected_clarity_responses": len(clarity_values),
        "rejected_clarity_rate": clarity_rate,
        "go_no_go_alert": alert,
    }


def write_report(summary: dict[str, object], markdown_path: Path, csv_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_note = (
        "No real tester records exist. The invite-only external beta has not started; zero counts are not validation."
        if summary["beta_status"] == "not_started" and summary["tester_records"] == 0
        else "Counts reflect only non-empty operational records. This report is product QA, not clinical validation."
    )
    markdown_path.write_text(
        "# External Beta Monitoring Report\n\n"
        "> Invite-only product QA only. No public release, real patient data, clinical use, diagnosis, or treatment claims.\n\n"
        f"**Beta status:** `{summary['beta_status']}`\n\n"
        f"**Evidence note:** {evidence_note}\n\n"
        "## Participation and consent\n\n"
        f"- Tester records: {summary['tester_records']}\n"
        f"- Invited: {summary['invited_testers']}\n"
        f"- Accepted: {summary['accepted_testers']}\n"
        f"- Consent complete: {summary['consent_complete_testers']} "
        f"({format_rate(summary['consent_completion_rate'])})\n"
        f"- Active: {summary['active_testers']}\n"
        f"- Completed: {summary['completed_testers']}\n\n"
        "## Execution and feedback\n\n"
        f"- Assignments: {summary['assignment_records']} (completed {summary['completed_assignments']})\n"
        f"- Exercises actually tested: {summary['exercises_tested']}\n"
        f"- Feedback records: {summary['feedback_records']}\n"
        f"- Roster feedback-submitted flags: {summary['feedback_submitted_flags']}\n"
        f"- Rejected-result clarity: {summary['rejected_clarity_responses']} response(s), "
        f"{format_rate(summary['rejected_clarity_rate'])}\n\n"
        "## Issues and safety\n\n"
        f"- Issues: {summary['issues_recorded']} ({summary['issues_by_severity']})\n"
        f"- Blocker/high issues: {summary['blocker_high_issues']}\n"
        f"- Safety/privacy flags: {summary['safety_privacy_flags']}\n"
        f"- Upload-related issues: {summary['upload_related_issues']}\n\n"
        "## Go/no-go alert\n\n"
        f"**{summary['go_no_go_alert']}**\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in summary.items():
            if key in {"consent_completion_rate", "rejected_clarity_rate"}:
                value = format_rate(value)
            writer.writerow([key, value])


def run_report(
    roster_path: Path,
    consent_path: Path,
    assignments_path: Path,
    feedback_path: Path,
    issues_path: Path,
    markdown_path: Path,
    csv_path: Path,
) -> dict[str, object]:
    summary = build_summary(
        read_rows(roster_path),
        read_rows(consent_path),
        read_rows(assignments_path),
        read_rows(feedback_path),
        read_rows(issues_path),
    )
    write_report(summary, markdown_path, csv_path)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--consent", type=Path, default=DEFAULT_CONSENT)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK)
    parser.add_argument("--issues", type=Path, default=DEFAULT_ISSUES)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    summary = run_report(
        args.roster,
        args.consent,
        args.assignments,
        args.feedback,
        args.issues,
        args.markdown_output,
        args.csv_output,
    )
    print(f"External beta monitoring report written: {args.markdown_output} (status={summary['beta_status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

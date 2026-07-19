import csv

from scripts.review_external_beta_results import run_review


def write_csv(path, headers, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def paths(tmp_path):
    inputs = [tmp_path / f"{name}.csv" for name in ("roster", "consent", "assignments", "feedback", "issues")]
    outputs = [tmp_path / name for name in ("review.md", "review.csv", "metrics.md", "metrics.csv")]
    return inputs, outputs


def test_missing_inputs_block_sprint_30_without_fabricated_rates(tmp_path):
    inputs, outputs = paths(tmp_path)
    summary = run_review(*inputs, *outputs)

    assert summary["review_status"] == "blocked_no_beta_data"
    assert summary["tester_records"] == 0
    assert summary["upload_success_rate"] is None
    assert summary["result_clarity_rate"] is None
    assert summary["rejected_result_clarity_rate"] is None
    assert all(path.exists() for path in outputs)
    assert "not_available" in outputs[3].read_text(encoding="utf-8")
    assert "Continue Sprint 29B" in outputs[0].read_text(encoding="utf-8")


def test_header_only_inputs_are_not_treated_as_beta_results(tmp_path):
    inputs, outputs = paths(tmp_path)
    headers = [
        ["tester_id", "invite_status"], ["tester_id", "consent_acknowledged"],
        ["assignment_id", "status"], ["feedback_id", "upload_success"],
        ["issue_id", "severity"],
    ]
    for path, fieldnames in zip(inputs, headers):
        write_csv(path, fieldnames)

    summary = run_review(*inputs, *outputs)

    assert summary["review_status"] == "blocked_no_beta_data"
    assert summary["feedback_records"] == 0
    assert summary["issue_records"] == 0
    assert "Zero is a record count" in outputs[0].read_text(encoding="utf-8")


def test_recorded_rows_drive_counts_and_safety_pause(tmp_path):
    inputs, outputs = paths(tmp_path)
    roster, consent, assignments, feedback, issues = inputs
    write_csv(roster, ["tester_id", "invite_status", "testing_status"], [{"tester_id": "t-1", "invite_status": "accepted", "testing_status": "completed"}])
    write_csv(consent, ["tester_id", "consent_acknowledged", "data_handling_acknowledged", "no_real_patient_data_acknowledged", "safety_limitations_acknowledged", "withdrawal_requested"], [{"tester_id": "t-1", "consent_acknowledged": "yes", "data_handling_acknowledged": "yes", "no_real_patient_data_acknowledged": "yes", "safety_limitations_acknowledged": "yes", "withdrawal_requested": "no"}])
    write_csv(assignments, ["assignment_id", "tester_id", "exercise_id", "status"], [{"assignment_id": "a-1", "tester_id": "t-1", "exercise_id": "bodyweight_squat", "status": "completed"}])
    write_csv(feedback, ["feedback_id", "device_model", "os_version", "exercise_tested", "upload_success", "analysis_status", "rejected_result_clear", "result_easy_to_understand", "privacy_safety_concern"], [{"feedback_id": "f-1", "device_model": "device", "os_version": "14", "exercise_tested": "bodyweight_squat", "upload_success": "yes", "analysis_status": "rejected", "rejected_result_clear": "yes", "result_easy_to_understand": "yes", "privacy_safety_concern": "no"}])
    write_csv(issues, ["issue_id", "severity", "privacy_safety_related", "issue_category"], [{"issue_id": "i-1", "severity": "critical", "privacy_safety_related": "yes", "issue_category": "network"}])

    summary = run_review(*inputs, *outputs)

    assert summary["review_status"] == "paused_for_safety_or_blocker_review"
    assert summary["consent_completion_rate"] == 1.0
    assert summary["upload_success_rate"] == 1.0
    assert summary["result_clarity_rate"] == 1.0
    assert summary["blocker_issue_count"] == 1
    assert summary["safety_privacy_issue_count"] == 1
    assert summary["network_issue_count"] == 1

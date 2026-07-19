import csv

from scripts.build_external_beta_monitoring_report import run_report


def write_csv(path, headers, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def paths(tmp_path):
    return [tmp_path / name for name in ("roster.csv", "consent.csv", "assignments.csv", "feedback.csv", "issues.csv")]


def test_missing_files_generate_not_started_report_without_fabricated_metrics(tmp_path):
    roster, consent, assignments, feedback, issues = paths(tmp_path)
    markdown = tmp_path / "monitoring.md"
    output_csv = tmp_path / "monitoring.csv"

    summary = run_report(roster, consent, assignments, feedback, issues, markdown, output_csv)

    assert summary["beta_status"] == "not_started"
    assert summary["tester_records"] == 0
    assert summary["invited_testers"] == 0
    assert summary["feedback_records"] == 0
    assert summary["issues_recorded"] == 0
    assert summary["consent_completion_rate"] is None
    assert "has not started" in markdown.read_text(encoding="utf-8")
    assert output_csv.read_text(encoding="utf-8").startswith("metric,value")


def test_header_only_files_remain_not_started(tmp_path):
    roster, consent, assignments, feedback, issues = paths(tmp_path)
    write_csv(roster, ["tester_id", "invite_status", "testing_status", "safety_privacy_flag"])
    write_csv(consent, ["tester_id", "consent_acknowledged"])
    write_csv(assignments, ["assignment_id", "tester_id", "status"])
    write_csv(feedback, ["feedback_id", "tester_alias", "analysis_status"])
    write_csv(issues, ["issue_id", "severity", "privacy_safety_related"])
    markdown = tmp_path / "monitoring.md"
    output_csv = tmp_path / "monitoring.csv"

    summary = run_report(roster, consent, assignments, feedback, issues, markdown, output_csv)

    assert summary["beta_status"] == "not_started"
    assert summary["assignment_records"] == 0
    assert summary["exercises_tested"] == "None recorded"
    assert "Not measured" in output_csv.read_text(encoding="utf-8")


def test_safety_privacy_issue_pauses_monitoring(tmp_path):
    roster, consent, assignments, feedback, issues = paths(tmp_path)
    write_csv(
        roster,
        ["tester_id", "invite_status", "testing_status", "safety_privacy_flag"],
        [{"tester_id": "beta-001", "invite_status": "accepted", "testing_status": "in_progress"}],
    )
    write_csv(
        consent,
        ["tester_id", "consent_acknowledged", "data_handling_acknowledged", "no_real_patient_data_acknowledged", "safety_limitations_acknowledged", "withdrawal_requested"],
        [{"tester_id": "beta-001", "consent_acknowledged": "yes", "data_handling_acknowledged": "yes", "no_real_patient_data_acknowledged": "yes", "safety_limitations_acknowledged": "yes", "withdrawal_requested": "no"}],
    )
    write_csv(assignments, ["assignment_id", "tester_id", "status"])
    write_csv(feedback, ["feedback_id", "privacy_safety_concern"])
    write_csv(
        issues,
        ["issue_id", "severity", "privacy_safety_related", "issue_category"],
        [{"issue_id": "issue-001", "severity": "critical", "privacy_safety_related": "yes", "issue_category": "privacy_security"}],
    )
    markdown = tmp_path / "monitoring.md"
    output_csv = tmp_path / "monitoring.csv"

    summary = run_report(roster, consent, assignments, feedback, issues, markdown, output_csv)

    assert summary["beta_status"] == "paused"
    assert summary["safety_privacy_flags"] == 1
    assert str(summary["go_no_go_alert"]).startswith("PAUSE")
    assert markdown.exists() and output_csv.exists()


def test_monitoring_separates_first_and_second_wave_records(tmp_path):
    roster, consent, assignments, feedback, issues = paths(tmp_path)
    second_assignments = tmp_path / "second_assignments.csv"
    first_assignments = tmp_path / "first_assignments.csv"
    write_csv(
        roster,
        ["tester_id", "beta_wave", "invite_status", "testing_status"],
        [
            {"tester_id": "first-1", "beta_wave": "first", "invite_status": "accepted", "testing_status": "completed"},
            {"tester_id": "second-1", "beta_wave": "second", "invite_status": "planned", "testing_status": "in_progress"},
        ],
    )
    write_csv(consent, ["tester_id", "consent_acknowledged"])
    write_csv(assignments, ["assignment_id", "tester_id", "status"])
    write_csv(
        second_assignments,
        ["assignment_id", "tester_id", "beta_wave", "status"],
        [{"assignment_id": "wave2-a1", "tester_id": "second-1", "beta_wave": "second", "status": "planned"}],
    )
    write_csv(
        first_assignments,
        ["assignment_id", "tester_id", "beta_wave", "status"],
        [{"assignment_id": "wave1-a1", "tester_id": "first-1", "beta_wave": "first", "status": "completed"}],
    )
    write_csv(
        feedback,
        ["feedback_id", "beta_wave"],
        [{"feedback_id": "f1", "beta_wave": "first"}, {"feedback_id": "f2", "beta_wave": "second"}],
    )
    write_csv(
        issues,
        ["issue_id", "beta_wave"],
        [{"issue_id": "i2", "beta_wave": "second"}],
    )

    summary = run_report(
        roster,
        consent,
        assignments,
        feedback,
        issues,
        tmp_path / "monitoring.md",
        tmp_path / "monitoring.csv",
        second_assignments,
        first_assignments,
    )

    assert summary["first_wave_tester_records"] == 1
    assert summary["first_wave_feedback_records"] == 1
    assert summary["first_wave_assignment_records"] == 1
    assert summary["second_wave_planned_testers"] == 1
    assert summary["second_wave_active_testers"] == 1
    assert summary["second_wave_assignment_records"] == 1
    assert summary["second_wave_feedback_records"] == 1
    assert summary["second_wave_issue_records"] == 1


def test_internal_pt_review_is_counted_without_starting_external_beta(tmp_path):
    roster, consent, assignments, feedback, issues = paths(tmp_path)
    internal = tmp_path / "internal.csv"
    write_csv(
        internal,
        ["review_id", "role", "test_type", "result_status"],
        [{
            "review_id": "internal-1",
            "role": "physical_therapist_internal_reviewer",
            "test_type": "internal_physical_device_qa",
            "result_status": "partial_pass",
        }],
    )
    summary = run_report(
        roster,
        consent,
        assignments,
        feedback,
        issues,
        tmp_path / "report.md",
        tmp_path / "report.csv",
        None,
        None,
        internal,
    )

    assert summary["beta_status"] == "not_started"
    assert summary["tester_records"] == 0
    assert summary["internal_reviewer_records"] == 1
    assert summary["internal_pt_physical_device_reviews"] == 1
    assert summary["internal_partial_pass_records"] == 1
    assert "not external beta evidence" in (tmp_path / "report.md").read_text(encoding="utf-8")

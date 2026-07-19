import csv

from scripts.summarize_external_beta_feedback import run_summary


def write_csv(path, headers, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def test_empty_external_beta_templates_generate_no_go_summary(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(feedback, ["tester_alias", "exercise_tested", "upload_success"])
    write_csv(issues, ["severity", "issue_category", "description"])

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_sessions"] == 0
    assert str(summary["recommendation"]).startswith("NO-GO")
    assert "not clinical validation" in markdown.read_text(encoding="utf-8")
    assert output_csv.read_text(encoding="utf-8").startswith("metric,value")


def test_external_beta_summary_counts_rates_and_privacy_flags(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(
        feedback,
        [
            "tester_alias", "exercise_tested", "upload_success", "analysis_status",
            "rejected_result_clear", "issue_type", "issue_description", "severity",
            "privacy_safety_concern", "suggested_improvement", "device_model", "os_version",
        ],
        [
            {
                "tester_alias": "beta-a", "exercise_tested": "bodyweight_squat",
                "upload_success": "yes", "analysis_status": "rejected",
                "rejected_result_clear": "yes", "device_model": "Pixel Test",
                "os_version": "Android 16", "issue_type": "upload",
            },
            {
                "tester_alias": "beta-b", "exercise_tested": "knee_extension",
                "upload_success": "no", "analysis_status": "error",
                "issue_type": "privacy_security", "issue_description": "Sensitive URL appeared",
                "privacy_safety_concern": "yes", "suggested_improvement": "Redact URLs",
                "device_model": "Galaxy Test", "os_version": "Android 15",
            },
        ],
    )
    write_csv(
        issues,
        ["severity", "issue_category", "privacy_safety_related", "description"],
        [{"severity": "high", "issue_category": "network", "description": "Retry failed"}],
    )

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_testers"] == 2
    assert summary["number_of_devices"] == 2
    assert summary["upload_success_rate"] == 0.5
    assert summary["rejected_result_clarity_rate"] == 1.0
    assert summary["blocker_high_count"] == 1
    assert summary["safety_privacy_count"] == 1
    assert str(summary["recommendation"]).startswith("NO-GO")


def test_partially_filled_external_beta_row_is_safe(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(
        feedback,
        ["tester_alias", "device_model", "os_version", "exercise_tested", "upload_success"],
        [{"tester_alias": "beta-a", "device_model": "Test Phone"}],
    )
    write_csv(issues, ["severity", "issue_category", "description"])

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_sessions"] == 1
    assert summary["number_of_devices"] == 1
    assert summary["upload_success_rate"] is None


def test_issue_only_alias_device_and_exercise_are_counted(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(feedback, ["tester_alias", "device_model", "exercise_tested"])
    write_csv(
        issues,
        ["reported_by_alias", "device_model", "exercise", "severity", "issue_category"],
        [{
            "reported_by_alias": "beta-issue-reporter",
            "device_model": "Android Test Device",
            "exercise": "sit_to_stand",
            "severity": "medium",
            "issue_category": "mobile_ui",
        }],
    )

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_testers"] == 1
    assert summary["number_of_devices"] == 1
    assert "sit_to_stand (1)" == summary["exercises_tested"]


def test_build_registry_and_optional_qa_are_summarized(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    builds = tmp_path / "builds.csv"
    qa = tmp_path / "qa.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(feedback, ["tester_alias"])
    write_csv(issues, ["severity", "description"])
    write_csv(
        builds,
        ["rc_version", "build_status"],
        [{"rc_version": "0.28.0-rc.1", "build_status": "blocked_not_submitted"}],
    )
    write_csv(qa, ["check_id", "status"], [{"check_id": "health", "status": "pass"}, {"check_id": "device", "status": "blocked"}])

    summary = run_summary(feedback, issues, markdown, output_csv, builds, qa)

    assert summary["builds_recorded"] == 1
    assert summary["blocked_build_count"] == 1
    assert summary["latest_rc_version"] == "0.28.0-rc.1"
    assert summary["qa_pass_count"] == 1
    assert summary["qa_blocked_count"] == 1
    assert "Empty feedback is not evidence" in markdown.read_text(encoding="utf-8")


def test_summary_separates_first_and_second_wave_records(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(
        feedback,
        ["feedback_id", "beta_wave"],
        [{"feedback_id": "f1", "beta_wave": "first"}, {"feedback_id": "f2", "beta_wave": "second"}],
    )
    write_csv(
        issues,
        ["issue_id", "beta_wave"],
        [{"issue_id": "i1", "beta_wave": "first"}, {"issue_id": "i2", "beta_wave": "wave_2"}],
    )

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["first_wave_feedback_records"] == 1
    assert summary["first_wave_issue_records"] == 1
    assert summary["second_wave_feedback_records"] == 1
    assert summary["second_wave_issue_records"] == 1

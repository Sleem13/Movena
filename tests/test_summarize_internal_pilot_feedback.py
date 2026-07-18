import csv

from scripts.summarize_internal_pilot_feedback import run_summary


def write_csv(path, headers, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def test_empty_pilot_templates_generate_no_go_summary(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(feedback, ["tester_id_or_alias", "exercise_tested", "upload_success"])
    write_csv(issues, ["severity", "issue_category", "description"])

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_testers"] == 0
    assert summary["number_of_devices"] == 0
    assert summary["number_of_sessions"] == 0
    assert str(summary["recommendation"]).startswith("NO-GO")
    assert "not clinical validation" in markdown.read_text(encoding="utf-8")
    assert output_csv.read_text(encoding="utf-8").startswith("metric,value")


def test_pilot_summary_counts_rates_and_safety_gate(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(
        feedback,
        [
            "tester_id_or_alias", "exercise_tested", "upload_success", "analysis_status",
            "rejected_result_clear", "issue_type", "issue_description", "severity",
            "suggested_improvement", "device_model", "os_version",
        ],
        [
            {
                "tester_id_or_alias": "tester-a", "exercise_tested": "bodyweight_squat",
                "upload_success": "yes", "analysis_status": "rejected",
                "rejected_result_clear": "yes", "issue_type": "upload",
                "device_model": "Pixel Test", "os_version": "Android 16",
            },
            {
                "tester_id_or_alias": "tester-b", "exercise_tested": "knee_extension",
                "upload_success": "no", "analysis_status": "error",
                "issue_type": "privacy_security", "issue_description": "Sensitive URL appeared",
                "severity": "safety_privacy", "suggested_improvement": "Redact URLs",
                "device_model": "Galaxy Test", "os_version": "Android 15",
            },
        ],
    )
    write_csv(
        issues,
        ["severity", "issue_category", "description"],
        [{"severity": "high", "issue_category": "network", "description": "Retry failed"}],
    )

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_testers"] == 2
    assert summary["number_of_devices"] == 2
    assert summary["number_of_sessions"] == 2
    assert summary["upload_success_rate"] == 0.5
    assert summary["rejected_result_clarity_rate"] == 1.0
    assert summary["blocker_high_count"] == 1
    assert summary["safety_privacy_count"] == 1
    assert str(summary["recommendation"]).startswith("NO-GO")


def test_partially_filled_feedback_row_is_safe(tmp_path):
    feedback = tmp_path / "feedback.csv"
    issues = tmp_path / "issues.csv"
    markdown = tmp_path / "summary.md"
    output_csv = tmp_path / "summary.csv"
    write_csv(
        feedback,
        ["tester_id_or_alias", "device_model", "os_version", "exercise_tested", "upload_success"],
        [{"tester_id_or_alias": "tester-a", "device_model": "Test Phone"}],
    )
    write_csv(issues, ["severity", "issue_category", "description"])

    summary = run_summary(feedback, issues, markdown, output_csv)

    assert summary["number_of_sessions"] == 1
    assert summary["number_of_devices"] == 1
    assert summary["upload_success_rate"] is None

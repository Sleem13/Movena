"""Therapist-friendly PDF session report generation."""

from datetime import datetime, timezone
from pathlib import Path

from app.schemas.analysis_schema import AnalysisResponse
from app.services.feedback_service import DISCLAIMER


class ReportGenerationError(RuntimeError):
    pass


def generate_session_report(report: AnalysisResponse, output_path: Path) -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        from reportlab.lib import colors
    except ImportError as exc:
        raise ReportGenerationError(
            "ReportLab is required. Run python -m pip install -r requirements.txt."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    display_names = {
        "bodyweight_squat": "Bodyweight Squat",
        "sit_to_stand": "Sit-to-Stand",
        "knee_extension": "Knee Extension",
        "shoulder_abduction": "Shoulder Abduction",
        "shoulder_flexion": "Shoulder Flexion",
        "hip_abduction": "Hip Abduction",
        "walking_gait_screen": "Walking Gait Screen",
        "balance": "Static Balance Screen",
        "push_up": "Push-Up",
        "shoulder_press": "Shoulder Press",
        "bicep_curl": "Bicep Curl",
        "hammer_curl": "Hammer Curl",
    }
    exercise_name = report.exercise_name or display_names.get(report.exercise, report.exercise.replace("_", " ").title())
    story = [
        Paragraph(
            f"PhysioVision AI - {exercise_name} Session Report",
            styles["Title"],
        ),
        Spacer(1, 5 * mm),
        Paragraph("Patient: ____________________ &nbsp;&nbsp; Session: ____________________", styles["BodyText"]),
        Paragraph(
            "Generated: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            styles["BodyText"],
        ),
        Spacer(1, 5 * mm),
    ]
    data = [
        ["Exercise", exercise_name],
        ["Total repetitions", str(report.total_reps)],
        ["Movement score", "Not scored" if report.movement_score is None else f"{report.movement_score}/100"],
        ["Average trunk angle", f"{report.average_trunk_angle:.2f} deg"],
    ]
    if report.exercise in {"shoulder_abduction", "shoulder_flexion"}:
        data.insert(3, ["Average shoulder angle", f"{(report.average_shoulder_angle or 0):.2f} deg"])
    elif report.exercise == "hip_abduction":
        data.insert(3, ["Average hip-abduction angle", f"{(report.average_hip_abduction_angle or 0):.2f} deg"])
    elif report.exercise in {"push_up", "shoulder_press", "bicep_curl", "hammer_curl"}:
        data.insert(3, ["Average elbow angle", f"{(report.average_elbow_angle or 0):.2f} deg"])
    else:
        data[3:3] = [["Average knee angle", f"{report.average_knee_angle:.2f} deg"], ["Average hip angle", f"{report.average_hip_angle:.2f} deg"]]
    table = Table(data, colWidths=[55 * mm, 110 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F3F2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 5 * mm)])

    def section(title: str, items: list[str], empty: str) -> None:
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Paragraph("<br/>".join(f"- {item}" for item in items) if items else empty, styles["BodyText"]))
        story.append(Spacer(1, 3 * mm))

    section("Detected observations", [item.replace("_", " ") for item in report.detected_issues], "No major movement issue was flagged.")
    section("Feedback", report.feedback, "No feedback available.")
    section("Known limitations", report.limitations, "No limitations supplied.")
    story.append(Paragraph("Medical disclaimer", styles["Heading2"]))
    story.append(Paragraph(DISCLAIMER, styles["BodyText"]))

    try:
        SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm).build(story)
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        raise ReportGenerationError("Unable to generate session PDF.") from exc
    return output_path

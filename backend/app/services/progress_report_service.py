"""Generate patient progress reports from persisted care and analysis data."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AdherenceEntry, AnalysisSession, Appointment, ClinicalSessionNote, PatientProfile,
)


def generate_progress_report(
    db: Session, patient: PatientProfile, period_start: date, period_end: date,
    output_path: Path,
) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    adherence = list(db.scalars(select(AdherenceEntry).where(
        AdherenceEntry.patient_id == patient.patient_id,
        AdherenceEntry.scheduled_date.between(period_start, period_end),
    ).order_by(AdherenceEntry.scheduled_date.asc())).all())
    appointments = list(db.scalars(select(Appointment).where(
        Appointment.patient_id == patient.patient_id,
        Appointment.starts_at >= datetime.combine(period_start, datetime.min.time(), tzinfo=timezone.utc),
        Appointment.starts_at <= datetime.combine(period_end, datetime.max.time(), tzinfo=timezone.utc),
    ).order_by(Appointment.starts_at.asc())).all())
    analyses = list(db.scalars(select(AnalysisSession).where(
        AnalysisSession.patient_id == patient.patient_id,
        AnalysisSession.created_at >= datetime.combine(period_start, datetime.min.time(), tzinfo=timezone.utc),
        AnalysisSession.created_at <= datetime.combine(period_end, datetime.max.time(), tzinfo=timezone.utc),
    ).order_by(AnalysisSession.created_at.asc())).all())
    notes = list(db.scalars(select(ClinicalSessionNote).join(
        Appointment, ClinicalSessionNote.appointment_id == Appointment.appointment_id,
    ).where(
        Appointment.patient_id == patient.patient_id,
        ClinicalSessionNote.patient_visible.is_(True),
    ).order_by(ClinicalSessionNote.created_at.asc())).all())

    completed = sum(row.completion_status in {"completed", "partial"} for row in adherence)
    pain_before = [row.pain_before for row in adherence if row.pain_before is not None]
    pain_after = [row.pain_after for row in adherence if row.pain_after is not None]
    exertion = [row.perceived_exertion for row in adherence if row.perceived_exertion is not None]
    follow_up_responses = sum(row.response_state == "clinical_follow_up" for row in adherence)
    pending_response_reviews = sum(row.clinician_review_required for row in adherence)
    scores = [row.movement_score for row in analyses if row.movement_score is not None]
    appointment_counts = Counter(row.status for row in appointments)

    styles = getSampleStyleSheet()
    story = [
        Paragraph("PhysioVision AI - Patient Progress Report", styles["Title"]),
        Spacer(1, 4 * mm),
        Paragraph(f"Patient: {patient.display_name}", styles["BodyText"]),
        Paragraph(f"Period: {period_start.isoformat()} to {period_end.isoformat()}", styles["BodyText"]),
        Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", styles["BodyText"]),
        Spacer(1, 5 * mm),
    ]
    summary = [
        ["Metric", "Value"],
        ["Recorded home exercises", str(len(adherence))],
        ["Completed or partial", f"{completed} ({round(completed / len(adherence) * 100)}%)" if adherence else "No entries"],
        ["Average pain before", f"{mean(pain_before):.1f}/10" if pain_before else "Not recorded"],
        ["Average pain after", f"{mean(pain_after):.1f}/10" if pain_after else "Not recorded"],
        ["Average reported effort", f"{mean(exertion):.1f}/10" if exertion else "Not recorded"],
        ["Exercise responses needing follow-up", str(follow_up_responses)],
        ["Pending therapist response reviews", str(pending_response_reviews)],
        ["Appointments", str(len(appointments))],
        ["Completed appointments", str(appointment_counts.get("completed", 0))],
        ["Movement analyses", str(len(analyses))],
        ["Average movement score", f"{mean(scores):.1f}/100" if scores else "Not scored"],
    ]
    table = Table(summary, colWidths=[75 * mm, 90 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B2F6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#EAF5F4")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([table, Spacer(1, 5 * mm)])
    story.append(Paragraph("Patient-visible therapist notes", styles["Heading2"]))
    if notes:
        for note in notes:
            story.append(Paragraph(f"- {note.summary}", styles["BodyText"]))
            if note.recommendations:
                story.append(Paragraph(f"Recommendations: {note.recommendations}", styles["BodyText"]))
    else:
        story.append(Paragraph("No patient-visible notes were recorded in this report.", styles["BodyText"]))
    story.extend([
        Spacer(1, 5 * mm),
        Paragraph("Important limitation", styles["Heading2"]),
        Paragraph(
            "This report summarizes recorded activity, patient-reported exercise responses, and computer-vision observations. "
            "It does not diagnose a condition, prescribe treatment, or establish clinical improvement.",
            styles["BodyText"],
        ),
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(output_path), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
    ).build(story)
    return output_path


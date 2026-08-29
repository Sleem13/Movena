"""Enqueue appointment reminders and deliver retryable care emails."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import SessionLocal
from app.services.notification_service import deliver_pending_emails, enqueue_due_appointment_reminders, enqueue_low_adherence_alerts


def main() -> None:
    with SessionLocal() as db:
        reminders = enqueue_due_appointment_reminders(db)
        adherence_alerts = enqueue_low_adherence_alerts(db)
        sent, failed = deliver_pending_emails(db)
    print({"reminders_created": reminders, "adherence_alerts_created": adherence_alerts, "emails_sent": sent, "emails_failed": failed})


if __name__ == "__main__":
    main()

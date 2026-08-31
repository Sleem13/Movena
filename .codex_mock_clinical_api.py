import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PATIENT = {"user_id": "patient-user", "email": "patient@test.local", "full_name": "Patient One", "role": "patient"}
THERAPIST = {"user_id": "therapist-user", "email": "therapist@test.local", "full_name": "Therapist One", "role": "therapist"}
ENTRY = {
    "adherence_id": "entry-1", "plan_item_id": "item-1", "scheduled_date": "2026-08-31",
    "completion_status": "partial", "pain_before": 2, "pain_after": 5,
    "difficulty": 3, "fatigue": 3, "perceived_exertion": 9,
    "symptoms_changed": True, "stopped_due_to_symptoms": True,
    "symptom_flags": ["dizziness"], "response_state": "clinical_follow_up",
    "supportive_instruction": "Do not progress this exercise. Contact your treating clinician for review.",
    "clinician_review_required": True, "reviewed_at": None,
    "review_disposition": None, "analysis_session_id": None, "note": "Stopped when dizzy.",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:4173")
        self.send_header("Access-Control-Allow-Headers", "Authorization,Content-Type,Idempotency-Key")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PATCH,PUT,DELETE,OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({})

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/v1/auth/me":
            user = THERAPIST if "therapist-token" in self.headers.get("Authorization", "") else PATIENT
            return self.send_json(user)
        if path == "/api/v1/patient/today":
            return self.send_json({
                "patient_id": "profile-1", "date": "2026-08-31", "plan_title": "Graded activity",
                "plan_items": [{
                    "item_id": "item-1", "exercise_id": "sit_to_stand", "sets": 2, "reps": 6,
                    "duration_minutes": 10, "rest_interval_seconds": 60,
                    "instructions": "Use the stable chair and prescribed support.",
                    "precautions": "Stop if symptoms change.", "symptom_flags": [],
                    "response_state": "not_assessed",
                }],
                "unread_notifications": 0, "adherence_percent_7d": 75, "average_pain_7d": 3,
                "completed_count_7d": 3, "partial_count_7d": 1, "missed_count_7d": 1,
            })
        if path in {
            "/api/v1/patient/appointments", "/api/v1/patient/notifications",
            "/api/v1/catalog/services", "/api/v1/catalog/packages", "/api/v1/therapist/appointments",
        }:
            return self.send_json([])
        if path == "/api/v1/therapist/dashboard":
            return self.send_json({
                "total_patients": 1, "total_sessions": 4, "low_confidence_sessions": 0,
                "recent_sessions": [], "common_detected_issues": [], "sessions_by_exercise": {},
                "program_adherence_percent": 75, "prototype_warning": "Clinical review remains required.",
            })
        if path == "/api/v1/therapist/patients":
            return self.send_json([{
                "patient_id": "profile-1", "display_name": "Patient One", "age_group": "adult",
                "clinical_group": "post-operative rehabilitation", "session_count": 4,
                "created_at": "2026-08-01T00:00:00Z", "updated_at": "2026-08-31T00:00:00Z",
            }])
        if path == "/api/v1/therapist/adherence-alerts":
            return self.send_json([{
                "notification_id": "notice-1", "kind": "exercise_response_follow_up",
                "title": "Exercise response review needed",
                "body": "Patient One recorded an exercise response that needs professional review.",
                "created_at": "2026-08-31T16:00:00Z",
            }])
        if path == "/api/v1/therapist/patients/profile-1":
            return self.send_json({
                "patient_id": "profile-1", "display_name": "Patient One", "age_group": "adult",
                "clinical_group": "post-operative rehabilitation", "session_count": 4,
                "created_at": "2026-08-01T00:00:00Z", "updated_at": "2026-08-31T00:00:00Z",
                "notes": None, "progress": {"total_sessions": 4},
                "prototype_warning": "Clinical review remains required.",
            })
        if path.endswith("/sessions") or path.endswith("/exercise-plans"):
            return self.send_json([])
        if path.endswith("/progress"):
            return self.send_json({
                "total_sessions": 4, "average_movement_score": 82,
                "movement_score_observation_count": 4, "average_analysis_confidence": 0.88,
                "analysis_confidence_observation_count": 4, "low_confidence_session_count": 0,
                "exercise_comparisons": [],
            })
        if path.endswith("/adherence"):
            return self.send_json([ENTRY])
        self.send_json({"detail": "not found"}, 404)

    def do_POST(self):
        global ENTRY
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if path == "/api/v1/auth/login":
            therapist = "therapist" in payload.get("email", "")
            user = THERAPIST if therapist else PATIENT
            return self.send_json({
                "access_token": "therapist-token" if therapist else "patient-token",
                "token_type": "bearer", "user": user,
            })
        if path == "/api/v1/patient/adherence":
            ENTRY = {**ENTRY, **payload}
            return self.send_json(ENTRY, 201)
        if path.endswith("/acknowledge"):
            ENTRY = {
                **ENTRY, "clinician_review_required": False,
                "reviewed_at": "2026-08-31T16:30:00Z", "reviewed_by_user_id": "therapist-user",
                "review_disposition": payload.get("disposition"), "review_note": payload.get("note"),
            }
            return self.send_json(ENTRY)
        if path == "/api/v1/auth/logout":
            return self.send_json({"status": "success"})
        self.send_json({"detail": "not found"}, 404)


ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()

"""Contracts for patient care, scheduling, notifications, catalog, and billing."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


CompletionStatus = Literal["completed", "partial", "not_completed"]
AppointmentStatus = Literal["scheduled", "confirmed", "completed", "cancelled", "no_show"]
ExerciseSymptomFlag = Literal[
    "pain_increase", "dizziness", "faintness", "unusual_shortness_of_breath",
    "chest_discomfort", "new_numbness_or_weakness", "instability", "other",
]
ExerciseResponseState = Literal["not_assessed", "within_reported_tolerance", "clinical_follow_up"]


class CarePlanItem(BaseModel):
    plan_title: str | None = None
    created_by_name: str | None = None
    item_id: str
    exercise_id: str
    sets: int
    reps: int
    duration_minutes: int | None = None
    rest_interval_seconds: int | None = None
    tempo: str | None = None
    instructions: str | None = None
    precautions: str | None = None
    target_rom_degrees: float | None = None
    target_score: float | None = None
    requested_media_upload: bool = False
    requires_ai_analysis: bool = False
    completion_status: CompletionStatus | None = None
    pain_before: int | None = None
    pain_after: int | None = None
    difficulty: int | None = None
    fatigue: int | None = None
    perceived_exertion: int | None = None
    symptoms_changed: bool = False
    stopped_due_to_symptoms: bool = False
    symptom_flags: list[ExerciseSymptomFlag] = Field(default_factory=list)
    response_state: ExerciseResponseState = "not_assessed"
    supportive_instruction: str | None = None
    clinician_review_required: bool = False
    reviewed_at: datetime | None = None
    patient_comment: str | None = None
    analysis_session_id: str | None = None


class AppointmentSummary(BaseModel):
    appointment_id: str
    patient_id: str
    therapist_user_id: str
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus
    delivery_mode: Literal["video", "in_person"]
    payment_status: str
    can_join: bool = False


class NotificationSummary(BaseModel):
    notification_id: str
    kind: str
    title: str
    body: str
    action_url: str | None = None
    read_at: datetime | None = None
    created_at: datetime


class PatientTodayResponse(BaseModel):
    patient_id: str
    date: date
    plan_title: str | None = None
    plan_items: list[CarePlanItem] = Field(default_factory=list)
    upcoming_appointment: AppointmentSummary | None = None
    unread_notifications: int = 0
    adherence_percent_7d: float | None = None
    average_pain_7d: float | None = None
    completed_count_7d: int = 0
    partial_count_7d: int = 0
    missed_count_7d: int = 0


class AdherenceCreate(BaseModel):
    plan_item_id: str
    scheduled_date: date
    completion_status: CompletionStatus
    pain_before: int | None = Field(default=None, ge=0, le=10)
    pain_after: int | None = Field(default=None, ge=0, le=10)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    fatigue: int | None = Field(default=None, ge=1, le=5)
    perceived_exertion: int | None = Field(default=None, ge=0, le=10)
    symptoms_changed: bool = False
    stopped_due_to_symptoms: bool = False
    symptom_flags: list[ExerciseSymptomFlag] = Field(default_factory=list, max_length=8)
    safety_acknowledged: bool = False
    note: str | None = Field(default=None, max_length=1000)
    analysis_session_id: str | None = Field(default=None, max_length=36)

    @model_validator(mode="after")
    def acknowledge_symptom_scope(self):
        if (self.symptoms_changed or self.stopped_due_to_symptoms or self.symptom_flags) and not self.safety_acknowledged:
            raise ValueError("Safety acknowledgement is required when symptoms are reported.")
        return self


class AdherenceDetail(AdherenceCreate):
    adherence_id: str
    patient_id: str
    alert_created: bool = False
    response_state: ExerciseResponseState
    supportive_instruction: str
    clinician_review_required: bool
    reviewed_at: datetime | None = None
    reviewed_by_user_id: str | None = None
    review_disposition: str | None = None
    review_note: str | None = None
    created_at: datetime
    updated_at: datetime


class ExerciseResponseReview(BaseModel):
    disposition: Literal[
        "contacted_patient", "plan_modified", "appointment_scheduled",
        "referred_for_medical_review", "reviewed_no_change",
    ]
    note: str | None = Field(default=None, max_length=2000)
    clinician_attestation: bool

    @model_validator(mode="after")
    def require_attestation_and_context(self):
        if not self.clinician_attestation:
            raise ValueError("Clinical review attestation is required.")
        if self.disposition == "reviewed_no_change" and not (self.note or "").strip():
            raise ValueError("Document a rationale when no change is needed.")
        return self


class AvailabilityCreate(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_minute: int = Field(ge=0, le=1439)
    end_minute: int = Field(ge=1, le=1440)
    timezone_name: str = Field(default="Africa/Cairo", max_length=64)

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_minute <= self.start_minute:
            raise ValueError("End time must be after start time.")
        return self


class AvailabilityDetail(AvailabilityCreate):
    availability_id: str
    therapist_user_id: str
    is_active: bool
    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    patient_id: str
    therapist_user_id: str
    service_id: str | None = None
    starts_at: datetime
    ends_at: datetime
    delivery_mode: Literal["video", "in_person"] = "video"

    @model_validator(mode="after")
    def validate_range(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Appointment timestamps must include a timezone.")
        if self.ends_at <= self.starts_at:
            raise ValueError("Appointment end must be after its start.")
        return self


class AppointmentUpdate(BaseModel):
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: AppointmentStatus | None = None
    cancellation_reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_update(self):
        if bool(self.starts_at) != bool(self.ends_at):
            raise ValueError("Start and end must be updated together.")
        if self.starts_at and (
            self.starts_at.tzinfo is None or self.ends_at.tzinfo is None or self.ends_at <= self.starts_at
        ):
            raise ValueError("Updated appointment timestamps must be timezone-aware and ordered.")
        if self.status == "cancelled" and not self.cancellation_reason:
            raise ValueError("Cancellation reason is required.")
        return self


class AppointmentJoinResponse(BaseModel):
    appointment_id: str
    room_url: str
    meeting_token: str
    expires_at: datetime


class ClinicalNoteCreate(BaseModel):
    summary: str = Field(min_length=1, max_length=10000)
    recommendations: str | None = Field(default=None, max_length=10000)
    patient_visible: bool = False


class ClinicalNoteDetail(ClinicalNoteCreate):
    note_id: str
    appointment_id: str
    therapist_user_id: str
    created_at: datetime
    updated_at: datetime
    author_name: str | None = None
    model_config = {"from_attributes": True}


class ServiceOfferingCreate(BaseModel):
    name_en: str = Field(min_length=1, max_length=120)
    name_ar: str = Field(min_length=1, max_length=120)
    description_en: str | None = Field(default=None, max_length=2000)
    description_ar: str | None = Field(default=None, max_length=2000)
    duration_minutes: int = Field(ge=10, le=240)
    price_minor: int = Field(ge=0, le=100_000_000)


class ServiceOfferingDetail(ServiceOfferingCreate):
    service_id: str
    currency: str = "EGP"
    is_active: bool
    model_config = {"from_attributes": True}


class PackageOfferingCreate(BaseModel):
    name_en: str = Field(min_length=1, max_length=120)
    name_ar: str = Field(min_length=1, max_length=120)
    sessions_count: int = Field(ge=1, le=100)
    validity_days: int = Field(ge=1, le=730)
    price_minor: int = Field(ge=0, le=100_000_000)


class PackageOfferingDetail(PackageOfferingCreate):
    package_id: str
    currency: str = "EGP"
    is_active: bool
    model_config = {"from_attributes": True}


class CheckoutCreate(BaseModel):
    service_id: str | None = None
    package_id: str | None = None
    appointment_id: str | None = None
    billing_phone: str = Field(pattern=r"^\+?20[0-9]{10}$")

    @model_validator(mode="after")
    def exactly_one_product(self):
        if bool(self.service_id) == bool(self.package_id):
            raise ValueError("Choose exactly one service or package.")
        return self


class CheckoutResponse(BaseModel):
    order_id: str
    amount_minor: int
    currency: str
    status: str
    payment_url: str | None = None


class RefundCreate(BaseModel):
    payment_id: str
    amount_minor: int = Field(gt=0)
    reason: str = Field(min_length=3, max_length=1000)


class AssignmentCreate(BaseModel):
    therapist_user_id: str
    patient_id: str
    reason: str | None = Field(None, max_length=1000)


class AssignmentDetail(AssignmentCreate):
    assignment_id: str
    status: str
    assigned_at: datetime
    model_config = {"from_attributes": True}


class NotificationPreferenceUpdate(BaseModel):
    care_email_enabled: bool = True


class PatientHealthProfileUpdate(BaseModel):
    emergency_contact_name: str | None = Field(default=None, max_length=120)
    emergency_contact_phone: str | None = Field(default=None, max_length=32)
    medical_summary: str | None = Field(default=None, max_length=5000)
    precautions: str | None = Field(default=None, max_length=5000)


class ConsentUpdate(BaseModel):
    consent_type: Literal["privacy", "terms", "care_data", "media_upload"]
    accepted: bool
    version: str = Field(min_length=1, max_length=32)


class DataRightsRequestCreate(BaseModel):
    request_type: Literal["export", "correction", "deletion"]
    details: str | None = Field(default=None, max_length=5000)

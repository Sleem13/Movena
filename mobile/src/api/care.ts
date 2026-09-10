import { apiRequest } from "@/src/api/client";

export type PlanItem = {
  plan_title?: string | null;
  created_by_name?: string | null;
  item_id: string;
  exercise_id: string;
  sets: number;
  reps: number;
  duration_minutes?: number | null;
  rest_interval_seconds?: number | null;
  tempo?: string | null;
  target_rom_degrees?: number | null;
  target_score?: number | null;
  instructions?: string | null;
  precautions?: string | null;
  requested_media_upload?: boolean;
  requires_ai_analysis?: boolean;
  completion_status?: string | null;
  pain_before?: number | null;
  pain_after?: number | null;
  difficulty?: number | null;
  fatigue?: number | null;
  perceived_exertion?: number | null;
  symptoms_changed?: boolean;
  stopped_due_to_symptoms?: boolean;
  symptom_flags?: string[];
  response_state?: string;
  supportive_instruction?: string | null;
  clinician_review_required?: boolean;
  reviewed_at?: string | null;
  patient_comment?: string | null;
  analysis_session_id?: string | null;
};
export type Appointment = {
  appointment_id: string;
  patient_id?: string;
  therapist_user_id?: string;
  starts_at: string;
  ends_at: string;
  status: string;
  delivery_mode: string;
  can_join: boolean;
};
export type Today = {
  patient_id: string;
  date: string;
  plan_title?: string | null;
  plan_items: PlanItem[];
  upcoming_appointment?: Appointment | null;
  unread_notifications: number;
  adherence_percent_7d?: number | null;
  average_pain_7d?: number | null;
  completed_count_7d: number;
  partial_count_7d: number;
  missed_count_7d: number;
};
export type CareNotification = {
  notification_id: string;
  kind: string;
  title: string;
  body: string;
  action_url?: string | null;
  read_at?: string | null;
  created_at: string;
};
export type Connection = {
  assignment_id: string;
  therapist_user_id: string;
  patient_id: string;
  therapist_name: string;
  patient_name: string;
  status: string;
  source: string;
  assigned_at: string;
};
export type CareInvitation = {
  invitation_id: string;
  email: string;
  therapist_name: string;
  status: string;
  expires_at: string;
  delivery_status: string;
};
export type PatientSummary = {
  patient_id: string;
  display_name: string;
  clinical_group?: string | null;
  session_count: number;
  latest_session_date?: string | null;
};
export type PatientDetail = PatientSummary & { notes?: string | null; progress: PatientProgress };
export type PatientProgress = {
  total_sessions: number;
  average_movement_score?: number | null;
  average_analysis_confidence?: number | null;
  latest_session_date?: string | null;
  low_confidence_session_count: number;
};
export type AdherenceResponse = {
  adherence_id: string;
  patient_id: string;
  plan_item_id: string;
  scheduled_date: string;
  completion_status: string;
  pain_before?: number | null;
  pain_after?: number | null;
  difficulty?: number | null;
  fatigue?: number | null;
  perceived_exertion?: number | null;
  symptoms_changed: boolean;
  stopped_due_to_symptoms: boolean;
  symptom_flags: string[];
  response_state: string;
  supportive_instruction?: string | null;
  clinician_review_required: boolean;
  reviewed_at?: string | null;
  review_disposition?: string | null;
  note?: string | null;
};
export type TherapistAppointment = Appointment & { patient_id: string; therapist_user_id: string };
export type CoachingGoal = { goal_id: string; title: string; specific_action: string; measurement: string; why_important: string; target_date: string; progress_percent: number; status: string };
export type CoachingDashboard = { goals: CoachingGoal[]; action_plans: { action_plan_id: string; action_step: string; frequency: string; review_date: string; status: string }[]; summary: { active_goals: number; completed_goals: number; check_ins_30d: number; follow_up_needed: number } };
export type CatalogItem = {
  service_id?: string;
  package_id?: string;
  name_en: string;
  name_ar: string;
  price_minor: number;
  currency: string;
  sessions_count?: number;
};

export const getToday = () =>
  apiRequest<Today>("/api/v1/patient/today", {}, true);
export const getAppointments = () =>
  apiRequest<Appointment[]>("/api/v1/patient/appointments", {}, true);
export const getNotifications = () =>
  apiRequest<CareNotification[]>("/api/v1/patient/notifications", {}, true);
export const markNotificationRead = (id: string) =>
  apiRequest<CareNotification>(`/api/v1/patient/notifications/${encodeURIComponent(id)}/read`, { method: "POST" }, true);
export const logAdherence = (payload: object, idempotencyKey = `${Date.now()}-${Math.random()}`) =>
  apiRequest(
    "/api/v1/patient/adherence",
    {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(payload),
    },
    true,
  );
export const joinAppointment = (id: string) =>
  apiRequest<{ room_url: string; meeting_token: string }>(
    `/api/v1/scheduling/appointments/${encodeURIComponent(id)}/join`,
    {},
    true,
  );
export async function getCatalog() {
  const [services, packages] = await Promise.all([
    apiRequest<CatalogItem[]>("/api/v1/catalog/services"),
    apiRequest<CatalogItem[]>("/api/v1/catalog/packages"),
  ]);
  return { services, packages };
}
export const checkout = (payload: object) =>
  apiRequest<{ payment_url?: string }>(
    "/api/v1/checkout",
    {
      method: "POST",
      headers: { "Idempotency-Key": `${Date.now()}-${Math.random()}` },
      body: JSON.stringify(payload),
    },
    true,
  );

export const getConnections = () => apiRequest<Connection[]>("/api/v1/connections", {}, true);
export const getInvitations = () => apiRequest<CareInvitation[]>("/api/v1/care-invitations", {}, true);
export const respondToInvitation = (id: string, action: "accept" | "decline") => apiRequest<CareInvitation>(`/api/v1/care-invitations/${encodeURIComponent(id)}/respond`, { method: "POST", body: JSON.stringify({ action }) }, true);
export const invitePatient = (email: string) => apiRequest<CareInvitation>("/api/v1/care-invitations", { method: "POST", body: JSON.stringify({ email }) }, true);
export const getPatients = () => apiRequest<PatientSummary[]>("/api/v1/therapist/patients", {}, true);
export const getPatient = (id: string) => apiRequest<PatientDetail>(`/api/v1/therapist/patients/${encodeURIComponent(id)}`, {}, true);
export const getPatientAdherence = (id: string) => apiRequest<AdherenceResponse[]>(`/api/v1/therapist/patients/${encodeURIComponent(id)}/adherence`, {}, true);
export const acknowledgeResponse = (patientId: string, adherenceId: string, payload: object) => apiRequest(`/api/v1/therapist/patients/${encodeURIComponent(patientId)}/adherence/${encodeURIComponent(adherenceId)}/acknowledge`, { method: "POST", body: JSON.stringify(payload) }, true);
export const getTherapistAppointments = () => apiRequest<TherapistAppointment[]>("/api/v1/therapist/appointments", {}, true);
export const getCoachingDashboard = (patientId?: string) => apiRequest<CoachingDashboard>(`/api/v1/recovery-coaching/dashboard${patientId ? `?patient_id=${encodeURIComponent(patientId)}` : ""}`, {}, true);

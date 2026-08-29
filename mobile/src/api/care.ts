import { apiRequest } from "@/src/api/client";

export type PlanItem = {
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
  patient_comment?: string | null;
  analysis_session_id?: string | null;
};
export type Appointment = {
  appointment_id: string;
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
  title: string;
  body: string;
  read_at?: string | null;
  created_at: string;
};
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
export const logAdherence = (payload: object) =>
  apiRequest(
    "/api/v1/patient/adherence",
    {
      method: "POST",
      headers: { "Idempotency-Key": `${Date.now()}-${Math.random()}` },
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

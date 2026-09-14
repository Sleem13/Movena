export type Role =
  | "patient"
  | "therapist"
  | "admin"
  | "super_admin"
  | "support"
  | "researcher_demo";
export type User = {
  user_id: string;
  role: Role;
  full_name?: string | null;
  username?: string;
  email: string;
};
export type {
  CarePlanItem as PlanItem,
  PatientTodayResponse as Today,
} from "../../../../packages/contracts/generated";
export type Exercise = {
  id?: string;
  exercise_id?: string;
  name?: string;
  display_name?: string;
  name_en?: string;
  name_ar?: string;
  supported_in_app: boolean;
  endpoint_path?: string | null;
};
export type Connection = {
  assignment_id: string;
  therapist_name: string;
  patient_name: string;
  status: string;
};
export type Invitation = {
  invitation_id: string;
  therapist_name: string;
  status: string;
  email: string;
};
export type Patient = {
  patient_id: string;
  display_name: string;
  session_count: number;
  latest_session_date?: string | null;
};
export type ResponseRecord = {
  adherence_id: string;
  analysis_session_id?: string | null;
  plan_item_id: string;
  scheduled_date: string;
  completion_status: string;
  pain_before?: number | null;
  pain_after?: number | null;
  note?: string | null;
  supportive_instruction?: string;
  clinician_review_required: boolean;
  reviewed_at?: string | null;
};
export type AnalysisResult = {
  status: "success" | "rejected" | "error";
  session_id?: string;
  total_reps?: number | null;
  movement_score?: number | null;
  feedback?: string[];
  message?: string;
  analysis_confidence_level?: string | null;
  analysis_confidence?: { level?: string };
  [key: string]: unknown;
};
export type Job = {
  job_id: string;
  exercise_id?: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  stage: string;
  result?: AnalysisResult | null;
  message?: string | null;
  engine_version?: string;
  model_version?: string | null;
};

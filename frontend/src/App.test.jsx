import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import { analyzeExerciseVideo } from "./services/api.js";
import { getRehabRlExercises, getRehabRlGovernance, getRehabRlModelManifest, getRehabRlOverview, getRehabRlProtocols } from "./services/api.js";
import { getArtifactBlob, getExercises, getMlModelReadiness, getSavedSession, listSavedSessions } from "./services/api.js";
import { confirmRecognitionSuggestion, getRecognitionModels, recognizeExerciseVideo } from "./services/api.js";
import { EXERCISES } from "./data/exercises.js";
import {
  createPatientExercisePlan, createPatientProfile, getPatientProfile, getPatientProgress,
  getTherapistDashboard, listPatientAdherence, listPatientExercisePlans, listPatientProfiles, listPatientSessions,
} from "./services/api.js";

const authState = vi.hoisted(() => ({
  user: { user_id: "test-admin", email: "admin@example.com", role: "admin" },
}));

vi.mock("./context/AuthContext.jsx", () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({ user: authState.user, login: vi.fn(), register: vi.fn(), logout: vi.fn() }),
}));

vi.mock("./services/api.js", () => ({
  analyzeExerciseVideo: vi.fn(),
  getExercises: vi.fn(),
  getMlModelReadiness: vi.fn(),
  getRehabRlOverview: vi.fn(),
  getRehabRlExercises: vi.fn(),
  getRehabRlProtocols: vi.fn(),
  getRehabRlModelManifest: vi.fn(),
  getRehabRlGovernance: vi.fn(),
  createRehabRlAssessment: vi.fn(),
  simulateRehabRlTrajectory: vi.fn(),
  getRehabRlInspector: vi.fn(),
  getRehabRlTrainingStatus: vi.fn(),
  startRehabRlTraining: vi.fn(),
  restoreRehabRlCheckpoint: vi.fn(),
  getRecoveryCoachingDashboard: vi.fn(),
  getRecoveryCoachingTemplates: vi.fn().mockResolvedValue({ templates: [], can_apply_template: false }),
  createRecoveryCoachingGoal: vi.fn(),
  createRecoveryCoachingCheckIn: vi.fn(),
  createRecoveryCoachingActionPlan: vi.fn(),
  updateRecoveryCoachingGoal: vi.fn(),
  acknowledgeRecoveryCoachingCheckIn: vi.fn(),
  updateRecoveryCoachingReminderPreference: vi.fn(),
  getRecognitionModels: vi.fn().mockResolvedValue({ status: "not_available", models: [] }),
  recognizeExerciseVideo: vi.fn(),
  confirmRecognitionSuggestion: vi.fn().mockResolvedValue({ status: "confirmed" }),
  listSavedSessions: vi.fn(),
  getSavedSession: vi.fn(),
  getArtifactBlob: vi.fn(),
  deleteSavedSession: vi.fn(),
  getTherapistDashboard: vi.fn(),
  listPatientAdherence: vi.fn(),
  listPatientProfiles: vi.fn(),
  createPatientProfile: vi.fn(),
  getPatientProfile: vi.fn(),
  listPatientSessions: vi.fn(),
  getPatientProgress: vi.fn(),
  listPatientExercisePlans: vi.fn(),
  listTherapistAdherenceAlerts: vi.fn().mockResolvedValue([]),
  listTherapistAppointments: vi.fn().mockResolvedValue([]),
  createPatientExercisePlan: vi.fn(),
  updatePatientExercisePlanStatus: vi.fn(),
  verifyEmailToken: vi.fn(),
  resendVerificationEmail: vi.fn(),
  requestPasswordReset: vi.fn(),
  submitPasswordReset: vi.fn(),
  listManagedUsers: vi.fn(),
  getManagedUser: vi.fn(),
  updateManagedUserStatus: vi.fn(),
  updateManagedUserRole: vi.fn(),
  resetManagedUserPassword: vi.fn(),
  deleteManagedUser: vi.fn(),
  artifactUrl: (path) => path ? `http://127.0.0.1:8000${path}` : null,
}));

const report = {
  exercise: "bodyweight_squat",
  status: "success",
  total_reps: 2,
  average_knee_angle: 98,
  average_hip_angle: 75,
  average_trunk_angle: 20,
  movement_score: 90,
  rep_count_confidence: 0.88,
  ignored_partial_reps: 1,
  pose_quality: { score: 0.84, level: "high", pose_detection_rate: 0.92, warnings: [] },
  analysis_confidence: { score: 0.81, level: "high", reasons: [], warnings: [] },
  score_breakdown: { depth_score: 90, knee_alignment_score: 88, trunk_control_score: 92, consistency_score: 80, pose_confidence_score: 84 },
  detected_issues: ["poor_depth"],
  feedback: ["Possible movement issue detected."],
  summary: "Two repetitions analyzed.",
  limitations: ["This does not replace clinical assessment."],
  report_download_url: "/api/v1/artifacts/reports/test-report",
  overlay_preview_url: "/api/v1/artifacts/overlays/test-overlay/preview",
  overlay_download_url: "/api/v1/artifacts/overlays/test-overlay/download",
  frame_analysis: [{ frame_index: 0, timestamp_sec: 0, knee_angle: 98, hip_angle: 75, trunk_angle: 20, phase: "standing", detected_issue: "poor_depth" }],
};

const rejectedReport = {
  exercise: "bodyweight_squat",
  status: "rejected",
  error_code: "INVALID_SQUAT_VIDEO",
  message: "No valid squat movement was detected.",
  total_reps: 0,
  movement_score: null,
  detected_issues: ["no_valid_squat_detected"],
  feedback: ["Please upload a video showing the full body performing 3–5 squat repetitions."],
  limitations: ["Full-body movement is required."],
  validation_warnings: ["Video appears static or does not show enough squat movement.", "No complete squat repetition was detected."],
  input_validity: { is_valid: false, reason: "no_valid_squat_detected", valid_reps: 0 },
  analysis_confidence: { score: 0.2, level: "low", reasons: [], warnings: [] },
  ml_prediction: { enabled: false, warning: "ML prediction skipped because no valid squat movement was detected." },
};

function openUpload({ chooseExercise = true } = {}) {
  render(<App />);
  fireEvent.click(screen.getAllByRole("button", { name: authState.user ? "Open care workspace" : "Get started" }).at(-1));
  if (authState.user) fireEvent.click(screen.getAllByRole("button", { name: "Movement check" }).at(-1));
  if (authState.user && chooseExercise) chooseSelectOption("Exercise selector", "Bodyweight Squat");
}

function selectVideo() {
  const file = new File(["video"], "squat.mp4", { type: "video/mp4" });
  fireEvent.change(screen.getByLabelText(/choose a squat exercise video/i), { target: { files: [file] } });
}

function chooseSelectOption(label, option) {
  fireEvent.click(screen.getByRole("combobox", { name: label }));
  fireEvent.click(screen.getByRole("option", { name: option }));
}

async function analyzeWith(response = report) {
  analyzeExerciseVideo.mockResolvedValue(response);
  openUpload();
  selectVideo();
  fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
  await screen.findByText(response.status === "rejected" ? "Recording rejected" : "Analysis complete");
}

describe("Squat Analyzer healthcare dashboard", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/");
    authState.user = { user_id: "test-admin", email: "admin@example.com", role: "admin" };
    vi.clearAllMocks();
    getExercises.mockResolvedValue(EXERCISES);
    getMlModelReadiness.mockResolvedValue({
      feature_enabled: true,
      models: EXERCISES.filter((item) => item.supported_in_app).map((item) => ({
        exercise_id: item.exercise_id,
        status: "ready",
      })),
    });
    getRehabRlOverview.mockResolvedValue({
      metrics: { algorithm: "Double Dueling DQN", state_features: 32, clinical_actions: 30 },
      signals: { last_checkpoint: { name: "best_model.pt.npy" }, policy_source: "trained policy", backend: "numpy", device: "cpu" },
      trajectory: [{ session: 0, rom: 32, strength: 18, pain: 70 }],
    });
    getRehabRlExercises.mockResolvedValue({ items: [], categories: [], injuries: ["ACL Tear"], conditions: [] });
    getRehabRlProtocols.mockResolvedValue({ items: [], disclaimer: "Clinician review required." });
    getRehabRlModelManifest.mockResolvedValue({ checkpoint: { compatible: true }, contract: { version: "rehabrl-state-v1", state_dim: 32, action_dim: 30, sha256: "a".repeat(64) } });
    getRehabRlGovernance.mockResolvedValue({ window_days: 30, decisions: 0, safety_holds: 0, referrals: 0, audit: { privacy_profile: "No patient identifiers" }, escalation: { configured: false, organization: "Your organization", contact: "", instruction: "Follow your organization's urgent or emergency referral pathway." } });
    getArtifactBlob.mockResolvedValue(new Blob(["webm-video"], { type: "video/webm" }));
    listSavedSessions.mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    getTherapistDashboard.mockResolvedValue({ total_patients: 0, total_sessions: 0, low_confidence_sessions: 0, recent_sessions: [], common_detected_issues: [], sessions_by_exercise: {}, prototype_warning: "Prototype" });
    listPatientAdherence.mockResolvedValue([]);
    listPatientProfiles.mockResolvedValue([]);
    listPatientExercisePlans.mockResolvedValue([]);
  });

  it("renders the upload page and analysis options", () => {
    openUpload();
    expect(screen.getByText("Squat video upload")).toBeInTheDocument();
    expect(screen.getByText(/MP4, MOV, AVI, MKV, or WEBM/)).toBeInTheDocument();
    expect(
      screen
        .getByText("Advanced options")
        .compareDocumentPosition(screen.getByText("Squat video upload")) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(screen.getByLabelText(/choose a squat exercise video/i)).toHaveAttribute("accept", ".mp4,.mov,.avi,.mkv,.webm");
    expect(screen.getByText("Analysis options")).toBeInTheDocument();
    expect(screen.getByLabelText("Annotated video")).not.toBeChecked();
    expect(screen.getByLabelText("PDF session report")).not.toBeChecked();
    expect(screen.getByLabelText("Angle trend data")).not.toBeChecked();
    fireEvent.click(screen.getByRole("button", { name: "Select all" }));
    expect(screen.getByLabelText("Annotated video")).toBeChecked();
    expect(screen.getByLabelText("PDF session report")).toBeChecked();
    expect(screen.getByLabelText("Angle trend data")).toBeChecked();
    expect(screen.getByLabelText("ML second opinion")).toBeChecked();
    expect(screen.getByLabelText("Save session history")).toBeChecked();
    fireEvent.click(screen.getByRole("button", { name: "Clear all" }));
    expect(screen.getByLabelText("Annotated video")).not.toBeChecked();
    expect(screen.getByLabelText("PDF session report")).not.toBeChecked();
    expect(screen.getByLabelText("Angle trend data")).not.toBeChecked();
    expect(screen.getByLabelText("ML second opinion")).not.toBeChecked();
    expect(screen.getByLabelText("Save session history")).not.toBeChecked();
    expect(screen.getByRole("button", { name: "Analyze squat" })).toBeDisabled();
    const exerciseSelector = screen.getByRole("combobox", { name: "Exercise selector" });
    expect(exerciseSelector).toHaveTextContent("Bodyweight Squat");
    fireEvent.click(exerciseSelector);
    expect(screen.getByRole("option", { name: "Sit-to-Stand" })).toBeInTheDocument();
    fireEvent.click(exerciseSelector);
    expect(screen.getByText("One person only")).toBeInTheDocument();
    expect(screen.getByText(/keep coaches, spotters, and bystanders outside the frame/i)).toBeInTheDocument();
  });

  it("disables an unavailable exercise model without blocking rule analysis", async () => {
    getMlModelReadiness.mockResolvedValueOnce({
      feature_enabled: true,
      models: [
        { exercise_id: "bodyweight_squat", status: "available" },
        { exercise_id: "sit_to_stand", status: "blocked" },
      ],
    });
    openUpload();
    chooseSelectOption("Exercise selector", "Sit-to-Stand");

    await waitFor(() => expect(screen.getByLabelText("ML second opinion")).toBeDisabled());
    expect(screen.getByText("Unavailable")).toBeInTheDocument();
    expect(screen.getByText(/No sit-to-stand ML model is available/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze sit-to-stand" })).toBeDisabled();
  });

  it("renders the authenticated clinical workspace with role-aware navigation", async () => {
    window.history.replaceState({}, "", "/workspace");
    render(<App />);
    expect(await screen.findByRole("heading", { name: /Welcome back, admin/i })).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Movement check" })).toHaveLength(2);
    expect(screen.getAllByRole("button", { name: "Caseload" })).toHaveLength(2);
    expect(screen.queryByRole("button", { name: "Users & access" })).not.toBeInTheDocument();
    expect(screen.getByText("Platform readiness")).toBeInTheDocument();
  });

  it("renders the exercise library with supported and unavailable planned exercises", async () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "Open care workspace" }).at(-1));
    fireEvent.click(screen.getByRole("button", { name: "Exercise library" }));
    expect(await screen.findByText("Available exercises")).toBeInTheDocument();
    expect(screen.getByText("Bodyweight Squat")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Next exercises" }));
    expect(screen.getByText("Hip Abduction")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Next exercises" }));
    expect(screen.getByText("Walking Gait Screen")).toBeInTheDocument();
    expect(screen.getByText("Static Balance Screen")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Research and planned exercises"));
    const planned = within(screen.getByRole("region", { name: "Planned exercises" }));
    expect(planned.getAllByRole("button", { name: "Not available" })).toHaveLength(4);
    expect(planned.getAllByRole("button", { name: "Not available" })[0]).toBeDisabled();
  });

  it("filters the exercise library by search text and availability", async () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "Open care workspace" }).at(-1));
    fireEvent.click(screen.getByRole("button", { name: "Exercise library" }));
    expect(await screen.findByText("Available exercises")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Search exercises"), { target: { value: "shoulder" } });
    chooseSelectOption("Availability", "Supported only");
    expect(screen.getByText("3 exercises match your filters.")).toBeInTheDocument();
    expect(screen.getByText("Shoulder Abduction")).toBeInTheDocument();
    expect(screen.getByText("Shoulder Flexion")).toBeInTheDocument();
    expect(screen.getByText("Shoulder Press")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Clear exercise filters" }));
    expect(screen.getByText("16 exercises match your filters.")).toBeInTheDocument();
    expect(screen.getByText("Bodyweight Squat")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous exercises" })).toBeDisabled();
  });

  it("opens Analyze from an exercise card with exercise-specific guidance", async () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "Open care workspace" }).at(-1));
    fireEvent.click(screen.getByRole("button", { name: "Exercise library" }));
    fireEvent.change(await screen.findByRole("searchbox"), { target: { value: "shoulder abduction" } });
    const shoulderCard = screen.getByRole("heading", { name: "Shoulder Abduction" }).closest("article");
    fireEvent.click(within(shoulderCard).getByRole("button", { name: /Analyze this exercise/i }));
    expect(screen.getByLabelText("Exercise selector")).toHaveTextContent("Shoulder Abduction");
    expect(screen.getByText("Front view preferred.")).toBeInTheDocument();
    expect(screen.getByText(/raise the arm outward through a comfortable range/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Camera placement guide" })).toBeInTheDocument();
  });

  it("carries a recognized video into analysis without a second upload", async () => {
    getRecognitionModels.mockResolvedValue({
      status: "available",
      models: [{ model_id: "exercise_pose_gru_candidate", artifact_format: "torchscript_sequence", status: "candidate" }],
    });
    recognizeExerciseVideo.mockResolvedValue({
      status: "success",
      suggested_exercise_id: "push_up",
      confidence: 0.83,
      analyzer_available: true,
      recognition_event_id: "11111111-1111-1111-1111-111111111111",
      top_predictions: [{ exercise_id: "push_up", confidence: 0.83 }],
    });

    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: "Open care workspace" }).at(-1));
    fireEvent.click(screen.getAllByRole("button", { name: "Movement check" }).at(-1));
    fireEvent.click(screen.getByRole("button", { name: "Identify from video" }));

    expect(window.location.pathname).toBe("/analyze");
    expect(screen.queryByText("Exercise coaching lab")).not.toBeInTheDocument();

    const file = new File(["video"], "push-up.mp4", { type: "video/mp4" });
    fireEvent.change(await screen.findByLabelText("Choose a movement video"), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Identify exercise" }));
    await screen.findByText("Model confidence 83%");
    fireEvent.click(screen.getByRole("button", { name: "Confirm push-up and continue" }));

    expect(await screen.findByText("Suggestion confirmed — video ready")).toBeInTheDocument();
    expect(screen.getByLabelText("Exercise selector")).toHaveTextContent("Push-Up");
    expect(screen.getByText("push-up.mp4")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze push-up" })).toBeEnabled();
    expect(window.location.pathname).toBe("/analyze");
    expect(confirmRecognitionSuggestion).toHaveBeenCalledWith(
      "11111111-1111-1111-1111-111111111111", "push_up",
    );
  });

  it("selects sit-to-stand, shows chair guidance, and calls its endpoint service", async () => {
    const sitReport = {
      ...report,
      exercise: "sit_to_stand",
      total_reps: 3,
      summary: "Three sit-to-stand repetitions analyzed.",
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not available for sit-to-stand yet." },
      score_breakdown: { completion_score: 100, control_score: 88, trunk_control_score: 90, consistency_score: 85, pose_confidence_score: 84 },
    };
    analyzeExerciseVideo.mockResolvedValue(sitReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Sit-to-Stand");
    expect(screen.getByText("Use a stable chair")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "chair.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a sit-to-stand exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze sit-to-stand" }));
    await screen.findByText("Sit-to-Stand report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("sit_to_stand", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText(/not available for sit-to-stand yet/i)).toBeInTheDocument();
    expect(screen.getByText("Completion")).toBeInTheDocument();
  });

  it("selects knee extension, shows side-view guidance, and renders its rule-based result", async () => {
    const kneeReport = {
      ...report,
      exercise: "knee_extension",
      exercise_id: "knee_extension",
      exercise_name: "Knee Extension",
      valid_reps: 2,
      summary: "Two complete knee extension repetitions analyzed.",
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not applicable for knee extension." },
      score_breakdown: { extension_range_score: 90, control_score: 88, consistency_score: 85, posture_visibility_score: 92, rep_completion_score: 100 },
    };
    analyzeExerciseVideo.mockResolvedValue(kneeReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Knee Extension");
    expect(screen.getByText("Seated position visible")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "extension.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a knee extension exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze knee extension" }));
    await screen.findByText("Knee Extension report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("knee_extension", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Extension range")).toBeInTheDocument();
  });

  it("selects shoulder abduction, shows front-view guidance, and renders its rule-based result", async () => {
    const shoulderReport = {
      ...report,
      exercise: "shoulder_abduction",
      exercise_id: "shoulder_abduction",
      exercise_name: "Shoulder Abduction",
      average_shoulder_angle: 82,
      valid_reps: 2,
      summary: "Two complete shoulder abduction repetitions analyzed.",
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not applicable for shoulder abduction." },
      score_breakdown: { abduction_range_score: 90, control_score: 88, consistency_score: 85, posture_visibility_score: 92, rep_completion_score: 100 },
      frame_analysis: [{ frame_index: 0, timestamp_sec: 0, knee_angle: 0, hip_angle: 0, shoulder_angle: 25, trunk_angle: 5, phase: "lowered", detected_issue: null }],
    };
    analyzeExerciseVideo.mockResolvedValue(shoulderReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Shoulder Abduction");
    expect(screen.getByText("Upper body visible")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "shoulder.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a shoulder abduction exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze shoulder abduction" }));
    await screen.findByText("Shoulder Abduction report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("shoulder_abduction", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Average shoulder")).toBeInTheDocument();
    expect(screen.getByText("Abduction range")).toBeInTheDocument();
  });

  it("selects shoulder flexion, shows forward-raise guidance, and renders its rule-based result", async () => {
    const flexionReport = {
      ...report,
      exercise: "shoulder_flexion",
      exercise_id: "shoulder_flexion",
      exercise_name: "Shoulder Flexion",
      average_shoulder_angle: 118,
      valid_reps: 2,
      summary: "Two complete shoulder flexion repetitions analyzed.",
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not applicable for shoulder flexion." },
      score_breakdown: { extension_range_score: 90, control_score: 88, consistency_score: 85, posture_visibility_score: 92, rep_completion_score: 100 },
      frame_analysis: [{ frame_index: 0, timestamp_sec: 0, knee_angle: 0, hip_angle: 0, shoulder_angle: 25, trunk_angle: 5, phase: "lowered", detected_issue: null }],
    };
    analyzeExerciseVideo.mockResolvedValue(flexionReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Shoulder Flexion");
    expect(screen.getByText("Raise the arm forward through a comfortable visible range and return to the side.")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "flexion.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a shoulder flexion exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze shoulder flexion" }));
    await screen.findByText("Shoulder Flexion report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("shoulder_flexion", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Average shoulder")).toBeInTheDocument();
    expect(screen.getByText("Flexion range")).toBeInTheDocument();
  });

  it("selects hip abduction, shows lower-body guidance, and renders its rule-based result", async () => {
    const hipReport = {
      ...report,
      exercise: "hip_abduction",
      exercise_id: "hip_abduction",
      exercise_name: "Hip Abduction",
      average_hip_abduction_angle: 27,
      valid_reps: 2,
      summary: "Two complete hip abduction repetitions analyzed.",
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not applicable for hip abduction." },
      score_breakdown: { abduction_range_score: 88, control_score: 86, consistency_score: 84, posture_visibility_score: 91, rep_completion_score: 100, pelvis_trunk_stability_score: 90 },
      frame_analysis: [{ frame_index: 0, timestamp_sec: 0, knee_angle: 0, hip_angle: 8, hip_abduction_angle: 8, trunk_angle: 4, phase: "neutral", detected_issue: null }],
    };
    analyzeExerciseVideo.mockResolvedValue(hipReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Hip Abduction");
    expect(screen.getByText("Full lower body visible")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "hip.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a hip abduction exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze hip abduction" }));
    await screen.findByText("Hip Abduction report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("hip_abduction", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Average hip abduction")).toBeInTheDocument();
    expect(screen.getByText("Pelvis/trunk stability")).toBeInTheDocument();
  });

  it("selects hammer curl, shows grip-limited guidance, and renders its rule-based result", async () => {
    const hammerReport = {
      ...report,
      exercise: "hammer_curl",
      exercise_id: "hammer_curl",
      exercise_name: "Hammer Curl",
      average_elbow_angle: 126,
      valid_reps: 2,
      summary: "Two complete hammer curl repetitions analyzed.",
      limitations: ["Hammer-curl grip orientation cannot be confirmed from body pose alone."],
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not applicable for hammer curl." },
      score_breakdown: { extension_range_score: 87, control_score: 88, consistency_score: 85, posture_visibility_score: 92, rep_completion_score: 100 },
      frame_analysis: [{ frame_index: 0, timestamp_sec: 0, knee_angle: 0, hip_angle: 0, elbow_angle: 160, trunk_angle: 5, phase: "extended", detected_issue: null }],
    };
    analyzeExerciseVideo.mockResolvedValue(hammerReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Hammer Curl");
    expect(screen.getByText(/body pose cannot confirm neutral grip/i)).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "hammer.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a hammer curl exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze hammer curl" }));
    await screen.findByText("Hammer Curl report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("hammer_curl", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Average elbow")).toBeInTheDocument();
    expect(screen.getByText("Flexion range")).toBeInTheDocument();
  });

  it("selects balance, shows safe support guidance, and renders balance metrics", async () => {
    const balanceReport = {
      ...report,
      exercise: "balance",
      exercise_id: "balance",
      exercise_name: "Static Balance Screen",
      total_reps: 0,
      valid_reps: 1,
      summary: "A static balance hold was analyzed.",
      balance_metrics: {
        hold_duration_sec: 5,
        balance_mode: "quiet_standing",
        sway_rms: 0.018,
        sway_velocity: 0.034,
        max_trunk_lean_deg: 5.2,
      },
      ml_prediction: { enabled: false, model_version: "not_applicable", warning: "ML prediction is not applicable for balance screening." },
      score_breakdown: { hold_duration_score: 50, sway_control_score: 88, trunk_control_score: 90, pelvis_control_score: 92, knee_stability_score: 86, posture_visibility_score: 91 },
      frame_analysis: [{ frame_index: 0, timestamp_sec: 0, knee_angle: 178, hip_angle: 0, trunk_angle: 4, phase: "balance_hold", detected_issue: null }],
    };
    analyzeExerciseVideo.mockResolvedValue(balanceReport);
    openUpload();
    chooseSelectOption("Exercise selector", "Static Balance Screen");
    expect(screen.getByText("Hold steady")).toBeInTheDocument();
    expect(screen.getByText(/stable counter, rail, or chair nearby/i)).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeEnabled();
    const file = new File(["video"], "balance.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a balance screen exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze balance screen" }));
    await screen.findByText("Static Balance Screen report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("balance", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getAllByText("Hold duration")).toHaveLength(2);
    expect(screen.getByText("Sway control")).toBeInTheDocument();
  });

  it("renders the camera placement guide", () => {
    openUpload();
    expect(screen.getByText("Camera placement guide")).toBeInTheDocument();
    expect(screen.getByText("Side view")).toBeInTheDocument();
    expect(screen.getByText(/best for squat depth and trunk lean/i)).toBeInTheDocument();
    expect(screen.getByText(/avoid very loose clothing/i)).toBeInTheDocument();
  });

  it("shows loading progress after a video is submitted", async () => {
    analyzeExerciseVideo.mockReturnValue(new Promise(() => {}));
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByText("Analyzing")).toBeInTheDocument();
    expect(screen.getByText(/uploading video/i)).toBeInTheDocument();
  });

  it("sends save_session when the local history option is enabled", async () => {
    analyzeExerciseVideo.mockResolvedValue({ ...report, session_id: "12345678-test-session" });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByLabelText("Save session history"));
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    await screen.findByText("Saved session");
    expect(analyzeExerciseVideo.mock.calls[0][2].save_session).toBe(true);
    expect(screen.getByRole("button", { name: "View Session History" })).toBeInTheDocument();
  });

  it("shows the session history empty state", async () => {
    window.history.replaceState({}, "", "/history");
    render(<App />);
    expect(await screen.findByText(/No saved sessions yet/i)).toBeInTheDocument();
  });

  it("filters session history by exercise and status", async () => {
    window.history.replaceState({}, "", "/history");
    render(<App />);
    await screen.findByText(/No saved sessions yet/i);
    chooseSelectOption("Exercise", "Hip Abduction");
    chooseSelectOption("Status", "Rejected");
    await waitFor(() => expect(listSavedSessions).toHaveBeenLastCalledWith({ exercise_id: "hip_abduction", status: "rejected" }));
  });

  it("renders saved sessions and opens detail", async () => {
    const saved = {
      session_id: "abcdef12-session", exercise_id: "sit_to_stand",
      exercise_display_name: "Sit-to-Stand", status: "success",
      created_at: "2026-07-14T12:00:00Z", total_reps: 3, movement_score: 86,
      analysis_confidence_level: "medium", detected_issues: ["poor_control"],
    };
    listSavedSessions.mockResolvedValue({ items: [saved], total: 1, limit: 50, offset: 0 });
    getSavedSession.mockResolvedValue({ ...saved, summary: "Three repetitions analyzed.", feedback: ["Move steadily."] });
    window.history.replaceState({}, "", "/history");
    render(<App />);
    expect(await screen.findByText("Sit-to-Stand")).toBeInTheDocument();
    expect(screen.getByText("Poor Control")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "View details" }));
    expect(await screen.findByText("Three repetitions analyzed.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hide details" })).toHaveAttribute("aria-expanded", "true");
    fireEvent.click(screen.getByRole("button", { name: "Hide details" }));
    expect(screen.queryByText("Three repetitions analyzed.")).not.toBeInTheDocument();
  });

  it("opens the integrated RehabRL decision-support workspace", async () => {
    window.history.replaceState({}, "", "/workspace");
    render(<App />);
    fireEvent.click(screen.getByText("More tools", { exact: true }));
    fireEvent.click(screen.getByRole("button", { name: "RehabRL Decision Support" }));
    expect(await screen.findByRole("heading", { name: "Rehabilitation planning workspace" })).toBeInTheDocument();
    expect(screen.getByText("Double Dueling DQN")).toBeInTheDocument();
    expect(window.location.pathname).toBe("/rehab-policy");
  });

  it("asks for an exercise in a focused picker and keeps the selected video", async () => {
    openUpload({ chooseExercise: false });
    const file = new File(["video"], "movement.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a movement exercise video/i), { target: { files: [file] } });
    const analyze = (await screen.findAllByRole("button", { name: "Analyze movement" })).at(-1);
    await waitFor(() => expect(analyze).toBeEnabled());
    fireEvent.click(analyze);

    const dialog = screen.getByRole("dialog", { name: "Which exercise is shown?" });
    expect(dialog).toBeInTheDocument();
    const pickerButtons = within(dialog).getAllByRole("button");
    fireEvent.keyDown(dialog, { key: "Tab", shiftKey: true });
    expect(pickerButtons.at(-1)).toHaveFocus();
    fireEvent.keyDown(pickerButtons.at(-1), { key: "Tab" });
    expect(pickerButtons[0]).toHaveFocus();
    fireEvent.click(within(dialog).getByRole("button", { name: /Bodyweight Squat/i }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByText("movement.mp4")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze squat" })).toBeEnabled();
  });

  it("cancels an in-flight analysis and keeps the selected video", async () => {
    let requestSignal;
    analyzeExerciseVideo.mockImplementation((_exercise, _file, options) => {
      requestSignal = options.signal;
      return new Promise((_resolve, reject) => {
        requestSignal.addEventListener("abort", () => reject({ code: "ERR_CANCELED" }));
      });
    });
    openUpload();
    selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    fireEvent.click(await screen.findByRole("button", { name: "Cancel analysis" }));

    expect(requestSignal.aborted).toBe(true);
    expect(await screen.findByRole("alert")).toHaveTextContent("Analysis cancelled. Your video remains selected.");
    expect(screen.getByText("squat.mp4")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze squat" })).toBeEnabled();
  });

  it("compares two saved sessions of the same exercise", async () => {
    const earlier = {
      session_id: "compare1-session", exercise_id: "bodyweight_squat", exercise_display_name: "Bodyweight Squat",
      status: "success", created_at: "2026-08-01T10:00:00Z", total_reps: 3, movement_score: 80,
      analysis_confidence_level: "medium", detected_issues: [],
    };
    const later = { ...earlier, session_id: "compare2-session", created_at: "2026-08-20T10:00:00Z", total_reps: 5, movement_score: 88 };
    listSavedSessions.mockResolvedValue({ items: [later, earlier], total: 2, limit: 50, offset: 0 });
    getSavedSession
      .mockResolvedValueOnce({ ...later, metrics: [{ metric_name: "average_knee_angle", metric_value_float: 105 }] })
      .mockResolvedValueOnce({ ...earlier, metrics: [{ metric_name: "average_knee_angle", metric_value_float: 112 }] });
    window.history.replaceState({}, "", "/history");
    render(<App />);
    const compareButtons = await screen.findAllByRole("button", { name: "Compare" });
    fireEvent.click(compareButtons[0]);
    expect(screen.getByText(/Select another session/i)).toBeInTheDocument();
    fireEvent.click(compareButtons[1]);
    expect(await screen.findByText("+8/100")).toBeInTheDocument();
    expect(screen.getByText("-7°")).toBeInTheDocument();
    expect(getSavedSession).toHaveBeenCalledTimes(2);
    fireEvent.click(screen.getByRole("button", { name: "Clear comparison" }));
    expect(screen.queryByLabelText("Compare saved sessions")).not.toBeInTheDocument();
  });

  it("opens a saved report in an authenticated in-page viewer", async () => {
    const saved = {
      session_id: "report12-session", exercise_id: "bodyweight_squat", exercise_display_name: "Bodyweight Squat",
      status: "success", created_at: "2026-07-29T12:00:00Z", report_download_url: "/api/v1/artifacts/reports/report-1",
    };
    listSavedSessions.mockResolvedValue({ items: [saved], total: 1, limit: 50, offset: 0 });
    getArtifactBlob.mockResolvedValue(new Blob(["pdf"], { type: "application/pdf" }));
    const createObjectUrl = vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:report-1");
    window.history.replaceState({}, "", "/history");
    render(<App />);
    await screen.findByText("Bodyweight Squat");
    fireEvent.click(screen.getByRole("button", { name: "Report" }));
    expect(await screen.findByRole("dialog", { name: "Session report" })).toBeInTheDocument();
    expect(getArtifactBlob).toHaveBeenCalledWith(saved.report_download_url);
    expect(screen.getByTitle("Session report")).toHaveAttribute("src", "blob:report-1");
    const closeButtons = screen.getAllByRole("button", { name: "Close" });
    expect(closeButtons).toHaveLength(2);
    await waitFor(() => expect(closeButtons[1]).toHaveFocus());
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog", { name: "Session report" })).not.toBeInTheDocument();
    createObjectUrl.mockRestore();
  });

  it("shows an expired artifact message instead of navigating silently", async () => {
    const saved = {
      session_id: "oldreport-session", exercise_id: "bodyweight_squat", exercise_display_name: "Bodyweight Squat",
      status: "success", created_at: "2026-07-23T12:00:00Z", overlay_preview_url: "/api/v1/artifacts/overlays/missing/preview",
    };
    listSavedSessions.mockResolvedValue({ items: [saved], total: 1, limit: 50, offset: 0 });
    getArtifactBlob.mockRejectedValue({ response: { status: 404, data: { error_code: "ARTIFACT_NOT_FOUND" } } });
    window.history.replaceState({}, "", "/history");
    render(<App />);
    await screen.findByText("Bodyweight Squat");
    fireEvent.click(screen.getByRole("button", { name: "Overlay" }));
    expect(await screen.findByText(/temporary artifact has expired/i)).toBeInTheDocument();
  });

  it("renders therapist dashboard summary, empty profiles, and privacy warning", async () => {
    window.history.replaceState({}, "", "/therapist");
    render(<App />);
    expect(await screen.findByText("Total patients")).toBeInTheDocument();
    expect(screen.getByText(/privacy and clinical-use notice/i)).toBeInTheDocument();
    expect(screen.getByText(/only process patient information with appropriate authorization and consent/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Patient profiles" }));
    expect(await screen.findByText("No patient profiles yet")).toBeInTheDocument();
  });

  it("visualizes real therapist session scores, exercise volume, and issue frequency", async () => {
    getTherapistDashboard.mockResolvedValue({
      total_patients: 3,
      total_sessions: 4,
      low_confidence_sessions: 1,
      recent_sessions: [
        { session_id: "viz-2", exercise_id: "bodyweight_squat", exercise_display_name: "Bodyweight Squat", movement_score: 86, total_reps: 4 },
        { session_id: "viz-1", exercise_id: "sit_to_stand", exercise_display_name: "Sit-to-Stand", movement_score: 74, total_reps: 3 },
      ],
      common_detected_issues: [{ issue_code: "possible_knee_valgus", count: 3 }],
      sessions_by_exercise: { bodyweight_squat: 3, sit_to_stand: 1 },
      low_confidence_sessions_by_exercise: { sit_to_stand: 1 },
    });
    window.history.replaceState({}, "", "/therapist");
    render(<App />);
    expect(await screen.findByRole("img", { name: "Movement score trend" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Sessions by exercise" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Common detected issues" })).toBeInTheDocument();
  });

  it("renders a patient profile and session detail", async () => {
    const patient = { patient_id: "patient-1234", display_name: "Demo Profile A", age_group: "adult", clinical_group: "unknown", session_count: 1 };
    listPatientProfiles.mockResolvedValue([patient]);
    getPatientProfile.mockResolvedValue({ ...patient, notes: null });
    listPatientSessions.mockResolvedValue([{ session_id: "session-1", exercise_display_name: "Bodyweight Squat", total_reps: 3, movement_score: 88 }]);
    getPatientProgress.mockResolvedValue({
      total_sessions: 2,
      average_movement_score: 84,
      average_analysis_confidence: 0.8,
      low_confidence_session_count: 0,
      detected_issue_counts: [{ issue_code: "poor_depth", count: 1 }],
      exercise_comparisons: [{
        exercise_id: "bodyweight_squat", session_count: 2, scored_session_count: 2,
        baseline_date: "2026-08-01T10:00:00Z", baseline_movement_score: 80, baseline_total_reps: 3,
        latest_date: "2026-08-20T10:00:00Z", latest_movement_score: 88, latest_total_reps: 5,
        score_delta: 8, reps_delta: 2, has_comparison: true,
      }],
    });
    window.history.replaceState({}, "", "/therapist");
    render(<App />);
    await screen.findByText("Total patients");
    fireEvent.click(screen.getByRole("button", { name: "Patient profiles" }));
    expect(await screen.findByText("Demo Profile A")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "View profile" }));
    expect(await screen.findByText("Exercise session history")).toBeInTheDocument();
    expect(screen.getByText(/Bodyweight Squat · 3 reps · score 88/i)).toBeInTheDocument();
    expect(screen.getByText("Poor Depth: 1")).toBeInTheDocument();
    expect(screen.getByText("Baseline and latest session")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Bodyweight Squat: baseline score 80, latest score 88" })).toBeInTheDocument();
    expect(screen.getByText("+8")).toBeInTheDocument();
  });

  it("creates a clinician-authored exercise plan for a patient", async () => {
    const patient = { patient_id: "patient-plan", display_name: "Patient Plan", age_group: "adult", clinical_group: "unknown", session_count: 0 };
    listPatientProfiles.mockResolvedValue([patient]);
    getPatientProfile.mockResolvedValue({ ...patient, notes: null });
    listPatientSessions.mockResolvedValue([]);
    getPatientProgress.mockResolvedValue({ total_sessions: 0, detected_issue_counts: [] });
    createPatientExercisePlan.mockResolvedValue({
      plan_id: "plan-1", patient_id: patient.patient_id, title: "Home plan", notes: null,
      status: "active", items: [{ item_id: "item-1", exercise_id: "bodyweight_squat", sets: 3, reps: 8, days_per_week: 3, instructions: null }],
    });
    window.history.replaceState({}, "", "/therapist");
    render(<App />);
    await screen.findByText("Total patients");
    fireEvent.click(screen.getByRole("button", { name: "Patient profiles" }));
    fireEvent.click(await screen.findByRole("button", { name: "View profile" }));
    await screen.findByText("Create exercise plan");
    fireEvent.change(screen.getByLabelText("Plan title"), { target: { value: "Home plan" } });
    fireEvent.click(screen.getByRole("button", { name: "Assign plan" }));
    await waitFor(() => expect(createPatientExercisePlan).toHaveBeenCalledWith(
      "patient-plan",
      expect.objectContaining({ title: "Home plan", items: [expect.objectContaining({ exercise_id: "bodyweight_squat", sets: 3, reps: 8, days_per_week: 3 })] }),
    ));
    expect(await screen.findByText("Home plan")).toBeInTheDocument();
  });

  it("renders result KPI cards and charts", async () => {
    await analyzeWith();
    expect(screen.getAllByText("Movement score").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Total reps")).toBeInTheDocument();
    expect(screen.getByText("Average knee")).toBeInTheDocument();
    expect(screen.getByText("Average hip")).toBeInTheDocument();
    expect(screen.getByText("Average trunk")).toBeInTheDocument();
    expect(screen.getAllByText("90").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Angle trend")).toBeInTheDocument();
    expect(screen.getByText("Movement profile")).toBeInTheDocument();
    expect(screen.getByText("Rep quality")).toBeInTheDocument();
    expect(screen.getAllByText("Analysis confidence").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Rep count confidence")).toBeInTheDocument();
    expect(screen.getByText("Score breakdown")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
    expect(screen.getByText(/Movena supports exercise monitoring and does not replace assessment by a licensed physiotherapist/i)).toBeInTheDocument();
  });

  it("renders the ML second opinion only when returned", async () => {
    await analyzeWith({ ...report, ml_prediction: { enabled: true, predicted_label: "squat_correct", confidence: 0.82, experimental_quality_score: 80, artifact_verified: true, model_name: "svc_rbf", model_version: "sprint_5_baseline", warning: "Experimental baseline model. Not clinically validated." } });
    expect(screen.getByText("ML second opinion")).toBeInTheDocument();
    expect(screen.getByText("Squat Correct")).toBeInTheDocument();
    expect(screen.getByText("82%")).toBeInTheDocument();
    expect(screen.getByText("svc_rbf")).toBeInTheDocument();
    expect(screen.getAllByText("80/100").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Verified artifact · therapist review required")).toBeInTheDocument();
    expect(screen.getByText(/rule-based analysis remains primary/i)).toBeInTheDocument();
  });

  it("shows the safe ML disagreement note without replacing rule results", async () => {
    await analyzeWith({ ...report, ml_prediction: { enabled: true, predicted_label: "squat_correct", confidence: 0.9, model_name: "svc_rbf", model_version: "sprint_5_baseline", warning: "Experimental baseline.", disagreement_note: "The experimental ML prediction disagrees with rule-based analysis. Rule-based biomechanical feedback remains primary." } });
    expect(screen.getByText("Experimental ML disagreement")).toBeInTheDocument();
    expect(screen.getByText(/rule-based biomechanical feedback remains primary/i)).toBeInTheDocument();
    expect(screen.getAllByText("Poor Depth").length).toBeGreaterThanOrEqual(1);
  });

  it("recommends manual review when rep count confidence is low", async () => {
    await analyzeWith({ ...report, rep_count_confidence: 0.42, ignored_partial_reps: 2 });
    expect(screen.getByText("Manual review recommended")).toBeInTheDocument();
    expect(screen.getByText(/movement was detected, but rep count confidence is low/i)).toBeInTheDocument();
    expect(screen.getByText(/consider trimming the video to only the squat set/i)).toBeInTheDocument();
  });

  it("shows an annotated-video fallback when the overlay URL is missing", async () => {
    await analyzeWith({ ...report, overlay_preview_url: null, overlay_download_url: null });
    expect(screen.getByText("No annotated preview was generated for this analysis.")).toBeInTheDocument();
  });

  it("renders the annotated video with a full backend URL", async () => {
    await analyzeWith();
    const video = await screen.findByLabelText("Annotated squat movement preview");
    expect(video).toHaveAttribute("preload", "auto");
    expect(video).toHaveAttribute("playsinline");
    expect(video).toHaveAttribute("src", "blob:test-artifact");
    expect(getArtifactBlob).toHaveBeenCalledWith("http://127.0.0.1:8000/api/v1/artifacts/overlays/test-overlay/preview");
    expect(screen.getAllByRole("link", { name: "Download annotated video" })[0]).toHaveAttribute(
      "href", "http://127.0.0.1:8000/api/v1/artifacts/overlays/test-overlay/download"
    );
  });

  it("shows a fallback when annotated video playback fails", async () => {
    await analyzeWith();
    fireEvent.error(await screen.findByLabelText("Annotated squat movement preview"));
    expect(screen.getByText("Annotated preview could not be loaded")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry preview" })).toBeInTheDocument();
  });

  it("renders an API error state", async () => {
    analyzeExerciseVideo.mockRejectedValue({ response: { data: { message: "Video is too large." } } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Video is too large.");
  });

  it.each([401, 403])("shows a login prompt for an HTTP %s analysis response", async (status) => {
    analyzeExerciseVideo.mockRejectedValue({ response: { status, data: {} } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Please log in before analyzing a video.");
  });

  it("routes logged-out users from the primary CTA to account creation", async () => {
    authState.user = null;
    openUpload();
    expect(screen.getByRole("heading", { name: "Create your account" })).toBeInTheDocument();
    expect(analyzeExerciseVideo).not.toHaveBeenCalled();
  });

  it("keeps log in as the distinct path for existing users", () => {
    authState.user = null;
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(screen.getByRole("heading", { name: "Log in to Movena" })).toBeInTheDocument();
  });

  it("shows the supported formats for an unsupported-file response", async () => {
    analyzeExerciseVideo.mockRejectedValue({ response: { status: 400, data: { error_code: "UNSUPPORTED_FILE_TYPE" } } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Unsupported video format. Please upload MP4, MOV, AVI, MKV, or WEBM.");
  });

  it("automatically proceeds with a warning when pose tracking switches people", async () => {
    analyzeExerciseVideo
      .mockRejectedValueOnce({
        response: {
          status: 422,
          data: { error_code: "SUBJECT_SWITCH_DETECTED", message: "Internal subject tracking message." },
        },
      })
      .mockResolvedValueOnce({ ...report, validation_warnings: ["Subject-continuity warning overridden by user request."] });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    const warningAlert = await screen.findByRole("alert");
    expect(warningAlert).toHaveTextContent(
      "More than one person may have been tracked. For best reliability, record only the person being analyzed",
    );
    expect(warningAlert).toHaveTextContent("Continuing automatically with this warning included in the report.");
    expect(screen.queryByRole("button", { name: "Proceed with warning" })).not.toBeInTheDocument();
    await screen.findByText("Bodyweight Squat report");
    expect(analyzeExerciseVideo).toHaveBeenCalledTimes(2);
    expect(analyzeExerciseVideo).toHaveBeenLastCalledWith(
      "bodyweight_squat",
      expect.any(File),
      expect.objectContaining({ continue_on_subject_warning: true }),
      expect.any(Function),
    );
    expect(recognizeExerciseVideo).not.toHaveBeenCalled();
  });

  it("shows a connection message for a network or CORS failure", async () => {
    analyzeExerciseVideo.mockRejectedValue({ code: "ERR_NETWORK", request: {} });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not connect to the analysis server.");
  });

  it("keeps the generic backend message for a server error", async () => {
    analyzeExerciseVideo.mockRejectedValue({ response: { status: 500, data: { message: "Internal detail" } } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to analyze this video. Check the backend and try again.");
  });

  it("renders rejected input guidance without score or ML panels", async () => {
    await analyzeWith(rejectedReport);
    expect(screen.getByText("No valid squat movement detected")).toBeInTheDocument();
    expect(screen.getByText(/record full body, 3–5 squat reps, stable camera, good lighting/i)).toBeInTheDocument();
    expect(screen.getByText("Camera placement guide")).toBeInTheDocument();
    expect(screen.queryByText("Movement score")).not.toBeInTheDocument();
    expect(screen.queryByText("ML second opinion")).not.toBeInTheDocument();
  });

  it("keeps the manually selected analyzer when its movement validation rejects", async () => {
    analyzeExerciseVideo.mockResolvedValueOnce(rejectedReport);
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));

    await screen.findByText("Recording rejected");
    expect(analyzeExerciseVideo).toHaveBeenCalledTimes(1);
    expect(analyzeExerciseVideo).toHaveBeenCalledWith(
      "bodyweight_squat",
      expect.any(File),
      expect.any(Object),
      expect.any(Function),
    );
    expect(recognizeExerciseVideo).not.toHaveBeenCalled();
  });

  it("does not spend recognition inference on a successful selected analysis", async () => {
    await analyzeWith(report);

    expect(analyzeExerciseVideo).toHaveBeenCalledTimes(1);
    expect(recognizeExerciseVideo).not.toHaveBeenCalled();
  });

  it("explains a cloud gateway timeout without discarding the video", async () => {
    analyzeExerciseVideo.mockRejectedValue({ response: { status: 504, data: {} } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("The analysis took longer than the cloud connection allows.");
    expect(screen.getByText("squat.mp4")).toBeInTheDocument();
  });

  it("explains when a different exercise was recognized and assessed", async () => {
    const autoRouted = {
      ...report,
      exercise: "push_up",
      exercise_id: "push_up",
      exercise_name: "Push-Up",
      selected_exercise_id: "bodyweight_squat",
      recognized_exercise_id: "push_up",
      recognition_confidence: 0.86,
      recognition_status: "auto_routed",
      recognition_message: "Push-Up was recognized with 86% confidence and assessed automatically.",
      auto_routed: true,
    };

    await analyzeWith(autoRouted);

    expect(screen.getByText("Exercise recognized and assessed")).toBeInTheDocument();
    expect(screen.getByText(/recognition suggested Push-Up with 86% confidence/i)).toBeInTheDocument();
    expect(screen.getByText("Push-Up report")).toBeInTheDocument();
    expect(analyzeExerciseVideo).toHaveBeenCalledTimes(1);
  });
});

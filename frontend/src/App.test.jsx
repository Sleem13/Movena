import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import { analyzeExerciseVideo } from "./services/api.js";
import { getExercises, getSavedSession, listSavedSessions } from "./services/api.js";
import { EXERCISES } from "./data/exercises.js";
import { createPatientProfile, getPatientProfile, getPatientProgress, getTherapistDashboard, listPatientProfiles, listPatientSessions } from "./services/api.js";

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
  getRecognitionModels: vi.fn().mockResolvedValue({ status: "not_available", models: [] }),
  recognizeExerciseVideo: vi.fn(),
  listSavedSessions: vi.fn(),
  getSavedSession: vi.fn(),
  deleteSavedSession: vi.fn(),
  getTherapistDashboard: vi.fn(),
  listPatientProfiles: vi.fn(),
  createPatientProfile: vi.fn(),
  getPatientProfile: vi.fn(),
  listPatientSessions: vi.fn(),
  getPatientProgress: vi.fn(),
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

function openUpload() {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "Analyze Squat Video" }));
}

function selectVideo() {
  const file = new File(["video"], "squat.mp4", { type: "video/mp4" });
  fireEvent.change(screen.getByLabelText(/choose a squat exercise video/i), { target: { files: [file] } });
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
    listSavedSessions.mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    getTherapistDashboard.mockResolvedValue({ total_patients: 0, total_sessions: 0, low_confidence_sessions: 0, recent_sessions: [], common_detected_issues: [], sessions_by_exercise: {}, prototype_warning: "Prototype" });
    listPatientProfiles.mockResolvedValue([]);
  });

  it("renders the upload page and analysis options", () => {
    openUpload();
    expect(screen.getByText("Squat video upload")).toBeInTheDocument();
    expect(screen.getByText(/MP4, MOV, AVI, MKV, or WEBM/)).toBeInTheDocument();
    expect(screen.getByLabelText(/choose a squat exercise video/i)).toHaveAttribute("accept", ".mp4,.mov,.avi,.mkv,.webm");
    expect(screen.getByText("Analysis options")).toBeInTheDocument();
    expect(screen.getByLabelText("Annotated video")).toBeChecked();
    expect(screen.getByRole("button", { name: "Analyze squat" })).toBeDisabled();
    expect(screen.getByLabelText("Exercise selector")).toHaveValue("bodyweight_squat");
    expect(screen.getByRole("option", { name: "Sit-to-Stand" })).toBeInTheDocument();
  });

  it("renders the exercise library with supported and unavailable planned exercises", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Exercises" }));
    expect(await screen.findByText("Supported exercises")).toBeInTheDocument();
    expect(screen.getByText("Bodyweight Squat")).toBeInTheDocument();
    expect(screen.getByText("Hip Abduction")).toBeInTheDocument();
    expect(screen.getAllByText("Planned — not available yet")).toHaveLength(7);
    expect(screen.getAllByRole("button", { name: "Not available" })[0]).toBeDisabled();
  });

  it("filters the exercise library by search text and availability", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Exercises" }));
    expect(await screen.findByText("Supported exercises")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Search exercises"), { target: { value: "shoulder" } });
    fireEvent.change(screen.getByLabelText("Availability"), { target: { value: "supported" } });
    expect(screen.getByText("2 exercises match your filters.")).toBeInTheDocument();
    expect(screen.getByText("Shoulder Abduction")).toBeInTheDocument();
    expect(screen.getByText("Shoulder Press")).toBeInTheDocument();
    expect(screen.queryByText("Shoulder Flexion")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Clear exercise filters" }));
    expect(screen.getByText("16 exercises match your filters.")).toBeInTheDocument();
    expect(screen.getByText("Shoulder Flexion")).toBeInTheDocument();
  });

  it("opens Analyze from an exercise card with exercise-specific guidance", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Exercises" }));
    const cards = await screen.findAllByRole("button", { name: /Analyze this exercise/i });
    fireEvent.click(cards[3]);
    expect(screen.getByLabelText("Exercise selector")).toHaveValue("shoulder_abduction");
    expect(screen.getByText("Front view preferred.")).toBeInTheDocument();
    expect(screen.getByText(/raise the arm outward through a comfortable range/i)).toBeInTheDocument();
    expect(screen.getByText("Recording tips")).toBeInTheDocument();
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
    fireEvent.change(screen.getByLabelText("Exercise selector"), { target: { value: "sit_to_stand" } });
    expect(screen.getByText("Use a stable chair")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeDisabled();
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
    fireEvent.change(screen.getByLabelText("Exercise selector"), { target: { value: "knee_extension" } });
    expect(screen.getByText("Seated position visible")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeDisabled();
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
    fireEvent.change(screen.getByLabelText("Exercise selector"), { target: { value: "shoulder_abduction" } });
    expect(screen.getByText("Upper body visible")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeDisabled();
    const file = new File(["video"], "shoulder.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a shoulder abduction exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze shoulder abduction" }));
    await screen.findByText("Shoulder Abduction report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("shoulder_abduction", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Average shoulder")).toBeInTheDocument();
    expect(screen.getByText("Abduction range")).toBeInTheDocument();
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
    fireEvent.change(screen.getByLabelText("Exercise selector"), { target: { value: "hip_abduction" } });
    expect(screen.getByText("Full lower body visible")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeDisabled();
    const file = new File(["video"], "hip.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a hip abduction exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze hip abduction" }));
    await screen.findByText("Hip Abduction report");
    expect(analyzeExerciseVideo).toHaveBeenCalledWith("hip_abduction", expect.any(File), expect.any(Object), expect.any(Function));
    expect(screen.getByText("Average hip abduction")).toBeInTheDocument();
    expect(screen.getByText("Pelvis/trunk stability")).toBeInTheDocument();
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
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "History" }));
    expect(await screen.findByText(/No saved sessions yet/i)).toBeInTheDocument();
  });

  it("filters session history by exercise and status", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "History" }));
    await screen.findByText(/No saved sessions yet/i);
    fireEvent.change(screen.getByLabelText("Exercise"), { target: { value: "hip_abduction" } });
    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "rejected" } });
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
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "History" }));
    expect(await screen.findByText("Sit-to-Stand")).toBeInTheDocument();
    expect(screen.getByText("Poor Control")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "View details" }));
    expect(await screen.findByText("Three repetitions analyzed.")).toBeInTheDocument();
  });

  it("renders therapist dashboard summary, empty profiles, and privacy warning", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Therapist" }));
    expect(await screen.findByText("Total patients")).toBeInTheDocument();
    expect(screen.getByText(/prototype dashboard for development use only/i)).toBeInTheDocument();
    expect(screen.getByText(/do not enter real patient-identifiable information/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Patient profiles" }));
    expect(screen.getByText("No development patient profiles yet")).toBeInTheDocument();
  });

  it("renders a development profile and patient session detail", async () => {
    const patient = { patient_id: "patient-1234", display_name: "Demo Profile A", age_group: "adult", clinical_group: "unknown", session_count: 1 };
    listPatientProfiles.mockResolvedValue([patient]);
    getPatientProfile.mockResolvedValue({ ...patient, notes: null });
    listPatientSessions.mockResolvedValue([{ session_id: "session-1", exercise_display_name: "Bodyweight Squat", total_reps: 3, movement_score: 88 }]);
    getPatientProgress.mockResolvedValue({ total_sessions: 1, average_movement_score: 88, average_analysis_confidence: 0.8, low_confidence_session_count: 0, detected_issue_counts: [{ issue_code: "poor_depth", count: 1 }] });
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Therapist" }));
    await screen.findByText("Total patients");
    fireEvent.click(screen.getByRole("button", { name: "Patient profiles" }));
    expect(screen.getByText("Demo Profile A")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "View profile" }));
    expect(await screen.findByText("Exercise session history")).toBeInTheDocument();
    expect(screen.getByText(/Bodyweight Squat · 3 reps · score 88/i)).toBeInTheDocument();
    expect(screen.getByText("Poor Depth: 1")).toBeInTheDocument();
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
    expect(screen.getByText(/PhysioVision AI supports exercise monitoring and does not replace assessment by a licensed physiotherapist/i)).toBeInTheDocument();
  });

  it("renders the ML second opinion only when returned", async () => {
    await analyzeWith({ ...report, ml_prediction: { enabled: true, predicted_label: "squat_correct", confidence: 0.82, model_name: "svc_rbf", model_version: "sprint_5_baseline", warning: "Experimental baseline model. Not clinically validated." } });
    expect(screen.getByText("ML second opinion")).toBeInTheDocument();
    expect(screen.getByText("Squat Correct")).toBeInTheDocument();
    expect(screen.getByText("82%")).toBeInTheDocument();
    expect(screen.getByText("svc_rbf")).toBeInTheDocument();
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
    const video = screen.getByLabelText("Annotated squat movement preview");
    expect(video).toHaveAttribute("preload", "metadata");
    expect(video.querySelector("source")).toHaveAttribute("src", "http://127.0.0.1:8000/api/v1/artifacts/overlays/test-overlay/preview");
    expect(screen.getAllByRole("link", { name: "Download annotated video" })[0]).toHaveAttribute(
      "href", "http://127.0.0.1:8000/api/v1/artifacts/overlays/test-overlay/download"
    );
  });

  it("shows a fallback when annotated video playback fails", async () => {
    await analyzeWith();
    fireEvent.error(screen.getByLabelText("Annotated squat movement preview"));
    expect(screen.getByText("Annotated preview could not be loaded")).toBeInTheDocument();
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

  it("does not start analysis while the user is logged out", async () => {
    authState.user = null;
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Please log in before analyzing a video.");
    expect(analyzeExerciseVideo).not.toHaveBeenCalled();
  });

  it("shows the supported formats for an unsupported-file response", async () => {
    analyzeExerciseVideo.mockRejectedValue({ response: { status: 400, data: { error_code: "UNSUPPORTED_FILE_TYPE" } } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Unsupported video format. Please upload MP4, MOV, AVI, MKV, or WEBM.");
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
});

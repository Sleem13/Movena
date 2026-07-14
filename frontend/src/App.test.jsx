import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import { analyzeSitToStandVideo, analyzeSquatVideo } from "./services/api.js";

vi.mock("./services/api.js", () => ({
  analyzeSquatVideo: vi.fn(),
  analyzeSitToStandVideo: vi.fn(),
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
  analyzeSquatVideo.mockResolvedValue(response);
  openUpload();
  selectVideo();
  fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
  await screen.findByText(response.status === "rejected" ? "Recording rejected" : "Analysis complete");
}

describe("Squat Analyzer healthcare dashboard", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders the upload page and analysis options", () => {
    openUpload();
    expect(screen.getByText("Squat video upload")).toBeInTheDocument();
    expect(screen.getByText("Analysis options")).toBeInTheDocument();
    expect(screen.getByLabelText("Annotated video")).toBeChecked();
    expect(screen.getByRole("button", { name: "Analyze squat" })).toBeDisabled();
    expect(screen.getByLabelText("Exercise selector")).toHaveValue("bodyweight_squat");
    expect(screen.getByRole("option", { name: "Sit-to-Stand" })).toBeInTheDocument();
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
    analyzeSitToStandVideo.mockResolvedValue(sitReport);
    openUpload();
    fireEvent.change(screen.getByLabelText("Exercise selector"), { target: { value: "sit_to_stand" } });
    expect(screen.getByText("Use a stable chair")).toBeInTheDocument();
    expect(screen.getByLabelText("ML second opinion")).toBeDisabled();
    const file = new File(["video"], "chair.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText(/choose a sit-to-stand exercise video/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze sit-to-stand" }));
    await screen.findByText("Sit-to-Stand report");
    expect(analyzeSitToStandVideo).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/not available for sit-to-stand yet/i)).toBeInTheDocument();
    expect(screen.getByText("Completion")).toBeInTheDocument();
  });

  it("renders the camera placement guide", () => {
    openUpload();
    expect(screen.getByText("Camera placement guide")).toBeInTheDocument();
    expect(screen.getByText("Side view")).toBeInTheDocument();
    expect(screen.getByText(/best for squat depth and trunk lean/i)).toBeInTheDocument();
    expect(screen.getByText(/avoid very loose clothing/i)).toBeInTheDocument();
  });

  it("shows loading progress after a video is submitted", async () => {
    analyzeSquatVideo.mockReturnValue(new Promise(() => {}));
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByText("Analyzing")).toBeInTheDocument();
    expect(screen.getByText(/uploading video/i)).toBeInTheDocument();
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
    analyzeSquatVideo.mockRejectedValue({ response: { data: { message: "Video is too large." } } });
    openUpload(); selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Video is too large.");
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

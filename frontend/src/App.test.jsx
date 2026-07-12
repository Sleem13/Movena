import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import { analyzeSquatVideo } from "./services/api.js";

vi.mock("./services/api.js", () => ({
  analyzeSquatVideo: vi.fn(),
  artifactUrl: (path) => path ? `http://127.0.0.1:8000${path}` : null,
}));

const report = {
  total_reps: 2,
  average_knee_angle: 98,
  average_hip_angle: 75,
  average_trunk_angle: 20,
  movement_score: 90,
  detected_issues: ["poor_depth"],
  feedback: [
    "Possible movement issue detected.",
    "This analysis is educational and does not replace assessment by a licensed physiotherapist.",
  ],
  summary: "Two repetitions analyzed.",
  limitations: ["This does not replace clinical assessment."],
  report_download_url: "/api/v1/artifacts/reports/test-report",
  overlay_download_url: "/api/v1/artifacts/overlays/test-overlay",
};

function openUpload() {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "Analyze Squat Video" }));
}

function selectVideo() {
  const file = new File(["video"], "squat.mp4", { type: "video/mp4" });
  fireEvent.change(screen.getByLabelText(/choose a squat exercise video/i), {
    target: { files: [file] },
  });
}

describe("Squat Analyzer UI", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders upload controls and disables submit without a file", () => {
    openUpload();
    expect(screen.getByText("Squat video upload")).toBeInTheDocument();
    expect(screen.getByText("Camera placement guide")).toBeInTheDocument();
    expect(screen.getByText(/side view for squat depth/i)).toBeInTheDocument();
    expect(screen.getByText(/avoid very loose clothing/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze squat" })).toBeDisabled();
  });

  it("accepts a video and shows the loading state", async () => {
    analyzeSquatVideo.mockReturnValue(new Promise(() => {}));
    openUpload();
    selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByRole("button", { name: "Analyzing" })).toBeDisabled();
  });

  it("displays a backend API error", async () => {
    analyzeSquatVideo.mockRejectedValue({ response: { data: { message: "Video is too large." } } });
    openUpload();
    selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByText("Video is too large.")).toBeInTheDocument();
  });

  it("displays repetitions, score, issues, feedback, and disclaimer", async () => {
    analyzeSquatVideo.mockResolvedValue(report);
    openUpload();
    selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    await waitFor(() => expect(screen.getByText("Analysis complete")).toBeInTheDocument());
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("90")).toBeInTheDocument();
    expect(screen.getByText("poor depth")).toBeInTheDocument();
    expect(screen.getByText("Possible movement issue detected.")).toBeInTheDocument();
    expect(screen.getByText(/does not replace assessment by a licensed physiotherapist/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /download pdf report/i })).toBeInTheDocument();
    expect(screen.getByText("Annotated movement preview")).toBeInTheDocument();
    expect(document.querySelector("video source")).toHaveAttribute(
      "src", "http://127.0.0.1:8000/api/v1/artifacts/overlays/test-overlay"
    );
    expect(screen.getByText("Educational analysis only")).toBeInTheDocument();
  });

  it("shows an annotated preview fallback when no overlay URL exists", async () => {
    analyzeSquatVideo.mockResolvedValue({ ...report, overlay_download_url: null });
    openUpload();
    selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    expect(await screen.findByText("No annotated preview was generated for this analysis.")).toBeInTheDocument();
  });

  it("shows a helpful fallback when the overlay video fails to load", async () => {
    analyzeSquatVideo.mockResolvedValue(report);
    openUpload();
    selectVideo();
    fireEvent.click(screen.getByRole("button", { name: "Analyze squat" }));
    const video = await screen.findByLabelText("Annotated squat movement preview");
    fireEvent.error(video);
    expect(screen.getByText(/annotated preview could not be loaded/i)).toBeInTheDocument();
  });
});

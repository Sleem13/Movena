import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LocaleProvider } from "../../i18n/LocaleContext.jsx";
import RecognitionUploadCard from "./RecognitionUploadCard.jsx";
import { recognizeExerciseVideo } from "../../services/api.js";
import { confirmRecognitionSuggestion } from "../../services/api.js";


vi.mock("../../services/api.js", () => ({
  recognizeExerciseVideo: vi.fn(),
  confirmRecognitionSuggestion: vi.fn().mockResolvedValue({ status: "confirmed" }),
}));

const temporalModel = {
  model_id: "exercise_pose_gru_candidate",
  artifact_format: "torchscript_sequence",
  status: "candidate",
};


describe("RecognitionUploadCard", () => {
  it("uploads a clip, presents ranked suggestions, and requires confirmation", async () => {
    const onConfirm = vi.fn();
    recognizeExerciseVideo.mockResolvedValue({
      status: "success",
      suggested_exercise_id: "push_up",
      confidence: 0.83,
      analyzer_available: true,
      recognition_event_id: "11111111-1111-1111-1111-111111111111",
      top_predictions: [
        { exercise_id: "push_up", confidence: 0.83 },
        { exercise_id: "shoulder_press", confidence: 0.11 },
      ],
    });
    render(
      <LocaleProvider>
        <RecognitionUploadCard models={[temporalModel]} onConfirmSuggestion={onConfirm} />
      </LocaleProvider>,
    );
    const file = new File(["video"], "push-up.mp4", { type: "video/mp4" });
    fireEvent.change(screen.getByLabelText("Choose a movement video"), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Identify exercise" }));
    await waitFor(() => expect(screen.getByText("Model confidence 83%")).toBeInTheDocument());
    expect(screen.getAllByText("Push-Up")).toHaveLength(2);
    expect(onConfirm).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Confirm push-up and continue" }));
    await waitFor(() => expect(confirmRecognitionSuggestion).toHaveBeenCalledWith(
      "11111111-1111-1111-1111-111111111111", "push_up",
    ));
    expect(onConfirm).toHaveBeenCalledWith("push_up", file);
  });

  it("does not offer analyzer routing for a recognized unsupported label", async () => {
    recognizeExerciseVideo.mockResolvedValue({
      status: "success",
      suggested_exercise_id: "hammer_curl",
      confidence: 0.72,
      analyzer_available: false,
      top_predictions: [{ exercise_id: "hammer_curl", confidence: 0.72 }],
    });
    render(<LocaleProvider><RecognitionUploadCard models={[temporalModel]} /></LocaleProvider>);
    fireEvent.change(screen.getByLabelText("Choose a movement video"), {
      target: { files: [new File(["video"], "curl.mp4", { type: "video/mp4" })] },
    });
    fireEvent.click(screen.getByRole("button", { name: "Identify exercise" }));
    await waitFor(() => expect(screen.getByText("Analyzer unavailable")).toBeInTheDocument());
    expect(screen.queryByRole("button", { name: /confirm/i })).not.toBeInTheDocument();
  });

  it("blocks confirmation when calibrated confidence requires abstention", async () => {
    recognizeExerciseVideo.mockResolvedValue({
      status: "uncertain",
      suggested_exercise_id: "push_up",
      confidence: 0.54,
      confidence_threshold: 0.75,
      analyzer_available: true,
      top_predictions: [{ exercise_id: "push_up", confidence: 0.54 }],
    });
    render(<LocaleProvider><RecognitionUploadCard models={[temporalModel]} /></LocaleProvider>);
    fireEvent.change(screen.getByLabelText("Choose a movement video"), {
      target: { files: [new File(["video"], "uncertain.mp4", { type: "video/mp4" })] },
    });
    fireEvent.click(screen.getByRole("button", { name: "Identify exercise" }));
    await waitFor(() => expect(screen.getByText("Choose the exercise manually")).toBeInTheDocument());
    expect(screen.getByText(/75% acceptance threshold/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /confirm/i })).not.toBeInTheDocument();
  });
});

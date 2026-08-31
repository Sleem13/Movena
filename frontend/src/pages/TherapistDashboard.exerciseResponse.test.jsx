import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ExerciseResponseReview } from "./TherapistDashboard.jsx";
import { acknowledgeExerciseResponse } from "../services/api.js";

vi.mock("../services/api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  acknowledgeExerciseResponse: vi.fn(),
}));

describe("ExerciseResponseReview", () => {
  it("requires attestation and records a bounded clinical disposition", async () => {
    acknowledgeExerciseResponse.mockResolvedValue({
      adherence_id: "entry-1",
      clinician_review_required: false,
      reviewed_at: "2026-08-31T16:00:00Z",
      review_disposition: "contacted_patient",
    });
    const onReviewed = vi.fn();
    render(
      <ExerciseResponseReview
        patientId="patient-1"
        entry={{
          adherence_id: "entry-1",
          response_state: "clinical_follow_up",
          clinician_review_required: true,
          reviewed_at: null,
        }}
        onReviewed={onReviewed}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Review" }));
    const submit = screen.getByRole("button", { name: "Acknowledge review" });
    expect(submit).toBeDisabled();
    fireEvent.click(screen.getByLabelText(/I attest that I reviewed/i));
    fireEvent.click(submit);

    await waitFor(() => expect(acknowledgeExerciseResponse).toHaveBeenCalledWith(
      "patient-1",
      "entry-1",
      expect.objectContaining({
        disposition: "contacted_patient",
        clinician_attestation: true,
      }),
    ));
    expect(onReviewed).toHaveBeenCalled();
  });
});

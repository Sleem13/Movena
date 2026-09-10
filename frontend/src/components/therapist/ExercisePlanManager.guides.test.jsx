import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import ExercisePlanManager from "./ExercisePlanManager.jsx";
import { createPatientExercisePlan } from "../../services/api.js";

vi.mock("../../services/api.js", () => ({
  createPatientExercisePlan: vi.fn().mockResolvedValue({ plan_id: "synthetic-plan", items: [] }),
  updatePatientExercisePlanStatus: vi.fn(),
}));

it("assigns a guide with editable instructions and clears incompatible analysis requirements", async () => {
  const onPlansChange = vi.fn();
  const { container } = render(<ExercisePlanManager patientId="synthetic-patient" plans={[]} onPlansChange={onPlansChange} />);
  fireEvent.click(screen.getByLabelText("Require Movena analysis"));
  fireEvent.click(screen.getByLabelText("Request video"));
  fireEvent.click(screen.getByRole("combobox"));
  fireEvent.click(screen.getByRole("option", { name: "Ankle Pumps" }));
  expect(screen.getByLabelText("Require Movena analysis")).toBeDisabled();
  expect(screen.getByLabelText("Require Movena analysis")).not.toBeChecked();
  expect(screen.getByLabelText("Request video")).not.toBeChecked();
  fireEvent.click(screen.getByRole("button", { name: "Use guide instructions" }));
  fireEvent.change(container.querySelector('input[maxlength="120"]'), { target: { value: "Synthetic care plan" } });
  fireEvent.submit(container.querySelector("form"));
  await waitFor(() => expect(onPlansChange).toHaveBeenCalled());
  const item = createPatientExercisePlan.mock.calls[0][1].items[0];
  expect(item.exercise_id).toBe("ankle_pumps");
  expect(item.instructions).toContain("Move the foot toward you");
  expect(item.precautions).toContain("immobilization");
  expect(item.requires_ai_analysis).toBe(false);
  expect(item.requested_media_upload).toBe(false);
});

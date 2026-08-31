import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import PatientCareDashboard from "./PatientCareDashboard.jsx";
import {
  getPatientToday, listCatalog, listPatientAppointments,
  listPatientNotifications, recordPatientAdherence,
} from "../services/api.js";

vi.mock("../services/api.js", () => ({
  getPatientToday: vi.fn(),
  listCatalog: vi.fn(),
  listPatientAppointments: vi.fn(),
  listPatientNotifications: vi.fn(),
  recordPatientAdherence: vi.fn(),
  joinAppointment: vi.fn(),
  markPatientNotificationRead: vi.fn(),
  startCheckout: vi.fn(),
}));
vi.mock("../i18n/LocaleContext.jsx", () => ({
  useLocale: () => ({ locale: "en" }),
}));
vi.mock("../context/AuthContext.jsx", () => ({
  useAuth: () => ({ user: { full_name: "Patient One" } }),
}));

const today = {
  date: "2026-08-31",
  plan_title: "Graded activity",
  plan_items: [{
    item_id: "item-1",
    exercise_id: "sit_to_stand",
    sets: 2,
    reps: 6,
    symptom_flags: [],
  }],
  adherence_percent_7d: 75,
  average_pain_7d: 3,
};

describe("PatientCareDashboard exercise response", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getPatientToday.mockResolvedValue(today);
    listPatientAppointments.mockResolvedValue([]);
    listPatientNotifications.mockResolvedValue([]);
    listCatalog.mockResolvedValue({ services: [], packages: [] });
    recordPatientAdherence.mockResolvedValue({
      response_state: "clinical_follow_up",
      clinician_review_required: true,
      supportive_instruction: "Do not progress this exercise. Contact your treating clinician for review.",
    });
  });

  it("captures symptom context and shows the returned follow-up instruction", async () => {
    render(<PatientCareDashboard />);
    const startButtons = await screen.findAllByRole("button", { name: "Start exercise" });
    fireEvent.click(startButtons[0]);
    fireEvent.change(screen.getByLabelText("Effort (0–10)"), { target: { value: "9" } });
    fireEvent.click(screen.getByLabelText("I noticed new or worsening symptoms."));
    fireEvent.click(screen.getByLabelText("Dizziness"));
    fireEvent.click(screen.getByLabelText(/I understand this check-in is not monitored/i));
    fireEvent.click(screen.getByRole("button", { name: "Save check-in" }));

    await waitFor(() => expect(recordPatientAdherence).toHaveBeenCalledWith(
      expect.objectContaining({
        plan_item_id: "item-1",
        perceived_exertion: 9,
        symptoms_changed: true,
        symptom_flags: ["dizziness"],
        safety_acknowledged: true,
      }),
    ));
    expect(await screen.findByText("Your therapist needs to review this response")).toBeInTheDocument();
    expect(screen.getByText(/Do not progress this exercise/i)).toBeInTheDocument();
  });
});

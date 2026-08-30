import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import RecoveryCoachingWorkspace from "./RecoveryCoachingWorkspace.jsx";
import {
  acknowledgeRecoveryCoachingCheckIn, createRecoveryCoachingCheckIn,
  getRecoveryCoachingDashboard, getRecoveryCoachingTemplates,
} from "../services/api.js";

vi.mock("../services/api.js", () => ({
  getRecoveryCoachingDashboard: vi.fn(),
  getRecoveryCoachingTemplates: vi.fn(),
  createRecoveryCoachingGoal: vi.fn(),
  createRecoveryCoachingCheckIn: vi.fn(),
  createRecoveryCoachingActionPlan: vi.fn(),
  updateRecoveryCoachingGoal: vi.fn(),
  acknowledgeRecoveryCoachingCheckIn: vi.fn(),
  updateRecoveryCoachingReminderPreference: vi.fn(),
  listPatientProfiles: vi.fn().mockResolvedValue([]),
}));

const dashboard = {
  patient: { patient_id: "profile-1", display_name: "Patient One" },
  goals: [], check_ins: [], action_plans: [], trends: [],
  reminder_preference: { enabled: false, local_time: "19:00", cadence: "daily", missed_follow_up_days: 3, patient_agreed: false },
  summary: { active_goals: 0, completed_goals: 0, check_ins_30d: 0, average_confidence: null, follow_up_needed: 0, unacknowledged_follow_up: 0 },
  scope: { disclaimer: "Coaching does not replace care.", urgent_instruction: "Follow the urgent pathway.", urgent_contact: "", organization: "Clinic" },
};

describe("RecoveryCoachingWorkspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getRecoveryCoachingDashboard.mockResolvedValue(dashboard);
    getRecoveryCoachingTemplates.mockResolvedValue({ templates: [], can_apply_template: false });
  });

  it("renders trends separately from validated outcomes", async () => {
    getRecoveryCoachingDashboard.mockResolvedValue({
      ...dashboard,
      trends: [{ check_in_id: "check-1", check_in_date: "2026-08-30", energy: 3, sleep_quality: 4, stress: 2, recovery_confidence: 4, activity_minutes: 20 }],
    });
    render(<RecoveryCoachingWorkspace user={{ role: "patient" }} />);
    await screen.findByRole("heading", { name: "Recovery & Lifestyle Coaching" });
    fireEvent.click(screen.getByRole("tab", { name: "Trends" }));
    expect(screen.getByText(/shown separately from validated clinical outcome measures/i)).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Recovery reflection trends" })).toBeInTheDocument();
  });

  it("allows a clinician to acknowledge a follow-up with attestation", async () => {
    getRecoveryCoachingDashboard.mockResolvedValue({
      ...dashboard,
      check_ins: [{ check_in_id: "check-1", check_in_date: "2026-08-30", coaching_state: "clinical_follow_up", supportive_prompt: "Contact the treating clinician.", reviewed_at: null }],
    });
    acknowledgeRecoveryCoachingCheckIn.mockResolvedValue({ reviewed_at: "2026-08-30T12:00:00Z" });
    const { listPatientProfiles } = await import("../services/api.js");
    listPatientProfiles.mockResolvedValue([{ patient_id: "profile-1", display_name: "Patient One" }]);
    render(<RecoveryCoachingWorkspace user={{ role: "therapist" }} />);
    await screen.findByRole("heading", { name: "Recovery & Lifestyle Coaching" });
    fireEvent.click(screen.getByRole("tab", { name: "Follow-up needed" }));
    fireEvent.click(screen.getByLabelText(/I attest that I reviewed this check-in/i));
    fireEvent.click(screen.getByRole("button", { name: "Acknowledge follow-up" }));
    await waitFor(() => expect(acknowledgeRecoveryCoachingCheckIn).toHaveBeenCalledWith(
      "check-1", expect.objectContaining({ clinician_attestation: true }), "profile-1",
    ));
  });

  it("renders the bounded patient coaching workspace", async () => {
    render(<RecoveryCoachingWorkspace user={{ role: "patient" }} />);
    expect(await screen.findByRole("heading", { name: "Recovery & Lifestyle Coaching" })).toBeInTheDocument();
    expect(screen.getByText(/does not diagnose, prescribe, provide psychotherapy/i)).toBeInTheDocument();
    expect(screen.getByText("No coaching goals yet.")).toBeInTheDocument();
  });

  it("supports arrow-key navigation across the tab workspace", async () => {
    render(<RecoveryCoachingWorkspace user={{ role: "patient" }} />);
    const overview = await screen.findByRole("tab", { name: "Overview" });
    overview.focus();
    fireEvent.keyDown(overview, { key: "ArrowRight" });
    const checkIn = screen.getByRole("tab", { name: "Daily check-in" });
    expect(checkIn).toHaveAttribute("aria-selected", "true");
    await waitFor(() => expect(checkIn).toHaveFocus());
  });

  it("hard-labels an urgent check-in and shows the returned escalation prompt", async () => {
    createRecoveryCoachingCheckIn.mockResolvedValue({
      coaching_state: "urgent_escalation",
      supportive_prompt: "Coaching is paused. Follow the approved emergency pathway.",
    });
    render(<RecoveryCoachingWorkspace user={{ role: "patient" }} />);
    await screen.findByRole("heading", { name: "Recovery & Lifestyle Coaching" });
    fireEvent.click(screen.getByRole("tab", { name: "Daily check-in" }));
    fireEvent.click(screen.getByLabelText("I have an immediate safety or health concern."));
    fireEvent.click(screen.getByLabelText("I understand this check-in is not emergency or diagnostic care."));
    fireEvent.click(screen.getByRole("button", { name: "Save check-in" }));
    await waitFor(() => expect(createRecoveryCoachingCheckIn).toHaveBeenCalled());
    expect(await screen.findByText("Coaching is paused. Follow the approved emergency pathway.")).toBeInTheDocument();
  });
});

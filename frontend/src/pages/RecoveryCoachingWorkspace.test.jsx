import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import RecoveryCoachingWorkspace from "./RecoveryCoachingWorkspace.jsx";
import {
  createRecoveryCoachingCheckIn, getRecoveryCoachingDashboard,
} from "../services/api.js";

vi.mock("../services/api.js", () => ({
  getRecoveryCoachingDashboard: vi.fn(),
  createRecoveryCoachingGoal: vi.fn(),
  createRecoveryCoachingCheckIn: vi.fn(),
  createRecoveryCoachingActionPlan: vi.fn(),
  updateRecoveryCoachingGoal: vi.fn(),
  listPatientProfiles: vi.fn().mockResolvedValue([]),
}));

const dashboard = {
  patient: { patient_id: "profile-1", display_name: "Patient One" },
  goals: [], check_ins: [], action_plans: [],
  summary: { active_goals: 0, completed_goals: 0, check_ins_30d: 0, average_confidence: null, follow_up_needed: 0 },
  scope: { disclaimer: "Coaching does not replace care.", urgent_instruction: "Follow the urgent pathway.", urgent_contact: "", organization: "Clinic" },
};

describe("RecoveryCoachingWorkspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getRecoveryCoachingDashboard.mockResolvedValue(dashboard);
  });

  it("renders the bounded patient coaching workspace", async () => {
    render(<RecoveryCoachingWorkspace user={{ role: "patient" }} />);
    expect(await screen.findByRole("heading", { name: "Recovery & Lifestyle Coaching" })).toBeInTheDocument();
    expect(screen.getByText(/does not diagnose, prescribe, provide psychotherapy/i)).toBeInTheDocument();
    expect(screen.getByText("No coaching goals yet.")).toBeInTheDocument();
  });

  it("hard-labels an urgent check-in and shows the returned escalation prompt", async () => {
    createRecoveryCoachingCheckIn.mockResolvedValue({
      coaching_state: "urgent_escalation",
      supportive_prompt: "Coaching is paused. Follow the approved emergency pathway.",
    });
    render(<RecoveryCoachingWorkspace user={{ role: "patient" }} />);
    await screen.findByRole("heading", { name: "Recovery & Lifestyle Coaching" });
    fireEvent.click(screen.getByRole("button", { name: "Daily check-in" }));
    fireEvent.click(screen.getByLabelText("I have an immediate safety or health concern."));
    fireEvent.click(screen.getByLabelText("I understand this check-in is not emergency or diagnostic care."));
    fireEvent.click(screen.getByRole("button", { name: "Save check-in" }));
    await waitFor(() => expect(createRecoveryCoachingCheckIn).toHaveBeenCalled());
    expect(await screen.findByText("Coaching is paused. Follow the approved emergency pathway.")).toBeInTheDocument();
  });
});

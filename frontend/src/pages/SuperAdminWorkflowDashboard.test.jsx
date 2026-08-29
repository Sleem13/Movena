import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

const api = vi.hoisted(() => ({ getAdminWorkflow: vi.fn() }));
vi.mock("../services/api.js", () => api);

import SuperAdminWorkflowDashboard from "./SuperAdminWorkflowDashboard.jsx";

const snapshot = {
  generated_at: "2026-08-29T09:00:00Z",
  metrics: {
    users: 81,
    patients: 48,
    active_assignments: 46,
    appointments: 23,
    paid_orders: 18,
  },
  stages: [
    {
      key: "account_consent",
      total: 48,
      attention_count: 0,
      status: "on_track",
    },
    {
      key: "therapist_assignment",
      total: 46,
      attention_count: 2,
      status: "attention",
    },
    { key: "care_plan", total: 44, attention_count: 1, status: "attention" },
    { key: "appointment", total: 23, attention_count: 0, status: "on_track" },
    { key: "payment", total: 18, attention_count: 1, status: "attention" },
    { key: "follow_up", total: 12, attention_count: 0, status: "on_track" },
  ],
  attention_queue: [
    {
      id: "assignment:1",
      type: "assignment",
      subject_ref: "Patient …cbeef001",
      owner: "Assignment Team",
      age_seconds: 90000,
      priority: "medium",
    },
    {
      id: "payment:1",
      type: "payment",
      subject_ref: "Order …cbeef002",
      owner: "Payments Team",
      age_seconds: 7000,
      priority: "high",
    },
    {
      id: "password_recovery:1",
      type: "password_recovery",
      subject_ref: "User …target01",
      owner: "Account Support",
      age_seconds: 120,
      priority: "high",
      action_url: "/admin/users/target-user-id",
    },
  ],
  today: { date: "2026-08-29", appointments: 6 },
  payment_exceptions: {
    pending_orders: 1,
    failed_payments: 1,
    pending_refunds: 0,
  },
  privacy_requests: { pending: 2, export: 1, correction: 0, deletion: 1 },
  recent_audit: [
    {
      id: 1,
      actor_ref: "User …cbeef009",
      action: "assignment.updated",
      resource_ref: "Assignment …cbeef010",
      created_at: "2026-08-29T08:00:00Z",
    },
  ],
};

beforeEach(() => {
  vi.clearAllMocks();
  api.getAdminWorkflow.mockResolvedValue(snapshot);
});

it("renders the de-identified operational workflow and filters exceptions", async () => {
  render(<SuperAdminWorkflowDashboard />);
  expect(
    await screen.findByRole("heading", { name: "Operations Dashboard" }),
  ).toBeInTheDocument();
  expect(screen.getByText("81")).toBeInTheDocument();
  expect(screen.getByText("Patient …cbeef001")).toBeInTheDocument();
  expect(screen.queryByText(/Ahmed|Mona|Sarah/)).not.toBeInTheDocument();

  fireEvent.change(screen.getByLabelText("Workflow type"), {
    target: { value: "payment" },
  });
  expect(screen.queryByText("Patient …cbeef001")).not.toBeInTheDocument();
  expect(screen.getByText("Order …cbeef002")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Review" }));
  expect(screen.getByText(/Reviewing Order/)).toBeInTheDocument();
});

it("routes password recovery alerts to the affected user account", async () => {
  const onNavigate = vi.fn();
  render(<SuperAdminWorkflowDashboard onNavigate={onNavigate} />);
  await screen.findByRole("heading", { name: "Operations Dashboard" });
  fireEvent.change(screen.getByLabelText("Workflow type"), {
    target: { value: "password_recovery" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Review" }));
  expect(onNavigate).toHaveBeenCalledWith("adminUsers", {
    user: "target-user-id",
  });
});

it("retries when the snapshot fails", async () => {
  api.getAdminWorkflow
    .mockRejectedValueOnce(new Error("offline"))
    .mockResolvedValueOnce(snapshot);
  render(<SuperAdminWorkflowDashboard />);
  fireEvent.click(await screen.findByRole("button", { name: "Try again" }));
  await waitFor(() => expect(api.getAdminWorkflow).toHaveBeenCalledTimes(2));
  expect(await screen.findByText("Care delivery workflow")).toBeInTheDocument();
});

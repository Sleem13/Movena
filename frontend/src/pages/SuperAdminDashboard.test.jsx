import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

const api = vi.hoisted(() => ({
  createManagedUser: vi.fn(),
  deleteManagedUser: vi.fn(),
  getManagedUser: vi.fn(),
  listManagedUsers: vi.fn(),
  resetManagedUserPassword: vi.fn(),
  updateManagedUserRole: vi.fn(),
  updateManagedUserStatus: vi.fn(),
}));

vi.mock("../services/api.js", () => api);

import SuperAdminDashboard from "./SuperAdminDashboard.jsx";

beforeEach(() => {
  vi.clearAllMocks();
  api.listManagedUsers.mockResolvedValue([]);
  api.createManagedUser.mockResolvedValue({
    user_id: "created-1", username: "therapist.one", email: "therapist@example.com",
    full_name: "Therapist One", role: "patient", is_verified: true,
  });
  api.getManagedUser.mockResolvedValue({
    user_id: "created-1", username: "therapist.one", email: "therapist@example.com",
    full_name: "Therapist One", role: "patient", is_verified: true,
    is_active: true, account_status: "active", sessions: [], consents: [], session_count: 0,
  });
});

it("lets a super administrator create an active user with assigned credentials", async () => {
  render(<SuperAdminDashboard />);
  fireEvent.click(screen.getByRole("button", { name: "Create user" }));
  fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Therapist One" } });
  fireEvent.change(screen.getByLabelText("Username"), { target: { value: "therapist.one" } });
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "therapist@example.com" } });
  fireEvent.change(screen.getByLabelText("Temporary password"), { target: { value: "AssignedPassword123" } });
  fireEvent.click(screen.getByRole("button", { name: "Create active account" }));

  await waitFor(() => expect(api.createManagedUser).toHaveBeenCalledWith({
    full_name: "Therapist One",
    username: "therapist.one",
    email: "therapist@example.com",
    password: "AssignedPassword123",
    role: "patient",
  }));
  expect(await screen.findByText(/active and ready to log in/i)).toBeInTheDocument();
});

import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CareConnections from "./CareConnections.jsx";
import { connectionsApi as api } from "../services/connectionsApi.js";

const context = vi.hoisted(() => ({
  user: { role: "patient", is_verified: true },
  locale: "en",
}));
vi.mock("../context/AuthContext.jsx", () => ({
  useAuth: () => ({ user: context.user }),
}));
vi.mock("../i18n/LocaleContext.jsx", () => ({
  useLocale: () => ({ locale: context.locale }),
}));
vi.mock("../services/connectionsApi.js", () => ({
  connectionsApi: {
    list: vi.fn(),
    invitations: vi.fn(),
    invite: vi.fn(),
    respond: vi.fn(),
    manage: vi.fn(),
    end: vi.fn(),
    options: vi.fn(),
    assign: vi.fn(),
    lookup: vi.fn(),
  },
  pendingInvitation: () => null,
  clearInvitation: vi.fn(),
}));
const invitation = {
  invitation_id: "i",
  therapist_name: "Dr Morgan",
  email: "patient@example.com",
  status: "pending",
  expires_at: "2026-09-16",
  delivery_status: "sent",
};
const connection = {
  assignment_id: "a",
  therapist_name: "Dr Morgan",
  patient_name: "Alex",
  status: "active",
  source: "invitation",
  assigned_at: "2026-09-09",
};

beforeEach(() => {
  vi.clearAllMocks();
  context.user = { role: "patient", is_verified: true };
  context.locale = "en";
  api.list.mockResolvedValue([]);
  api.invitations.mockResolvedValue([]);
  api.options.mockResolvedValue({
    patients: [{ patient_id: "p", name: "Alex" }],
    therapists: [{ user_id: "t", name: "Dr Morgan" }],
  });
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});

describe("Care connections", () => {
  it("keeps independent patients informed without blocking self-directed care", async () => {
    render(<CareConnections />);
    expect(
      await screen.findByText("No connected therapist"),
    ).toBeInTheDocument();
    expect(screen.getByText(/exercises, movement checks/)).toBeInTheDocument();
  });
  it("requires a sharing confirmation before accepting", async () => {
    api.invitations.mockResolvedValue([invitation]);
    render(<CareConnections />);
    await screen.findByText("No connected therapist");
    fireEvent.click(screen.getByRole("tab", { name: "Invitations" }));
    fireEvent.click(screen.getByRole("button", { name: "Accept connection" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("full care record");
    expect(api.respond).not.toHaveBeenCalled();
    fireEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "Confirm",
      }),
    );
    await waitFor(() =>
      expect(api.respond).toHaveBeenCalledWith("i", "accept", undefined),
    );
  });
  it("ends a connection without deleting a patient", async () => {
    api.list.mockResolvedValue([connection]);
    render(<CareConnections />);
    fireEvent.click(
      await screen.findByRole("button", { name: "End connection" }),
    );
    expect(screen.getByRole("dialog")).toHaveTextContent(
      "records and plans will be kept",
    );
    fireEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "Confirm",
      }),
    );
    await waitFor(() => expect(api.end).toHaveBeenCalledWith("a", ""));
  });
  it("lets therapists retry failed invitation email", async () => {
    context.user = { role: "therapist" };
    api.invitations.mockResolvedValue([
      { ...invitation, delivery_status: "failed" },
    ]);
    render(<CareConnections />);
    await screen.findByText("No connections yet");
    fireEvent.click(screen.getByRole("tab", { name: "Invitations" }));
    expect(screen.getByText("Email failed")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Resend" }));
    await waitFor(() => expect(api.manage).toHaveBeenCalledWith("i", "resend"));
  });
  it("requires an admin reason and submits the selected accounts", async () => {
    context.user = { role: "admin" };
    render(<CareConnections />);
    await screen.findByRole("option", { name: "Alex" });
    fireEvent.change(screen.getByLabelText("Patient"), {
      target: { value: "p" },
    });
    fireEvent.change(screen.getByLabelText("Therapist"), {
      target: { value: "t" },
    });
    expect(
      screen.getByRole("button", { name: "Assign therapist" }),
    ).toBeDisabled();
    fireEvent.change(screen.getByLabelText("Reason"), {
      target: { value: "Clinic intake" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Assign therapist" }));
    await waitFor(() =>
      expect(api.assign).toHaveBeenCalledWith("p", "t", "Clinic intake"),
    );
  });
  it("renders Arabic labels", async () => {
    context.locale = "ar";
    render(<CareConnections />);
    expect(await screen.findByText("لا يوجد معالج مرتبط")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "فريق رعايتي" }),
    ).toBeInTheDocument();
  });
});

import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import AppShell from "./AppShell.jsx";

vi.mock("../../context/AuthContext.jsx", () => ({ useAuth: () => ({ logout: vi.fn() }) }));
const user = { full_name: "Test User", role: "admin" };

describe("workspace navigation accessibility", () => {
  it("shows the reference navigation to visitors and requires login for protected destinations", () => {
    const onNavigate = vi.fn();
    render(<AppShell currentPage="exercises" user={null} onNavigate={onNavigate}><main>Library</main></AppShell>);
    const navigation = screen.getByRole("navigation", { name: "Workspace navigation" });
    for (const name of ["Overview", "Caseload", "Movement reviews", "Exercise library", "Movement check", "Recovery coaching", "Account"]) {
      expect(within(navigation).getByRole("button", { name })).toBeInTheDocument();
    }
    fireEvent.click(within(navigation).getByRole("button", { name: "Caseload" }));
    expect(onNavigate).toHaveBeenCalledWith("login");
  });
  it("keeps mobile labels after collapsing desktop navigation and restores focus", () => {
    const onNavigate = vi.fn();
    render(<AppShell currentPage="exercises" user={user} onNavigate={onNavigate}><main>Library</main></AppShell>);
    fireEvent.click(screen.getByRole("button", { name: "Collapse", exact: true }));
    const trigger = screen.getByRole("button", { name: "Open navigation" });
    trigger.focus();
    fireEvent.click(trigger);
    const dialog = screen.getByRole("dialog", { name: "Open navigation" });
    expect(within(dialog).getByRole("button", { name: "Exercise library" })).toHaveTextContent("Exercise library");
    expect(dialog).toHaveFocus();
    fireEvent.keyDown(dialog, { key: "Tab", shiftKey: true });
    expect(dialog).toContainElement(document.activeElement);
    expect(document.activeElement).not.toBe(dialog);
    fireEvent.keyDown(dialog, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
    expect(document.body.style.overflow).not.toBe("hidden");
  });

  it("provides a skip target and closes mobile navigation after selecting a destination", () => {
    const onNavigate = vi.fn();
    render(<AppShell currentPage="exercises" user={user} onNavigate={onNavigate}><main>Library</main></AppShell>);
    expect(screen.getByRole("link", { name: "Skip to content" })).toHaveAttribute("href", "#workspace-content");
    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Movement check" }));
    expect(onNavigate).toHaveBeenCalledWith("analyze");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});

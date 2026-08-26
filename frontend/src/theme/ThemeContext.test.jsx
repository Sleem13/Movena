import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { THEME_STORAGE_KEY, ThemeProvider, useTheme } from "./ThemeContext.jsx";

let systemDark = false;
let changeListener;

function Probe() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  return <div><span>{theme}:{resolvedTheme}</span><button onClick={() => setTheme("dark")}>dark</button><button onClick={() => setTheme("system")}>system</button></div>;
}

beforeEach(() => {
  systemDark = false;
  changeListener = undefined;
  vi.stubGlobal("matchMedia", vi.fn(() => ({
    matches: systemDark,
    addEventListener: (_event, listener) => { changeListener = listener; },
    removeEventListener: vi.fn(),
  })));
});

afterEach(() => {
  localStorage.removeItem(THEME_STORAGE_KEY);
  delete document.documentElement.dataset.theme;
  document.documentElement.style.colorScheme = "";
  vi.unstubAllGlobals();
});

describe("ThemeProvider", () => {
  it("defaults to the system preference and follows system changes", () => {
    render(<ThemeProvider><Probe /></ThemeProvider>);
    expect(screen.getByText("system:light")).toBeInTheDocument();
    expect(document.documentElement.dataset.theme).toBe("light");
    systemDark = true;
    act(() => changeListener({ matches: true }));
    expect(screen.getByText("system:dark")).toBeInTheDocument();
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("persists an explicit choice", () => {
    render(<ThemeProvider><Probe /></ThemeProvider>);
    fireEvent.click(screen.getByRole("button", { name: "dark" }));
    expect(screen.getByText("dark:dark")).toBeInTheDocument();
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
  });
});

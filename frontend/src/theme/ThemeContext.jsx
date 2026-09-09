import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { BRAND } from "../config/brand.js";

export const THEME_STORAGE_KEY = "movena_theme";
export const THEME_OPTIONS = ["light", "dark", "system"];

const ThemeContext = createContext(null);

function preferredTheme() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function storedTheme() {
  if (typeof localStorage === "undefined") return "system";
  const value = localStorage.getItem(THEME_STORAGE_KEY);
  return THEME_OPTIONS.includes(value) ? value : "system";
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(storedTheme);
  const [systemTheme, setSystemTheme] = useState(preferredTheme);
  const resolvedTheme = theme === "system" ? systemTheme : theme;

  const setTheme = useCallback((nextTheme) => {
    if (!THEME_OPTIONS.includes(nextTheme)) return;
    setThemeState(nextTheme);
    if (typeof localStorage !== "undefined") localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  }, []);

  useEffect(() => {
    const query = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (!query) return undefined;
    const update = (event) => setSystemTheme(event.matches ? "dark" : "light");
    setSystemTheme(query.matches ? "dark" : "light");
    query.addEventListener?.("change", update);
    return () => query.removeEventListener?.("change", update);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme;
    document.documentElement.style.colorScheme = resolvedTheme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", resolvedTheme === "dark" ? BRAND.colors.darkCanvas : BRAND.colors.blue);
  }, [resolvedTheme]);

  const value = useMemo(() => ({ theme, resolvedTheme, setTheme }), [theme, resolvedTheme, setTheme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  return context || { theme: "system", resolvedTheme: preferredTheme(), setTheme: () => {} };
}

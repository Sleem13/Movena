"use client";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import exerciseNames from "../../../../packages/contracts/exercise-names.json";
import messages from "../../../../packages/contracts/messages.json";
type Locale = "en" | "ar";
type Theme = "light" | "dark" | "system";
type Key = keyof typeof messages.en;
const Context = createContext({
  locale: "en" as Locale,
  theme: "system" as Theme,
  setLocale: (_v: Locale) => {},
  setTheme: (_v: Theme) => {},
  t: (key: Key): string => messages.en[key],
  exerciseName: (id: string): string => id.replaceAll("_", " "),
});
export function Preferences({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en");
  const [theme, setTheme] = useState<Theme>("system");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try {
      setLocale(localStorage.getItem("movena_locale") === "ar" ? "ar" : "en");
      const v = localStorage.getItem("movena_theme");
      if (v === "light" || v === "dark") setTheme(v);
    } catch {}
    setReady(true);
  }, []);
  useEffect(() => {
    if (!ready) return;
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "ar" ? "rtl" : "ltr";
    try {
      localStorage.setItem("movena_locale", locale);
    } catch {}
  }, [locale, ready]);
  useEffect(() => {
    if (!ready) return;
    const query = matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      document.documentElement.dataset.theme =
        theme === "system" ? (query.matches ? "dark" : "light") : theme;
    };
    apply();
    query.addEventListener("change", apply);
    try {
      localStorage.setItem("movena_theme", theme);
    } catch {}
    return () => query.removeEventListener("change", apply);
  }, [theme, ready]);
  return (
    <Context.Provider
      value={{
        locale,
        theme,
        setLocale,
        setTheme,
        t: (key) => messages[locale][key],
        exerciseName: (id) =>
          (exerciseNames as Record<string, Record<Locale, string>>)[id]?.[
            locale
          ] ?? id.replaceAll("_", " "),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export const usePreferences = () => useContext(Context);

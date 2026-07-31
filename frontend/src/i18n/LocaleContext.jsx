import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { DEFAULT_LOCALE, LOCALE_STORAGE_KEY, SUPPORTED_LOCALES, translate } from "./messages.js";

const LocaleContext = createContext(null);

function storedLocale() {
  if (typeof localStorage === "undefined") return DEFAULT_LOCALE;
  const value = localStorage.getItem(LOCALE_STORAGE_KEY);
  return SUPPORTED_LOCALES.some(({ code }) => code === value) ? value : DEFAULT_LOCALE;
}

export function LocaleProvider({ children }) {
  const [locale, setLocaleState] = useState(storedLocale);
  const localeDefinition = SUPPORTED_LOCALES.find(({ code }) => code === locale) || SUPPORTED_LOCALES[0];

  const setLocale = useCallback((nextLocale) => {
    if (!SUPPORTED_LOCALES.some(({ code }) => code === nextLocale)) return;
    setLocaleState(nextLocale);
    if (typeof localStorage !== "undefined") localStorage.setItem(LOCALE_STORAGE_KEY, nextLocale);
  }, []);

  useEffect(() => {
    document.documentElement.lang = localeDefinition.code;
    document.documentElement.dir = localeDefinition.direction;
  }, [localeDefinition]);

  const t = useCallback((key, values) => translate(locale, key, values), [locale]);
  const value = useMemo(
    () => ({ locale, direction: localeDefinition.direction, setLocale, t }),
    [locale, localeDefinition.direction, setLocale, t],
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const context = useContext(LocaleContext);
  if (!context) throw new Error("useLocale must be used within LocaleProvider");
  return context;
}

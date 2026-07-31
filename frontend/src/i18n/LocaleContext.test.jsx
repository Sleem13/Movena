import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import LanguageSelector from "./LanguageSelector.jsx";
import { LocaleProvider, useLocale } from "./LocaleContext.jsx";
import { LOCALE_STORAGE_KEY } from "./messages.js";

function Probe() {
  const { direction, t } = useLocale();
  return <div><span>{t("nav.home")}</span><span>{direction}</span><LanguageSelector /></div>;
}

afterEach(() => {
  localStorage.removeItem(LOCALE_STORAGE_KEY);
  document.documentElement.lang = "en";
  document.documentElement.dir = "ltr";
});

describe("LocaleProvider", () => {
  it("switches to Arabic, persists the choice, and updates document direction", () => {
    render(<LocaleProvider><Probe /></LocaleProvider>);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "ar" } });
    expect(screen.getByText("الرئيسية")).toBeInTheDocument();
    expect(screen.getByText("rtl")).toBeInTheDocument();
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("ar");
    expect(document.documentElement.lang).toBe("ar");
    expect(document.documentElement.dir).toBe("rtl");
  });
});

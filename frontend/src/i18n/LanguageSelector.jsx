import { Languages } from "lucide-react";
import { useLocale } from "./LocaleContext.jsx";
import { SUPPORTED_LOCALES } from "./messages.js";

export default function LanguageSelector() {
  const { locale, setLocale, t } = useLocale();
  return <label className="relative inline-flex h-10 shrink-0 items-center gap-1.5 rounded-xl bg-slate-100 px-2 text-slate-600">
    <Languages size={15} aria-hidden="true" />
    <span className="sr-only">{t("language.label")}</span>
    <select
      aria-label={t("language.label")}
      className="max-w-20 cursor-pointer appearance-none bg-transparent pr-3 text-xs font-semibold outline-none"
      value={locale}
      onChange={(event) => setLocale(event.target.value)}
    >
      {SUPPORTED_LOCALES.map(({ code, label }) => <option key={code} value={code}>{label}</option>)}
    </select>
  </label>;
}

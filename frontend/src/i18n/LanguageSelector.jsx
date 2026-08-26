import { Languages } from "lucide-react";
import Select from "../components/common/Select.jsx";
import { useLocale } from "./LocaleContext.jsx";
import { SUPPORTED_LOCALES } from "./messages.js";

export default function LanguageSelector() {
  const { locale, setLocale, t } = useLocale();
  return <Select
    ariaLabel={t("language.label")}
    className="shrink-0"
    buttonClassName="min-h-10 w-auto border-transparent bg-slate-100 px-3 text-xs font-semibold shadow-none hover:border-blue-100 hover:bg-blue-50"
    icon={Languages}
    minMenuWidth={168}
    value={locale}
    options={SUPPORTED_LOCALES.map(({ code, label }) => ({ value: code, label }))}
    onChange={setLocale}
  />;
}

import { Laptop, Moon, Sun } from "lucide-react";
import Select from "../components/common/Select.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { useTheme } from "./ThemeContext.jsx";

const ICONS = { light: Sun, dark: Moon, system: Laptop };

export default function ThemeSelector() {
  const { t } = useLocale();
  const { theme, resolvedTheme, setTheme } = useTheme();
  return <Select
    ariaLabel={t("theme.label")}
    className="shrink-0"
    buttonClassName="h-10 min-h-10 w-10 justify-center border-transparent bg-slate-100 px-0 shadow-none hover:border-blue-100 hover:bg-blue-50 [&>span>span]:hidden [&>svg]:hidden"
    icon={ICONS[theme === "system" ? resolvedTheme : theme]}
    minMenuWidth={176}
    value={theme}
    options={[
      { value: "light", label: t("theme.light") },
      { value: "dark", label: t("theme.dark") },
      { value: "system", label: t("theme.system") },
    ]}
    onChange={setTheme}
  />;
}

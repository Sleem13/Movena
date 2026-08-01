import { BookOpenCheck, HeartHandshake, ShieldCheck } from "lucide-react";
import { Button, Card } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function About({ onStart }) {
  const { t } = useLocale();
  const principles = [
    [ShieldCheck, t("about.safetyTitle"), t("about.safetyText")],
    [BookOpenCheck, t("about.transparentTitle"), t("about.transparentText")],
    [HeartHandshake, t("about.conversationTitle"), t("about.conversationText")],
  ];

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-12">
      <PageHeader eyebrow={t("about.eyebrow")} title={t("about.title")} description={t("about.description")} />
      <div className="grid gap-5 md:grid-cols-3">
        {principles.map(([Icon, title, text]) => (
          <Card key={title} className="p-6">
            <span className="grid h-11 w-11 place-items-center rounded-xl bg-clinical-mint text-clinical-teal">
              <Icon size={21} aria-hidden="true" />
            </span>
            <h2 className="mt-5 text-lg font-bold text-clinical-ink">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
          </Card>
        ))}
      </div>
      <Card className="mt-6 flex flex-col gap-5 bg-gradient-to-r from-blue-50 to-teal-50 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-bold text-clinical-ink">{t("about.readyTitle")}</h2>
          <p className="mt-1 text-sm text-slate-600">{t("about.readyText")}</p>
        </div>
        <Button type="button" onClick={onStart}>{t("about.openAnalyzer")}</Button>
      </Card>
    </main>
  );
}

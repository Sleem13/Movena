import { BrainCircuit, ChartNoAxesCombined, CheckCheck, Database, FileText, ScanSearch } from "lucide-react";
import { Badge, Button, Card } from "../common/UI.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const optionDefinitions = [
  { key: "include_overlay", titleKey: "options.overlayTitle", descriptionKey: "options.overlayDescription", icon: ScanSearch },
  { key: "generate_report", titleKey: "options.reportTitle", descriptionKey: "options.reportDescription", icon: FileText },
  { key: "include_frame_data", titleKey: "options.frameDataTitle", descriptionKey: "options.frameDataDescription", icon: ChartNoAxesCombined },
  { key: "include_ml", titleKey: "options.mlTitle", descriptionKey: "options.mlDescription", icon: BrainCircuit, experimental: true },
  { key: "save_session", titleKey: "options.saveTitle", descriptionKey: "options.saveDescription", icon: Database },
];

export default function AnalysisOptions({ exercise = "bodyweight_squat", value, onChange, disabled }) {
  const { t, exerciseText } = useLocale();
  const allSelected = optionDefinitions.every(({ key }) => Boolean(value[key]));

  function toggleAll() {
    const nextSelected = !allSelected;
    onChange({
      ...value,
      ...Object.fromEntries(optionDefinitions.map(({ key }) => [key, nextSelected])),
    });
  }

  return (
    <Card className="p-5">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-clinical-ink">{t("options.title")}</h2>
          <p className="mt-1 text-xs leading-5 text-slate-500">{t("options.description")}</p>
        </div>
        <Button
          type="button"
          variant="secondary"
          className="min-h-9 shrink-0 px-3 text-xs"
          aria-pressed={allSelected}
          disabled={disabled}
          onClick={toggleAll}
        >
          <CheckCheck size={16} aria-hidden="true" />
          {t(allSelected ? "options.clearAll" : "options.selectAll")}
        </Button>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {optionDefinitions.map(({ key, titleKey, descriptionKey, icon: Icon, experimental }) => {
          const title = t(titleKey);
          return (
            <label
              key={key}
              className={`flex gap-3 rounded-xl border p-3.5 transition ${
                "cursor-pointer"
              } ${value[key] ? "border-blue-200 bg-blue-50/70" : "border-slate-200 hover:border-slate-300"}`}
            >
              <input
                aria-label={title}
                type="checkbox"
                className="mt-1 h-4 w-4 accent-blue-600"
                checked={value[key]}
                disabled={disabled}
                onChange={(event) => onChange({ ...value, [key]: event.target.checked })}
              />
              <Icon className="mt-0.5 shrink-0 text-clinical-blue" size={18} aria-hidden="true" />
              <span>
                <span className="flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-800">
                  {title}
                  {experimental && <Badge tone="amber">{t("status.experimental")}</Badge>}
                </span>
                <span className="mt-1 block text-xs leading-5 text-slate-500">
                  {t(descriptionKey, { exercise: exerciseText(exercise).short })}
                </span>
              </span>
            </label>
          );
        })}
      </div>
    </Card>
  );
}

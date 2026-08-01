import { BrainCircuit, ChartNoAxesCombined, Database, FileText, ScanSearch } from "lucide-react";
import { Badge, Card } from "../common/UI.jsx";
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
  return (
    <Card className="p-5">
      <div className="mb-4">
        <h2 className="text-base font-bold text-clinical-ink">{t("options.title")}</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">{t("options.description")}</p>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {optionDefinitions.map(({ key, titleKey, descriptionKey, icon: Icon, experimental }) => {
          const unavailable = exercise !== "bodyweight_squat" && key === "include_ml";
          const title = t(titleKey);
          return (
            <label
              key={key}
              className={`flex gap-3 rounded-xl border p-3.5 transition ${
                unavailable ? "cursor-not-allowed bg-slate-50 opacity-70" : "cursor-pointer"
              } ${value[key] ? "border-blue-200 bg-blue-50/70" : "border-slate-200 hover:border-slate-300"}`}
            >
              <input
                aria-label={title}
                type="checkbox"
                className="mt-1 h-4 w-4 accent-blue-600"
                checked={unavailable ? false : value[key]}
                disabled={disabled || unavailable}
                onChange={(event) => onChange({ ...value, [key]: event.target.checked })}
              />
              <Icon className="mt-0.5 shrink-0 text-clinical-blue" size={18} aria-hidden="true" />
              <span>
                <span className="flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-800">
                  {title}
                  {experimental && <Badge tone="amber">{unavailable ? t("status.notAvailable") : t("status.experimental")}</Badge>}
                </span>
                <span className="mt-1 block text-xs leading-5 text-slate-500">
                  {unavailable
                    ? t("options.mlUnavailable", { exercise: exerciseText(exercise).short })
                    : t(descriptionKey)}
                </span>
              </span>
            </label>
          );
        })}
      </div>
    </Card>
  );
}

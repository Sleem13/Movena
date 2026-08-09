import { Camera, CheckCircle2, Lightbulb, ScanLine } from "lucide-react";
import { Card } from "../common/UI.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const tipsByExercise = {
  bodyweight_squat: [
    ["camera.tip.side", "camera.tip.sideSquat"],
    ["camera.tip.front", "camera.tip.frontSquat"],
    ["camera.tip.fullBody", "camera.tip.fullBodyText"],
    ["camera.tip.stableBright", "camera.tip.stableBrightText"],
    ["camera.tip.reps", "camera.tip.repsText"],
    ["camera.tip.clearJoint", "camera.tip.clearJointText"],
  ],
  sit_to_stand: [
    ["camera.tip.chairView", "camera.tip.chairViewText"],
    ["camera.tip.bodyChair", "camera.tip.bodyChairText"],
    ["camera.tip.stableChair", "camera.tip.stableChairText"],
    ["camera.tip.stableBright", "camera.tip.stableBrightText"],
    ["camera.tip.reps", "camera.tip.chairRepsText"],
    ["camera.tip.stop", "camera.tip.stopText"],
  ],
  knee_extension: [
    ["camera.tip.side", "camera.tip.kneeViewText"],
    ["camera.tip.seated", "camera.tip.seatedText"],
    ["camera.tip.secureChair", "camera.tip.stableChairText"],
    ["camera.tip.stableBright", "camera.tip.kneeStableText"],
    ["camera.tip.reps", "camera.tip.kneeRepsText"],
    ["camera.tip.stop", "camera.tip.stopText"],
  ],
  shoulder_abduction: [
    ["camera.tip.front", "camera.tip.shoulderViewText"],
    ["camera.tip.upperBody", "camera.tip.upperBodyText"],
    ["camera.tip.stablePosture", "camera.tip.stableChairText"],
    ["camera.tip.stableBright", "camera.tip.armStableText"],
    ["camera.tip.reps", "camera.tip.shoulderRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
  hip_abduction: [
    ["camera.tip.front", "camera.tip.hipViewText"],
    ["camera.tip.lowerBody", "camera.tip.lowerBodyText"],
    ["camera.tip.stableSupport", "camera.tip.stableChairText"],
    ["camera.tip.stableBright", "camera.tip.hipStableText"],
    ["camera.tip.reps", "camera.tip.hipRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
  push_up: [
    ["camera.tip.side", "camera.tip.pushUpSideText"],
    ["camera.tip.fullBody", "camera.tip.fullBodyText"],
    ["camera.tip.stableSupport", "camera.tip.pushUpSupportText"],
    ["camera.tip.stableBright", "camera.tip.stableBrightText"],
    ["camera.tip.reps", "camera.tip.pushUpRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
  shoulder_press: [
    ["camera.tip.front", "camera.tip.pressViewText"],
    ["camera.tip.upperBody", "camera.tip.upperBodyText"],
    ["camera.tip.stablePosture", "camera.tip.pressPostureText"],
    ["camera.tip.stableBright", "camera.tip.armStableText"],
    ["camera.tip.reps", "camera.tip.pressRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
  bicep_curl: [
    ["camera.tip.front", "camera.tip.curlViewText"],
    ["camera.tip.upperBody", "camera.tip.upperBodyText"],
    ["camera.tip.stablePosture", "camera.tip.curlPostureText"],
    ["camera.tip.stableBright", "camera.tip.armStableText"],
    ["camera.tip.reps", "camera.tip.curlRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
};

export default function CameraGuide({ exercise = "bodyweight_squat", metadata }) {
  const { t } = useLocale();
  const tips = tipsByExercise[exercise] || tipsByExercise.bodyweight_squat;
  const landmarks = metadata?.required_landmarks?.join(", ");

  return (
    <Card className="overflow-hidden">
      <div className="bg-gradient-to-br from-clinical-navy to-clinical-blue p-6 text-white">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-white/15">
            <Camera size={22} aria-hidden="true" />
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-blue-100">{t("camera.recordingTips")}</p>
            <h2 className="mt-1 text-xl font-bold">{t("camera.title")}</h2>
          </div>
        </div>
        {metadata && (
          <p className="mt-4 text-sm text-blue-50">
            <strong>{metadata.recommended_camera_view}.</strong> {t("camera.visible", { landmarks })}
          </p>
        )}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <div className="rounded-xl bg-white/10 p-3">
            <ScanLine size={18} aria-hidden="true" />
            <p className="mt-2 text-xs leading-5 text-blue-50">{t("camera.frame")}</p>
          </div>
          <div className="rounded-xl bg-white/10 p-3">
            <Lightbulb size={18} aria-hidden="true" />
            <p className="mt-2 text-xs leading-5 text-blue-50">{t("camera.lighting")}</p>
          </div>
        </div>
      </div>
      <ul aria-label={t("camera.checklist")} className="grid gap-1 p-5">
        {tips.map(([titleKey, textKey]) => (
          <li key={titleKey + textKey} className="flex gap-3 rounded-xl px-2 py-2.5">
            <CheckCircle2 className="mt-0.5 shrink-0 text-clinical-teal" size={17} aria-hidden="true" />
            <div>
              <p className="text-sm font-semibold text-slate-800">{t(titleKey)}</p>
              <p className="mt-0.5 text-xs leading-5 text-slate-500">{t(textKey)}</p>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}

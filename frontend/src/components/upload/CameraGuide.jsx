import { Camera, CheckCircle2, ChevronDown, Lightbulb, ScanLine } from "lucide-react";
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
  shoulder_flexion: [
    ["camera.tip.front", "camera.tip.flexionViewText"],
    ["camera.tip.upperBody", "camera.tip.upperBodyText"],
    ["camera.tip.stablePosture", "camera.tip.flexionPostureText"],
    ["camera.tip.stableBright", "camera.tip.armStableText"],
    ["camera.tip.reps", "camera.tip.flexionRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
  walking_gait_screen: [
    ["camera.tip.side", "camera.tip.gaitSideText"],
    ["camera.tip.lowerBody", "camera.tip.gaitLowerBodyText"],
    ["camera.tip.clearPath", "camera.tip.clearPathText"],
    ["camera.tip.stableBright", "camera.tip.gaitStableText"],
    ["camera.tip.steps", "camera.tip.gaitStepsText"],
    ["camera.tip.stop", "camera.tip.gaitStopText"],
  ],
  balance: [
    ["camera.tip.front", "camera.tip.balanceViewText"],
    ["camera.tip.fullBody", "camera.tip.balanceFullBodyText"],
    ["camera.tip.stableSupport", "camera.tip.balanceSupportText"],
    ["camera.tip.stableBright", "camera.tip.balanceStableText"],
    ["camera.tip.hold", "camera.tip.balanceHoldText"],
    ["camera.tip.stop", "camera.tip.balanceStopText"],
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
  hammer_curl: [
    ["camera.tip.front", "camera.tip.curlViewText"],
    ["camera.tip.upperBody", "camera.tip.upperBodyText"],
    ["camera.tip.stablePosture", "camera.tip.curlPostureText"],
    ["camera.tip.stableBright", "camera.tip.hammerStableText"],
    ["camera.tip.reps", "camera.tip.hammerRepsText"],
    ["camera.tip.stop", "camera.tip.shoulderStopText"],
  ],
};

export default function CameraGuide({ exercise = "bodyweight_squat", metadata, compact = false }) {
  const { t } = useLocale();
  const tips = [
    ["camera.tip.singleSubject", "camera.tip.singleSubjectText"],
    ...(tipsByExercise[exercise] || tipsByExercise.bodyweight_squat),
  ];
  const landmarks = metadata?.required_landmarks?.join(", ");

  const content = <>
      <div className="border-b border-clinical-line p-5 text-clinical-ink">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-lg bg-clinical-mint text-clinical-teal">
            <Camera size={22} aria-hidden="true" />
          </span>
          <div>
            <h2 className="text-lg font-bold">{t("camera.title")}</h2>
          </div>
        </div>
        {metadata && (
          <p className="mt-4 text-sm leading-6 text-slate-600">
            <strong>{metadata.recommended_camera_view}.</strong> {t("camera.visible", { landmarks })}
          </p>
        )}
        <div className="mt-5 grid grid-cols-2 gap-4 text-clinical-teal">
          <div>
            <ScanLine size={18} aria-hidden="true" />
            <p className="mt-2 text-xs leading-5 text-slate-600">{t("camera.frame")}</p>
          </div>
          <div>
            <Lightbulb size={18} aria-hidden="true" />
            <p className="mt-2 text-xs leading-5 text-slate-600">{t("camera.lighting")}</p>
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
  </>;

  if (compact) return <details className="group overflow-hidden rounded-lg border border-slate-200 bg-white">
    <summary className="flex min-h-16 cursor-pointer list-none items-center gap-3 px-4 font-bold text-clinical-ink marker:hidden">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-clinical-blue"><Camera size={20} aria-hidden="true" /></span>
      <span className="flex-1">{t("camera.title")}</span>
      <ChevronDown size={19} className="text-slate-400 transition group-open:rotate-180" aria-hidden="true" />
    </summary>
    <div className="border-t border-slate-200">{content}</div>
  </details>;

  return <Card className="overflow-hidden">{content}</Card>;
}

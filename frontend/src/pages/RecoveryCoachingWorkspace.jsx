import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bell,
  CalendarCheck,
  CheckCheck,
  ClipboardCheck,
  Clock3,
  HeartHandshake,
  LineChart,
  LoaderCircle,
  Plus,
  ShieldAlert,
  Sparkles,
  Target,
} from "lucide-react";

import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import {
  acknowledgeRecoveryCoachingCheckIn,
  createRecoveryCoachingActionPlan,
  createRecoveryCoachingCheckIn,
  createRecoveryCoachingGoal,
  getRecoveryCoachingDashboard,
  getRecoveryCoachingTemplates,
  listPatientProfiles,
  updateRecoveryCoachingGoal,
  updateRecoveryCoachingReminderPreference,
} from "../services/api.js";
import { getApiErrorMessage } from "../utils/requestErrors.js";

const COPY = {
  en: {
    eyebrow: "Recovery coaching",
    title: "Recovery & Lifestyle Coaching",
    description:
      "Turn patient-chosen goals into small, measurable actions aligned with the rehabilitation plan.",
    partnership: "Accountability partnership.",
    boundary:
      "Coaching supports self-directed behavior change; it does not diagnose, prescribe, provide psychotherapy, or replace clinical care.",
    patient: "Patient",
    selectPatient: "Select patient",
    activeGoals: "Active goals",
    completedGoals: "Completed goals",
    checkIns: "30-day check-ins",
    averageConfidence: "Average confidence",
    followUp: "Follow-up needed",
    unacknowledged: "Unacknowledged",
    overview: "Overview",
    dailyCheckIn: "Daily check-in",
    goals: "Goals",
    trends: "Trends",
    reminders: "Reminders",
    actionPlan: "Action plan",
    currentGoals: "Current goals",
    noGoals: "No coaching goals yet.",
    activeSteps: "Active action steps",
    noPlan: "No active action plan.",
    safetyBoundary: "Safety boundary",
    safetyText:
      "New or worsening symptoms require clinical review. Immediate concerns pause coaching and use the approved urgent or emergency pathway.",
    noRealtime:
      "Check-ins are not monitored in real time and do not guarantee a response within a specific period.",
    createGoal: "Create a SMART recovery goal",
    goalHelp:
      "Goals must be self-directed, measurable, and aligned with the clinical plan.",
    template: "Therapist-approved template",
    customGoal: "Start without a template",
    templateScope:
      "Templates support behavior goals only and never prescribe treatment dosage.",
    domain: "Domain",
    goalTitle: "Goal title",
    specificAction: "Specific action",
    measurement: "How progress is measured",
    targetDate: "Target date",
    why: "Why this matters",
    confidence: "Confidence",
    patientAgreedGoal: "The patient chose or explicitly agreed to this goal.",
    scopeGoal:
      "I understand coaching does not replace clinical or mental-health care.",
    saveGoal: "Save goal",
    progress: "Progress",
    saveProgress: "Save progress",
    markCompleted: "Mark completed",
    measure: "Measure",
    checkInTitle: "Daily recovery check-in",
    checkInHelp:
      "This is a non-diagnostic reflection used to adjust agreed action steps.",
    date: "Date",
    energy: "Energy",
    sleep: "Sleep quality",
    stress: "Stress",
    activityMinutes: "Activity minutes",
    mainBarrier: "Main barrier",
    barrierNote: "Barrier note (optional)",
    symptomsChanged:
      "I have new or worsening symptoms that need clinical review.",
    urgentConcern: "I have an immediate safety or health concern.",
    checkInScope:
      "I understand this check-in is not emergency or diagnostic care.",
    saveCheckIn: "Save check-in",
    trendTitle: "Recovery reflection trends",
    trendHelp:
      "Informal 1–5 reflections are shown separately from validated clinical outcome measures.",
    noTrend: "Record at least one check-in to see trends.",
    activityTrend: "Activity minutes",
    reminderTitle: "Check-in reminder preferences",
    reminderHelp:
      "Opt in to routine reminders. Delivery timing is approximate and is not clinical monitoring.",
    enableReminder: "Enable recovery check-in reminders",
    reminderTime: "Local reminder time",
    cadence: "Cadence",
    daily: "Daily",
    weekdays: "Weekdays",
    missedDays: "Routine therapist follow-up after",
    days: "days without a check-in",
    reminderAgreement:
      "The patient explicitly agreed to these reminder preferences.",
    saveReminder: "Save reminder preferences",
    followUpQueue: "Clinical follow-up queue",
    followUpHelp:
      "Acknowledge review without implying real-time monitoring or guaranteed response times.",
    noFollowUp: "No unacknowledged coaching follow-up.",
    reviewed: "Reviewed",
    pending: "Pending review",
    disposition: "Clinical disposition",
    contacted: "Contacted patient",
    scheduled: "Scheduled clinical review",
    escalated: "Escalated through urgent pathway",
    noAction: "Reviewed — no additional action",
    reviewNote: "Review note (optional)",
    attestation:
      "I attest that I reviewed this check-in under the organization’s clinical workflow.",
    acknowledge: "Acknowledge follow-up",
    actionPlanTitle: "Therapist-reviewed action plan",
    agreedStep: "Agreed action step",
    frequency: "Frequency",
    support: "Support needed",
    reviewDate: "Review date",
    planAgreement: "The patient explicitly agreed to this action plan.",
    savePlan: "Save action plan",
    needGoal:
      "Create a patient-agreed goal before adding a weekly action plan.",
    unavailable: "Select an assigned patient to open coaching records.",
    profileRequired: "A patient profile is required to use recovery coaching.",
    updateError: "Unable to update recovery coaching right now.",
    nonDiagnostic: "Non-diagnostic · 1–5",
  },
  ar: {
    eyebrow: "تدريب التعافي",
    title: "تدريب التعافي ونمط الحياة",
    description:
      "حوّل الأهداف التي يختارها المريض إلى خطوات صغيرة قابلة للقياس ومتوافقة مع خطة التأهيل.",
    partnership: "شراكة للمساءلة والدعم.",
    boundary:
      "يدعم التدريب تغيير السلوك الذي يقوده المريض، ولا يشخّص أو يصف علاجًا أو يقدم علاجًا نفسيًا أو يحل محل الرعاية السريرية.",
    patient: "المريض",
    selectPatient: "اختر المريض",
    activeGoals: "الأهداف النشطة",
    completedGoals: "الأهداف المكتملة",
    checkIns: "متابعات 30 يومًا",
    averageConfidence: "متوسط الثقة",
    followUp: "تحتاج متابعة",
    unacknowledged: "غير مُراجعة",
    overview: "نظرة عامة",
    dailyCheckIn: "المتابعة اليومية",
    goals: "الأهداف",
    trends: "المؤشرات",
    reminders: "التذكيرات",
    actionPlan: "خطة العمل",
    currentGoals: "الأهداف الحالية",
    noGoals: "لا توجد أهداف تدريبية بعد.",
    activeSteps: "خطوات العمل النشطة",
    noPlan: "لا توجد خطة عمل نشطة.",
    safetyBoundary: "حدود السلامة",
    safetyText:
      "تتطلب الأعراض الجديدة أو المتفاقمة مراجعة سريرية. توقف المخاوف الفورية التدريب وتستخدم مسار الطوارئ المعتمد.",
    noRealtime:
      "لا تتم مراقبة المتابعات لحظيًا ولا تضمن استجابة خلال مدة محددة.",
    createGoal: "إنشاء هدف تعافٍ ذكي",
    goalHelp:
      "يجب أن يكون الهدف محددًا وقابلًا للقياس ومتوافقًا مع الخطة السريرية.",
    template: "نموذج معتمد من المعالج",
    customGoal: "البدء دون نموذج",
    templateScope: "تدعم النماذج أهداف السلوك فقط ولا تصف جرعة علاجية.",
    domain: "المجال",
    goalTitle: "عنوان الهدف",
    specificAction: "الإجراء المحدد",
    measurement: "طريقة قياس التقدم",
    targetDate: "التاريخ المستهدف",
    why: "أهمية هذا الهدف",
    confidence: "الثقة",
    patientAgreedGoal: "اختار المريض هذا الهدف أو وافق عليه صراحةً.",
    scopeGoal: "أفهم أن التدريب لا يحل محل الرعاية السريرية أو النفسية.",
    saveGoal: "حفظ الهدف",
    progress: "التقدم",
    saveProgress: "حفظ التقدم",
    markCompleted: "تحديد كمكتمل",
    measure: "القياس",
    checkInTitle: "متابعة التعافي اليومية",
    checkInHelp: "هذا تأمل غير تشخيصي يُستخدم لمراجعة الخطوات المتفق عليها.",
    date: "التاريخ",
    energy: "الطاقة",
    sleep: "جودة النوم",
    stress: "التوتر",
    activityMinutes: "دقائق النشاط",
    mainBarrier: "العائق الرئيسي",
    barrierNote: "ملاحظة عن العائق (اختياري)",
    symptomsChanged: "لدي أعراض جديدة أو متفاقمة تحتاج مراجعة سريرية.",
    urgentConcern: "لدي قلق صحي أو متعلق بالسلامة يحتاج تدخلًا فوريًا.",
    checkInScope: "أفهم أن هذه المتابعة ليست رعاية طارئة أو تشخيصية.",
    saveCheckIn: "حفظ المتابعة",
    trendTitle: "مؤشرات تأملات التعافي",
    trendHelp:
      "تُعرض التقييمات غير الرسمية من 1 إلى 5 منفصلة عن مقاييس النتائج السريرية المعتمدة.",
    noTrend: "سجّل متابعة واحدة على الأقل لعرض المؤشرات.",
    activityTrend: "دقائق النشاط",
    reminderTitle: "تفضيلات تذكير المتابعة",
    reminderHelp:
      "اشترك في التذكيرات الروتينية. توقيت الإرسال تقريبي ولا يمثل مراقبة سريرية.",
    enableReminder: "تفعيل تذكيرات متابعة التعافي",
    reminderTime: "وقت التذكير المحلي",
    cadence: "التكرار",
    daily: "يوميًا",
    weekdays: "أيام العمل",
    missedDays: "متابعة روتينية من المعالج بعد",
    days: "أيام دون متابعة",
    reminderAgreement: "وافق المريض صراحةً على تفضيلات التذكير هذه.",
    saveReminder: "حفظ تفضيلات التذكير",
    followUpQueue: "قائمة المتابعة السريرية",
    followUpHelp:
      "وثّق المراجعة دون الإيحاء بالمراقبة اللحظية أو ضمان زمن استجابة.",
    noFollowUp: "لا توجد متابعة تدريبية غير مُراجعة.",
    reviewed: "تمت المراجعة",
    pending: "بانتظار المراجعة",
    disposition: "نتيجة المراجعة السريرية",
    contacted: "تم التواصل مع المريض",
    scheduled: "تم تحديد مراجعة سريرية",
    escalated: "تم التصعيد عبر مسار الطوارئ",
    noAction: "تمت المراجعة — لا إجراء إضافي",
    reviewNote: "ملاحظة المراجعة (اختياري)",
    attestation: "أقر بأنني راجعت هذه المتابعة وفق مسار العمل السريري للمؤسسة.",
    acknowledge: "توثيق المتابعة",
    actionPlanTitle: "خطة عمل راجعها المعالج",
    agreedStep: "خطوة العمل المتفق عليها",
    frequency: "التكرار",
    support: "الدعم المطلوب",
    reviewDate: "تاريخ المراجعة",
    planAgreement: "وافق المريض صراحةً على خطة العمل هذه.",
    savePlan: "حفظ خطة العمل",
    needGoal: "أنشئ هدفًا وافق عليه المريض قبل إضافة خطة عمل أسبوعية.",
    unavailable: "اختر مريضًا مُسندًا لفتح سجلات التدريب.",
    profileRequired: "يلزم ملف مريض لاستخدام تدريب التعافي.",
    updateError: "تعذر تحديث تدريب التعافي الآن.",
    nonDiagnostic: "غير تشخيصي · 1–5",
  },
};

const DOMAINS = [
  "activity",
  "mobility_routine",
  "sleep_routine",
  "participation",
  "adherence",
  "stress_management",
  "social_support",
];
const DOMAIN_LABELS = {
  en: {
    activity: "Daily activity",
    mobility_routine: "Mobility routine",
    sleep_routine: "Sleep routine",
    participation: "Life participation",
    adherence: "Plan adherence",
    stress_management: "Stress-management routine",
    social_support: "Social support",
  },
  ar: {
    activity: "النشاط اليومي",
    mobility_routine: "روتين الحركة",
    sleep_routine: "روتين النوم",
    participation: "المشاركة في الحياة",
    adherence: "الالتزام بالخطة",
    stress_management: "روتين إدارة التوتر",
    social_support: "الدعم الاجتماعي",
  },
};
const BARRIERS = [
  "none",
  "time",
  "symptoms",
  "fatigue",
  "confidence",
  "environment",
  "support",
  "access",
  "other",
];
const BARRIER_LABELS = {
  en: {
    none: "No major barrier",
    time: "Time",
    symptoms: "Symptoms",
    fatigue: "Fatigue",
    confidence: "Confidence",
    environment: "Environment",
    support: "Support",
    access: "Access",
    other: "Other",
  },
  ar: {
    none: "لا يوجد عائق رئيسي",
    time: "الوقت",
    symptoms: "الأعراض",
    fatigue: "الإجهاد",
    confidence: "الثقة",
    environment: "البيئة",
    support: "الدعم",
    access: "الوصول",
    other: "أخرى",
  },
};

const today = () => new Date().toISOString().slice(0, 10);
const futureDate = (days) => {
  const value = new Date();
  value.setDate(value.getDate() + days);
  return value.toISOString().slice(0, 10);
};

function Metric({ label, value, note }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-2xl font-bold text-[#071b4a]">{value}</p>
      {note ? <p className="mt-1 text-xs text-slate-500">{note}</p> : null}
    </div>
  );
}

function Empty({ children }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
      {children}
    </div>
  );
}

function GoalCard({ goal, patientId, onRefresh, c }) {
  const [progress, setProgress] = useState(goal.progress_percent);
  const [busy, setBusy] = useState(false);
  async function save(
    status = goal.status === "proposed" ? "active" : goal.status,
  ) {
    setBusy(true);
    try {
      await updateRecoveryCoachingGoal(
        goal.goal_id,
        { progress_percent: Number(progress), status },
        patientId,
      );
      await onRefresh();
    } finally {
      setBusy(false);
    }
  }
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-teal-700">
            {goal.domain.replaceAll("_", " ")}
          </p>
          <h3 className="mt-1 font-bold text-[#071b4a]">{goal.title}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {goal.specific_action}
          </p>
        </div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold capitalize text-blue-700">
          {goal.status}
        </span>
      </div>
      <dl className="mt-4 grid gap-3 text-xs sm:grid-cols-2">
        <div>
          <dt className="font-bold text-slate-500">{c.measure}</dt>
          <dd className="mt-1 text-slate-700">{goal.measurement}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-500">{c.targetDate}</dt>
          <dd className="mt-1 text-slate-700">{goal.target_date}</dd>
        </div>
      </dl>
      <label className="mt-4 block text-xs font-bold text-slate-600">
        {c.progress} · {progress}%
        <input
          aria-label={`${c.progress}: ${goal.title}`}
          type="range"
          min="0"
          max="100"
          step="5"
          value={progress}
          onChange={(event) => setProgress(event.target.value)}
          className="mt-2 w-full accent-blue-600"
        />
      </label>
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          disabled={busy}
          onClick={() => save()}
          className="min-h-10 rounded-xl bg-blue-600 px-4 text-xs font-bold text-white disabled:opacity-50"
        >
          {c.saveProgress}
        </button>
        {goal.status !== "completed" ? (
          <button
            disabled={busy}
            onClick={() => save("completed")}
            className="min-h-10 rounded-xl border border-emerald-200 px-4 text-xs font-bold text-emerald-700 disabled:opacity-50"
          >
            {c.markCompleted}
          </button>
        ) : null}
      </div>
    </article>
  );
}

function GoalForm({
  patientId,
  onSaved,
  templates,
  canApplyTemplate,
  locale,
  c,
}) {
  const [form, setForm] = useState({
    domain: "activity",
    title: "",
    specific_action: "",
    measurement: "",
    why_important: "",
    target_date: futureDate(42),
    confidence: 3,
    patient_agreed: false,
    scope_acknowledged: false,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const update = (key, value) =>
    setForm((current) => ({ ...current, [key]: value }));
  function applyTemplate(templateId) {
    const template = templates.find((item) => item.template_id === templateId);
    if (!template) return;
    setForm((current) => ({
      ...current,
      domain: template.domain,
      title: template.title,
      specific_action: template.specific_action,
      measurement: template.measurement,
      why_important: template.why_important,
      patient_agreed: false,
    }));
  }
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await createRecoveryCoachingGoal(form, patientId);
      setForm((current) => ({
        ...current,
        title: "",
        specific_action: "",
        measurement: "",
        why_important: "",
        patient_agreed: false,
        scope_acknowledged: false,
      }));
      await onSaved();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, c.updateError));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <h2 className="flex items-center gap-2 font-bold text-[#071b4a]">
        <Target size={19} className="text-blue-600" />
        {c.createGoal}
      </h2>
      <p className="mt-1 text-xs leading-5 text-slate-500">{c.goalHelp}</p>
      {canApplyTemplate ? (
        <label className="mt-4 block text-xs font-bold text-slate-600">
          {c.template}
          <select
            defaultValue=""
            onChange={(event) => applyTemplate(event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
          >
            <option value="">{c.customGoal}</option>
            {templates.map((template) => (
              <option key={template.template_id} value={template.template_id}>
                {template.pathway} — {template.title}
              </option>
            ))}
          </select>
          <span className="mt-1 block font-normal text-slate-500">
            {c.templateScope}
          </span>
        </label>
      ) : null}
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <label className="text-xs font-bold text-slate-600">
          {c.domain}
          <select
            value={form.domain}
            onChange={(event) => update("domain", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
          >
            {DOMAINS.map((value) => (
              <option key={value} value={value}>
                {DOMAIN_LABELS[locale][value]}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.goalTitle}
          <input
            required
            minLength="3"
            maxLength="120"
            value={form.title}
            onChange={(event) => update("title", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600 sm:col-span-2">
          {c.specificAction}
          <textarea
            required
            minLength="5"
            maxLength="600"
            value={form.specific_action}
            onChange={(event) => update("specific_action", event.target.value)}
            className="mt-1 min-h-20 w-full rounded-xl border border-slate-300 p-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.measurement}
          <input
            required
            value={form.measurement}
            onChange={(event) => update("measurement", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.targetDate}
          <input
            required
            type="date"
            min={today()}
            value={form.target_date}
            onChange={(event) => update("target_date", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600 sm:col-span-2">
          {c.why}
          <textarea
            required
            value={form.why_important}
            onChange={(event) => update("why_important", event.target.value)}
            className="mt-1 min-h-20 w-full rounded-xl border border-slate-300 p-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600 sm:col-span-2">
          {c.confidence} · {form.confidence}/5
          <input
            type="range"
            min="1"
            max="5"
            value={form.confidence}
            onChange={(event) =>
              update("confidence", Number(event.target.value))
            }
            className="mt-2 w-full accent-blue-600"
          />
        </label>
      </div>
      <div className="mt-4 space-y-2">
        <label className="flex gap-2 text-xs text-slate-700">
          <input
            type="checkbox"
            checked={form.patient_agreed}
            onChange={(event) => update("patient_agreed", event.target.checked)}
          />
          {c.patientAgreedGoal}
        </label>
        <label className="flex gap-2 text-xs text-slate-700">
          <input
            type="checkbox"
            checked={form.scope_acknowledged}
            onChange={(event) =>
              update("scope_acknowledged", event.target.checked)
            }
          />
          {c.scopeGoal}
        </label>
      </div>
      {error ? (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      ) : null}
      <button
        disabled={busy || !form.patient_agreed || !form.scope_acknowledged}
        className="mt-4 inline-flex min-h-11 items-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white disabled:opacity-50"
      >
        {busy ? (
          <LoaderCircle className="animate-spin" size={17} />
        ) : (
          <Plus size={17} />
        )}
        {c.saveGoal}
      </button>
    </form>
  );
}

function CheckInForm({ patientId, onSaved, locale, c }) {
  const [form, setForm] = useState({
    check_in_date: today(),
    energy: 3,
    sleep_quality: 3,
    stress: 3,
    recovery_confidence: 3,
    activity_minutes: 0,
    barrier_category: "none",
    barrier_note: "",
    symptoms_changed: false,
    urgent_concern: false,
    scope_acknowledged: false,
  });
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const update = (key, value) =>
    setForm((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const next = await createRecoveryCoachingCheckIn(
        { ...form, barrier_note: form.barrier_note || null },
        patientId,
      );
      setResult(next);
      await onSaved();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, c.updateError));
    } finally {
      setBusy(false);
    }
  }
  const ratings = [
    ["energy", c.energy],
    ["sleep_quality", c.sleep],
    ["stress", c.stress],
    ["recovery_confidence", c.confidence],
  ];
  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <h2 className="flex items-center gap-2 font-bold text-[#071b4a]">
        <CalendarCheck size={19} className="text-teal-600" />
        {c.checkInTitle}
      </h2>
      <p className="mt-1 text-xs leading-5 text-slate-500">{c.checkInHelp}</p>
      <label className="mt-4 block text-xs font-bold text-slate-600">
        {c.date}
        <input
          type="date"
          max={today()}
          value={form.check_in_date}
          onChange={(event) => update("check_in_date", event.target.value)}
          className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
        />
      </label>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {ratings.map(([key, label]) => (
          <label
            key={key}
            className="rounded-xl border border-slate-200 p-3 text-xs font-bold text-slate-600"
          >
            {label} · {form[key]}/5
            <input
              aria-label={label}
              type="range"
              min="1"
              max="5"
              value={form[key]}
              onChange={(event) => update(key, Number(event.target.value))}
              className="mt-2 w-full accent-teal-600"
            />
          </label>
        ))}
      </div>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <label className="text-xs font-bold text-slate-600">
          {c.activityMinutes}
          <input
            type="number"
            min="0"
            max="1440"
            value={form.activity_minutes}
            onChange={(event) =>
              update("activity_minutes", Number(event.target.value))
            }
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.mainBarrier}
          <select
            value={form.barrier_category}
            onChange={(event) => update("barrier_category", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
          >
            {BARRIERS.map((value) => (
              <option key={value} value={value}>
                {BARRIER_LABELS[locale][value]}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="mt-3 block text-xs font-bold text-slate-600">
        {c.barrierNote}
        <textarea
          maxLength="600"
          value={form.barrier_note}
          onChange={(event) => update("barrier_note", event.target.value)}
          className="mt-1 min-h-20 w-full rounded-xl border border-slate-300 p-3 font-normal"
        />
      </label>
      <div className="mt-4 space-y-2">
        <label className="flex gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs font-semibold text-amber-900">
          <input
            type="checkbox"
            checked={form.symptoms_changed}
            onChange={(event) =>
              update("symptoms_changed", event.target.checked)
            }
          />
          {c.symptomsChanged}
        </label>
        <label className="flex gap-2 rounded-xl border border-red-200 bg-red-50 p-3 text-xs font-bold text-red-800">
          <input
            type="checkbox"
            checked={form.urgent_concern}
            onChange={(event) => update("urgent_concern", event.target.checked)}
          />
          {c.urgentConcern}
        </label>
        <label className="flex gap-2 text-xs text-slate-700">
          <input
            type="checkbox"
            checked={form.scope_acknowledged}
            onChange={(event) =>
              update("scope_acknowledged", event.target.checked)
            }
          />
          {c.checkInScope}
        </label>
      </div>
      {error ? (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      ) : null}
      {result ? (
        <div
          role="status"
          className={`mt-4 rounded-xl border p-4 ${result.coaching_state === "urgent_escalation" ? "border-red-200 bg-red-50 text-red-900" : result.coaching_state === "ready" ? "border-emerald-200 bg-emerald-50 text-emerald-900" : "border-amber-200 bg-amber-50 text-amber-900"}`}
        >
          <p className="text-xs font-bold uppercase tracking-wide">
            {result.coaching_state.replaceAll("_", " ")}
          </p>
          <p className="mt-1 text-sm leading-6">{result.supportive_prompt}</p>
        </div>
      ) : null}
      <button
        disabled={busy || !form.scope_acknowledged}
        className={`mt-4 inline-flex min-h-11 items-center gap-2 rounded-xl px-4 text-sm font-bold text-white disabled:opacity-50 ${form.urgent_concern ? "bg-red-700" : "bg-teal-600"}`}
      >
        {busy ? (
          <LoaderCircle className="animate-spin" size={17} />
        ) : (
          <ClipboardCheck size={17} />
        )}
        {c.saveCheckIn}
      </button>
    </form>
  );
}

function TrendPanel({ rows, c }) {
  if (!rows.length) return <Empty>{c.noTrend}</Empty>;
  const width = 720;
  const height = 240;
  const left = 42;
  const top = 24;
  const chartWidth = 650;
  const chartHeight = 150;
  const x = (index) =>
    left +
    (rows.length === 1
      ? chartWidth / 2
      : (index * chartWidth) / (rows.length - 1));
  const y = (value) => top + ((5 - value) * chartHeight) / 4;
  const series = [
    ["energy", c.energy, "#2563eb"],
    ["sleep_quality", c.sleep, "#0f8f83"],
    ["stress", c.stress, "#d97706"],
    ["recovery_confidence", c.confidence, "#7c3aed"],
  ];
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="flex items-center gap-2 font-bold text-[#071b4a]">
        <LineChart size={19} className="text-blue-600" />
        {c.trendTitle}
      </h2>
      <p className="mt-1 text-xs leading-5 text-slate-500">{c.trendHelp}</p>
      <div className="mt-4 overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={c.trendTitle}
          className="min-w-[620px]"
        >
          {[1, 2, 3, 4, 5].map((value) => (
            <g key={value}>
              <line
                x1={left}
                x2={left + chartWidth}
                y1={y(value)}
                y2={y(value)}
                stroke="#e2e8f0"
              />
              <text x="18" y={y(value) + 4} fontSize="11" fill="#64748b">
                {value}
              </text>
            </g>
          ))}
          {series.map(([key, label, color]) => (
            <g key={key}>
              <polyline
                points={rows
                  .map((row, index) => `${x(index)},${y(row[key])}`)
                  .join(" ")}
                fill="none"
                stroke={color}
                strokeWidth="3"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
              {rows.map((row, index) => (
                <circle
                  key={`${key}-${row.check_in_id}`}
                  cx={x(index)}
                  cy={y(row[key])}
                  r="4"
                  fill={color}
                >
                  <title>{`${label}: ${row[key]}/5 — ${row.check_in_date}`}</title>
                </circle>
              ))}
            </g>
          ))}
          {rows.map((row, index) => (
            <text
              key={row.check_in_id}
              x={x(index)}
              y="204"
              textAnchor="middle"
              fontSize="10"
              fill="#64748b"
            >
              {row.check_in_date.slice(5)}
            </text>
          ))}
        </svg>
      </div>
      <div className="mt-3 flex flex-wrap gap-3 text-xs font-semibold">
        {series.map(([, label, color]) => (
          <span key={label} className="inline-flex items-center gap-1.5">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: color }}
            />
            {label}
          </span>
        ))}
      </div>
      <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {rows.slice(-4).map((row) => (
          <div key={row.check_in_id} className="rounded-xl bg-slate-50 p-3">
            <p className="text-xs text-slate-500">{row.check_in_date}</p>
            <p className="mt-1 text-sm font-bold text-slate-800">
              {c.activityTrend}: {row.activity_minutes}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

function ReminderForm({ preference, patientId, onSaved, c }) {
  const [form, setForm] = useState(preference);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    setForm(preference);
  }, [preference]);
  const update = (key, value) =>
    setForm((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await updateRecoveryCoachingReminderPreference(
        {
          enabled: form.enabled,
          local_time: form.local_time,
          cadence: form.cadence,
          missed_follow_up_days: Number(form.missed_follow_up_days),
          patient_agreed: true,
        },
        patientId,
      );
      await onSaved();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, c.updateError));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <h2 className="flex items-center gap-2 font-bold text-[#071b4a]">
        <Bell size={19} className="text-blue-600" />
        {c.reminderTitle}
      </h2>
      <p className="mt-1 text-xs leading-5 text-slate-500">{c.reminderHelp}</p>
      <label className="mt-4 flex gap-2 rounded-xl border border-blue-100 bg-blue-50 p-3 text-sm font-bold text-blue-950">
        <input
          type="checkbox"
          checked={form.enabled}
          onChange={(event) => update("enabled", event.target.checked)}
        />
        {c.enableReminder}
      </label>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <label className="text-xs font-bold text-slate-600">
          {c.reminderTime}
          <input
            type="time"
            value={form.local_time}
            onChange={(event) => update("local_time", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.cadence}
          <select
            value={form.cadence}
            onChange={(event) => update("cadence", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
          >
            <option value="daily">{c.daily}</option>
            <option value="weekdays">{c.weekdays}</option>
          </select>
        </label>
        <label className="text-xs font-bold text-slate-600 sm:col-span-2">
          {c.missedDays}
          <span className="mt-1 flex items-center gap-2">
            <input
              type="number"
              min="1"
              max="14"
              value={form.missed_follow_up_days}
              onChange={(event) =>
                update("missed_follow_up_days", Number(event.target.value))
              }
              className="min-h-11 w-24 rounded-xl border border-slate-300 px-3 font-normal"
            />
            <span className="font-normal">{c.days}</span>
          </span>
        </label>
      </div>
      <label className="mt-4 flex gap-2 text-xs text-slate-700">
        <input
          type="checkbox"
          checked={form.patient_agreed || false}
          onChange={(event) => update("patient_agreed", event.target.checked)}
        />
        {c.reminderAgreement}
      </label>
      {error ? (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      ) : null}
      <button
        disabled={busy || !form.patient_agreed}
        className="mt-4 inline-flex min-h-11 items-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white disabled:opacity-50"
      >
        {busy ? (
          <LoaderCircle className="animate-spin" size={17} />
        ) : (
          <Clock3 size={17} />
        )}
        {c.saveReminder}
      </button>
    </form>
  );
}

function FollowUpCard({ row, patientId, onSaved, c }) {
  const [form, setForm] = useState({
    disposition:
      row.coaching_state === "urgent_escalation"
        ? "escalated_urgent_pathway"
        : "contacted_patient",
    note: "",
    clinician_attestation: false,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await acknowledgeRecoveryCoachingCheckIn(
        row.check_in_id,
        { ...form, note: form.note || null },
        patientId,
      );
      await onSaved();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, c.updateError));
    } finally {
      setBusy(false);
    }
  }
  return (
    <article
      className={`rounded-2xl border p-5 shadow-sm ${row.coaching_state === "urgent_escalation" ? "border-red-200 bg-red-50" : "border-amber-200 bg-amber-50"}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-slate-600">
            {row.check_in_date} · {row.coaching_state.replaceAll("_", " ")}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-800">
            {row.supportive_prompt}
          </p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-bold ${row.reviewed_at ? "bg-emerald-100 text-emerald-800" : "bg-white text-amber-900"}`}
        >
          {row.reviewed_at ? c.reviewed : c.pending}
        </span>
      </div>
      {row.reviewed_at ? (
        <dl className="mt-4 text-xs text-slate-700">
          <dt className="font-bold">{c.disposition}</dt>
          <dd className="mt-1">
            {row.review_disposition?.replaceAll("_", " ")}
          </dd>
        </dl>
      ) : (
        <form onSubmit={submit} className="mt-4 grid gap-3">
          <label className="text-xs font-bold text-slate-700">
            {c.disposition}
            <select
              value={form.disposition}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  disposition: event.target.value,
                }))
              }
              className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
            >
              <option value="contacted_patient">{c.contacted}</option>
              <option value="scheduled_clinical_review">{c.scheduled}</option>
              <option value="escalated_urgent_pathway">{c.escalated}</option>
              {row.coaching_state !== "urgent_escalation" ? (
                <option value="reviewed_no_additional_action">
                  {c.noAction}
                </option>
              ) : null}
            </select>
          </label>
          <label className="text-xs font-bold text-slate-700">
            {c.reviewNote}
            <textarea
              maxLength="600"
              value={form.note}
              onChange={(event) =>
                setForm((current) => ({ ...current, note: event.target.value }))
              }
              className="mt-1 min-h-20 w-full rounded-xl border border-slate-300 bg-white p-3 font-normal"
            />
          </label>
          <label className="flex gap-2 text-xs font-semibold text-slate-700">
            <input
              type="checkbox"
              checked={form.clinician_attestation}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  clinician_attestation: event.target.checked,
                }))
              }
            />
            {c.attestation}
          </label>
          {error ? (
            <p role="alert" className="text-sm font-semibold text-red-700">
              {error}
            </p>
          ) : null}
          <button
            disabled={busy || !form.clinician_attestation}
            className="inline-flex min-h-11 w-fit items-center gap-2 rounded-xl bg-[#071b4a] px-4 text-sm font-bold text-white disabled:opacity-50"
          >
            {busy ? (
              <LoaderCircle className="animate-spin" size={17} />
            ) : (
              <CheckCheck size={17} />
            )}
            {c.acknowledge}
          </button>
        </form>
      )}
    </article>
  );
}

function ActionPlanForm({ patientId, goals, onSaved, c }) {
  const [form, setForm] = useState({
    goal_id: "",
    action_step: "",
    frequency: "",
    support_needed: "",
    review_date: futureDate(14),
    patient_agreed: false,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    if (!form.goal_id && goals.length)
      setForm((current) => ({ ...current, goal_id: goals[0].goal_id }));
  }, [goals, form.goal_id]);
  const update = (key, value) =>
    setForm((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await createRecoveryCoachingActionPlan(
        { ...form, support_needed: form.support_needed || null },
        patientId,
      );
      setForm((current) => ({
        ...current,
        action_step: "",
        frequency: "",
        support_needed: "",
        patient_agreed: false,
      }));
      await onSaved();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, c.updateError));
    } finally {
      setBusy(false);
    }
  }
  if (!goals.length) return <Empty>{c.needGoal}</Empty>;
  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <h2 className="flex items-center gap-2 font-bold text-[#071b4a]">
        <ClipboardCheck size={19} className="text-purple-600" />
        {c.actionPlanTitle}
      </h2>
      <div className="mt-4 grid gap-3">
        <label className="text-xs font-bold text-slate-600">
          {c.goals}
          <select
            value={form.goal_id}
            onChange={(event) => update("goal_id", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
          >
            {goals.map((goal) => (
              <option key={goal.goal_id} value={goal.goal_id}>
                {goal.title}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.agreedStep}
          <textarea
            required
            value={form.action_step}
            onChange={(event) => update("action_step", event.target.value)}
            className="mt-1 min-h-20 w-full rounded-xl border border-slate-300 p-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.frequency}
          <input
            required
            value={form.frequency}
            onChange={(event) => update("frequency", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.support}
          <textarea
            value={form.support_needed}
            onChange={(event) => update("support_needed", event.target.value)}
            className="mt-1 min-h-20 w-full rounded-xl border border-slate-300 p-3 font-normal"
          />
        </label>
        <label className="text-xs font-bold text-slate-600">
          {c.reviewDate}
          <input
            type="date"
            min={today()}
            value={form.review_date}
            onChange={(event) => update("review_date", event.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <label className="flex gap-2 text-xs text-slate-700">
          <input
            type="checkbox"
            checked={form.patient_agreed}
            onChange={(event) => update("patient_agreed", event.target.checked)}
          />
          {c.planAgreement}
        </label>
      </div>
      {error ? (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      ) : null}
      <button
        disabled={busy || !form.patient_agreed}
        className="mt-4 inline-flex min-h-11 items-center gap-2 rounded-xl bg-purple-600 px-4 text-sm font-bold text-white disabled:opacity-50"
      >
        {busy ? (
          <LoaderCircle className="animate-spin" size={17} />
        ) : (
          <Plus size={17} />
        )}
        {c.savePlan}
      </button>
    </form>
  );
}

export default function RecoveryCoachingWorkspace({ user }) {
  const { locale, direction } = useLocale();
  const c = COPY[locale] || COPY.en;
  const clinicalRole = ["therapist", "admin", "super_admin"].includes(
    user?.role,
  );
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState("");
  const [data, setData] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [canApplyTemplate, setCanApplyTemplate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("overview");
  useEffect(() => {
    if (!clinicalRole) return undefined;
    let active = true;
    listPatientProfiles()
      .then((rows) => {
        if (active) {
          setPatients(rows);
          setPatientId((current) => current || rows[0]?.patient_id || "");
        }
      })
      .catch((requestError) => {
        if (active) setError(getApiErrorMessage(requestError, c.updateError));
      })
      .finally(() => {
        if (active && !patientId) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [clinicalRole, c.updateError, patientId]);
  const refresh = useCallback(
    async (silent = Boolean(data)) => {
      if (clinicalRole && !patientId) {
        setData(null);
        setLoading(false);
        return;
      }
      if (!silent) setLoading(true);
      try {
        const [nextData, templateData] = await Promise.all([
          getRecoveryCoachingDashboard(patientId || undefined),
          getRecoveryCoachingTemplates(),
        ]);
        setData(nextData);
        setTemplates(templateData.templates || []);
        setCanApplyTemplate(Boolean(templateData.can_apply_template));
        setError("");
      } catch (requestError) {
        setError(getApiErrorMessage(requestError, c.updateError));
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [c.updateError, clinicalRole, data, patientId],
  );
  useEffect(() => {
    refresh(false);
  }, [patientId, clinicalRole]);
  const activePlans = useMemo(
    () => data?.action_plans?.filter((plan) => plan.status === "active") || [],
    [data],
  );
  const followUps = useMemo(
    () =>
      data?.check_ins?.filter((row) => row.coaching_state !== "ready") || [],
    [data],
  );
  const tabs = [
    ["overview", c.overview],
    ["checkin", c.dailyCheckIn],
    ["goals", c.goals],
    ["trends", c.trends],
    ["reminders", c.reminders],
    ...(clinicalRole
      ? [
          ["followup", c.followUp],
          ["plan", c.actionPlan],
        ]
      : []),
  ];
  function handleTabKeyDown(event, index) {
    let nextIndex = index;
    if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = tabs.length - 1;
    else if (event.key === "ArrowRight")
      nextIndex =
        (index + (direction === "rtl" ? -1 : 1) + tabs.length) % tabs.length;
    else if (event.key === "ArrowLeft")
      nextIndex =
        (index + (direction === "rtl" ? 1 : -1) + tabs.length) % tabs.length;
    else return;
    event.preventDefault();
    const nextId = tabs[nextIndex][0];
    setTab(nextId);
    requestAnimationFrame(() =>
      document.getElementById(`recovery-tab-${nextId}`)?.focus(),
    );
  }
  return (
    <main
      dir={direction}
      className="mx-auto max-w-[1450px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8"
    >
      <PageHeader
        eyebrow={c.eyebrow}
        title={c.title}
        description={c.description}
      />
      <div className="mb-5 grid gap-3 lg:grid-cols-[1fr_auto]">
        <div className="flex gap-3 rounded-2xl border border-blue-100 bg-blue-50 p-4 text-sm leading-6 text-blue-950">
          <HeartHandshake className="mt-0.5 shrink-0 text-blue-700" size={20} />
          <p>
            <strong>{c.partnership}</strong> {c.boundary}
          </p>
        </div>
        {clinicalRole ? (
          <label className="rounded-2xl border border-slate-200 bg-white p-3 text-xs font-bold text-slate-600 shadow-sm">
            {c.patient}
            <select
              aria-label={c.patient}
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              className="ms-3 min-h-11 rounded-xl border border-slate-300 bg-white px-3 font-normal"
            >
              <option value="">{c.selectPatient}</option>
              {patients.map((patient) => (
                <option key={patient.patient_id} value={patient.patient_id}>
                  {patient.display_name}
                </option>
              ))}
            </select>
          </label>
        ) : null}
      </div>
      {error ? (
        <p
          role="alert"
          className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700"
        >
          {error}
        </p>
      ) : null}
      {loading ? (
        <div className="grid min-h-64 place-items-center">
          <LoaderCircle className="animate-spin text-blue-600" size={34} />
        </div>
      ) : !data ? (
        <Empty>{clinicalRole ? c.unavailable : c.profileRequired}</Empty>
      ) : (
        <>
          <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <Metric label={c.activeGoals} value={data.summary.active_goals} />
            <Metric
              label={c.completedGoals}
              value={data.summary.completed_goals}
            />
            <Metric label={c.checkIns} value={data.summary.check_ins_30d} />
            <Metric
              label={c.averageConfidence}
              value={data.summary.average_confidence ?? "—"}
              note={c.nonDiagnostic}
            />
            <Metric
              label={clinicalRole ? c.unacknowledged : c.followUp}
              value={
                clinicalRole
                  ? data.summary.unacknowledged_follow_up
                  : data.summary.follow_up_needed
              }
            />
          </div>
          <div className="mb-5 overflow-x-auto">
            <div
              role="tablist"
              aria-label={c.title}
              className="inline-flex min-w-full gap-1 rounded-xl border border-slate-200 bg-white p-1 shadow-sm sm:min-w-0"
            >
              {tabs.map(([id, label], index) => (
                <button
                  id={`recovery-tab-${id}`}
                  role="tab"
                  aria-controls="recovery-tabpanel"
                  aria-selected={tab === id}
                  tabIndex={tab === id ? 0 : -1}
                  key={id}
                  onClick={() => setTab(id)}
                  onKeyDown={(event) => handleTabKeyDown(event, index)}
                  className={`min-h-11 flex-1 whitespace-nowrap rounded-lg px-4 text-sm font-bold ${tab === id ? "bg-[#071b4a] text-white" : "text-slate-600 hover:bg-slate-50"}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <div
            id="recovery-tabpanel"
            role="tabpanel"
            aria-labelledby={`recovery-tab-${tab}`}
          >
            {tab === "overview" ? (
              <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
                <section className="space-y-3">
                  <h2 className="font-bold text-[#071b4a]">{c.currentGoals}</h2>
                  {data.goals.length ? (
                    data.goals.map((goal) => (
                      <GoalCard
                        key={goal.goal_id}
                        goal={goal}
                        patientId={patientId || undefined}
                        onRefresh={refresh}
                        c={c}
                      />
                    ))
                  ) : (
                    <Empty>{c.noGoals}</Empty>
                  )}
                </section>
                <aside className="space-y-4">
                  <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                    <h2 className="flex items-center gap-2 font-bold text-[#071b4a]">
                      <Sparkles size={18} className="text-teal-600" />
                      {c.activeSteps}
                    </h2>
                    {activePlans.length ? (
                      <div className="mt-3 space-y-3">
                        {activePlans.map((plan) => (
                          <div
                            key={plan.action_plan_id}
                            className="rounded-xl bg-slate-50 p-4"
                          >
                            <p className="text-sm font-bold text-slate-800">
                              {plan.action_step}
                            </p>
                            <p className="mt-1 text-xs text-slate-500">
                              {plan.frequency} · {c.reviewDate}{" "}
                              {plan.review_date}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-3 text-sm text-slate-500">{c.noPlan}</p>
                    )}
                  </div>
                  <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
                    <h2 className="flex items-center gap-2 font-bold text-amber-900">
                      <ShieldAlert size={18} />
                      {c.safetyBoundary}
                    </h2>
                    <p className="mt-2 text-sm leading-6 text-amber-950">
                      {c.safetyText}
                    </p>
                    <p className="mt-2 text-xs font-semibold leading-5 text-amber-900">
                      {c.noRealtime}
                    </p>
                    {data.scope.urgent_contact ? (
                      <p className="mt-2 text-sm font-bold text-amber-950">
                        {data.scope.organization}: {data.scope.urgent_contact}
                      </p>
                    ) : null}
                  </div>
                </aside>
              </div>
            ) : null}
            {tab === "checkin" ? (
              <CheckInForm
                patientId={patientId || undefined}
                onSaved={refresh}
                locale={locale}
                c={c}
              />
            ) : null}
            {tab === "goals" ? (
              <GoalForm
                patientId={patientId || undefined}
                onSaved={refresh}
                templates={templates}
                canApplyTemplate={canApplyTemplate}
                locale={locale}
                c={c}
              />
            ) : null}
            {tab === "trends" ? (
              <TrendPanel rows={data.trends || []} c={c} />
            ) : null}
            {tab === "reminders" ? (
              <ReminderForm
                preference={data.reminder_preference}
                patientId={patientId || undefined}
                onSaved={refresh}
                c={c}
              />
            ) : null}
            {tab === "followup" && clinicalRole ? (
              <section className="space-y-4">
                <div>
                  <h2 className="font-bold text-[#071b4a]">
                    {c.followUpQueue}
                  </h2>
                  <p className="mt-1 text-xs text-slate-500">
                    {c.followUpHelp}
                  </p>
                </div>
                {followUps.length ? (
                  followUps.map((row) => (
                    <FollowUpCard
                      key={row.check_in_id}
                      row={row}
                      patientId={patientId}
                      onSaved={refresh}
                      c={c}
                    />
                  ))
                ) : (
                  <Empty>{c.noFollowUp}</Empty>
                )}
              </section>
            ) : null}
            {tab === "plan" && clinicalRole ? (
              <ActionPlanForm
                patientId={patientId}
                goals={data.goals}
                onSaved={refresh}
                c={c}
              />
            ) : null}
          </div>
        </>
      )}
    </main>
  );
}

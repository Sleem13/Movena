import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bell,
  CalendarDays,
  CheckCircle2,
  Clock3,
  CreditCard,
  HeartPulse,
  MessageSquareText,
  Play,
  RefreshCw,
} from "lucide-react";
import { PageHeader } from "../components/layout/AppShell.jsx";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import {
  getPatientToday,
  joinAppointment,
  listCatalog,
  listPatientAppointments,
  listPatientNotifications,
  markPatientNotificationRead,
  recordPatientAdherence,
  startCheckout,
} from "../services/api.js";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { getApiErrorMessage } from "../utils/requestErrors.js";

const copy = {
  en: {
    eyebrow: "My care",
    title: "Today's rehabilitation plan",
    desc: "Complete your prescribed exercises, track pain, and stay connected with your therapist.",
    program: "Today's rehabilitation plan",
    appt: "Next appointment",
    alerts: "Notifications",
    progress: "7-day progress",
    adherence: "Adherence",
    pain: "Average pain",
    complete: "Start exercise",
    done: "Completed",
    partial: "Partial",
    missed: "Missed",
    before: "Pain before",
    after: "Pain after",
    difficulty: "Difficulty",
    exertion: "Effort (0–10)",
    symptomsChanged: "I noticed new or worsening symptoms.",
    stoppedForSymptoms: "I stopped because of symptoms.",
    symptomTypes: "Exercise response",
    safetyAck: "I understand this check-in is not monitored in real time and does not replace urgent or clinical care.",
    note: "Note for therapist",
    save: "Save check-in",
    join: "Join secure call",
    catalog: "Sessions & packages",
    buy: "Continue to payment",
    empty: "No exercises scheduled today",
    emptyHelp: "Your therapist has not assigned any exercises for today.",
    noAppt: "No upcoming appointment.",
    safe: "Video calls are private and are never recorded.",
    loading: "Loading your care plan…",
    loadError: "We couldn't load your care workspace",
    loadHelp: "Some information is temporarily unavailable. Please try again.",
    setupTitle: "Patient profile setup required",
    setupHelp:
      "Your care profile has not been linked yet. Contact your therapist or administrator to complete setup.",
    retry: "Retry",
    technical: "Technical details",
    responseReview: "Your therapist needs to review this response",
    responseOk: "Exercise response saved",
  },
  ar: {
    exertion: "المجهود (0–10)",
    symptomsChanged: "لاحظت أعراضًا جديدة أو متزايدة.",
    stoppedForSymptoms: "توقفت بسبب الأعراض.",
    symptomTypes: "استجابة التمرين",
    safetyAck: "أفهم أن هذا التسجيل لا تتم مراقبته فورًا ولا يحل محل الرعاية العاجلة أو السريرية.",
    responseReview: "تحتاج هذه الاستجابة إلى مراجعة المعالج",
    responseOk: "تم حفظ استجابة التمرين",
    eyebrow: "رعايتي",
    title: "خطة التأهيل اليوم",
    desc: "نفّذ التمارين التي وصفها الطبيب وسجّل الألم وابقَ على تواصل معه.",
    program: "خطة التأهيل اليوم",
    appt: "الموعد القادم",
    alerts: "التنبيهات",
    progress: "تقدم آخر 7 أيام",
    adherence: "الالتزام",
    pain: "متوسط الألم",
    complete: "ابدأ التمرين",
    done: "تم",
    partial: "جزئيًا",
    missed: "لم يتم",
    before: "الألم قبل",
    after: "الألم بعد",
    difficulty: "الصعوبة",
    note: "ملاحظة للطبيب",
    save: "حفظ التسجيل",
    join: "دخول المكالمة الآمنة",
    catalog: "الجلسات والباقات",
    buy: "متابعة الدفع",
    empty: "لا توجد تمارين مجدولة اليوم",
    emptyHelp: "لم يعيّن لك المعالج أي تمارين لهذا اليوم.",
    noAppt: "لا يوجد موعد قادم.",
    safe: "مكالمات الفيديو خاصة ولا يتم تسجيلها.",
    loading: "جارٍ تحميل خطة الرعاية…",
    loadError: "تعذر تحميل مساحة الرعاية",
    loadHelp: "بعض المعلومات غير متاحة مؤقتًا. يرجى المحاولة مرة أخرى.",
    setupTitle: "يلزم إعداد ملف المريض",
    setupHelp:
      "لم يتم ربط ملف الرعاية بعد. تواصل مع المعالج أو مسؤول النظام لاستكمال الإعداد.",
    retry: "إعادة المحاولة",
    technical: "تفاصيل تقنية",
  },
};

function formatDate(value, locale) {
  return value
    ? new Intl.DateTimeFormat(locale === "ar" ? "ar-EG" : "en-GB", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: "Africa/Cairo",
      }).format(new Date(value))
    : "—";
}

export default function PatientCareDashboard({
  onAnalyzeAssigned,
  pendingAnalysis,
  onAnalysisLinked,
}) {
  const { locale } = useLocale();
  const c = copy[locale] || copy.en;
  const { user } = useAuth();
  const [today, setToday] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [catalog, setCatalog] = useState({ services: [], packages: [] });
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({
    completion_status: "completed",
    pain_before: "",
    pain_after: "",
    difficulty: 1,
    fatigue: 1,
    perceived_exertion: "",
    symptoms_changed: false,
    stopped_due_to_symptoms: false,
    symptom_flags: [],
    safety_acknowledged: false,
    note: "",
    analysis_session_id: null,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [technicalError, setTechnicalError] = useState("");
  const [setupRequired, setSetupRequired] = useState(false);
  const [billingPhone, setBillingPhone] = useState("");
  const [responseNotice, setResponseNotice] = useState(null);
  const displayName =
    user?.full_name ||
    user?.email?.split("@")[0] ||
    (locale === "ar" ? "بك" : "back");
  const completedToday =
    today?.plan_items?.filter((item) => item.completion_status === "completed")
      .length || 0;
  const openCheckIn = (item) => {
    setResponseNotice(null);
    setSelected(item);
    setForm({
      completion_status: item.completion_status || "completed",
      pain_before: item.pain_before ?? "",
      pain_after: item.pain_after ?? "",
      difficulty: item.difficulty ?? 1,
      fatigue: item.fatigue ?? 1,
      perceived_exertion: item.perceived_exertion ?? "",
      symptoms_changed: item.symptoms_changed || false,
      stopped_due_to_symptoms: item.stopped_due_to_symptoms || false,
      symptom_flags: item.symptom_flags || [],
      safety_acknowledged: false,
      note: item.patient_comment || "",
      analysis_session_id: item.analysis_session_id || null,
    });
  };
  const load = async () => {
    setBusy(true);
    setError("");
    setTechnicalError("");
    setSetupRequired(false);
    try {
      const [day, appts, notices, products] = await Promise.all([
        getPatientToday(),
        listPatientAppointments(),
        listPatientNotifications(),
        listCatalog(),
      ]);
      setToday(day);
      setAppointments(appts);
      setNotifications(notices);
      setCatalog(products);
    } catch (e) {
      setSetupRequired(e.response?.status === 404);
      setError(e.response?.status === 404 ? c.setupTitle : c.loadError);
      setTechnicalError(getApiErrorMessage(e, e.message));
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    load();
  }, []);
  useEffect(() => {
    if (!today || !pendingAnalysis) return;
    const item = today.plan_items.find(
      (row) => row.item_id === pendingAnalysis.plan_item_id,
    );
    if (item) {
      setSelected(item);
      setForm((current) => ({
        ...current,
        analysis_session_id: pendingAnalysis.analysis_session_id,
      }));
    }
  }, [today, pendingAnalysis]);
  const upcoming = useMemo(
    () =>
      appointments
        .filter(
          (a) =>
            ["scheduled", "confirmed"].includes(a.status) &&
            new Date(a.ends_at) > new Date(),
        )
        .sort((a, b) => new Date(a.starts_at) - new Date(b.starts_at))[0] ||
      today?.upcoming_appointment,
    [appointments, today],
  );
  const submit = async (event) => {
    event.preventDefault();
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      const response = await recordPatientAdherence({
        plan_item_id: selected.item_id,
        scheduled_date: today.date,
        ...form,
        pain_before: form.pain_before === "" ? null : Number(form.pain_before),
        pain_after: form.pain_after === "" ? null : Number(form.pain_after),
        difficulty: Number(form.difficulty),
        fatigue: Number(form.fatigue),
        perceived_exertion: form.perceived_exertion === "" ? null : Number(form.perceived_exertion),
      });
      setResponseNotice(response);
      setSelected(null);
      onAnalysisLinked?.();
      await load();
    } catch (e) {
      setError(getApiErrorMessage(e, e.message));
      setBusy(false);
    }
  };
  const join = async () => {
    try {
      const data = await joinAppointment(upcoming.appointment_id);
      window.open(
        `${data.room_url}?t=${encodeURIComponent(data.meeting_token)}`,
        "_blank",
        "noopener,noreferrer",
      );
    } catch (e) {
      setError(getApiErrorMessage(e, e.message));
    }
  };
  const checkout = async (product, kind) => {
    if (!/^\+?20[0-9]{10}$/.test(billingPhone)) {
      setError(
        locale === "ar"
          ? "أدخل رقم موبايل مصريًا صحيحًا بصيغة +20."
          : "Enter a valid Egyptian mobile number in +20 format.",
      );
      return;
    }
    setBusy(true);
    try {
      const data = await startCheckout({
        [`${kind}_id`]: product[`${kind}_id`],
        billing_phone: billingPhone,
      });
      if (data.payment_url) window.location.assign(data.payment_url);
    } catch (e) {
      setError(getApiErrorMessage(e, e.message));
      setBusy(false);
    }
  };
  if (busy && !today)
    return (
      <main className="grid min-h-[65vh] place-items-center">
        <LoadingSpinner label={c.loading} />
      </main>
    );
  if (!today && error)
    return (
      <main className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <PageHeader
          title={
            locale === "ar"
              ? `مرحبًا بعودتك، ${displayName}`
              : `Welcome back, ${displayName}`
          }
          description={c.desc}
        />
        <Card className="p-5 sm:p-6">
          <Alert tone={setupRequired ? "info" : "error"} title={error}>
            <p>{setupRequired ? c.setupHelp : c.loadHelp}</p>
            <Button className="mt-4" variant="secondary" onClick={load}>
              <RefreshCw size={16} />
              {c.retry}
            </Button>
            {import.meta.env.DEV && technicalError ? (
              <details className="mt-4 text-xs">
                <summary className="cursor-pointer font-semibold">
                  {c.technical}
                </summary>
                <p className="mt-2 rounded-lg bg-white/70 p-3 font-mono">
                  {technicalError}
                </p>
              </details>
            ) : null}
          </Alert>
        </Card>
      </main>
    );
  return (
    <main className="mx-auto max-w-[1500px] px-4 py-7 sm:px-6 lg:px-9">
      <PageHeader
        title={
          locale === "ar"
            ? `مرحبًا بعودتك، ${displayName}`
            : `Welcome back, ${displayName}`
        }
        description={c.desc}
        actions={
          <Button variant="secondary" onClick={load}>
            <RefreshCw size={16} />
            {locale === "ar" ? "تحديث" : "Refresh"}
          </Button>
        }
      />
      {error ? <Alert className="mb-5">{error}</Alert> : null}
      {responseNotice ? (
        <Alert
          className="mb-5"
          tone={responseNotice.clinician_review_required ? "warning" : "success"}
          title={responseNotice.clinician_review_required ? c.responseReview : c.responseOk}
        >
          {responseNotice.supportive_instruction}
        </Alert>
      ) : null}
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(300px,.75fr)]">
        <div className="patient-care-primary min-w-0 flex flex-col gap-5">
          <Card className="overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <h2 className="flex items-center gap-2 font-bold text-clinical-ink">
                <HeartPulse size={19} className="text-teal-600" />
                {c.program}
              </h2>
              <Badge tone="teal">{today?.date}</Badge>
            </div>
            <div className="divide-y divide-slate-100">
              {today?.plan_items?.length ? (
                today.plan_items.map((item) => (
                  <div
                    key={item.item_id}
                    className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center"
                  >
                    <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-teal-50 text-teal-700">
                      <Play size={18} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-bold text-slate-900">
                        {item.exercise_id.replaceAll("_", " ")}
                      </h3>
                      <p className="mt-1 text-sm text-slate-500">
                        {item.sets} × {item.reps}
                        {item.duration_minutes
                          ? ` · ${item.duration_minutes} min`
                          : ""}
                        {item.rest_interval_seconds
                          ? ` · ${item.rest_interval_seconds}s rest`
                          : ""}
                        {item.tempo ? ` · ${item.tempo}` : ""}
                        {item.target_rom_degrees != null
                          ? ` · ROM ${item.target_rom_degrees}°`
                          : ""}
                        {item.target_score != null
                          ? ` · target ${item.target_score}/100`
                          : ""}
                      </p>
                      {item.instructions ? (
                        <p className="mt-1 text-xs leading-5 text-slate-600">
                          {item.instructions}
                        </p>
                      ) : null}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {onAnalyzeAssigned &&
                      (item.requires_ai_analysis ||
                        item.requested_media_upload) ? (
                        <Button
                          variant="secondary"
                          onClick={() => onAnalyzeAssigned(item, today.date)}
                        >
                          <Activity size={16} />
                          {locale === "ar"
                            ? "فتح مدرب التمارين"
                            : "Open AI Exercise Coach"}
                        </Button>
                      ) : null}
                      {item.completion_status ? (
                        <Badge tone="teal">
                          <CheckCircle2 size={13} className="me-1" />
                          {item.completion_status}
                        </Badge>
                      ) : (
                        <Button onClick={() => openCheckIn(item)}>
                          {c.complete}
                        </Button>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-5">
                  <EmptyState
                    compact
                    title={c.empty}
                    description={c.emptyHelp}
                  />
                </div>
              )}
            </div>
          </Card>
          <Card className="order-3 p-5">
            <h2 className="mb-4 flex items-center gap-2 font-bold">
              <CreditCard size={19} className="text-blue-600" />
              {c.catalog}
            </h2>
            <label className="mb-4 block text-sm font-semibold">
              {locale === "ar" ? "رقم الموبايل للدفع" : "Billing mobile number"}
              <input
                dir="ltr"
                inputMode="tel"
                autoComplete="tel"
                value={billingPhone}
                onChange={(event) => setBillingPhone(event.target.value.trim())}
                placeholder="+201001234567"
                className="mt-2 w-full max-w-sm rounded-xl border border-slate-200 bg-white px-3 py-2.5"
              />
            </label>
            <div className="grid gap-3 md:grid-cols-2">
              {[
                ...catalog.services.map((x) => [x, "service"]),
                ...catalog.packages.map((x) => [x, "package"]),
              ].map(([item, kind]) => (
                <div
                  key={item[`${kind}_id`]}
                  className="rounded-xl border border-slate-200 p-4"
                >
                  <p className="font-bold">
                    {locale === "ar" ? item.name_ar : item.name_en}
                  </p>
                  <p className="my-3 text-2xl font-extrabold text-[#071b4a]">
                    {(item.price_minor / 100).toLocaleString(
                      locale === "ar" ? "ar-EG" : "en-EG",
                    )}{" "}
                    <span className="text-sm">EGP</span>
                  </p>
                  <Button
                    variant="secondary"
                    onClick={() => checkout(item, kind)}
                  >
                    {c.buy}
                  </Button>
                </div>
              ))}
            </div>
          </Card>
          <Card className="order-2 overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <div>
                <h2 className="flex items-center gap-2 font-extrabold text-[#071b4a]">
                  <CheckCircle2 size={19} className="text-teal-700" />
                  {locale === "ar" ? "تسجيل تمارين اليوم" : "Today’s check-in"}
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  {locale === "ar"
                    ? "سجّل التنفيذ والألم والصعوبة ليتمكن طبيبك من متابعة الخطة."
                    : "Log completion, pain and difficulty so your therapist can adjust the plan."}
                </p>
              </div>
              <Badge tone="blue">
                {completedToday} / {today?.plan_items?.length || 0}
              </Badge>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-5 py-3">
                      {locale === "ar" ? "التمرين" : "Exercise"}
                    </th>
                    <th className="px-4 py-3">
                      {locale === "ar" ? "الحالة" : "Status"}
                    </th>
                    <th className="px-4 py-3">{c.before}</th>
                    <th className="px-4 py-3">{c.after}</th>
                    <th className="px-4 py-3">{c.difficulty}</th>
                    <th className="px-4 py-3">
                      {locale === "ar" ? "الإجهاد" : "Fatigue"}
                    </th>
                    <th className="px-4 py-3">
                      <span className="sr-only">{c.complete}</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {today?.plan_items?.length ? (
                    today.plan_items.map((item) => (
                      <tr key={item.item_id} className="hover:bg-blue-50/40">
                        <td className="px-5 py-3.5 font-bold capitalize text-[#071b4a]">
                          {item.exercise_id.replaceAll("_", " ")}
                        </td>
                        <td className="px-4 py-3.5">
                          {item.completion_status ? (
                            <Badge
                              tone={
                                item.completion_status === "completed"
                                  ? "teal"
                                  : "amber"
                              }
                            >
                              {item.completion_status.replaceAll("_", " ")}
                            </Badge>
                          ) : (
                            <Badge tone="slate">
                              {locale === "ar" ? "لم يُسجّل" : "Not logged"}
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 py-3.5 text-slate-600">
                          {item.pain_before ?? "—"}
                        </td>
                        <td className="px-4 py-3.5 text-slate-600">
                          {item.pain_after ?? "—"}
                        </td>
                        <td className="px-4 py-3.5 text-slate-600">
                          {item.difficulty ?? "—"}
                        </td>
                        <td className="px-4 py-3.5 text-slate-600">
                          {item.fatigue ?? "—"}
                        </td>
                        <td className="px-4 py-3.5">
                          <Button
                            variant={
                              item.completion_status ? "secondary" : "primary"
                            }
                            onClick={() => openCheckIn(item)}
                          >
                            <MessageSquareText size={15} />
                            {item.completion_status
                              ? locale === "ar"
                                ? "تعديل"
                                : "Update"
                              : c.complete}
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan="7"
                        className="px-5 py-8 text-center text-slate-500"
                      >
                        {c.empty}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
        <aside className="space-y-5">
          <Card className="p-5">
            <h2 className="flex items-center gap-2 font-bold">
              <CalendarDays size={19} className="text-blue-600" />
              {c.appt}
            </h2>
            {upcoming ? (
              <>
                <p className="mt-4 text-lg font-extrabold">
                  {formatDate(upcoming.starts_at, locale)}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {upcoming.delivery_mode} ·{" "}
                  <span className="uppercase">{upcoming.status}</span>
                </p>
                <Button
                  className="mt-4 w-full"
                  onClick={join}
                  disabled={!upcoming.can_join}
                >
                  <Clock3 size={17} />
                  {c.join}
                </Button>
                <p className="mt-3 text-xs leading-5 text-slate-500">
                  {c.safe}
                </p>
              </>
            ) : (
              <p className="mt-4 text-sm text-slate-500">{c.noAppt}</p>
            )}
          </Card>
          <Card className="p-5">
            <h2 className="font-bold">{c.progress}</h2>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-blue-50 p-4">
                <p className="text-xs font-semibold text-blue-700">
                  {c.adherence}
                </p>
                <p className="mt-2 text-2xl font-extrabold text-[#071b4a]">
                  {today?.adherence_percent_7d ?? 0}%
                </p>
              </div>
              <div className="rounded-xl bg-teal-50 p-4">
                <p className="text-xs font-semibold text-teal-700">{c.pain}</p>
                <p className="mt-2 text-2xl font-extrabold text-[#071b4a]">
                  {today?.average_pain_7d ?? "—"}
                  <span className="text-sm">/10</span>
                </p>
              </div>
            </div>
          </Card>
          <Card className="p-5">
            <h2 className="flex items-center gap-2 font-bold">
              <Bell size={19} className="text-amber-600" />
              {c.alerts}
            </h2>
            <div className="mt-3 space-y-2">
              {notifications.slice(0, 5).map((n) => (
                <button
                  key={n.notification_id}
                  onClick={async () => {
                    if (!n.read_at) {
                      await markPatientNotificationRead(n.notification_id);
                      setNotifications((rows) =>
                        rows.map((x) =>
                          x.notification_id === n.notification_id
                            ? { ...x, read_at: new Date().toISOString() }
                            : x,
                        ),
                      );
                    }
                  }}
                  className={`w-full rounded-xl border p-3 text-start text-sm ${n.read_at ? "border-slate-100 bg-white" : "border-blue-100 bg-blue-50"}`}
                >
                  <span className="block font-bold">{n.title}</span>
                  <span className="mt-1 block text-xs leading-5 text-slate-600">
                    {n.body}
                  </span>
                </button>
              ))}
            </div>
          </Card>
        </aside>
      </div>
      {selected ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/45 p-4">
          <Card as="form" onSubmit={submit} className="w-full max-w-lg p-6">
            <h2 className="text-xl font-extrabold">
              {c.complete}: {selected.exercise_id.replaceAll("_", " ")}
            </h2>
            {form.analysis_session_id ? (
              <Alert tone="success" className="mt-4">
                {locale === "ar"
                  ? "سيتم ربط نتيجة تحليل الحركة بهذا التسجيل."
                  : "This check-in will be linked to the saved movement analysis."}
              </Alert>
            ) : null}
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="text-sm font-semibold">
                {c.before}
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={form.pain_before}
                  onChange={(e) =>
                    setForm({ ...form, pain_before: e.target.value })
                  }
                  className="mt-2 w-full rounded-lg border p-2"
                />
              </label>
              <label className="text-sm font-semibold">
                {c.after}
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={form.pain_after}
                  onChange={(e) =>
                    setForm({ ...form, pain_after: e.target.value })
                  }
                  className="mt-2 w-full rounded-lg border p-2"
                />
              </label>
              <label className="text-sm font-semibold">
                {c.difficulty} (1–5)
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={form.difficulty}
                  onChange={(e) =>
                    setForm({ ...form, difficulty: e.target.value })
                  }
                  className="mt-2 w-full rounded-lg border p-2"
                />
              </label>
              <label className="text-sm font-semibold">
                {locale === "ar" ? "الإجهاد" : "Fatigue"} (1–5)
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={form.fatigue}
                  onChange={(e) =>
                    setForm({ ...form, fatigue: e.target.value })
                  }
                  className="mt-2 w-full rounded-lg border p-2"
                />
              </label>
              <label className="text-sm font-semibold">
                {c.exertion}
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={form.perceived_exertion}
                  onChange={(event) =>
                    setForm({ ...form, perceived_exertion: event.target.value })
                  }
                  className="mt-2 w-full rounded-lg border p-2"
                />
              </label>
            </div>
            <fieldset className="mt-5 rounded-xl border border-amber-200 bg-amber-50/60 p-4">
              <legend className="px-1 text-sm font-bold text-amber-950">
                {c.symptomTypes}
              </legend>
              <div className="space-y-3 text-sm text-slate-700">
                <label className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={form.symptoms_changed}
                    onChange={(event) =>
                      setForm({ ...form, symptoms_changed: event.target.checked })
                    }
                  />
                  <span>{c.symptomsChanged}</span>
                </label>
                <label className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={form.stopped_due_to_symptoms}
                    onChange={(event) =>
                      setForm({ ...form, stopped_due_to_symptoms: event.target.checked })
                    }
                  />
                  <span>{c.stoppedForSymptoms}</span>
                </label>
                <div className="grid gap-2 sm:grid-cols-2">
                  {[
                    ["pain_increase", locale === "ar" ? "زيادة الألم" : "Pain increase"],
                    ["dizziness", locale === "ar" ? "دوخة" : "Dizziness"],
                    ["faintness", locale === "ar" ? "شعور بالإغماء" : "Faintness"],
                    ["unusual_shortness_of_breath", locale === "ar" ? "ضيق نفس غير معتاد" : "Unusual shortness of breath"],
                    ["chest_discomfort", locale === "ar" ? "انزعاج في الصدر" : "Chest discomfort"],
                    ["new_numbness_or_weakness", locale === "ar" ? "خدر أو ضعف جديد" : "New numbness or weakness"],
                    ["instability", locale === "ar" ? "عدم ثبات" : "Instability"],
                    ["other", locale === "ar" ? "أخرى" : "Other"],
                  ].map(([value, label]) => (
                    <label key={value} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2">
                      <input
                        type="checkbox"
                        checked={form.symptom_flags.includes(value)}
                        onChange={() =>
                          setForm((current) => ({
                            ...current,
                            symptom_flags: current.symptom_flags.includes(value)
                              ? current.symptom_flags.filter((flag) => flag !== value)
                              : [...current.symptom_flags, value],
                          }))
                        }
                      />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>
                {form.symptoms_changed ||
                form.stopped_due_to_symptoms ||
                form.symptom_flags.length > 0 ? (
                  <label className="flex items-start gap-2 border-t border-amber-200 pt-3 font-semibold text-amber-950">
                    <input
                      type="checkbox"
                      required
                      className="mt-1"
                      checked={form.safety_acknowledged}
                      onChange={(event) =>
                        setForm({ ...form, safety_acknowledged: event.target.checked })
                      }
                    />
                    <span>{c.safetyAck}</span>
                  </label>
                ) : null}
              </div>
            </fieldset>
            <div className="mt-4 flex flex-wrap gap-2">
              {[
                ["completed", c.done],
                ["partial", c.partial],
                ["not_completed", c.missed],
              ].map(([value, label]) => (
                <button
                  type="button"
                  key={value}
                  onClick={() => setForm({ ...form, completion_status: value })}
                  className={`rounded-full border px-3 py-2 text-sm font-bold ${form.completion_status === value ? "border-blue-600 bg-blue-50 text-blue-700" : "border-slate-200"}`}
                >
                  {label}
                </button>
              ))}
            </div>
            <label className="mt-4 block text-sm font-semibold">
              {c.note}
              <textarea
                value={form.note}
                onChange={(e) => setForm({ ...form, note: e.target.value })}
                className="mt-2 min-h-24 w-full rounded-lg border p-3"
              />
            </label>
            <div className="mt-5 flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setSelected(null)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={busy}>
                {c.save}
              </Button>
            </div>
          </Card>
        </div>
      ) : null}
    </main>
  );
}

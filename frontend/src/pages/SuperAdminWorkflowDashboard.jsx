import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CalendarDays,
  Check,
  ChevronRight,
  CircleDollarSign,
  ClipboardCheck,
  Clock3,
  FileClock,
  HeartPulse,
  ListChecks,
  RefreshCw,
  ShieldCheck,
  UserCheck,
  UsersRound,
  WalletCards,
} from "lucide-react";

import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { getApiErrorMessage } from "../utils/requestErrors.js";
import { getAdminWorkflow } from "../services/api.js";

const STAGE_ICONS = {
  account_consent: ShieldCheck,
  therapist_assignment: UserCheck,
  care_plan: ClipboardCheck,
  appointment: CalendarDays,
  payment: WalletCards,
  follow_up: HeartPulse,
};

const METRIC_ICONS = {
  users: UsersRound,
  patients: HeartPulse,
  active_assignments: UserCheck,
  appointments: CalendarDays,
  paid_orders: CircleDollarSign,
};

function formatAge(seconds, locale) {
  const units =
    seconds >= 86400
      ? [Math.floor(seconds / 86400), "day"]
      : seconds >= 3600
        ? [Math.floor(seconds / 3600), "hour"]
        : [Math.max(1, Math.floor(seconds / 60)), "minute"];
  return new Intl.RelativeTimeFormat(locale, {
    numeric: "always",
    style: "short",
  }).format(-units[0], units[1]);
}

function formatDateTime(value, locale) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(locale, {
    timeZone: "Africa/Cairo",
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function MetricStrip({ metrics, t }) {
  return (
    <Card
      aria-label={t("workflow.metrics")}
      className="grid grid-cols-2 overflow-hidden xl:grid-cols-5"
    >
      {Object.entries(metrics || {}).map(([key, value], index) => {
        const Icon = METRIC_ICONS[key] || Activity;
        return (
          <div
            key={key}
            className={`flex min-h-24 items-center gap-3 px-4 py-4 sm:px-5 ${index > 1 ? "border-t border-slate-200 xl:border-t-0" : ""} ${index % 2 ? "border-l border-slate-200 rtl:border-l-0 rtl:border-r xl:rtl:border-r-0" : ""} ${index ? "xl:border-l xl:border-slate-200 rtl:xl:border-l-0 rtl:xl:border-r" : ""} ${index === 4 ? "col-span-2 xl:col-span-1" : ""}`}
          >
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-700">
              <Icon size={19} />
            </span>
            <div>
              <p className="text-2xl font-extrabold tracking-tight text-[#071b4a]">
                {value}
              </p>
              <p className="mt-0.5 text-xs font-semibold text-slate-500">
                {t(`workflow.metric.${key}`)}
              </p>
            </div>
          </div>
        );
      })}
    </Card>
  );
}

function WorkflowRail({ stages, t }) {
  return (
    <Card className="overflow-hidden" aria-labelledby="workflow-rail-title">
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4 sm:px-6">
        <div>
          <h2
            id="workflow-rail-title"
            className="font-extrabold text-[#071b4a]"
          >
            {t("workflow.railTitle")}
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            {t("workflow.railDescription")}
          </p>
        </div>
        <Badge
          tone={
            stages?.some((stage) => stage.attention_count) ? "amber" : "teal"
          }
        >
          {stages?.reduce((sum, stage) => sum + stage.attention_count, 0) || 0}{" "}
          {t("workflow.needAttention")}
        </Badge>
      </div>
      <div className="overflow-x-auto px-5 py-6 sm:px-6">
        <ol className="grid min-w-[780px] grid-cols-6">
          {(stages || []).map((stage, index) => {
            const Icon = STAGE_ICONS[stage.key] || ListChecks;
            const attention = stage.attention_count > 0;
            return (
              <li key={stage.key} className="relative px-2 text-center">
                {index < stages.length - 1 ? (
                  <span
                    className={`absolute left-1/2 top-6 h-0.5 w-full ${attention ? "bg-amber-200" : "bg-emerald-200"}`}
                    aria-hidden="true"
                  />
                ) : null}
                <span
                  className={`relative z-10 mx-auto grid h-12 w-12 place-items-center rounded-full border-4 border-white shadow-sm ${attention ? "bg-amber-100 text-amber-700 ring-1 ring-amber-200" : "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200"}`}
                >
                  <Icon size={20} />
                </span>
                <h3 className="mt-3 text-xs font-extrabold text-[#071b4a]">
                  {t(`workflow.stage.${stage.key}`)}
                </h3>
                <p className="mt-1 text-[11px] font-semibold text-slate-500">
                  {stage.total} {t("workflow.total")}
                </p>
                <p
                  className={`mt-1 text-[11px] font-bold ${attention ? "text-amber-700" : "text-emerald-700"}`}
                >
                  {attention
                    ? `${stage.attention_count} ${t("workflow.needAttention")}`
                    : t("workflow.onTrack")}
                </p>
              </li>
            );
          })}
        </ol>
      </div>
    </Card>
  );
}

function SummaryRail({ data, t, locale }) {
  const exceptions = [
    ["pending_orders", data.payment_exceptions?.pending_orders],
    ["failed_payments", data.payment_exceptions?.failed_payments],
    ["pending_refunds", data.payment_exceptions?.pending_refunds],
  ];
  const privacy = [
    ["export", data.privacy_requests?.export],
    ["correction", data.privacy_requests?.correction],
    ["deletion", data.privacy_requests?.deletion],
  ];
  return (
    <aside className="space-y-4">
      <Card className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.12em] text-slate-400">
              {t("workflow.today")}
            </p>
            <p className="mt-2 text-base font-extrabold text-[#071b4a]">
              {new Intl.DateTimeFormat(locale, {
                dateStyle: "full",
                timeZone: "Africa/Cairo",
              }).format(new Date(`${data.today.date}T12:00:00+03:00`))}
            </p>
          </div>
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-700">
            <CalendarDays size={19} />
          </span>
        </div>
        <div className="mt-5 flex items-end justify-between border-t border-slate-200 pt-4">
          <span className="text-sm font-semibold text-slate-600">
            {t("workflow.appointments")}
          </span>
          <span className="text-3xl font-extrabold text-[#071b4a]">
            {data.today.appointments}
          </span>
        </div>
      </Card>
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-amber-700">
            <WalletCards size={19} />
          </span>
          <h2 className="font-extrabold text-[#071b4a]">
            {t("workflow.paymentExceptions")}
          </h2>
        </div>
        <dl className="mt-4 divide-y divide-slate-100">
          {exceptions.map(([key, value]) => (
            <div
              key={key}
              className="flex items-center justify-between py-3 text-sm"
            >
              <dt className="font-medium text-slate-600">
                {t(`workflow.${key}`)}
              </dt>
              <dd
                className={`font-extrabold ${value ? "text-amber-700" : "text-slate-400"}`}
              >
                {value || 0}
              </dd>
            </div>
          ))}
        </dl>
      </Card>
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-50 text-violet-700">
            <FileClock size={19} />
          </span>
          <div>
            <h2 className="font-extrabold text-[#071b4a]">
              {t("workflow.privacyRequests")}
            </h2>
            <p className="mt-0.5 text-xs text-slate-500">
              {data.privacy_requests?.pending || 0} {t("workflow.pending")}
            </p>
          </div>
        </div>
        <dl className="mt-4 grid grid-cols-3 gap-2">
          {privacy.map(([key, value]) => (
            <div key={key} className="rounded-xl bg-slate-50 p-3 text-center">
              <dd className="text-lg font-extrabold text-[#071b4a]">
                {value || 0}
              </dd>
              <dt className="mt-1 text-[10px] font-bold text-slate-500">
                {t(`workflow.${key}`)}
              </dt>
            </div>
          ))}
        </dl>
      </Card>
    </aside>
  );
}

function AttentionQueue({ items, t, locale, onReview }) {
  const [type, setType] = useState("all");
  const [priority, setPriority] = useState("all");
  const types = useMemo(
    () => [...new Set((items || []).map((item) => item.type))],
    [items],
  );
  const visible = (items || []).filter(
    (item) =>
      (type === "all" || item.type === type) &&
      (priority === "all" || item.priority === priority),
  );
  return (
    <Card className="overflow-hidden" aria-labelledby="attention-title">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <h2 id="attention-title" className="font-extrabold text-[#071b4a]">
            {t("workflow.attentionQueue")}
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            {t("workflow.deidentified")}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <label className="sr-only" htmlFor="workflow-type">
            {t("workflow.type")}
          </label>
          <select
            id="workflow-type"
            value={type}
            onChange={(event) => setType(event.target.value)}
            className="min-h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700"
          >
            <option value="all">{t("workflow.allWorkflows")}</option>
            {types.map((value) => (
              <option key={value} value={value}>
                {t(`workflow.type.${value}`)}
              </option>
            ))}
          </select>
          <label className="sr-only" htmlFor="workflow-priority">
            {t("workflow.priority")}
          </label>
          <select
            id="workflow-priority"
            value={priority}
            onChange={(event) => setPriority(event.target.value)}
            className="min-h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700"
          >
            <option value="all">{t("workflow.allPriorities")}</option>
            <option value="high">{t("workflow.priority.high")}</option>
            <option value="medium">{t("workflow.priority.medium")}</option>
            <option value="low">{t("workflow.priority.low")}</option>
          </select>
        </div>
      </div>
      {!visible.length ? (
        <div className="p-5">
          <EmptyState
            compact
            title={t("workflow.queueEmpty")}
            description={t("workflow.queueEmptyDescription")}
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm rtl:text-right">
            <thead className="bg-slate-50 text-[11px] font-bold uppercase tracking-[.08em] text-slate-500">
              <tr>
                <th className="px-6 py-3">{t("workflow.workflow")}</th>
                <th className="px-4 py-3">{t("workflow.reference")}</th>
                <th className="px-4 py-3">{t("workflow.owner")}</th>
                <th className="px-4 py-3">{t("workflow.age")}</th>
                <th className="px-4 py-3">{t("workflow.priority")}</th>
                <th className="px-6 py-3 text-right rtl:text-left">
                  {t("workflow.action")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {visible.map((item) => (
                <tr key={item.id} className="transition hover:bg-blue-50/40">
                  <td className="px-6 py-4 font-bold text-[#071b4a]">
                    {t(`workflow.type.${item.type}`)}
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-600">
                    {item.subject_ref}
                  </td>
                  <td className="px-4 py-4 text-slate-600">{item.owner}</td>
                  <td className="px-4 py-4 text-slate-600">
                    {formatAge(item.age_seconds, locale)}
                  </td>
                  <td className="px-4 py-4">
                    <Badge
                      tone={
                        item.priority === "high"
                          ? "red"
                          : item.priority === "medium"
                            ? "amber"
                            : "slate"
                      }
                    >
                      {t(`workflow.priority.${item.priority}`)}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-right rtl:text-left">
                    <button
                      type="button"
                      onClick={() => onReview(item)}
                      className="inline-flex items-center gap-1 text-xs font-extrabold text-blue-700 hover:text-blue-900"
                    >
                      {t("workflow.review")}
                      <ChevronRight className="rtl:rotate-180" size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

function AuditLog({ items, t, locale }) {
  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 sm:px-6">
        <div>
          <h2 className="font-extrabold text-[#071b4a]">
            {t("workflow.recentAudit")}
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            {t("workflow.auditDescription")}
          </p>
        </div>
        <ShieldCheck className="text-emerald-700" size={20} />
      </div>
      {!items?.length ? (
        <div className="p-5">
          <EmptyState compact title={t("workflow.noAudit")} />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] text-left text-sm rtl:text-right">
            <thead className="bg-slate-50 text-[11px] font-bold uppercase tracking-[.08em] text-slate-500">
              <tr>
                <th className="px-6 py-3">{t("workflow.actor")}</th>
                <th className="px-4 py-3">{t("workflow.event")}</th>
                <th className="px-4 py-3">{t("workflow.resource")}</th>
                <th className="px-6 py-3">{t("workflow.when")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4 font-mono text-xs text-slate-600">
                    {item.actor_ref}
                  </td>
                  <td className="px-4 py-4 font-bold text-[#071b4a]">
                    {item.action}
                  </td>
                  <td className="px-4 py-4 text-slate-600">
                    {item.resource_ref}
                  </td>
                  <td className="px-6 py-4 text-slate-600">
                    {formatDateTime(item.created_at, locale)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

export default function SuperAdminWorkflowDashboard({ onNavigate }) {
  const { t, locale } = useLocale();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await getAdminWorkflow());
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, t("workflow.loadError")));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);

  function reviewItem(item) {
    if (item.type === "password_recovery") {
      const userId = item.action_url?.split("/").filter(Boolean).at(-1);
      onNavigate?.("adminUsers", userId ? { user: userId } : undefined);
      return;
    }
    setSelected(item);
  }

  return (
    <main className="mx-auto w-full max-w-[1500px] px-4 py-7 sm:px-6 lg:px-8">
      <PageHeader
        eyebrow={t("workflow.eyebrow")}
        title={t("workflow.title")}
        description={t("workflow.description")}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={load} disabled={loading}>
              <RefreshCw className={loading ? "animate-spin" : ""} size={16} />
              {t("workflow.refresh")}
            </Button>
            <Button onClick={() => onNavigate?.("adminUsers")}>
              <UsersRound size={16} />
              {t("workflow.manageUsers")}
            </Button>
          </div>
        }
      />
      {error ? (
        <Alert title={t("workflow.loadError")} className="mb-5">
          <button className="font-bold underline" onClick={load}>
            {t("workflow.tryAgain")}
          </button>
        </Alert>
      ) : null}
      {loading && !data ? (
        <div className="grid min-h-[420px] place-items-center">
          <LoadingSpinner label={t("workflow.loading")} />
        </div>
      ) : null}
      {data ? (
        <div className="space-y-5">
          <MetricStrip metrics={data.metrics} t={t} />
          <WorkflowRail stages={data.stages} t={t} />
          <div className="grid min-w-0 items-start gap-5 xl:grid-cols-[minmax(0,1fr)_310px]">
            <div className="min-w-0 space-y-4">
              <AttentionQueue
                items={data.attention_queue}
                t={t}
                locale={locale}
                onReview={reviewItem}
              />
              {selected ? (
                <Alert
                  tone="info"
                  title={`${t("workflow.reviewing")} ${selected.subject_ref}`}
                >
                  <span>
                    {t(`workflow.type.${selected.type}`)} · {selected.owner} ·{" "}
                    {t(`workflow.priority.${selected.priority}`)}
                  </span>
                  <button
                    type="button"
                    onClick={() => setSelected(null)}
                    className="ms-3 font-bold underline"
                  >
                    {t("common.close")}
                  </button>
                </Alert>
              ) : null}
            </div>
            <div className="min-w-0">
              <SummaryRail data={data} t={t} locale={locale} />
            </div>
          </div>
          <AuditLog items={data.recent_audit} t={t} locale={locale} />
          <p className="flex items-center justify-end gap-2 text-xs text-slate-500">
            <Clock3 size={14} />
            {t("workflow.generatedAt")}{" "}
            {formatDateTime(data.generated_at, locale)} · Africa/Cairo
          </p>
        </div>
      ) : null}
    </main>
  );
}

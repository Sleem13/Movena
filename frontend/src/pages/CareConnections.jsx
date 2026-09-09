import { useCallback, useEffect, useRef, useState } from "react";
import {
  Check,
  Link2Off,
  Mail,
  RefreshCw,
  Search,
  ShieldCheck,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import { useAuth } from "../context/AuthContext.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import {
  Alert,
  Badge,
  Button,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import {
  connectionsApi as api,
  pendingInvitation,
  clearInvitation,
} from "../services/connectionsApi.js";

const copy = {
  en: {
    team: "My care team",
    connections: "Care connections",
    admin: "Patient assignments",
    active: "Active",
    pending: "Invitations",
    ended: "Ended",
    email: "Patient email",
    invite: "Invite patient",
    resend: "Resend",
    cancel: "Cancel",
    accept: "Accept connection",
    decline: "Decline",
    end: "End connection",
    empty: "No connected therapist",
    emptyTherapist: "No connections yet",
    independent:
      "Your exercises, movement checks, and personal progress remain available.",
    sharing:
      "Connecting gives this therapist access to your full care record, including earlier results and plans. You can end the connection at any time.",
    endWarning:
      "This therapist will lose access immediately. Your records and plans will be kept. Contact the clinic about any upcoming appointments.",
    reason: "Reason",
    confirm: "Confirm",
    search: "Search patients",
    therapistSearch: "Search therapists",
    unassigned: "Unassigned only",
    patient: "Patient",
    therapist: "Therapist",
    choose: "Select",
    assign: "Assign therapist",
    loading: "Loading care connections",
    retry: "Retry",
    success: "Changes saved.",
    failed: "Unable to complete the request. Please try again.",
    noItems: "Nothing here yet.",
    sent: "Invitation sent.",
    deliveryFailed:
      "The invitation was saved, but email delivery failed. Use Resend to try again.",
    login: "Log in to review your invitation",
    loginButton: "Log in",
    denied:
      "This workspace is available to patients, therapists, and administrators.",
    pendingStatus: "Pending",
    accepted: "Accepted",
    declined: "Declined",
    cancelled: "Cancelled",
    expired: "Expired",
    sentStatus: "Email sent",
    failedStatus: "Email failed",
    legacy: "Existing connection",
    appointmentReview: "Upcoming appointments need review",
    invitation: "Patient accepted",
    adminSource: "Assigned by administrator",
    open: "Open patient",
    verify: "Verify your email to view and accept invitations.",
    dismiss: "Dismiss invitation link",
  },
  ar: {
    team: "فريق رعايتي",
    connections: "روابط الرعاية",
    admin: "تعيين المرضى",
    active: "نشطة",
    pending: "الدعوات",
    ended: "منتهية",
    email: "بريد المريض الإلكتروني",
    invite: "دعوة مريض",
    resend: "إعادة الإرسال",
    cancel: "إلغاء",
    accept: "قبول الارتباط",
    decline: "رفض",
    end: "إنهاء الارتباط",
    empty: "لا يوجد معالج مرتبط",
    emptyTherapist: "لا توجد روابط بعد",
    independent: "تبقى التمارين وفحوص الحركة والتقدم الشخصي متاحة لك.",
    sharing:
      "يمنح الارتباط المعالج حق الاطلاع على سجل رعايتك الكامل، بما فيه النتائج والخطط السابقة. يمكنك إنهاء الارتباط في أي وقت.",
    endWarning:
      "سيفقد المعالج حق الوصول فوراً. ستبقى سجلاتك وخططك محفوظة. تواصل مع العيادة بخصوص المواعيد القادمة.",
    reason: "السبب",
    confirm: "تأكيد",
    search: "البحث عن مرضى",
    therapistSearch: "البحث عن معالجين",
    unassigned: "غير المعينين فقط",
    patient: "المريض",
    therapist: "المعالج",
    choose: "اختر",
    assign: "تعيين معالج",
    loading: "جار تحميل روابط الرعاية",
    retry: "إعادة المحاولة",
    success: "تم حفظ التغييرات.",
    failed: "تعذر إكمال الطلب. حاول مرة أخرى.",
    noItems: "لا توجد عناصر بعد.",
    sent: "تم إرسال الدعوة.",
    deliveryFailed:
      "تم حفظ الدعوة لكن تعذر إرسال البريد. استخدم إعادة الإرسال للمحاولة مجدداً.",
    login: "سجل الدخول لمراجعة دعوتك",
    loginButton: "تسجيل الدخول",
    denied: "هذه المساحة متاحة للمرضى والمعالجين والمسؤولين.",
    pendingStatus: "قيد الانتظار",
    accepted: "مقبولة",
    declined: "مرفوضة",
    cancelled: "ملغاة",
    expired: "منتهية الصلاحية",
    sentStatus: "تم إرسال البريد",
    failedStatus: "فشل البريد",
    legacy: "ارتباط سابق",
    appointmentReview: "المواعيد القادمة تحتاج إلى مراجعة",
    invitation: "قبله المريض",
    adminSource: "عينه المسؤول",
    open: "فتح المريض",
    verify: "تحقق من بريدك لعرض الدعوات وقبولها.",
    dismiss: "تجاهل رابط الدعوة",
  },
};

function ConfirmDialog({
  title,
  children,
  onCancel,
  onConfirm,
  busy,
  labels,
  requireReason,
  error,
}) {
  const ref = useRef(null);
  const triggerRef = useRef(document.activeElement);
  const [reason, setReason] = useState("");
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => {
      dialog.close();
      if (triggerRef.current?.isConnected) triggerRef.current.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className="connection-dialog"
      aria-labelledby="connection-confirm-title"
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) onCancel();
      }}
    >
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onConfirm(reason);
        }}
      >
        <h2 id="connection-confirm-title" className="text-xl font-bold">
          {title}
        </h2>
        <p className="my-4 text-sm leading-6">{children}</p>
        {error && <Alert>{error}</Alert>}
        {requireReason && (
          <label className="grid gap-2 text-sm">
            {labels.reason}
            <textarea
              required
              maxLength={1000}
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            />
          </label>
        )}
        <div className="mt-5 flex flex-wrap justify-end gap-2">
          <Button
            type="button"
            variant="secondary"
            disabled={busy}
            onClick={onCancel}
          >
            {labels.cancel}
          </Button>
          <Button disabled={busy || (requireReason && !reason.trim())}>
            <Check size={17} />
            {labels.confirm}
          </Button>
        </div>
      </form>
    </dialog>
  );
}

export default function CareConnections({ onNavigate }) {
  const { user } = useAuth();
  const { locale } = useLocale();
  const c = copy[locale] || copy.en;
  const admin = ["admin", "super_admin"].includes(user?.role);
  const patient = user?.role === "patient";
  const allowed = admin || patient || user?.role === "therapist";
  const [token, setToken] = useState(pendingInvitation);
  const [tokenInvitation, setTokenInvitation] = useState(null);
  const [rows, setRows] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [options, setOptions] = useState({ patients: [], therapists: [] });
  const [tab, setTab] = useState(token ? "pending" : "active");
  const [email, setEmail] = useState("");
  const [query, setQuery] = useState("");
  const [therapistQuery, setTherapistQuery] = useState("");
  const [unassigned, setUnassigned] = useState(false);
  const [patientId, setPatientId] = useState("");
  const [therapistId, setTherapistId] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [dialog, setDialog] = useState(null);
  const load = useCallback(async () => {
    const [connections, invites] = await Promise.all([
      api.list(),
      admin || (patient && !user.is_verified)
        ? Promise.resolve([])
        : api.invitations(),
    ]);
    setRows(connections);
    setInvitations(invites);
  }, [admin, patient, user?.is_verified]);
  useEffect(() => {
    if (!allowed) {
      setLoading(false);
      return;
    }
    let current = true;
    setLoading(true);
    load()
      .catch(() => current && setError(c.failed))
      .finally(() => current && setLoading(false));
    return () => {
      current = false;
    };
  }, [allowed, load, c.failed]);
  useEffect(() => {
    if (!admin) return;
    let current = true;
    const timer = setTimeout(
      () =>
        api
          .options(query, unassigned)
          .then((result) => {
            if (current) setOptions(result);
          })
          .catch(() => current && setError(c.failed)),
      200,
    );
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [admin, query, unassigned, c.failed]);
  useEffect(() => {
    if (!token || !patient || !user.is_verified) return;
    let current = true;
    api
      .lookup(token)
      .then((result) => {
        if (current) {
          setTokenInvitation(result);
          setTab("pending");
        }
      })
      .catch(() => current && setError(c.failed));
    return () => {
      current = false;
    };
  }, [token, patient, user?.is_verified, c.failed]);
  async function run(action) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await action();
      setDialog(null);
      setNotice(
        result?.delivery_status === "failed" ? c.deliveryFailed : c.success,
      );
      await load();
      if (admin) setOptions(await api.options(query, unassigned));
    } catch (err) {
      setError(
        locale === "en" ? err.response?.data?.message || c.failed : c.failed,
      );
    } finally {
      setBusy(false);
    }
  }
  const dismissToken = () => {
    clearInvitation();
    setToken(null);
    setTokenInvitation(null);
  };
  if (!user)
    return (
      <main className="mx-auto max-w-3xl px-5 py-12">
        <h1 className="mb-5 text-2xl font-bold">{c.login}</h1>
        <Button onClick={() => onNavigate("login")}>{c.loginButton}</Button>
      </main>
    );
  if (!allowed)
    return (
      <main className="p-6">
        <Alert>{c.denied}</Alert>
      </main>
    );
  const visible = rows.filter(
    (row) =>
      row.status === tab &&
      (!query ||
        [row.patient_name, row.therapist_name].some((name) =>
          name.toLowerCase().includes(query.toLowerCase()),
        )),
  );
  const statusLabel = (status) =>
    c[status === "pending" ? "pendingStatus" : status] || status;
  const items = tokenInvitation
    ? [
        tokenInvitation,
        ...invitations.filter(
          (item) => item.invitation_id !== tokenInvitation.invitation_id,
        ),
      ]
    : invitations;
  return (
    <main
      className="care-connections mx-auto w-full max-w-7xl px-5 py-7 lg:px-7"
      aria-busy={busy || loading}
    >
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-3xl font-bold">
          {admin ? c.admin : patient ? c.team : c.connections}
        </h1>
        <Users size={26} aria-hidden="true" />
      </header>
      {error && (
        <Alert className="mb-4">
          {error}
          <Button variant="ghost" disabled={busy} onClick={() => run(load)}>
            <RefreshCw size={16} />
            {c.retry}
          </Button>
        </Alert>
      )}
      {notice && (
        <p
          role="status"
          className="mb-4 border-s-4 border-teal-600 bg-teal-50 p-3 text-sm text-teal-900"
        >
          {notice}
        </p>
      )}
      {patient && !user.is_verified && (
        <Alert tone="warning" className="mb-4">
          {c.verify}
          <Button variant="ghost" onClick={() => onNavigate("verifyEmail")}>
            {c.confirm}
          </Button>
        </Alert>
      )}
      {token && (
        <Button variant="ghost" onClick={dismissToken}>
          <X size={16} />
          {c.dismiss}
        </Button>
      )}
      {admin && (
        <form
          className="connection-admin-form mb-6 border-b pb-6"
          onSubmit={(event) => {
            event.preventDefault();
            run(() => api.assign(patientId, therapistId, reason));
          }}
        >
          <label>
            {c.search}
            <span className="connection-search">
              <Search size={17} />
              <input
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPatientId("");
                }}
              />
            </span>
          </label>
          <label className="connection-checkbox">
            <input
              type="checkbox"
              checked={unassigned}
              onChange={(event) => {
                setUnassigned(event.target.checked);
                setPatientId("");
              }}
            />
            {c.unassigned}
          </label>
          <label>
            {c.patient}
            <select
              aria-label={c.patient}
              required
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
            >
              <option value="">{c.choose}</option>
              {options.patients.map((p) => (
                <option key={p.patient_id} value={p.patient_id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {c.therapistSearch}
            <input
              value={therapistQuery}
              onChange={(event) => {
                setTherapistQuery(event.target.value);
                setTherapistId("");
              }}
            />
          </label>
          <label>
            {c.therapist}
            <select
              aria-label={c.therapist}
              required
              value={therapistId}
              onChange={(event) => setTherapistId(event.target.value)}
            >
              <option value="">{c.choose}</option>
              {options.therapists
                .filter((t) =>
                  t.name.toLowerCase().includes(therapistQuery.toLowerCase()),
                )
                .map((t) => (
                  <option key={t.user_id} value={t.user_id}>
                    {t.name}
                  </option>
                ))}
            </select>
          </label>
          <label>
            {c.reason}
            <input
              required
              maxLength={1000}
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            />
          </label>
          <Button disabled={busy || !reason.trim()}>
            <UserPlus size={18} />
            {c.assign}
          </Button>
        </form>
      )}
      {user.role === "therapist" && (
        <form
          className="mb-6 flex flex-wrap items-end gap-3 border-b pb-6"
          onSubmit={(event) => {
            event.preventDefault();
            run(async () => {
              const result = await api.invite(email);
              setEmail("");
              setTab("pending");
              return result;
            });
          }}
        >
          <label className="grid min-w-0 flex-1 gap-2 text-sm">
            {c.email}
            <input
              required
              type="email"
              maxLength={320}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <Button disabled={busy}>
            <Mail size={18} />
            {c.invite}
          </Button>
        </form>
      )}
      <div
        className="mb-5 flex flex-wrap gap-2 border-b"
        role="tablist"
        aria-label={patient ? c.team : c.connections}
        onKeyDown={(event) => {
          const tabs = [
            ...event.currentTarget.querySelectorAll('[role="tab"]'),
          ];
          const index = tabs.indexOf(document.activeElement);
          const direction = locale === "ar" ? -1 : 1;
          const next =
            event.key === "Home"
              ? 0
              : event.key === "End"
                ? tabs.length - 1
                : event.key === "ArrowRight"
                  ? (index + direction + tabs.length) % tabs.length
                  : event.key === "ArrowLeft"
                    ? (index - direction + tabs.length) % tabs.length
                    : null;
          if (next !== null) {
            event.preventDefault();
            tabs[next].focus();
            tabs[next].click();
          }
        }}
      >
        {["active", ...(!admin ? ["pending"] : []), "ended"].map((value) => (
          <button
            type="button"
            role="tab"
            key={value}
            tabIndex={tab === value ? 0 : -1}
            aria-selected={tab === value}
            aria-controls="connection-panel"
            id={`connection-tab-${value}`}
            className={`connection-tab ${tab === value ? "is-active" : ""}`}
            onClick={() => setTab(value)}
          >
            {c[value]}
          </button>
        ))}
      </div>
      {loading ? (
        <LoadingSpinner label={c.loading} />
      ) : (
        <section
          id="connection-panel"
          role="tabpanel"
          aria-labelledby={`connection-tab-${tab}`}
        >
          {tab === "pending" ? (
            <div className="divide-y">
              {!items.length && <p className="py-8 text-sm">{c.noItems}</p>}
              {items.map((item) => (
                <article key={item.invitation_id} className="connection-row">
                  <div className="min-w-0">
                    <h2 className="break-words font-semibold">
                      {patient ? item.therapist_name : item.email}
                    </h2>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <Badge tone="slate">{statusLabel(item.status)}</Badge>
                      {!patient && (
                        <Badge
                          tone={
                            item.delivery_status === "failed" ? "amber" : "teal"
                          }
                        >
                          {item.delivery_status === "sent"
                            ? c.sentStatus
                            : item.delivery_status === "failed"
                              ? c.failedStatus
                              : c.pendingStatus}
                        </Badge>
                      )}
                    </div>
                    <p className="mt-2 text-xs">
                      {new Date(item.expires_at).toLocaleDateString(locale)}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {patient && item.status === "pending" && (
                      <>
                        <Button
                          disabled={busy}
                          onClick={() => setDialog({ type: "accept", item })}
                        >
                          <Check size={16} />
                          {c.accept}
                        </Button>
                        <Button
                          variant="secondary"
                          disabled={busy}
                          onClick={() => setDialog({ type: "decline", item })}
                        >
                          <X size={16} />
                          {c.decline}
                        </Button>
                      </>
                    )}
                    {!patient && item.status !== "accepted" && (
                      <Button
                        variant="secondary"
                        disabled={busy}
                        onClick={() =>
                          run(() => api.manage(item.invitation_id, "resend"))
                        }
                      >
                        <RefreshCw size={16} />
                        {c.resend}
                      </Button>
                    )}
                    {!patient && item.status === "pending" && (
                      <Button
                        variant="ghost"
                        disabled={busy}
                        onClick={() =>
                          run(() => api.manage(item.invitation_id, "cancel"))
                        }
                      >
                        <X size={16} />
                        {c.cancel}
                      </Button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="divide-y">
              {!visible.length && (
                <div className="py-9">
                  <Users className="mb-3 text-blue-600" size={32} />
                  <h2 className="font-semibold">
                    {patient && tab === "active" ? c.empty : c.emptyTherapist}
                  </h2>
                  {patient && <p className="mt-2 text-sm">{c.independent}</p>}
                </div>
              )}
              {visible.map((row) => (
                <article key={row.assignment_id} className="connection-row">
                  <div className="min-w-0">
                    <h2 className="break-words font-semibold">
                      {patient ? row.therapist_name : row.patient_name}
                    </h2>
                    {admin && (
                      <p className="mt-1 text-sm">{row.therapist_name}</p>
                    )}
                    <p className="my-2 text-xs">
                      {new Date(
                        row.ended_at || row.assigned_at,
                      ).toLocaleDateString(locale)}
                    </p>
                    <Badge tone={tab === "active" ? "teal" : "slate"}>
                      {row.source === "legacy"
                        ? c.legacy
                        : row.source === "admin"
                          ? c.adminSource
                          : c.invitation}
                    </Badge>
                    {admin && row.appointments_needing_review > 0 && <p className="mt-2 text-sm text-amber-700">{c.appointmentReview}: {row.appointments_needing_review}</p>}
                  </div>
                  {tab === "active" && (
                    <div className="flex flex-wrap gap-2">
                      {!patient && (
                        <Button
                          variant="secondary"
                          onClick={() => {
                            window.history.pushState(
                              {},
                              "",
                              `/therapist/patients/${row.patient_id}`,
                            );
                            window.dispatchEvent(new PopStateEvent("popstate"));
                          }}
                        >
                          {c.open}
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        disabled={busy}
                        onClick={() => setDialog({ type: "end", row })}
                      >
                        <Link2Off size={16} />
                        {c.end}
                      </Button>
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      )}
      {dialog && (
        <ConfirmDialog
          key={dialog.item?.invitation_id || dialog.row?.assignment_id}
          title={c[dialog.type]}
          labels={c}
          error={error}
          busy={busy}
          requireReason={admin}
          onCancel={() => setDialog(null)}
          onConfirm={(endReason) =>
            run(async () => {
              if (dialog.type === "end")
                return api.end(dialog.row.assignment_id, endReason);
              const result = await api.respond(
                dialog.item.invitation_id,
                dialog.type,
                dialog.item.invitation_id === tokenInvitation?.invitation_id
                  ? token
                  : undefined,
              );
              dismissToken();
              return result;
            })
          }
        >
          {dialog.type === "end" ? c.endWarning : c.sharing}
        </ConfirmDialog>
      )}
    </main>
  );
}

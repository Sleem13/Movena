import { useEffect, useState } from "react";
import {
  Ban,
  CheckCircle2,
  ChevronRight,
  KeyRound,
  PauseCircle,
  Plus,
  Search,
  ShieldCheck,
  Trash2,
  UserCog,
  UserPlus,
  Users,
  X,
} from "lucide-react";

import PasswordInput from "../components/auth/PasswordInput.jsx";
import Select from "../components/common/Select.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import {
  Alert,
  Badge,
  Button,
  EmptyState,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import {
  deleteManagedUser,
  createManagedUser,
  getManagedUser,
  listManagedUsers,
  resetManagedUserPassword,
  updateManagedUserRole,
  updateManagedUserStatus,
} from "../services/api.js";
import { getApiErrorMessage } from "../utils/requestErrors.js";

const ROLES = ["admin", "therapist", "patient", "researcher_demo"];
const STATUS_TONES = { active: "teal", paused: "amber", suspended: "red" };

function readableDate(value) {
  return value ? new Date(value).toLocaleString() : "Never";
}

function initials(user) {
  const source = user?.full_name || user?.email || "User";
  return source
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function DetailRow({ label, value }) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)] gap-4 py-3 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium text-clinical-ink rtl:text-left">
        {value}
      </span>
    </div>
  );
}

function UserDetail({ user, reason, onReasonChange, busy, onAction }) {
  const [password, setPassword] = useState("");
  if (!user)
    return (
      <div className="grid min-h-[34rem] place-items-center p-6">
        <EmptyState
          title="Select an account"
          description="Choose a user to review identity, access, and account activity."
          icon={UserCog}
          compact
        />
      </div>
    );
  const protectedAccount = user.is_protected || user.role === "super_admin";
  const actionDisabled = busy || reason.trim().length < 3;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 p-5 sm:p-6">
        <div className="flex min-w-0 items-center gap-3.5">
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-clinical-ink text-sm font-bold text-white">
            {initials(user)}
          </span>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="truncate text-lg font-bold text-clinical-ink">
                {user.full_name || "Unnamed user"}
              </h2>
              {protectedAccount ? (
                <Badge tone="blue">
                  <ShieldCheck size={12} className="me-1" />
                  Protected
                </Badge>
              ) : null}
            </div>
            <p className="mt-1 truncate text-sm text-slate-500">{user.email}</p>
          </div>
        </div>
        <Badge tone={STATUS_TONES[user.account_status] || "slate"}>
          {user.account_status}
        </Badge>
      </div>

      <div className="divide-y divide-slate-100 px-5 sm:px-6">
        <DetailRow label="Role" value={user.role} />
        <DetailRow label="Username" value={user.username || "Not assigned"} />
        <DetailRow
          label="Account created"
          value={readableDate(user.created_at)}
        />
        <DetailRow
          label="Last session"
          value={readableDate(user.last_session_at)}
        />
        <DetailRow label="Saved sessions" value={user.session_count} />
        <DetailRow
          label="Email verified"
          value={user.is_verified ? "Yes" : "No"}
        />
      </div>

      <div className="border-t border-slate-200 p-5 sm:p-6">
        {protectedAccount ? (
          <Alert tone="info" title="Protected root account">
            This account is immutable in the management API. Provisioning
            credentials are required to change it.
          </Alert>
        ) : (
          <div className="space-y-5">
            <label className="block text-sm font-semibold text-slate-700">
              Reason for change
              <textarea
                value={reason}
                onChange={(event) => onReasonChange(event.target.value)}
                rows={2}
                className="mt-2 w-full border bg-white px-3 py-2 text-sm"
                placeholder="Required for the audit log"
              />
              <span className="mt-1.5 block text-xs font-normal text-slate-500">
                Explain why this access change is needed.
              </span>
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="text-sm font-semibold text-slate-700">
                <span>Role</span>
                <Select
                  className="mt-2"
                  ariaLabel="Role"
                  value={user.role}
                  disabled={actionDisabled}
                  onChange={(role) => onAction("role", role)}
                  options={ROLES.map((role) => ({ value: role, label: role }))}
                />
              </div>
              <div className="text-sm font-semibold text-slate-700">
                <span>Account status</span>
                <div className="mt-2 grid grid-cols-3 gap-1 rounded-xl bg-slate-100 p-1">
                  <button
                    className={`min-h-9 rounded-lg text-xs font-semibold transition ${user.account_status === "active" ? "bg-white text-teal-700 shadow-sm" : "text-slate-600 hover:bg-white/70"}`}
                    disabled={
                      actionDisabled || user.account_status === "active"
                    }
                    onClick={() => onAction("status", "active")}
                  >
                    <CheckCircle2 className="me-1 inline" size={14} />
                    Active
                  </button>
                  <button
                    className={`min-h-9 rounded-lg text-xs font-semibold transition ${user.account_status === "paused" ? "bg-white text-amber-700 shadow-sm" : "text-slate-600 hover:bg-white/70"}`}
                    disabled={
                      actionDisabled || user.account_status === "paused"
                    }
                    onClick={() => onAction("status", "paused")}
                  >
                    <PauseCircle className="me-1 inline" size={14} />
                    Paused
                  </button>
                  <button
                    className={`min-h-9 rounded-lg text-xs font-semibold transition ${user.account_status === "suspended" ? "bg-white text-red-700 shadow-sm" : "text-slate-600 hover:bg-white/70"}`}
                    disabled={
                      actionDisabled || user.account_status === "suspended"
                    }
                    onClick={() => onAction("status", "suspended")}
                  >
                    <Ban className="me-1 inline" size={14} />
                    Suspended
                  </button>
                </div>
              </div>
            </div>
            <div className="border-t border-slate-200 pt-5">
              <PasswordInput
                label="Set a new password"
                name="managed-password"
                autoComplete="new-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={8}
                placeholder="At least 8 characters"
              />
              <Button
                className="mt-3"
                disabled={actionDisabled || password.length < 8}
                onClick={async () => {
                  await onAction("password", password);
                  setPassword("");
                }}
              >
                <KeyRound size={16} />
                Change password
              </Button>
            </div>
            <div className="border-t border-red-100 pt-5">
              <p className="text-sm font-semibold text-clinical-ink">
                Danger zone
              </p>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                Permanently remove this account and its access. Existing
                confirmation remains required.
              </p>
              <Button
                variant="ghost"
                className="mt-3 border border-red-200 text-red-700 hover:bg-red-50 hover:text-red-800"
                disabled={actionDisabled}
                onClick={() => onAction("delete")}
              >
                <Trash2 size={16} />
                Delete account
              </Button>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-slate-200 px-5 sm:px-6">
        <details className="group border-b border-slate-200 py-4">
          <summary className="flex cursor-pointer list-none items-center justify-between text-sm font-semibold text-clinical-ink">
            Recent analysis data{" "}
            <ChevronRight
              size={17}
              className="text-slate-400 transition group-open:rotate-90 rtl:rotate-180"
            />
          </summary>
          {user.sessions?.length ? (
            <div className="mt-3 space-y-2">
              {user.sessions.map((session) => (
                <div
                  key={session.session_id}
                  className="rounded-xl bg-slate-50 px-3 py-2.5 text-sm"
                >
                  <span className="font-semibold text-slate-700">
                    {session.exercise_display_name}
                  </span>
                  <span className="ms-2 text-slate-400">
                    {readableDate(session.created_at)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-2 text-sm text-slate-500">
              No analysis sessions belong to this account.
            </p>
          )}
        </details>
        <details className="group py-4">
          <summary className="flex cursor-pointer list-none items-center justify-between text-sm font-semibold text-clinical-ink">
            Consents{" "}
            <ChevronRight
              size={17}
              className="text-slate-400 transition group-open:rotate-90 rtl:rotate-180"
            />
          </summary>
          <p className="mt-2 text-sm text-slate-500">
            {user.consents?.length
              ? `${user.consents.length} consent record(s)`
              : "No consent records."}
          </p>
        </details>
      </div>
    </div>
  );
}

export default function SuperAdminDashboard() {
  const initialUserId = new URLSearchParams(window.location.search).get("user");
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [createRole, setCreateRole] = useState("patient");
  const [creating, setCreating] = useState(false);

  async function loadUsers(query = search, preferredUserId = null) {
    setLoading(true);
    setError("");
    try {
      const items = await listManagedUsers(query ? { search: query } : {});
      setUsers(items);
      if (!items.length) setSelected(null);
      else if (
        preferredUserId &&
        items.some((item) => item.user_id === preferredUserId)
      ) {
        setSelected(await getManagedUser(preferredUserId));
        setReason("");
      } else if (
        !selected ||
        !items.some((item) => item.user_id === selected.user_id)
      ) {
        setSelected(await getManagedUser(items[0].user_id));
        setReason("");
      }
    } catch (requestError) {
      setError(
        getApiErrorMessage(requestError, "User accounts could not be loaded."),
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUsers("", initialUserId);
  }, []);

  async function selectUser(userId) {
    setError("");
    setNotice("");
    setReason("");
    try {
      setSelected(await getManagedUser(userId));
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          "Account details could not be loaded.",
        ),
      );
    }
  }

  async function performAction(kind, value) {
    if (reason.trim().length < 3) return;
    if (
      kind === "delete" &&
      !window.confirm(`Permanently delete ${selected.email}?`)
    )
      return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      let result;
      if (kind === "status")
        result = await updateManagedUserStatus(selected.user_id, value, reason);
      if (kind === "role")
        result = await updateManagedUserRole(selected.user_id, value, reason);
      if (kind === "password")
        result = await resetManagedUserPassword(
          selected.user_id,
          value,
          reason,
        );
      if (kind === "delete")
        result = await deleteManagedUser(selected.user_id, reason);
      setNotice(result.message);
      setReason("");
      await loadUsers();
      if (kind === "delete") setSelected(null);
      else setSelected(await getManagedUser(selected.user_id));
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The account action failed."));
    } finally {
      setBusy(false);
    }
  }

  async function createAccount(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setCreating(true);
    setError("");
    setNotice("");
    try {
      const created = await createManagedUser({
        full_name: data.get("full_name"),
        username: data.get("username"),
        email: data.get("email"),
        password: data.get("password"),
        role: createRole,
      });
      setNotice(
        `Account created for ${created.full_name || created.username}. It is active and ready to log in.`,
      );
      setCreateOpen(false);
      setCreateRole("patient");
      form.reset();
      await loadUsers("");
      setSelected(await getManagedUser(created.user_id));
    } catch (requestError) {
      setError(
        getApiErrorMessage(requestError, "The account could not be created."),
      );
    } finally {
      setCreating(false);
    }
  }

  return (
    <main>
      <PageHeader
        eyebrow="Protected administration"
        title="User Administration"
        description="Create user profiles and manage identity, roles, passwords, status, and application access. Every administrative change is written to the audit log."
        actions={
          <Button
            type="button"
            onClick={() => setCreateOpen((value) => !value)}
          >
            {createOpen ? <X size={17} /> : <Plus size={17} />}
            {createOpen ? "Cancel" : "Create user"}
          </Button>
        }
      />
      {error ? <Alert className="mb-5">{error}</Alert> : null}
      {notice ? (
        <Alert tone="info" className="mb-5">
          {notice}
        </Alert>
      ) : null}
      {createOpen ? (
        <section
          className="mb-5 rounded-[14px] border border-blue-200 bg-white p-5 shadow-panel"
          aria-labelledby="create-user-heading"
        >
          <div className="flex items-start gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-700">
              <UserPlus size={19} />
            </span>
            <div>
              <h2
                id="create-user-heading"
                className="text-lg font-bold text-clinical-ink"
              >
                Create a platform user
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                The account is activated immediately; no email verification is
                required while managed access is enabled.
              </p>
            </div>
          </div>
          <form
            className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5"
            onSubmit={createAccount}
          >
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              Full name
              <input
                name="full_name"
                required
                maxLength={120}
                className="min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-clinical-ink"
                placeholder="Dr Jane Smith"
              />
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              Username
              <input
                name="username"
                required
                minLength={3}
                maxLength={64}
                pattern="[A-Za-z0-9._-]+"
                className="min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-clinical-ink"
                placeholder="jane.smith"
              />
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              Email
              <input
                name="email"
                type="email"
                required
                maxLength={320}
                className="min-h-11 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-clinical-ink"
                placeholder="jane@example.com"
              />
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              Role
              <Select
                ariaLabel="New user role"
                value={createRole}
                onChange={setCreateRole}
                options={ROLES.map((role) => ({
                  value: role,
                  label: role.replaceAll("_", " "),
                }))}
              />
            </label>
            <div className="grid gap-2 text-sm font-semibold text-slate-700">
              <PasswordInput
                label="Temporary password"
                name="password"
                autoComplete="new-password"
                minLength={8}
              />
            </div>
            <div className="flex items-end gap-2 md:col-span-2 xl:col-span-5">
              <Button disabled={creating}>
                {creating ? "Creating account…" : "Create active account"}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setCreateOpen(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </section>
      ) : null}
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(420px,0.85fr)]">
        <section
          className="overflow-hidden rounded-[14px] border border-clinical-line bg-white shadow-panel"
          aria-label="User accounts"
        >
          <form
            className="flex gap-2 border-b border-slate-200 p-4"
            onSubmit={(event) => {
              event.preventDefault();
              loadUsers();
            }}
          >
            <label className="relative flex-1">
              <span className="sr-only">Search users</span>
              <Search
                className="absolute left-3 top-3 text-slate-400"
                size={18}
              />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="min-h-11 w-full border bg-white pl-10 pr-3 text-sm"
                placeholder="Search by name, username, or email"
              />
            </label>
            <Button type="submit" variant="secondary">
              Search
            </Button>
          </form>
          <div className="hidden grid-cols-[minmax(0,1.4fr)_minmax(110px,.6fr)_minmax(100px,.55fr)_minmax(100px,.55fr)_72px] gap-4 border-b border-slate-200 bg-slate-50/70 px-4 py-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 sm:grid">
            <span>User</span>
            <span>Role</span>
            <span>Status</span>
            <span>Verification</span>
            <span>Sessions</span>
          </div>
          <div className="max-h-[44rem] overflow-y-auto [content-visibility:auto]">
            {loading ? (
              <div className="p-10 text-center">
                <LoadingSpinner label="Loading accounts" />
              </div>
            ) : users.length ? (
              users.map((user) => {
                const active = selected?.user_id === user.user_id;
                return (
                  <button
                    key={user.user_id}
                    onClick={() => selectUser(user.user_id)}
                    aria-current={active ? "true" : undefined}
                    className={`grid w-full gap-2 border-b border-slate-100 px-4 py-3.5 text-left transition last:border-b-0 sm:grid-cols-[minmax(0,1.4fr)_minmax(110px,.6fr)_minmax(100px,.55fr)_minmax(100px,.55fr)_72px] sm:items-center sm:gap-4 ${active ? "bg-blue-50 shadow-[inset_3px_0_0_#2563eb]" : "hover:bg-slate-50"}`}
                  >
                    <span className="flex min-w-0 items-center gap-3">
                      <span
                        className={`grid h-9 w-9 shrink-0 place-items-center rounded-full text-xs font-bold ${active ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600"}`}
                      >
                        {initials(user)}
                      </span>
                      <span className="min-w-0">
                        <span className="flex items-center gap-1.5">
                          <span className="block truncate text-sm font-semibold text-clinical-ink">
                            {user.full_name || user.email}
                          </span>
                          {user.is_protected ? (
                            <ShieldCheck
                              size={13}
                              className="shrink-0 text-blue-600"
                            />
                          ) : null}
                        </span>
                        <span className="mt-0.5 block truncate text-xs text-slate-500">
                          {user.email}
                        </span>
                      </span>
                    </span>
                    <span className="text-xs font-medium text-slate-600">
                      {user.role}
                    </span>
                    <span>
                      <Badge
                        tone={STATUS_TONES[user.account_status] || "slate"}
                      >
                        {user.account_status}
                      </Badge>
                    </span>
                    <span>
                      <Badge tone={user.is_verified ? "teal" : "slate"}>
                        {user.is_verified ? "Verified" : "Pending"}
                      </Badge>
                    </span>
                    <span className="text-xs text-slate-500">
                      <Users className="me-1 inline" size={13} />
                      {user.session_count}
                    </span>
                  </button>
                );
              })
            ) : (
              <div className="p-6">
                <EmptyState
                  title="No accounts found"
                  description="Try a different name, username, or email."
                  icon={Users}
                  compact
                />
              </div>
            )}
          </div>
        </section>
        <aside className="overflow-hidden rounded-[14px] border border-clinical-line bg-white shadow-panel xl:sticky xl:top-[88px]">
          <UserDetail
            user={selected}
            reason={reason}
            onReasonChange={setReason}
            busy={busy}
            onAction={performAction}
          />
        </aside>
      </div>
    </main>
  );
}

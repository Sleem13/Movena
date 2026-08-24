import { useEffect, useState } from "react";
import { Ban, KeyRound, PauseCircle, RefreshCw, Search, ShieldCheck, Trash2, UserCog, Users } from "lucide-react";

import { PageHeader } from "../components/layout/AppShell.jsx";
import { Alert, Badge, Button, Card, EmptyState, LoadingSpinner } from "../components/common/UI.jsx";
import {
  deleteManagedUser,
  getManagedUser,
  listManagedUsers,
  resetManagedUserPassword,
  updateManagedUserRole,
  updateManagedUserStatus,
} from "../services/api.js";

const ROLES = ["admin", "therapist", "patient", "researcher_demo"];
const STATUS_TONES = { active: "teal", paused: "amber", suspended: "red" };

function readableDate(value) {
  return value ? new Date(value).toLocaleString() : "Never";
}

function UserDetail({ user, reason, onReasonChange, busy, onAction }) {
  const [password, setPassword] = useState("");
  if (!user) return <EmptyState title="Select an account" description="Choose a user to review account data and management options." icon={UserCog} />;
  const protectedAccount = user.is_protected || user.role === "super_admin";
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-extrabold text-clinical-ink">{user.full_name || "Unnamed user"}</h2>
            {protectedAccount ? <Badge tone="blue"><ShieldCheck size={12} className="mr-1" />Protected</Badge> : null}
          </div>
          <p className="mt-1 text-sm text-slate-500">{user.email}</p>
          <p className="mt-2 text-xs text-slate-400">Created {readableDate(user.created_at)} · Last session {readableDate(user.last_session_at)}</p>
        </div>
        <Badge tone={STATUS_TONES[user.account_status] || "slate"}>{user.account_status}</Badge>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl bg-slate-50 p-4"><p className="text-xs font-bold uppercase tracking-wider text-slate-400">Role</p><p className="mt-1 font-semibold text-slate-700">{user.role}</p></div>
        <div className="rounded-2xl bg-slate-50 p-4"><p className="text-xs font-bold uppercase tracking-wider text-slate-400">Sessions</p><p className="mt-1 font-semibold text-slate-700">{user.session_count}</p></div>
        <div className="rounded-2xl bg-slate-50 p-4"><p className="text-xs font-bold uppercase tracking-wider text-slate-400">Verified</p><p className="mt-1 font-semibold text-slate-700">{user.is_verified ? "Yes" : "No"}</p></div>
      </div>

      {protectedAccount ? (
        <Alert tone="info">This root account is immutable in the management API. Provisioning credentials are required to change it.</Alert>
      ) : (
        <>
          <label className="block text-sm font-semibold text-slate-700">
            Reason for change
            <textarea value={reason} onChange={(event) => onReasonChange(event.target.value)} rows={2} className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" placeholder="Required for the audit log" />
          </label>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm font-semibold text-slate-700">Role
              <select value={user.role} disabled={busy || reason.trim().length < 3} onChange={(event) => onAction("role", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm">
                {ROLES.map((role) => <option key={role} value={role}>{role}</option>)}
              </select>
            </label>
            <div className="text-sm font-semibold text-slate-700">Account status
              <div className="mt-2 flex flex-wrap gap-2">
                <Button variant="secondary" disabled={busy || reason.trim().length < 3 || user.account_status === "active"} onClick={() => onAction("status", "active")}><RefreshCw size={15} />Activate</Button>
                <Button variant="secondary" disabled={busy || reason.trim().length < 3 || user.account_status === "paused"} onClick={() => onAction("status", "paused")}><PauseCircle size={15} />Pause</Button>
                <Button variant="secondary" disabled={busy || reason.trim().length < 3 || user.account_status === "suspended"} onClick={() => onAction("status", "suspended")}><Ban size={15} />Suspend</Button>
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-slate-200 p-4">
            <p className="text-sm font-semibold text-slate-700">Set a new password</p>
            <div className="mt-2 flex flex-col gap-2 sm:flex-row">
              <input type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={12} className="min-h-11 flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="At least 12 characters" />
              <Button disabled={busy || password.length < 12 || reason.trim().length < 3} onClick={async () => { await onAction("password", password); setPassword(""); }}><KeyRound size={16} />Change password</Button>
            </div>
          </div>
          <Button variant="ghost" className="text-red-700 hover:bg-red-50 hover:text-red-800" disabled={busy || reason.trim().length < 3} onClick={() => onAction("delete")}><Trash2 size={16} />Delete account</Button>
        </>
      )}

      <div>
        <h3 className="font-bold text-clinical-ink">Recent analysis data</h3>
        {user.sessions?.length ? <div className="mt-3 space-y-2">{user.sessions.map((session) => <div key={session.session_id} className="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm"><span className="font-semibold text-slate-700">{session.exercise_display_name}</span><span className="ml-2 text-slate-400">{readableDate(session.created_at)}</span></div>)}</div> : <p className="mt-2 text-sm text-slate-500">No analysis sessions belong to this account.</p>}
      </div>
      <div>
        <h3 className="font-bold text-clinical-ink">Consents</h3>
        <p className="mt-2 text-sm text-slate-500">{user.consents?.length ? `${user.consents.length} consent record(s)` : "No consent records."}</p>
      </div>
    </div>
  );
}

export default function SuperAdminDashboard() {
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadUsers(query = search) {
    setLoading(true); setError("");
    try { setUsers(await listManagedUsers(query ? { search: query } : {})); }
    catch (requestError) { setError(requestError.response?.data?.message || "User accounts could not be loaded."); }
    finally { setLoading(false); }
  }

  useEffect(() => { loadUsers(""); }, []);

  async function selectUser(userId) {
    setError(""); setNotice(""); setReason("");
    try { setSelected(await getManagedUser(userId)); }
    catch (requestError) { setError(requestError.response?.data?.message || "Account details could not be loaded."); }
  }

  async function performAction(kind, value) {
    if (reason.trim().length < 3) return;
    if (kind === "delete" && !window.confirm(`Permanently delete ${selected.email}?`)) return;
    setBusy(true); setError(""); setNotice("");
    try {
      let result;
      if (kind === "status") result = await updateManagedUserStatus(selected.user_id, value, reason);
      if (kind === "role") result = await updateManagedUserRole(selected.user_id, value, reason);
      if (kind === "password") result = await resetManagedUserPassword(selected.user_id, value, reason);
      if (kind === "delete") result = await deleteManagedUser(selected.user_id, reason);
      setNotice(result.message);
      setReason("");
      await loadUsers();
      if (kind === "delete") setSelected(null); else setSelected(await getManagedUser(selected.user_id));
    } catch (requestError) { setError(requestError.response?.data?.message || "The account action failed."); }
    finally { setBusy(false); }
  }

  return <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
    <PageHeader eyebrow="Protected administration" title="User access control" description="Review every account and its application data. Role, status, password, and deletion changes are enforced by the server and written to the audit log." />
    {error ? <Alert className="mb-5">{error}</Alert> : null}
    {notice ? <Alert tone="info" className="mb-5">{notice}</Alert> : null}
    <div className="grid gap-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
      <Card className="overflow-hidden">
        <form className="flex gap-2 border-b border-slate-100 p-4" onSubmit={(event) => { event.preventDefault(); loadUsers(); }}>
          <label className="relative flex-1"><span className="sr-only">Search users</span><Search className="absolute left-3 top-3 text-slate-400" size={18} /><input value={search} onChange={(event) => setSearch(event.target.value)} className="min-h-11 w-full rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm" placeholder="Name or email" /></label>
          <Button type="submit" variant="secondary">Search</Button>
        </form>
        <div className="max-h-[44rem] overflow-y-auto p-3 [content-visibility:auto]">
          {loading ? <div className="p-6 text-center"><LoadingSpinner label="Loading accounts" /></div> : users.length ? users.map((user) => <button key={user.user_id} onClick={() => selectUser(user.user_id)} className={`mb-2 w-full rounded-2xl border p-4 text-left transition ${selected?.user_id === user.user_id ? "border-blue-200 bg-blue-50" : "border-slate-100 hover:border-slate-200 hover:bg-slate-50"}`}><div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="truncate font-bold text-clinical-ink">{user.full_name || user.email}</p><p className="mt-1 truncate text-xs text-slate-500">{user.email}</p></div><Badge tone={STATUS_TONES[user.account_status] || "slate"}>{user.account_status}</Badge></div><div className="mt-3 flex items-center gap-3 text-xs text-slate-400"><span>{user.role}</span><span><Users className="mr-1 inline" size={12} />{user.session_count} sessions</span>{user.is_protected ? <ShieldCheck size={14} className="text-blue-600" /> : null}</div></button>) : <EmptyState title="No accounts found" description="Try a different name or email." icon={Users} />}
        </div>
      </Card>
      <Card className="p-5 sm:p-7"><UserDetail user={selected} reason={reason} onReasonChange={setReason} busy={busy} onAction={performAction} /></Card>
    </div>
  </main>;
}

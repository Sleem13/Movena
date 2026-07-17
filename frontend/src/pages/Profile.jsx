import { useAuth } from "../context/AuthContext.jsx";
export default function Profile({ onLogout }) {
  const { user, logout } = useAuth();
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl font-bold">Profile</h1>
      <div className="mt-6 rounded-2xl border bg-white p-6">
        <p>{user?.full_name || "Development user"}</p>
        <p>{user?.email}</p>
        <p>Role: {user?.role}</p>
        <button
          onClick={async () => {
            await logout();
            onLogout?.();
          }}
          className="mt-6 rounded-xl bg-slate-900 px-4 py-2 text-white"
        >
          Log out
        </button>
      </div>
    </main>
  );
}

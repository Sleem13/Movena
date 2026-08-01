import { useAuth } from "../context/AuthContext.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function Profile({ onLogout }) {
  const { user, logout } = useAuth();
  const { t } = useLocale();
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl font-bold">{t("profile.title")}</h1>
      <div className="mt-6 rounded-2xl border bg-white p-6">
        <p>{user?.full_name || t("profile.developmentUser")}</p>
        <p>{user?.email}</p>
        <p>{t("common.role")}: {user?.role}</p>
        <button
          onClick={async () => {
            await logout();
            onLogout?.();
          }}
          className="mt-6 rounded-xl bg-slate-900 px-4 py-2 text-white"
        >
          {t("profile.logout")}
        </button>
      </div>
    </main>
  );
}

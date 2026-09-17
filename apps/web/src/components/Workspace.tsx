"use client";
import { useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowUpRight,
  CalendarDays,
  ChartNoAxesCombined,
  ClipboardCheck,
  Home,
  LayoutDashboard,
  LogOut,
  Settings2,
  Users,
  UserRound,
} from "lucide-react";
import { usePreferences } from "./Preferences";
import { useResource } from "./Resource";
import { api } from "../lib/api";
import type { User } from "../lib/types";
import { TodayView, CareView, PatientsView, ReviewView } from "./care/Views";
import { CheckInView } from "./care/CheckIn";
import { ScheduleView } from "./scheduling/Views";
import { VisitNotes } from "./scheduling/VisitNotes";
import { PlansView } from "./care/Plans";
import { ProgressView } from "./care/History";
import { HealthProfileView, NotificationsView } from "./account/PatientAccount";
import { AnalyzeView, ResultView } from "./analysis/Views";
import { AdminDataRights, PatientDataRights } from "./account/DataRights";

export function Workspace({ section }: { section: string[] }) {
  const { data: user, error, loading } = useResource<User>("auth/me");
  const { t, locale, setLocale } = usePreferences();
  const isAdmin = user?.role === "super_admin" || user?.role === "admin";
  const clinical = user?.role === "therapist";
  const tabs = isAdmin
    ? ([
        ["overview", LayoutDashboard],
        ["people", Users],
        ["operations", Settings2],
        ["account", UserRound],
      ] as const)
    : clinical
      ? ([
          ["patients", Users],
          ["review", ClipboardCheck],
          ["schedule", CalendarDays],
          ["account", UserRound],
        ] as const)
      : user?.role === "patient"
        ? ([
            ["today", Home],
            ["progress", ChartNoAxesCombined],
            ["care", Users],
            ["account", UserRound],
          ] as const)
        : ([["account", UserRound]] as const);
  const current = section[0] || tabs[0][0];
  if (loading)
    return (
      <main className="loading-page" role="status">
        {t("loading")}
      </main>
    );
  if (error || !user)
    return (
      <main className="loading-page">
        <p role="alert">{error}</p>
        <Link href="/login">{t("login")}</Link>
      </main>
    );
  const title =
    (
      {
        today: t("welcome"),
        progress: t("progress"),
        care: t("careTeam"),
        patients: t("patients"),
        review: t("review"),
        schedule: t("schedule"),
        account: t("account"),
        overview: t("overview"),
        people: t("people"),
        operations: t("operations"),
        analyze: t("analyze"),
        result: t("results"),
        "check-in": t("checkIn"),
        plans: t("carePlans"),
        health: t("healthProfile"),
        notifications: t("notifications"),
        "data-rights": t("dataRights"),
        "visit-notes": t("visitNotes"),
      } as Record<string, string>
    )[current] || t("details");
  return (
    <div className="workspace">
      <header className="topbar">
        <Link href="/workspace" className="wordmark">
          Movena
          <span className="brand-dot" />
        </Link>
        <div className="header-actions">
          <button
            className="language-toggle"
            onClick={() => setLocale(locale === "en" ? "ar" : "en")}
          >
            {locale === "en" ? "العربية" : "English"}
          </button>
          <Link href="/workspace/account" className="profile-link">
            <span className="avatar">
              {(user.full_name || user.username || user.email)
                .slice(0, 2)
                .toUpperCase()}
            </span>
            <span className="profile-name">
              {user.full_name || user.username}
            </span>
          </Link>
        </div>
      </header>
      <nav className="navigation" aria-label="Main">
        {tabs.map(([key, Icon]) => (
          <Link
            key={key}
            href={`/workspace/${key}`}
            aria-current={current === key ? "page" : undefined}
          >
            <Icon size={22} />
            <span>{t(key)}</span>
          </Link>
        ))}
        <p className="nav-footer">{t("analysisDisclaimer")}</p>
      </nav>
      <main className="workspace-main">
        <header className="page-heading">
          <div>
            <h1>{title}</h1>
            {current === "today" && <p>{t("todayIntro")}</p>}
            {current === "review" && <p>{t("reviewIntro")}</p>}
          </div>
          {user.role === "patient" && current !== "analyze" && (
            <Link className="secondary compact" href="/workspace/analyze">
              <Activity size={19} />
              {t("analyze")}
            </Link>
          )}
        </header>
        {current === "today" && user.role === "patient" ? (
          <TodayView />
        ) : current === "check-in" && user.role === "patient" ? (
          <CheckInView id={section[1] || ""} />
        ) : current === "progress" ? (
          <ProgressView />
        ) : current === "care" ? (
          <CareView user={user} />
        ) : current === "patients" && (clinical || isAdmin) ? (
          <PatientsView />
        ) : current === "review" && (clinical || isAdmin) ? (
          <ReviewView />
        ) : current === "plans" && (clinical || isAdmin) ? (
          <PlansView key={section[1]} patientId={section[1] || ""} />
        ) : current === "analyze" ? (
          <AnalyzeView />
        ) : current === "result" ? (
          <ResultView id={section[1] || ""} />
        ) : current === "schedule" &&
          (clinical || isAdmin || user.role === "patient") ? (
          <ScheduleView user={user} />
        ) : current === "visit-notes" &&
          (clinical || isAdmin || user.role === "patient") ? (
          <VisitNotes
            key={section[1]}
            appointmentId={section[1] || ""}
            staff={clinical || isAdmin}
          />
        ) : current === "account" ? (
          <Account user={user} />
        ) : current === "health" && user.role === "patient" ? (
          <HealthProfileView />
        ) : current === "notifications" && user.role === "patient" ? (
          <NotificationsView />
        ) : current === "data-rights" && user.role === "patient" ? (
          <PatientDataRights />
        ) : current === "operations" && user.role === "super_admin" ? (
          <>
            <AdminDataRights />
            <MigrationWorkspace section={current} />
          </>
        ) : (
          <MigrationWorkspace section={current} />
        )}
      </main>
    </div>
  );
}
function Account({ user }: { user: User }) {
  const { t, theme, setTheme, locale, setLocale } = usePreferences();
  const [error, setError] = useState("");
  async function logout() {
    try {
      await api("auth/logout", { method: "POST" });
      window.location.assign("/login");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <div className="narrow">
      <section className="panel">
        <h2>{user.full_name || user.username}</h2>
        <p className="muted">{user.email}</p>
        {user.role === "patient" && (
          <nav className="account-links" aria-label={t("account")}>
            <Link className="secondary" href="/workspace/health">
              {t("healthProfile")}
            </Link>
            <Link className="secondary" href="/workspace/notifications">
              {t("notifications")}
            </Link>
            <Link className="secondary" href="/workspace/data-rights">
              {t("dataRights")}
            </Link>
          </nav>
        )}
        <label>
          {t("theme")}
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value as typeof theme)}
          >
            {(["light", "dark", "system"] as const).map((v) => (
              <option key={v} value={v}>
                {t(v)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("language")}
          <select
            value={locale}
            onChange={(e) => setLocale(e.target.value as typeof locale)}
          >
            <option value="en">English</option>
            <option value="ar">العربية</option>
          </select>
        </label>
        {["patient", "therapist", "admin", "super_admin"].includes(
          user.role,
        ) && (
          <Link className="secondary" href="/workspace/schedule">
            <CalendarDays size={18} />
            {t("appointments")}
          </Link>
        )}
        <button className="secondary" onClick={logout}>
          <LogOut size={18} />
          {t("logout")}
        </button>
        {error && <p role="alert">{error}</p>}
      </section>
      <p className="fine-print">{t("analysisDisclaimer")}</p>
    </div>
  );
}
function MigrationWorkspace({ section }: { section: string }) {
  const { t } = usePreferences();
  const target =
    (
      {
        overview: "/admin/workflow",
        people: "/admin/users",
        operations: "/admin/workflow",
        schedule: "/therapist",
        goals: "/recovery-coaching",
        models: "/rehab-policy",
      } as Record<string, string>
    )[section] || "/workspace";
  const base =
    process.env.NEXT_PUBLIC_LEGACY_WEB_URL || "http://127.0.0.1:5173";
  return (
    <section className="panel narrow">
      {section === "operations" && (
        <Link className="primary" href="/workspace/schedule">
          <CalendarDays size={18} />
          {t("appointments")}
        </Link>
      )}
      <p>{t("readonly")}</p>
      <a
        className="secondary"
        href={`${base}${target}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        {t("openExisting")}
        <ArrowUpRight size={18} />
      </a>
    </section>
  );
}

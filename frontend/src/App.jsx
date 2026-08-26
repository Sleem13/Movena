import { lazy, Suspense, useEffect, useState } from "react";
import AppShell from "./components/layout/AppShell.jsx";
import About from "./pages/About.jsx";
import Home from "./pages/Home.jsx";
import Results from "./pages/Results.jsx";
import UploadSquat from "./pages/UploadSquat.jsx";
import SessionHistory from "./pages/SessionHistory.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import ExerciseLibrary from "./pages/ExerciseLibrary.jsx";
import ForgotPassword from "./pages/ForgotPassword.jsx";
import ResetPassword from "./pages/ResetPassword.jsx";
import VerifyEmail from "./pages/VerifyEmail.jsx";
import WorkspaceOverview from "./pages/WorkspaceOverview.jsx";
import { EXERCISES } from "./data/exercises.js";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import { LocaleProvider, useLocale } from "./i18n/LocaleContext.jsx";
import { ThemeProvider } from "./theme/ThemeContext.jsx";
import { ENABLE_REALTIME_COACHING_SPIKE } from "./config/featureFlags.js";
import { analyzeExerciseVideo, getExercises } from "./services/api.js";

const TherapistDashboard = lazy(() => import("./pages/TherapistDashboard.jsx"));
const RealtimeCoachingSpike = lazy(() => import("./pages/RealtimeCoachingSpike.jsx"));
const SuperAdminDashboard = lazy(() => import("./pages/SuperAdminDashboard.jsx"));

// Keep the default request on the low-latency path. Video encoding, PDF
// generation, and chart payloads remain available as explicit opt-ins.
const DEFAULT_OPTIONS = { include_overlay: false, generate_report: false, include_ml: false, include_frame_data: false, save_session: false };
const PAGE_PATHS = { home: "/", workspace: "/workspace", exercises: "/exercises", analyze: "/analyze", results: "/results", history: "/history", therapist: "/therapist", admin: "/admin/users", coach: "/coach", about: "/about", login: "/login", register: "/register", forgotPassword: "/forgot-password", resetPassword: "/reset-password", verifyEmail: "/verify-email", profile: "/profile" };
function analysisErrorMessage(requestError, t) {
  const status = requestError.response?.status;
  const apiError = requestError.response?.data;
  if (status === 401 || status === 403) return t("upload.loginRequired");
  if (status === 400 && apiError?.error_code === "UNSUPPORTED_FILE_TYPE") {
    return t("upload.unsupported");
  }
  if (status === 422 && apiError?.error_code === "SUBJECT_SWITCH_DETECTED") {
    return t("upload.subjectSwitch");
  }
  if (!requestError.response) return t("upload.network");
  if (status >= 500) return t("upload.genericError");
  return apiError?.message || apiError?.detail || t("upload.genericError");
}

function isSubjectSwitchError(requestError) {
  return requestError.response?.status === 422 && requestError.response?.data?.error_code === "SUBJECT_SWITCH_DETECTED";
}

function LazyPage({ children }) {
  return <Suspense fallback={<div className="grid min-h-[50vh] place-items-center text-sm font-semibold text-slate-500">Loading workspace…</div>}>{children}</Suspense>;
}

function initialPage() {
  const path = window.location.pathname;
  if (path.startsWith("/therapist")) return "therapist";
  if (path.startsWith("/admin")) return "admin";
  if (path.startsWith("/coach")) return ENABLE_REALTIME_COACHING_SPIKE ? "coach" : "home";
  return Object.entries(PAGE_PATHS).find(([, value]) => value === path)?.[0] || "home";
}

function AppContent() {
  const { user } = useAuth();
  const { t, exerciseText } = useLocale();
  const [page, setPage] = useState(initialPage);
  const [file, setFile] = useState(null);
  const [fileSource, setFileSource] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [canContinueAfterWarning, setCanContinueAfterWarning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [options, setOptions] = useState(DEFAULT_OPTIONS);
  const [originalVideoUrl, setOriginalVideoUrl] = useState(null);
  const [exercise, setExercise] = useState("bodyweight_squat");
  const [exercises, setExercises] = useState(EXERCISES);

  useEffect(() => {
    getExercises().then((items) => Array.isArray(items) && items.length && setExercises(items)).catch(() => {});
  }, []);

  useEffect(() => {
    function handlePopState() { setPage(initialPage()); }
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    if (!file || typeof URL.createObjectURL !== "function") { setOriginalVideoUrl(null); return undefined; }
    const url = URL.createObjectURL(file);
    setOriginalVideoUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function selectFile(selected, source = "manual") {
    setError("");
    setCanContinueAfterWarning(false);
    setFile(selected || null);
    setFileSource(selected ? source : null);
  }
  function navigate(nextPage) { setPage(nextPage); window.history.pushState({}, "", PAGE_PATHS[nextPage] || "/"); }
  function handleFileChange(event) { selectFile(event.target.files?.[0]); }

  async function analyzeSelectedExercise(selectedExercise, continueOnSubjectWarning) {
    const data = await analyzeExerciseVideo(selectedExercise, file, { ...options, continue_on_subject_warning: continueOnSubjectWarning }, setProgress);
    setReport(data); setCanContinueAfterWarning(false); navigate("results");
  }

  async function handleSubmit(event, overrides = {}) {
    event?.preventDefault?.();
    if (!file) { setError(t("upload.noFile")); return; }
    if (!user) { setError(t("upload.loginRequired")); return; }
    setIsLoading(true); setProgress(0); setError("");
    const continueOnSubjectWarning = Boolean(overrides.continueOnSubjectWarning);
    setCanContinueAfterWarning(false);
    const selectedExercise = exercise;
    try {
      await analyzeSelectedExercise(selectedExercise, continueOnSubjectWarning);
    } catch (requestError) {
      if (!continueOnSubjectWarning && isSubjectSwitchError(requestError)) {
        setError(t("upload.subjectSwitch"));
        setCanContinueAfterWarning(true);
        try {
          await new Promise((resolve) => setTimeout(resolve, 0));
          await analyzeSelectedExercise(selectedExercise, true);
        } catch (retryError) {
          setError(analysisErrorMessage(retryError, t));
          setCanContinueAfterWarning(false);
        }
        return;
      }
      setError(analysisErrorMessage(requestError, t));
      setCanContinueAfterWarning(false);
    } finally { setIsLoading(false); }
  }

  function handleAnalyzeAnother() { setFile(null); setFileSource(null); setReport(null); setError(""); setCanContinueAfterWarning(false); setProgress(0); navigate("analyze"); }

  return <AppShell currentPage={page} hasReport={Boolean(report)} onNavigate={navigate} user={user}>
    {page === "home" && <Home authenticated={Boolean(user)} onStart={() => navigate(user ? "analyze" : "register")} />}
    {page === "workspace" && (user ? <WorkspaceOverview onNavigate={navigate} /> : <Login onSuccess={() => navigate("workspace")} onRegister={() => navigate("register")} onForgotPassword={() => navigate("forgotPassword")} onVerifyEmail={() => navigate("verifyEmail")} />)}
    {page === "exercises" && <ExerciseLibrary exercises={exercises} onAnalyze={(value) => { setExercise(value); setFile(null); setFileSource(null); navigate("analyze"); }} />}
    {page === "analyze" && <UploadSquat exercises={exercises} exercise={exercise} onExerciseChange={(value) => { setExercise(value); setFile(null); setFileSource(null); setError(""); setCanContinueAfterWarning(false); }} file={file} fileSource={fileSource} error={error} canContinueAfterWarning={canContinueAfterWarning} isLoading={isLoading} progress={progress} options={options} onOptionsChange={setOptions} onFileChange={handleFileChange} onFileSelect={selectFile} onRecognitionConfirm={(exerciseId, recognizedFile) => { setExercise(exerciseId); selectFile(recognizedFile, "recognition"); }} onSubmit={handleSubmit} />}
    {page === "results" && <Results report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={handleAnalyzeAnother} onGoAnalyze={() => navigate("analyze")} onViewHistory={() => navigate("history")} />}
    {page === "history" && <SessionHistory onAnalyze={() => navigate("analyze")} onCoach={ENABLE_REALTIME_COACHING_SPIKE ? () => navigate("coach") : undefined} />}
    {page === "therapist" && <LazyPage><TherapistDashboard /></LazyPage>}
    {page === "admin" && (user?.role === "super_admin" ? <LazyPage><SuperAdminDashboard /></LazyPage> : <WorkspaceOverview onNavigate={navigate} />)}
    {page === "coach" && ENABLE_REALTIME_COACHING_SPIKE && <LazyPage><RealtimeCoachingSpike onConfirmSuggestion={(exerciseId, recognizedFile) => { setExercise(exerciseId); selectFile(recognizedFile, "recognition"); navigate("analyze"); }} /></LazyPage>}
    {page === "about" && <About onStart={() => navigate("analyze")} />}
    {page === "login" && <Login onSuccess={() => navigate("workspace")} onRegister={() => navigate("register")} onForgotPassword={() => navigate("forgotPassword")} onVerifyEmail={() => navigate("verifyEmail")} />}
    {page === "register" && <Register onLogin={() => navigate("login")} />}
    {page === "forgotPassword" && <ForgotPassword onLogin={() => navigate("login")} />}
    {page === "resetPassword" && <ResetPassword onLogin={() => navigate("login")} />}
    {page === "verifyEmail" && <VerifyEmail onLogin={() => navigate("login")} />}
    {page === "profile" && (user ? <Profile onLogout={() => navigate("home")} /> : <Login onSuccess={() => navigate("workspace")} onRegister={() => navigate("register")} onForgotPassword={() => navigate("forgotPassword")} onVerifyEmail={() => navigate("verifyEmail")} />)}
  </AppShell>;
}

export default function App(){return <ThemeProvider><LocaleProvider><AuthProvider><AppContent/></AuthProvider></LocaleProvider></ThemeProvider>;}

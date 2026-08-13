import { useEffect, useState } from "react";
import AppShell from "./components/layout/AppShell.jsx";
import About from "./pages/About.jsx";
import Home from "./pages/Home.jsx";
import Results from "./pages/Results.jsx";
import UploadSquat from "./pages/UploadSquat.jsx";
import SessionHistory from "./pages/SessionHistory.jsx";
import TherapistDashboard from "./pages/TherapistDashboard.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import ExerciseLibrary from "./pages/ExerciseLibrary.jsx";
import RealtimeCoachingSpike from "./pages/RealtimeCoachingSpike.jsx";
import { EXERCISES } from "./data/exercises.js";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import { LocaleProvider, useLocale } from "./i18n/LocaleContext.jsx";
import { ENABLE_REALTIME_COACHING_SPIKE } from "./config/featureFlags.js";
import { analyzeExerciseVideo, getExercises, recognizeExerciseVideo } from "./services/api.js";

const DEFAULT_OPTIONS = { include_overlay: true, generate_report: true, include_ml: false, include_frame_data: true, save_session: false };
const PAGE_PATHS = { home: "/", exercises: "/exercises", analyze: "/analyze", results: "/results", history: "/history", therapist: "/therapist", coach: "/coach", about: "/about", login: "/login", register: "/register", profile: "/profile" };
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

function isNoValidMovementRejection(data) {
  if (data?.status !== "rejected") return false;
  const issueText = [...(data.detected_issues || []), data.error_code, data.message].filter(Boolean).join(" ").toLowerCase();
  return data.movement_score == null && (issueText.includes("no_valid") || issueText.includes("no valid") || issueText.includes("no_complete"));
}

function initialPage() {
  const path = window.location.pathname;
  if (path.startsWith("/therapist")) return "therapist";
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

  function supportedExercise(exerciseId) {
    return exercises.find((item) => item.exercise_id === exerciseId && item.supported_in_app);
  }

  function autoRouteNotice(fromExerciseId, toExerciseId, confidence) {
    return t("upload.autoRerouteNotice", {
      selected: exerciseText(fromExerciseId).name,
      suggested: exerciseText(toExerciseId).name,
      confidence: `${Math.round((Number(confidence) || 0) * 100)}%`,
    });
  }

  function withAutoRouteNotice(data, fromExerciseId, recognition) {
    const notice = autoRouteNotice(fromExerciseId, recognition.suggested_exercise_id, recognition.confidence);
    return {
      ...data,
      validation_warnings: [...(data.validation_warnings || []), notice],
      limitations: [...(data.limitations || []), notice],
      analysis_confidence: data.analysis_confidence
        ? { ...data.analysis_confidence, warnings: [...(data.analysis_confidence.warnings || []), notice] }
        : data.analysis_confidence,
    };
  }

  function startRecognitionFallback(continueOnSubjectWarning = false) {
    return (async () => {
      try {
        return await recognizeExerciseVideo(file, undefined, { continue_on_subject_warning: continueOnSubjectWarning });
      } catch {
        return null;
      }
    })();
  }

  function actionableRecognition(result, selectedExercise) {
    const suggested = result?.suggested_exercise_id;
    if (result?.status !== "success" || !suggested || suggested === selectedExercise) return null;
    if (result.suggestion_actionable === false || result.analyzer_available === false) return null;
    return supportedExercise(suggested) ? result : null;
  }

  async function analyzeOrAutoRoute(selectedExercise, continueOnSubjectWarning, recognitionPromise) {
    const data = await analyzeExerciseVideo(selectedExercise, file, { ...options, continue_on_subject_warning: continueOnSubjectWarning }, setProgress);
    if (isNoValidMovementRejection(data)) {
      const recognition = actionableRecognition(await recognitionPromise, selectedExercise);
      if (recognition) {
        const rerouted = await analyzeExerciseVideo(recognition.suggested_exercise_id, file, { ...options, continue_on_subject_warning: continueOnSubjectWarning }, setProgress);
        setExercise(recognition.suggested_exercise_id);
        setReport(withAutoRouteNotice(rerouted, selectedExercise, recognition));
        setCanContinueAfterWarning(false); setPage("results");
        return;
      }
    }
    setReport(data); setCanContinueAfterWarning(false); setPage("results");
  }

  async function handleSubmit(event, overrides = {}) {
    event?.preventDefault?.();
    if (!file) { setError(t("upload.noFile")); return; }
    if (!user) { setError(t("upload.loginRequired")); return; }
    setIsLoading(true); setProgress(0); setError("");
    const continueOnSubjectWarning = Boolean(overrides.continueOnSubjectWarning);
    setCanContinueAfterWarning(false);
    const selectedExercise = exercise;
    const recognitionPromise = overrides.skipRecognitionFallback ? Promise.resolve(null) : startRecognitionFallback(continueOnSubjectWarning);
    try {
      await analyzeOrAutoRoute(selectedExercise, continueOnSubjectWarning, recognitionPromise);
    } catch (requestError) {
      if (!continueOnSubjectWarning && isSubjectSwitchError(requestError)) {
        setError(t("upload.subjectSwitch"));
        setCanContinueAfterWarning(true);
        try {
          await new Promise((resolve) => setTimeout(resolve, 0));
          const retryRecognitionPromise = overrides.skipRecognitionFallback ? Promise.resolve(null) : startRecognitionFallback(true);
          await analyzeOrAutoRoute(selectedExercise, true, retryRecognitionPromise);
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

  function handleAnalyzeAnother() { setFile(null); setFileSource(null); setReport(null); setError(""); setCanContinueAfterWarning(false); setProgress(0); setPage("analyze"); }

  return <AppShell currentPage={page} hasReport={Boolean(report)} onNavigate={navigate} user={user}>
    {page === "home" && <Home onStart={() => navigate("analyze")} />}
    {page === "exercises" && <ExerciseLibrary exercises={exercises} onAnalyze={(value) => { setExercise(value); setFile(null); setFileSource(null); navigate("analyze"); }} />}
    {page === "analyze" && <UploadSquat exercises={exercises} exercise={exercise} onExerciseChange={(value) => { setExercise(value); setFile(null); setFileSource(null); setError(""); setCanContinueAfterWarning(false); }} file={file} fileSource={fileSource} error={error} canContinueAfterWarning={canContinueAfterWarning} isLoading={isLoading} progress={progress} options={options} onOptionsChange={setOptions} onFileChange={handleFileChange} onFileSelect={selectFile} onRecognitionConfirm={(exerciseId, recognizedFile) => { setExercise(exerciseId); selectFile(recognizedFile, "recognition"); }} onSubmit={handleSubmit} />}
    {page === "results" && <Results report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={handleAnalyzeAnother} onGoAnalyze={() => setPage("analyze")} onViewHistory={() => setPage("history")} />}
    {page === "history" && <SessionHistory />}
    {page === "therapist" && <TherapistDashboard />}
    {page === "coach" && ENABLE_REALTIME_COACHING_SPIKE && <RealtimeCoachingSpike onConfirmSuggestion={(exerciseId, recognizedFile) => { setExercise(exerciseId); selectFile(recognizedFile, "recognition"); navigate("analyze"); }} />}
    {page === "about" && <About onStart={() => navigate("analyze")} />}
    {page === "login" && <Login onSuccess={() => navigate("profile")} onRegister={() => navigate("register")} />}
    {page === "register" && <Register onLogin={() => navigate("login")} />}
    {page === "profile" && (user ? <Profile onLogout={() => navigate("home")} /> : <Login onSuccess={() => navigate("profile")} onRegister={() => navigate("register")} />)}
  </AppShell>;
}

export default function App(){return <LocaleProvider><AuthProvider><AppContent/></AuthProvider></LocaleProvider>;}

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
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import { analyzeKneeExtensionVideo, analyzeShoulderAbductionVideo, analyzeSitToStandVideo, analyzeSquatVideo } from "./services/api.js";

const DEFAULT_OPTIONS = { include_overlay: true, generate_report: true, include_ml: false, include_frame_data: true, save_session: false };
const PAGE_PATHS = { home: "/", analyze: "/analyze", results: "/results", history: "/history", therapist: "/therapist", about: "/about", login: "/login", register: "/register", profile: "/profile" };

function initialPage() {
  const path = window.location.pathname;
  if (path.startsWith("/therapist")) return "therapist";
  return Object.entries(PAGE_PATHS).find(([, value]) => value === path)?.[0] || "home";
}

function AppContent() {
  const { user } = useAuth();
  const [page, setPage] = useState(initialPage);
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [options, setOptions] = useState(DEFAULT_OPTIONS);
  const [originalVideoUrl, setOriginalVideoUrl] = useState(null);
  const [exercise, setExercise] = useState("bodyweight_squat");

  useEffect(() => {
    if (!file || typeof URL.createObjectURL !== "function") { setOriginalVideoUrl(null); return undefined; }
    const url = URL.createObjectURL(file);
    setOriginalVideoUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function selectFile(selected) { setError(""); setFile(selected || null); }
  function navigate(nextPage) { setPage(nextPage); window.history.pushState({}, "", PAGE_PATHS[nextPage] || "/"); }
  function handleFileChange(event) { selectFile(event.target.files?.[0]); }

  async function handleSubmit(event) {
    event?.preventDefault?.();
    if (!file) { setError("Select a video before starting analysis."); return; }
    setIsLoading(true); setProgress(0); setError("");
    try {
      const analyze = exercise === "sit_to_stand" ? analyzeSitToStandVideo : exercise === "knee_extension" ? analyzeKneeExtensionVideo : exercise === "shoulder_abduction" ? analyzeShoulderAbductionVideo : analyzeSquatVideo;
      const data = await analyze(file, options, setProgress);
      setReport(data); setPage("results");
    } catch (requestError) {
      const apiError = requestError.response?.data;
      setError(apiError?.message || apiError?.detail || "Unable to analyze this video. Check the backend and try again.");
    } finally { setIsLoading(false); }
  }

  function handleAnalyzeAnother() { setFile(null); setReport(null); setError(""); setProgress(0); setPage("analyze"); }

  return <AppShell currentPage={page} hasReport={Boolean(report)} onNavigate={navigate} user={user}>
    {page === "home" && <Home onStart={() => navigate("analyze")} />}
    {page === "analyze" && <UploadSquat exercise={exercise} onExerciseChange={(value) => { setExercise(value); setFile(null); setError(""); if (value !== "bodyweight_squat") setOptions((current) => ({ ...current, include_ml: false })); }} file={file} error={error} isLoading={isLoading} progress={progress} options={options} onOptionsChange={setOptions} onFileChange={handleFileChange} onFileSelect={selectFile} onSubmit={handleSubmit} />}
    {page === "results" && <Results report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={handleAnalyzeAnother} onGoAnalyze={() => setPage("analyze")} onViewHistory={() => setPage("history")} />}
    {page === "history" && <SessionHistory />}
    {page === "therapist" && <TherapistDashboard />}
    {page === "about" && <About onStart={() => navigate("analyze")} />}
    {page === "login" && <Login onSuccess={() => navigate("profile")} onRegister={() => navigate("register")} />}
    {page === "register" && <Register onLogin={() => navigate("login")} />}
    {page === "profile" && (user ? <Profile onLogout={() => navigate("home")} /> : <Login onSuccess={() => navigate("profile")} onRegister={() => navigate("register")} />)}
  </AppShell>;
}

export default function App(){return <AuthProvider><AppContent/></AuthProvider>;}

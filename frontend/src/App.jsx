import { useEffect, useState } from "react";
import AppShell from "./components/layout/AppShell.jsx";
import About from "./pages/About.jsx";
import Home from "./pages/Home.jsx";
import Results from "./pages/Results.jsx";
import UploadSquat from "./pages/UploadSquat.jsx";
import { analyzeSquatVideo } from "./services/api.js";

const DEFAULT_OPTIONS = { include_overlay: true, generate_report: true, include_ml: false, include_frame_data: true };

export default function App() {
  const [page, setPage] = useState("home");
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [options, setOptions] = useState(DEFAULT_OPTIONS);
  const [originalVideoUrl, setOriginalVideoUrl] = useState(null);

  useEffect(() => {
    if (!file || typeof URL.createObjectURL !== "function") { setOriginalVideoUrl(null); return undefined; }
    const url = URL.createObjectURL(file);
    setOriginalVideoUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function selectFile(selected) { setError(""); setFile(selected || null); }
  function handleFileChange(event) { selectFile(event.target.files?.[0]); }

  async function handleSubmit(event) {
    event?.preventDefault?.();
    if (!file) { setError("Select a video before starting analysis."); return; }
    setIsLoading(true); setProgress(0); setError("");
    try {
      const data = await analyzeSquatVideo(file, options, setProgress);
      setReport(data); setPage("results");
    } catch (requestError) {
      const apiError = requestError.response?.data;
      setError(apiError?.message || apiError?.detail || "Unable to analyze this video. Check the backend and try again.");
    } finally { setIsLoading(false); }
  }

  function handleAnalyzeAnother() { setFile(null); setReport(null); setError(""); setProgress(0); setPage("analyze"); }

  return <AppShell currentPage={page} hasReport={Boolean(report)} onNavigate={setPage}>
    {page === "home" && <Home onStart={() => setPage("analyze")} />}
    {page === "analyze" && <UploadSquat file={file} error={error} isLoading={isLoading} progress={progress} options={options} onOptionsChange={setOptions} onFileChange={handleFileChange} onFileSelect={selectFile} onSubmit={handleSubmit} />}
    {page === "results" && <Results report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={handleAnalyzeAnother} onGoAnalyze={() => setPage("analyze")} />}
    {page === "about" && <About onStart={() => setPage("analyze")} />}
  </AppShell>;
}

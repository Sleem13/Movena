import { useState } from "react";

import Home from "./pages/Home.jsx";
import Results from "./pages/Results.jsx";
import UploadSquat from "./pages/UploadSquat.jsx";
import { analyzeSquatVideo } from "./services/api.js";

const pages = {
  home: "home",
  upload: "upload",
  results: "results",
};

export default function App() {
  const [page, setPage] = useState(pages.home);
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  function handleFileChange(event) {
    setError("");
    setFile(event.target.files?.[0] || null);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Select a video before starting analysis.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const data = await analyzeSquatVideo(file);
      setReport(data);
      setPage(pages.results);
    } catch (requestError) {
      const apiError = requestError.response?.data;
      setError(apiError?.message || apiError?.detail || "Unable to analyze this video. Check the backend and try again.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleAnalyzeAnother() {
    setFile(null);
    setReport(null);
    setError("");
    setPage(pages.upload);
  }

  return (
    <div className="min-h-screen bg-[#eef5f7]">
      <header className="border-b border-clinical-line bg-white/90">
        <nav className="mx-auto flex h-20 w-full max-w-6xl items-center justify-between px-6">
          <button
            type="button"
            onClick={() => setPage(pages.home)}
            className="text-left text-lg font-semibold text-clinical-ink"
          >
            PhysioVision AI
          </button>
          <button
            type="button"
            onClick={() => setPage(pages.upload)}
            className="rounded-lg border border-clinical-line px-4 py-2 text-sm font-semibold text-clinical-ink transition hover:border-clinical-teal"
          >
            Squat Analyzer
          </button>
        </nav>
      </header>

      {page === pages.home && <Home onStart={() => setPage(pages.upload)} />}
      {page === pages.upload && (
        <UploadSquat
          file={file}
          error={error}
          isLoading={isLoading}
          onFileChange={handleFileChange}
          onSubmit={handleSubmit}
        />
      )}
      {page === pages.results && (
        <Results report={report} onAnalyzeAnother={handleAnalyzeAnother} />
      )}
    </div>
  );
}

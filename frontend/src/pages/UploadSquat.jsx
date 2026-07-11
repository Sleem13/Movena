import UploadCard from "../components/UploadCard.jsx";
import CameraPlacementGuide from "../components/CameraPlacementGuide.jsx";

export default function UploadSquat({
  file,
  error,
  isLoading,
  onFileChange,
  onSubmit,
}) {
  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col px-6 py-10">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-wide text-clinical-teal">
          Squat analysis
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-clinical-ink">Upload video</h1>
      </div>
      <CameraPlacementGuide />
      <UploadCard
        file={file}
        error={error}
        isLoading={isLoading}
        onFileChange={onFileChange}
        onSubmit={onSubmit}
      />
    </main>
  );
}

export default function BrandLogo({ compact = false, className = "", markClassName = "", imageClassName = "" }) {
  if (compact) return (
    <span className={`relative inline-block h-12 w-12 shrink-0 overflow-hidden rounded-[13px] shadow-[0_8px_20px_rgba(37,99,235,0.18)] ${markClassName} ${className}`}>
      <img
        src="/brand-wordmark.png"
        alt=""
        aria-hidden="true"
        className="absolute left-[-7px] top-[-10px] h-[68px] max-w-none"
      />
    </span>
  );
  return (
    <span className={`inline-flex min-w-0 items-center rounded-xl px-1.5 py-1 shadow-sm ${className}`} style={{ backgroundColor: "#ffffff" }}>
      <img
        src="/brand-wordmark.png"
        alt="PhysioVision AI — AI-Assisted Rehabilitation Platform. Move Better, Recover Faster, Live Healthier."
        className={`h-auto w-[210px] max-w-full object-contain ${imageClassName}`}
      />
    </span>
  );
}

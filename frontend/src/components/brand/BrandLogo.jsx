export default function BrandLogo({ compact = false, className = "", markClassName = "" }) {
  return (
    <span className={`inline-flex min-w-0 items-center gap-3 ${className}`}>
      <img
        src="/favicon.svg"
        alt=""
        aria-hidden="true"
        className={`h-11 w-11 shrink-0 rounded-[13px] shadow-[0_8px_20px_rgba(37,99,235,0.18)] ${markClassName}`}
      />
      {compact ? null : (
        <span className="truncate text-[20px] font-extrabold tracking-[-0.04em] text-clinical-ink">
          PhysioVision AI
        </span>
      )}
    </span>
  );
}

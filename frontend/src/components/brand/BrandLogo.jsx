import { BRAND } from "../../config/brand.js";

export default function BrandLogo({ compact = false, className = "", markClassName = "", imageClassName = "" }) {
  if (compact) return (
    <span className={`relative inline-block h-12 w-12 shrink-0 overflow-hidden rounded-[13px] shadow-[0_8px_20px_rgba(37,99,235,0.18)] ${markClassName} ${className}`}>
      <img
        src={BRAND.assets.mark}
        alt=""
        aria-hidden="true"
        width="192"
        height="192"
        decoding="async"
        className="h-full w-full object-cover"
      />
    </span>
  );
  return (
    <span className={`inline-flex min-w-0 items-center rounded-xl px-1.5 py-1 shadow-sm ${className}`} style={{ backgroundColor: "#ffffff" }}>
      <picture>
        <source
          type="image/webp"
          srcSet={`${BRAND.assets.wordmarkWebp} 1x, ${BRAND.assets.wordmarkWebp2x} 2x`}
        />
        <img
          src={BRAND.assets.wordmarkFallback}
          alt={`${BRAND.name} — ${BRAND.description} ${BRAND.tagline}.`}
          width="420"
          height="147"
          decoding="async"
          className={`h-auto w-[210px] max-w-full object-contain ${imageClassName}`}
        />
      </picture>
    </span>
  );
}

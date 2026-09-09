import { BRAND } from "../../config/brand.js";

export default function BrandLogo({ compact = false, className = "", markClassName = "", imageClassName = "" }) {
  return (
    <span role="img" aria-label={BRAND.name} className={`brand-lockup ${compact ? "brand-lockup-compact" : ""} ${className} ${imageClassName}`}>
      <img src={BRAND.assets.mark} alt="" aria-hidden="true" width="1280" height="1280" className={`brand-symbol ${markClassName}`} />
      {!compact ? <span aria-hidden="true" className="brand-name">{BRAND.name}</span> : null}
    </span>
  );
}

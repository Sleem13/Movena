import { Eye, EyeOff, LockKeyhole } from "lucide-react";
import { useState } from "react";

export default function PasswordInput({ label, name, autoComplete, minLength, placeholder, required = true, value, onChange }) {
  const [visible, setVisible] = useState(false);
  return (
    <label className="grid gap-2 text-sm font-semibold text-slate-700">
      {label}
      <span className="relative">
        <LockKeyhole className="pointer-events-none absolute start-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
        <input
          name={name}
          type={visible ? "text" : "password"}
          autoComplete={autoComplete}
          minLength={minLength}
          placeholder={placeholder}
          required={required}
          value={value}
          onChange={onChange}
          className="w-full rounded-lg border border-slate-200 bg-white py-3 ps-11 pe-12 text-sm text-clinical-ink"
        />
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          className="absolute end-1 top-1/2 grid h-11 w-11 -translate-y-1/2 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-clinical-ink"
          aria-label={visible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}
          aria-pressed={visible}
        >
          {visible ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </span>
    </label>
  );
}

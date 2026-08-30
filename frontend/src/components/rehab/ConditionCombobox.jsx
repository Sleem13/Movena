import { Check, ChevronDown, Search } from "lucide-react";
import { useEffect, useId, useMemo, useRef, useState } from "react";

export default function ConditionCombobox({ conditions, id, label, onChange, value }) {
  const generatedId = useId();
  const inputId = id || generatedId;
  const listId = `${inputId}-conditions`;
  const rootRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const selected = conditions.find((condition) => condition.id === value);
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return conditions;
    return conditions.filter((condition) =>
      (condition.search_text || `${condition.name} ${(condition.aliases || []).join(" ")} ${condition.category} ${condition.body_region}`)
        .toLowerCase()
        .includes(normalized),
    );
  }, [conditions, query]);

  useEffect(() => {
    function close(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);

  function choose(condition) {
    onChange(condition);
    setQuery("");
    setOpen(false);
  }

  function handleKeyDown(event) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);
      setActive((current) => Math.min(current + 1, Math.max(0, filtered.length - 1)));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((current) => Math.max(0, current - 1));
    } else if (event.key === "Enter" && open && filtered[active]) {
      event.preventDefault();
      choose(filtered[active]);
    } else if (event.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <label ref={rootRef} className="relative block text-sm font-semibold text-slate-700" htmlFor={inputId}>
      {label}
      <div className="relative mt-2">
        <Search className="pointer-events-none absolute left-3 top-3.5 text-slate-400" size={17} />
        <input
          id={inputId}
          role="combobox"
          aria-autocomplete="list"
          aria-controls={listId}
          aria-expanded={open}
          autoComplete="off"
          className="min-h-11 w-full rounded-xl border border-slate-300 bg-white py-2 pl-10 pr-10 font-normal outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100"
          placeholder={selected?.name || "Search condition or diagnosis"}
          value={open ? query : selected?.name || ""}
          onChange={(event) => { setQuery(event.target.value); setActive(0); setOpen(true); }}
          onClick={() => setOpen(true)}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
        />
        <ChevronDown className="pointer-events-none absolute right-3 top-3.5 text-slate-400" size={17} />
      </div>
      {open ? (
        <div id={listId} role="listbox" className="absolute z-30 mt-2 max-h-80 w-full overflow-y-auto rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl">
          {filtered.length ? filtered.map((condition, index) => (
            <button
              key={condition.id}
              type="button"
              role="option"
              aria-selected={condition.id === value}
              className={`flex w-full items-start justify-between gap-3 rounded-lg px-3 py-2.5 text-left font-normal ${index === active ? "bg-blue-50" : "hover:bg-slate-50"}`}
              onMouseEnter={() => setActive(index)}
              onClick={() => choose(condition)}
            >
              <span>
                <span className="block font-semibold text-slate-800">{condition.name}</span>
                <span className="mt-0.5 block text-xs text-slate-500">{condition.category} · {condition.body_region}</span>
              </span>
              <span className="flex shrink-0 items-center gap-1.5">
                {condition.rl_supported ? <span className="rounded-full bg-cyan-50 px-2 py-0.5 text-[10px] font-bold text-cyan-700">RL</span> : null}
                {condition.id === value ? <Check className="text-teal-600" size={16} /> : null}
              </span>
            </button>
          )) : <p className="px-3 py-6 text-center text-sm font-normal text-slate-500">No matching condition</p>}
        </div>
      ) : null}
    </label>
  );
}

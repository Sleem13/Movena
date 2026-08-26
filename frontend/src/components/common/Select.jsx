import { createPortal } from "react-dom";
import { Check, ChevronDown } from "lucide-react";
import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";

function flattenOptions(groups) {
  return groups.flatMap((entry) => entry.options ? entry.options : [entry]);
}

export default function Select({
  ariaLabel,
  buttonClassName = "",
  className = "",
  disabled = false,
  icon: Icon,
  id,
  menuClassName = "",
  minMenuWidth = 0,
  onChange,
  options,
  value,
}) {
  const generatedId = useId();
  const listboxId = `${id || generatedId}-listbox`;
  const triggerRef = useRef(null);
  const menuRef = useRef(null);
  const optionRefs = useRef(new Map());
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [position, setPosition] = useState({ left: 0, top: 0, width: 0, maxHeight: 320 });
  const flatOptions = useMemo(() => flattenOptions(options), [options]);
  const selectedIndex = Math.max(0, flatOptions.findIndex((option) => option.value === value));
  const selected = flatOptions[selectedIndex];

  function enabledIndex(start, direction) {
    if (!flatOptions.length) return 0;
    let candidate = start;
    for (let count = 0; count < flatOptions.length; count += 1) {
      candidate = (candidate + direction + flatOptions.length) % flatOptions.length;
      if (!flatOptions[candidate]?.disabled) return candidate;
    }
    return selectedIndex;
  }

  function close({ restoreFocus = false } = {}) {
    setOpen(false);
    if (restoreFocus) requestAnimationFrame(() => triggerRef.current?.focus());
  }

  function choose(option) {
    if (option.disabled) return;
    onChange(option.value);
    close({ restoreFocus: true });
  }

  function openMenu(direction = 0) {
    if (disabled) return;
    const initialIndex = flatOptions[selectedIndex]?.disabled
      ? enabledIndex(selectedIndex - 1, 1)
      : selectedIndex;
    setActiveIndex(direction ? enabledIndex(selectedIndex, direction) : initialIndex);
    setOpen(true);
  }

  useLayoutEffect(() => {
    if (!open) return undefined;
    function updatePosition() {
      const rect = triggerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const desiredHeight = Math.min(360, flatOptions.length * 42 + options.filter((entry) => entry.options).length * 28 + 12);
      const below = window.innerHeight - rect.bottom - 12;
      const above = rect.top - 12;
      const showAbove = below < Math.min(desiredHeight, 220) && above > below;
      const maxHeight = Math.max(160, Math.min(desiredHeight, showAbove ? above : below));
      const width = Math.max(rect.width, minMenuWidth);
      const left = Math.min(Math.max(8, rect.left), Math.max(8, window.innerWidth - width - 8));
      setPosition({ left, top: showAbove ? rect.top - maxHeight - 8 : rect.bottom + 8, width, maxHeight });
    }
    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [flatOptions.length, minMenuWidth, open, options]);

  useEffect(() => {
    if (!open) return undefined;
    function handlePointerDown(event) {
      if (!triggerRef.current?.contains(event.target) && !menuRef.current?.contains(event.target)) close();
    }
    document.addEventListener("pointerdown", handlePointerDown);
    requestAnimationFrame(() => optionRefs.current.get(activeIndex)?.focus());
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [activeIndex, open]);

  function handleTriggerKeyDown(event) {
    if (["ArrowDown", "ArrowUp"].includes(event.key)) {
      event.preventDefault();
      openMenu(event.key === "ArrowDown" ? 1 : -1);
    } else if (["Enter", " "].includes(event.key)) {
      event.preventDefault();
      if (open) close(); else openMenu();
    } else if (event.key === "Escape") close();
  }

  function handleMenuKeyDown(event) {
    let nextIndex;
    if (event.key === "ArrowDown") nextIndex = enabledIndex(activeIndex, 1);
    else if (event.key === "ArrowUp") nextIndex = enabledIndex(activeIndex, -1);
    else if (event.key === "Home") nextIndex = enabledIndex(-1, 1);
    else if (event.key === "End") nextIndex = enabledIndex(0, -1);
    else if (event.key === "Escape") { event.preventDefault(); close({ restoreFocus: true }); return; }
    else if (event.key === "Tab") { close(); return; }
    else if (["Enter", " "].includes(event.key)) { event.preventDefault(); choose(flatOptions[activeIndex]); return; }
    else return;
    event.preventDefault();
    setActiveIndex(nextIndex);
    optionRefs.current.get(nextIndex)?.focus();
  }

  let optionIndex = -1;
  const menu = open ? createPortal(
    <div
      ref={menuRef}
      id={listboxId}
      role="listbox"
      aria-label={ariaLabel}
      aria-activedescendant={`${listboxId}-option-${activeIndex}`}
      className={`select-menu fixed z-[100] overflow-y-auto rounded-xl border border-clinical-line bg-white p-1.5 shadow-[0_18px_50px_rgba(7,27,74,0.18)] ${menuClassName}`}
      style={{ left: position.left, top: position.top, width: position.width, maxHeight: position.maxHeight }}
      onKeyDown={handleMenuKeyDown}
    >
      {options.map((entry) => {
        const group = entry.options ? entry : null;
        const entries = group ? group.options : [entry];
        return <div key={group?.label || entry.value} role={group ? "group" : undefined} aria-label={group?.label}>
          {group ? <div className="px-3 pb-1 pt-2 text-[10px] font-bold uppercase tracking-[0.13em] text-slate-400">{group.label}</div> : null}
          {entries.map((option) => {
            optionIndex += 1;
            const index = optionIndex;
            const isSelected = option.value === value;
            return <button
              key={option.value}
              ref={(node) => { if (node) optionRefs.current.set(index, node); else optionRefs.current.delete(index); }}
              id={`${listboxId}-option-${index}`}
              type="button"
              role="option"
              aria-selected={isSelected}
              disabled={option.disabled}
              tabIndex={index === activeIndex ? 0 : -1}
              className={`flex min-h-10 w-full items-center justify-between gap-3 rounded-lg px-3 text-start text-sm outline-none transition focus-visible:ring-2 focus-visible:ring-blue-300 ${isSelected ? "bg-blue-50 font-semibold text-blue-700" : "text-slate-700 hover:bg-slate-50 hover:text-clinical-ink"} disabled:cursor-not-allowed disabled:text-slate-400 disabled:opacity-70`}
              onMouseEnter={() => !option.disabled && setActiveIndex(index)}
              onClick={() => choose(option)}
            >
              <span className="min-w-0 truncate">{option.label}</span>
              {isSelected ? <Check size={16} className="shrink-0 text-clinical-teal" aria-hidden="true" /> : null}
            </button>;
          })}
        </div>;
      })}
    </div>,
    document.body,
  ) : null;

  return <div className={`relative ${className}`}>
    <button
      ref={triggerRef}
      id={id}
      type="button"
      role="combobox"
      aria-label={ariaLabel}
      aria-controls={listboxId}
      aria-expanded={open}
      aria-haspopup="listbox"
      disabled={disabled}
      className={`flex min-h-11 w-full items-center justify-between gap-3 rounded-[11px] border border-clinical-line bg-white px-3 text-start text-sm font-medium text-clinical-ink shadow-sm outline-none transition hover:border-blue-300 hover:bg-clinical-sky/40 focus-visible:border-blue-400 focus-visible:ring-4 focus-visible:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400 disabled:shadow-none ${buttonClassName}`}
      onClick={() => setOpen((current) => !current)}
      onKeyDown={handleTriggerKeyDown}
    >
      <span className="flex min-w-0 items-center gap-2.5">{Icon ? <Icon size={17} className="shrink-0 text-slate-500" aria-hidden="true" /> : null}<span className="truncate">{selected?.label || "—"}</span></span>
      <ChevronDown size={16} className={`shrink-0 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
    </button>
    {menu}
  </div>;
}

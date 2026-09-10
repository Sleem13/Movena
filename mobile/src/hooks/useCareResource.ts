import { useCallback, useRef, useState } from "react";
import { useFocusEffect } from "expo-router";

/** Reload on return from child screens; ignore late responses from an old screen. */
export function useCareResource<T>(fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const request = ++generation.current;
    setLoading(true); setError("");
    try {
      const result = await fetcher();
      if (request === generation.current) setData(result);
    } catch (cause) {
      if (request === generation.current) { setData(null); setError(cause instanceof Error ? cause.message : "Could not load this information."); }
    } finally { if (request === generation.current) setLoading(false); }
  }, [fetcher]);
  useFocusEffect(useCallback(() => { void reload(); return () => { generation.current++; }; }, [reload]));
  return { data, loading, error, reload };
}

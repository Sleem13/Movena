import { createContext, PropsWithChildren, useContext, useEffect, useState } from "react";
import type { User } from "@/src/types/auth";
import * as authApi from "@/src/api/auth";
import { getToken } from "@/src/utils/secureTokenStorage";
import { subscribeToSessionExpiry } from "@/src/utils/sessionEvents";

type State = { user: User | null; loading: boolean; sessionMessage: string; clearSessionMessage: () => void; signIn: (email: string, password: string) => Promise<void>; signOut: () => Promise<void>; refresh: () => Promise<void> };
const Context = createContext<State | null>(null);
export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null); const [loading, setLoading] = useState(true);
  const [sessionMessage, setSessionMessage] = useState("");
  async function refresh() { if (!await getToken()) { setUser(null); return; } setUser(await authApi.getCurrentUser()); }
  useEffect(() => { refresh().catch(() => setUser(null)).finally(() => setLoading(false)); }, []);
  useEffect(() => subscribeToSessionExpiry((message) => { setUser(null); setSessionMessage(message); }), []);
  async function signIn(email: string, password: string) { setUser(await authApi.login(email, password)); setSessionMessage(""); }
  async function signOut() { await authApi.logout(); setUser(null); setSessionMessage(""); }
  return <Context.Provider value={{ user, loading, sessionMessage, clearSessionMessage: () => setSessionMessage(""), signIn, signOut, refresh }}>{children}</Context.Provider>;
}
export function useAuth() { const value = useContext(Context); if (!value) throw new Error("AuthProvider is missing"); return value; }

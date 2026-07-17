import { createContext, useContext, useEffect, useState } from "react";
import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "../services/api.js";
const AuthContext = createContext(null);
const TOKEN_KEY = "physiovision_access_token";
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(
    Boolean(localStorage.getItem(TOKEN_KEY)),
  );
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) return;
    getCurrentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, []);
  async function login(email, password) {
    const result = await loginUser({ email, password });
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setUser(result.user);
    return result.user;
  }
  async function register(payload) {
    return registerUser(payload);
  }
  async function logout() {
    try {
      if (user) await logoutUser();
    } catch {
      /* stateless logout */
    }
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }
  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
export function useAuth() {
  return useContext(AuthContext);
}

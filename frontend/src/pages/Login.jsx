import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
export default function Login({ onSuccess, onRegister }) {
  const { login } = useAuth();
  const [error, setError] = useState("");
  async function submit(e) {
    e.preventDefault();
    setError("");
    const d = new FormData(e.currentTarget);
    try {
      await login(d.get("email"), d.get("password"));
      onSuccess?.();
    } catch (x) {
      setError(
        x.response?.data?.error_code === "TOKEN_EXPIRED"
          ? "Your session may have expired. Please log in again."
          : "Please check your email and password.",
      );
    }
  }
  return (
    <main className="mx-auto max-w-lg px-6 py-12">
      <h1 className="text-3xl font-bold">Log in</h1>
      <p className="mt-3 rounded-xl bg-amber-50 p-3 text-sm">
        Do not enter real patient-identifiable data in this development build.
      </p>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={submit} className="mt-6 grid gap-4">
        <label>
          Email
          <input
            name="email"
            type="email"
            required
            className="w-full rounded-xl border p-3"
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            required
            className="w-full rounded-xl border p-3"
          />
        </label>
        <button className="rounded-xl bg-blue-700 p-3 text-white">
          Log in
        </button>
      </form>
      <button onClick={onRegister} className="mt-4 text-blue-700">
        Create a development account
      </button>
    </main>
  );
}

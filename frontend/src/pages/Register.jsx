import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
export default function Register({ onLogin }) {
  const { register } = useAuth();
  const [message, setMessage] = useState("");
  async function submit(e) {
    e.preventDefault();
    const d = new FormData(e.currentTarget);
    try {
      await register({
        email: d.get("email"),
        password: d.get("password"),
        full_name: d.get("full_name"),
        role: "researcher_demo",
      });
      setMessage("Account created. You can now log in.");
    } catch (x) {
      setMessage(x.response?.data?.message || "Registration failed.");
    }
  }
  return (
    <main className="mx-auto max-w-lg px-6 py-12">
      <h1 className="text-3xl font-bold">Register</h1>
      <p className="mt-3 rounded-xl bg-amber-50 p-3 text-sm">
        Do not enter real patient-identifiable data in this development build.
      </p>
      {message && <p role="status">{message}</p>}
      <form onSubmit={submit} className="mt-6 grid gap-4">
        <label>
          Display name
          <input name="full_name" className="w-full rounded-xl border p-3" />
        </label>
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
            minLength="12"
            required
            className="w-full rounded-xl border p-3"
          />
        </label>
        <button className="rounded-xl bg-blue-700 p-3 text-white">
          Register
        </button>
      </form>
      <button onClick={onLogin} className="mt-4 text-blue-700">
        Back to login
      </button>
    </main>
  );
}

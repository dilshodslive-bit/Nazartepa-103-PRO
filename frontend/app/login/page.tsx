"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { uz } from "@/lib/i18n";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@nazartepa.uz");
  const [password, setPassword] = useState("Admin12345!");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
    } catch {
      setError(uz.loginError);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm rounded-2xl bg-slate-800/60 p-8 shadow-xl ring-1 ring-slate-700"
      >
        <div className="mb-6 text-center">
          <div className="text-3xl font-bold text-red-500">103</div>
          <h1 className="mt-1 text-xl font-semibold">{uz.appName}</h1>
          <p className="mt-1 text-xs text-slate-400">{uz.tagline}</p>
        </div>

        <label className="mb-1 block text-sm text-slate-300">{uz.email}</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mb-4 w-full rounded-lg bg-slate-900 px-3 py-2 text-sm outline-none ring-1 ring-slate-700 focus:ring-red-500"
          required
        />

        <label className="mb-1 block text-sm text-slate-300">{uz.password}</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mb-4 w-full rounded-lg bg-slate-900 px-3 py-2 text-sm outline-none ring-1 ring-slate-700 focus:ring-red-500"
          required
        />

        {error && <p className="mb-3 text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-lg bg-red-600 py-2 text-sm font-semibold text-white transition hover:bg-red-500 disabled:opacity-50"
        >
          {busy ? "..." : uz.signIn}
        </button>
      </form>
    </main>
  );
}

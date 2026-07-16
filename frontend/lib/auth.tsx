"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, clearToken, getToken, setToken } from "./api";
import type { User } from "./types";

const USER_KEY = "nz103_user";

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    const stored = typeof window !== "undefined" ? localStorage.getItem(USER_KEY) : null;
    if (token && stored) setUser(JSON.parse(stored));
    setLoading(false);
  }, []);

  async function login(email: string, password: string) {
    const res = await api.login(email, password);
    setToken(res.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.user));
    setUser(res.user);
    router.push("/dashboard");
  }

  function logout() {
    clearToken();
    localStorage.removeItem(USER_KEY);
    setUser(null);
    router.push("/login");
  }

  return (
    <Ctx.Provider value={{ user, loading, login, logout }}>{children}</Ctx.Provider>
  );
}

export function useAuth(): AuthCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth AuthProvider ichida ishlatilishi kerak");
  return ctx;
}

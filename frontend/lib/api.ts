import type {
  Ambulance,
  EmergencyCall,
  LoginResponse,
  Page,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const TOKEN_KEY = "nz103_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API}${path}`, { ...init, headers });
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      detail = (await resp.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(resp.status, detail);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  listCalls: (params: { status?: string; priority?: string } = {}) => {
    const q = new URLSearchParams({ size: "50" });
    if (params.status) q.set("status", params.status);
    if (params.priority) q.set("priority", params.priority);
    return request<Page<EmergencyCall>>(`/calls?${q.toString()}`);
  },

  getCall: (id: number) => request<EmergencyCall>(`/calls/${id}`),

  changeCallStatus: (id: number, status: string, note?: string) =>
    request<EmergencyCall>(`/calls/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, note }),
    }),

  dispatchCall: (id: number, ambulanceId?: number) =>
    request(`/calls/${id}/dispatch`, {
      method: "POST",
      body: JSON.stringify({ ambulance_id: ambulanceId ?? null }),
    }),

  listAmbulances: () => request<Page<Ambulance>>("/ambulances?size=100"),
};

export { ApiError };

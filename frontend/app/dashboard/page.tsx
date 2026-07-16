"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useWebSocket } from "@/lib/useWebSocket";
import { uz } from "@/lib/i18n";
import type { Ambulance, EmergencyCall, WsEvent } from "@/lib/types";
import CallList from "@/components/CallList";

// Leaflet faqat brauzerda ishlaydi (SSR o'chirilgan)
const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-slate-500">
      {uz.map}...
    </div>
  ),
});

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [calls, setCalls] = useState<EmergencyCall[]>([]);
  const [ambulances, setAmbulances] = useState<Ambulance[]>([]);
  const [busyId, setBusyId] = useState<number | null>(null);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  const loadCalls = useCallback(async () => {
    try {
      const res = await api.listCalls();
      setCalls(res.items);
    } catch {
      /* ignore */
    }
  }, []);

  const loadAmbulances = useCallback(async () => {
    try {
      const res = await api.listAmbulances();
      setAmbulances(res.items);
    } catch {
      /* ignore */
    }
  }, []);

  // Boshlang'ich yuklash + murojaatlarni har 5s yangilash
  useEffect(() => {
    if (!user) return;
    loadCalls();
    loadAmbulances();
    const t = setInterval(loadCalls, 5000);
    return () => clearInterval(t);
  }, [user, loadCalls, loadAmbulances]);

  // Jonli WebSocket voqealari
  const onWs = useCallback(
    (ev: WsEvent) => {
      if (ev.type === "ambulance_location" || ev.type === "ambulance_status") {
        setAmbulances((prev) =>
          prev.map((a) =>
            a.id === ev.ambulance_id
              ? {
                  ...a,
                  status: ev.status,
                  ...("latitude" in ev
                    ? { latitude: ev.latitude, longitude: ev.longitude }
                    : {}),
                }
              : a,
          ),
        );
      } else if (ev.type === "dispatch") {
        loadCalls();
        loadAmbulances();
      }
    },
    [loadCalls, loadAmbulances],
  );
  const connected = useWebSocket(onWs);

  async function handleTriage(id: number) {
    setBusyId(id);
    try {
      await api.changeCallStatus(id, "triaged", "Operator triaj qildi");
      await loadCalls();
    } finally {
      setBusyId(null);
    }
  }

  async function handleDispatch(id: number) {
    setBusyId(id);
    try {
      await api.dispatchCall(id);
      await loadCalls();
      await loadAmbulances();
    } catch (e) {
      alert((e as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  if (loading || !user) return null;

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-slate-700 px-5 py-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-red-500">103</span>
          <span className="font-semibold">{uz.appName}</span>
          <span className="ml-3 hidden text-xs text-slate-400 sm:inline">
            {uz.dashboard}
          </span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span
            className={`flex items-center gap-1 ${
              connected ? "text-green-400" : "text-slate-500"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                connected ? "bg-green-400" : "bg-slate-500"
              }`}
            />
            {connected ? uz.connected : uz.disconnected}
          </span>
          <span className="text-slate-400">{user.full_name}</span>
          <button
            onClick={logout}
            className="rounded-lg bg-slate-700 px-3 py-1 text-xs hover:bg-slate-600"
          >
            {uz.logout}
          </button>
        </div>
      </header>

      <main className="grid flex-1 grid-cols-1 gap-4 overflow-hidden p-4 lg:grid-cols-[minmax(0,420px)_1fr]">
        <section className="flex flex-col overflow-hidden">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-300">
              {uz.calls} ({calls.length})
            </h2>
            <button
              onClick={loadCalls}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              {uz.refresh}
            </button>
          </div>
          <div className="flex-1 overflow-y-auto pr-1">
            <CallList
              calls={calls}
              onTriage={handleTriage}
              onDispatch={handleDispatch}
              busyId={busyId}
            />
          </div>
        </section>

        <section className="overflow-hidden rounded-xl">
          <MapView ambulances={ambulances} calls={calls} />
        </section>
      </main>
    </div>
  );
}

"use client";

import type { EmergencyCall } from "@/lib/types";
import { statusLabel, uz } from "@/lib/i18n";
import PriorityBadge from "./PriorityBadge";

export default function CallList({
  calls,
  onTriage,
  onDispatch,
  busyId,
}: {
  calls: EmergencyCall[];
  onTriage: (id: number) => void;
  onDispatch: (id: number) => void;
  busyId: number | null;
}) {
  if (calls.length === 0) {
    return <p className="p-4 text-sm text-slate-400">{uz.noCalls}</p>;
  }

  return (
    <div className="space-y-3">
      {calls.map((c) => (
        <div
          key={c.id}
          className="rounded-xl bg-slate-800/60 p-4 ring-1 ring-slate-700"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-300">#{c.id}</span>
                <PriorityBadge priority={c.priority} />
                <span className="rounded bg-slate-700 px-2 py-0.5 text-xs text-slate-300">
                  {statusLabel[c.status] ?? c.status}
                </span>
              </div>
              <p className="mt-1 truncate text-sm text-slate-100">{c.complaint}</p>
            </div>
          </div>

          {c.ai_recommended_brigade && (
            <div className="mt-2 rounded-lg bg-slate-900/60 p-2 text-xs text-slate-400">
              <span className="text-slate-300">{uz.aiTriage}:</span>{" "}
              {uz.recommendedBrigade}: <b>{c.ai_recommended_brigade}</b> ·{" "}
              {uz.confidence}: {Math.round((c.ai_confidence ?? 0) * 100)}%
              {c.priority_source === "manual" && (
                <span className="ml-1 text-amber-400">(qo&apos;lda o&apos;zgartirilgan)</span>
              )}
              {c.ai_reason && <div className="mt-0.5 italic">{c.ai_reason}</div>}
            </div>
          )}

          <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
            <span>{c.caller_phone}</span>
            {c.address_text && <span>· {c.address_text}</span>}
          </div>

          <div className="mt-3 flex gap-2">
            {c.status === "new" && (
              <button
                onClick={() => onTriage(c.id)}
                disabled={busyId === c.id}
                className="rounded-lg bg-slate-600 px-3 py-1 text-xs font-medium hover:bg-slate-500 disabled:opacity-50"
              >
                {uz.markTriaged}
              </button>
            )}
            {c.status === "triaged" && c.latitude != null && (
              <button
                onClick={() => onDispatch(c.id)}
                disabled={busyId === c.id}
                className="rounded-lg bg-red-600 px-3 py-1 text-xs font-semibold hover:bg-red-500 disabled:opacity-50"
              >
                {uz.dispatch}
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

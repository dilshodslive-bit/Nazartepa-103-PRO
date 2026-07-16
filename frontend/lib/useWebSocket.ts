"use client";

import { useEffect, useRef, useState } from "react";
import { getToken } from "./api";
import type { WsEvent } from "./types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/dispatch";

/** /ws/dispatch ga ulanadi va kelgan voqealarni callback orqali uzatadi.
 *  Uzilganda avtomatik qayta ulanadi. */
export function useWebSocket(onEvent: (ev: WsEvent) => void): boolean {
  const [connected, setConnected] = useState(false);
  const cbRef = useRef(onEvent);
  cbRef.current = onEvent;

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    let ws: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | null = null;
    let closed = false;

    function connect() {
      ws = new WebSocket(`${WS_URL}?token=${token}`);
      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        if (!closed) retry = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws?.close();
      ws.onmessage = (e) => {
        try {
          cbRef.current(JSON.parse(e.data) as WsEvent);
        } catch {
          /* ignore */
        }
      };
    }
    connect();

    return () => {
      closed = true;
      if (retry) clearTimeout(retry);
      ws?.close();
    };
  }, []);

  return connected;
}

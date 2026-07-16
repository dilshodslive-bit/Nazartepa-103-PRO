"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import type { Ambulance, EmergencyCall } from "@/lib/types";
import { ambulanceStatusLabel } from "@/lib/i18n";

// Toshkent markazi
const CENTER: [number, number] = [41.311, 69.24];

const AMB_COLORS: Record<string, string> = {
  available: "#16a34a",
  dispatched: "#d97706",
  en_route: "#2563eb",
  on_scene: "#7c3aed",
  busy: "#dc2626",
  offline: "#64748b",
};

const PRIORITY_COLORS: Record<string, string> = {
  red: "#dc2626",
  yellow: "#d97706",
  green: "#16a34a",
};

function dotIcon(color: string, label: string): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div style="background:${color};width:22px;height:22px;border-radius:50%;
      border:2px solid #fff;box-shadow:0 0 4px rgba(0,0,0,.5);display:flex;
      align-items:center;justify-content:center;color:#fff;font-size:11px;
      font-weight:700">${label}</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
}

export default function MapView({
  ambulances,
  calls,
}: {
  ambulances: Ambulance[];
  calls: EmergencyCall[];
}) {
  return (
    <MapContainer
      center={CENTER}
      zoom={12}
      className="h-full w-full rounded-xl"
      scrollWheelZoom
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap"
      />

      {calls
        .filter((c) => c.latitude != null && c.longitude != null)
        .map((c) => (
          <Marker
            key={`c-${c.id}`}
            position={[c.latitude!, c.longitude!]}
            icon={dotIcon(PRIORITY_COLORS[c.priority ?? "green"] ?? "#64748b", "!")}
          >
            <Popup>
              <b>#{c.id}</b> — {c.complaint}
              <br />
              {c.address_text ?? ""}
            </Popup>
          </Marker>
        ))}

      {ambulances
        .filter((a) => a.latitude != null && a.longitude != null)
        .map((a) => (
          <Marker
            key={`a-${a.id}`}
            position={[a.latitude!, a.longitude!]}
            icon={dotIcon(AMB_COLORS[a.status] ?? "#64748b", "A")}
          >
            <Popup>
              <b>{a.callsign}</b> ({a.brigade_type})
              <br />
              {ambulanceStatusLabel[a.status] ?? a.status}
            </Popup>
          </Marker>
        ))}
    </MapContainer>
  );
}

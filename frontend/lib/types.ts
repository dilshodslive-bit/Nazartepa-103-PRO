export type Priority = "red" | "yellow" | "green";
export type CallStatus =
  | "new"
  | "triaged"
  | "dispatched"
  | "en_route"
  | "on_scene"
  | "completed"
  | "cancelled";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface EmergencyCall {
  id: number;
  caller_phone: string;
  caller_name: string | null;
  address_text: string | null;
  latitude: number | null;
  longitude: number | null;
  complaint: string;
  status: CallStatus;
  priority: Priority | null;
  priority_source: "ai" | "manual" | null;
  ai_severity: number | null;
  ai_recommended_brigade: string | null;
  ai_confidence: number | null;
  ai_reason: string | null;
  ai_provider: string | null;
  created_at: string;
}

export type AmbulanceStatus =
  | "available"
  | "dispatched"
  | "en_route"
  | "on_scene"
  | "busy"
  | "offline";

export interface Ambulance {
  id: number;
  callsign: string;
  brigade_type: string;
  status: AmbulanceStatus;
  latitude: number | null;
  longitude: number | null;
  current_call_id: number | null;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

// WebSocket voqea turlari
export type WsEvent =
  | {
      type: "ambulance_location";
      ambulance_id: number;
      callsign: string;
      latitude: number;
      longitude: number;
      status: AmbulanceStatus;
    }
  | {
      type: "ambulance_status";
      ambulance_id: number;
      callsign: string;
      status: AmbulanceStatus;
    }
  | {
      type: "dispatch";
      call_id: number;
      ambulance_id: number;
      callsign: string;
      distance_km: number;
      eta_minutes: number;
    };

export interface UserMessage {
  id: string;
  message: string;
  source: "discord" | "nextjs" | "api";
  user_id?: string;
  metadata?: Record<string, any>;
  is_confirmation?: boolean;
  confirmation_for?: string;
  confirmation_value?: boolean;
}

export interface ServerMessage {
  type: 
    | "welcome"
    | "message_processed"
    | "mission_confirmation"
    | "mission_confirmed"
    | "mission_cancelled"
    | "mission_execution_starting"
    | "mission_execution_result"
    | "mission_execution_blocked"
    | "error";
  id?: string;
  status?: "processed" | "error" | "rejected";
  message: string;
  timestamp?: string;
  api_version?: string;
  note?: string;
  mission_dsl?: MissionDSL;
  drone_id?: string;
  drone_ip?: string;
  ready?: string;
  reason?: string;
  report?: any;
}

export interface MissionDSL {
  missionId: string;
  understanding?: string;
  segments: MissionSegment[];
}

export interface MissionSegment {
  type: string;
  action: string;
  [key: string]: any;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  missionDSL?: MissionDSL;
  type?: ServerMessage["type"];
}

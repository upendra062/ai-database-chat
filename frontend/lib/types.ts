export interface Message {
  id: string;
  text: string;
  sender: "user" | "assistant";
  timestamp: Date;
  toolsUsed?: string[];
  executionTime?: number;
}

export interface ChatResponse {
  response: string;
  tools_used: string[];
  execution_time_ms: number;
  filtered: boolean;
  metadata?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

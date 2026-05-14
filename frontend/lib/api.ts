import { supabase } from "./supabase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (data.session?.access_token) {
    headers["Authorization"] = `Bearer ${data.session.access_token}`;
  }
  return headers;
}

export async function sendChatMessage(message: string, sessionId: string = "default") {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to send message");
  }
  return res.json();
}

export async function streamChatMessage(
  message: string,
  sessionId: string,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: string) => void
) {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers,
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    onError(err.detail || "Failed to send message");
    return;
  }

  const reader = res.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    onError("Streaming not supported");
    return;
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const data = JSON.parse(line.slice(6));
        if (data.type === "token") onToken(data.content);
        else if (data.type === "done") { onDone(); return; }
        else if (data.type === "error") { onError(data.content); return; }
      } catch {}
    }
  }
  onDone();
}

export async function getHealthStatus() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return res.json();
}

import axios from "axios";
import { ChatRequest, ChatResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function sendChatMessage(
  message: string,
  sessionId: string = "default"
): Promise<ChatResponse> {
  try {
    const response = await apiClient.post<ChatResponse>("/chat", {
      message,
      session_id: sessionId,
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || "Failed to send message");
  }
}

export async function getHealthStatus(): Promise<{ status: string }> {
  try {
    const response = await apiClient.get("/health");
    return response.data;
  } catch (error) {
    throw new Error("Health check failed");
  }
}

export async function getLogsSummary(): Promise<any> {
  try {
    const response = await apiClient.get("/logs/summary");
    return response.data;
  } catch (error) {
    throw new Error("Failed to fetch logs summary");
  }
}

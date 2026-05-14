from typing import List, Dict
from database import SupabaseDB

MAX_HISTORY_MESSAGES = 20  # load last 20 messages (10 turns) per session


class MemoryStore:
    @staticmethod
    def save(session_id: str, role: str, content: str, user_id: str = None):
        try:
            record = {"session_id": session_id, "role": role, "content": content}
            if user_id:
                record["user_id"] = user_id
            SupabaseDB.get_client().table("conversations").insert(record).execute()
        except Exception:
            pass  # memory failure must never block the chat

    @staticmethod
    def load(session_id: str) -> List[Dict]:
        try:
            result = (
                SupabaseDB.get_client()
                .table("conversations")
                .select("role, content")
                .eq("session_id", session_id)
                .order("created_at")
                .limit(MAX_HISTORY_MESSAGES)
                .execute()
            )
            return result.data if result and result.data else []
        except Exception:
            return []

    @staticmethod
    def format_for_prompt(history: List[Dict]) -> str:
        if not history:
            return ""
        lines = ["Here is the conversation history so far:"]
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

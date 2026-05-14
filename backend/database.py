import os
from supabase import create_client, Client
from config import get_settings


class SupabaseDB:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            settings = get_settings()
            cls._instance = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        return cls._instance

    @classmethod
    def execute_query(cls, table: str, query_type: str = "select", **kwargs):
        client = cls.get_client()

        if query_type == "select":
            return client.table(table).select("*").execute()
        elif query_type == "select_filtered":
            response = client.table(table).select("*")
            for key, value in kwargs.items():
                if isinstance(value, tuple):
                    response = response.gte(key, value[0]).lte(key, value[1])
                else:
                    response = response.eq(key, value)
            return response.execute()

        return None


def init_db():
    try:
        client = SupabaseDB.get_client()
        # Light connectivity check — fails fast if key is wrong
        client.table("students").select("id").limit(1).execute()
        print("✓ Supabase connected successfully")
    except Exception as e:
        # Allow startup to continue so /health still responds; DB queries will surface errors per-request
        print(f"⚠ Supabase connection warning: {e}")

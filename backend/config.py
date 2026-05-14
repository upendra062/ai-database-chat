import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    fastapi_port: int = int(os.getenv("FASTAPI_PORT", 8000))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "https://rockyai.dev",
        "https://www.rockyai.dev",
        "https://ai-database-chat.vercel.app",
    ]

    # Guardrail configurations
    max_input_length: int = 2000
    max_output_length: int = 10000
    max_results_per_query: int = 10000
    max_query_execution_time: int = 30
    rate_limit_requests_per_minute: int = 10
    max_json_depth: int = 5

    # Allowed tools
    allowed_tools: list = [
        "query_students",
        "query_courses",
        "query_transactions",
        "get_student_courses",
        "get_course_students",
        "get_student_transaction_summary",
        "get_course_statistics",
    ]

    # SQL injection patterns to block
    sql_injection_patterns: list = [
        r"(?i)(DROP|DELETE|UPDATE|INSERT|EXEC|EXECUTE|CREATE|ALTER)",
        r"(?i)(--|;|/\*|\*/|xp_|sp_)",
        r"(?i)(UNION|HAVING|WHERE\s+1\s*=\s*1)",
    ]

    # Prompt injection patterns to block
    prompt_injection_patterns: list = [
        r"(?i)(ignore|disregard|forget|override).*previous",
        r"(?i)(new instructions|system instructions|prompt)",
        r"(?i)(system message|admin|root)",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()

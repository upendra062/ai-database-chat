import re
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Tuple, Dict
from config import get_settings
from guardrails.monitoring_layer import MonitoringLayer


class InputLayer:
    def __init__(self, monitoring: MonitoringLayer):
        self.settings = get_settings()
        self.monitoring = monitoring
        self.rate_limiter: Dict[str, list] = defaultdict(list)

    def validate_input(self, user_input: str, session_id: str = "unknown") -> Tuple[bool, str]:
        user_input_hash = hashlib.sha256(user_input.encode()).hexdigest()

        if not user_input or not user_input.strip():
            self.monitoring.log_guardrail_block(
                layer="input",
                reason="empty_input",
                user_input_hash=user_input_hash,
            )
            return False, "Input cannot be empty"

        if len(user_input) > self.settings.max_input_length:
            self.monitoring.log_guardrail_block(
                layer="input",
                reason="input_too_long",
                user_input_hash=user_input_hash,
                details={"max": self.settings.max_input_length, "actual": len(user_input)},
            )
            return False, f"Input exceeds maximum length of {self.settings.max_input_length}"

        if not self._check_rate_limit(session_id):
            self.monitoring.log_guardrail_block(
                layer="input",
                reason="rate_limit_exceeded",
                user_input_hash=user_input_hash,
                details={"session_id": session_id},
            )
            return False, "Rate limit exceeded. Maximum 10 requests per minute."

        for pattern in self.settings.sql_injection_patterns:
            if re.search(pattern, user_input):
                self.monitoring.log_guardrail_block(
                    layer="input",
                    reason="sql_injection_detected",
                    user_input_hash=user_input_hash,
                    details={"pattern": pattern},
                )
                return False, "Invalid input detected"

        sanitized = self._sanitize_input(user_input)
        self.monitoring.log_request(user_input, session_id)
        return True, sanitized

    def _sanitize_input(self, text: str) -> str:
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _check_rate_limit(self, session_id: str) -> bool:
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)

        self.rate_limiter[session_id] = [
            ts for ts in self.rate_limiter[session_id]
            if ts > cutoff
        ]

        if len(self.rate_limiter[session_id]) >= self.settings.rate_limit_requests_per_minute:
            return False

        self.rate_limiter[session_id].append(now)
        return True

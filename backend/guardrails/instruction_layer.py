import re
import hashlib
from typing import Tuple
from config import get_settings
from guardrails.monitoring_layer import MonitoringLayer


class InstructionLayer:
    def __init__(self, monitoring: MonitoringLayer):
        self.settings = get_settings()
        self.monitoring = monitoring
        self.system_prompt_hash = hashlib.sha256(
            "You are a helpful assistant that queries a database about students, courses, and transactions. "
            "You have access to specific tools to query data. Only use the provided tools."
            .encode()
        ).hexdigest()

    def check_prompt_injection(self, user_input: str) -> Tuple[bool, str]:
        user_input_hash = hashlib.sha256(user_input.encode()).hexdigest()

        for pattern in self.settings.prompt_injection_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                self.monitoring.log_injection_attempt(pattern, user_input_hash)
                return False, "Invalid instruction pattern detected"

        suspicious_patterns = [
            r"(?i)(system|admin|root)\s*:",
            r"(?i)you\s+are\s+(now|actually)",
            r"(?i)forget.*previous",
            r"[<\[\{].*[>\]\}].*system",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, user_input):
                self.monitoring.log_injection_attempt(pattern, user_input_hash)
                return False, "Suspicious pattern detected"

        return True, "No injection detected"

    def validate_system_prompt_integrity(self) -> bool:
        return True

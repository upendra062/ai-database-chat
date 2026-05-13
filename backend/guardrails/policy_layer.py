import hashlib
from typing import Tuple, List, Dict, Any
from config import get_settings
from guardrails.monitoring_layer import MonitoringLayer


class PolicyLayer:
    def __init__(self, monitoring: MonitoringLayer):
        self.settings = get_settings()
        self.monitoring = monitoring

    def check_tool_access(self, tool_name: str, user_input_hash: str = "") -> Tuple[bool, str]:
        if tool_name not in self.settings.allowed_tools:
            self.monitoring.log_guardrail_block(
                layer="policy",
                reason="tool_not_allowed",
                user_input_hash=user_input_hash,
                details={"tool": tool_name, "allowed_tools": self.settings.allowed_tools},
            )
            return False, f"Tool '{tool_name}' is not allowed"

        self.monitoring.log_event(
            layer="policy",
            event_type="tool_access",
            action="allowed",
            tool_name=tool_name,
        )
        return True, "Allowed"

    def validate_query_scope(self, results_count: int, user_input_hash: str = "") -> Tuple[bool, str]:
        if results_count > self.settings.max_results_per_query:
            self.monitoring.log_guardrail_block(
                layer="policy",
                reason="query_scope_exceeded",
                user_input_hash=user_input_hash,
                details={"max": self.settings.max_results_per_query, "actual": results_count},
            )
            return False, f"Query results exceed maximum of {self.settings.max_results_per_query}"

        return True, "Query scope valid"

    def validate_execution_time(self, execution_time_ms: float, user_input_hash: str = "") -> Tuple[bool, str]:
        if execution_time_ms > (self.settings.max_query_execution_time * 1000):
            self.monitoring.log_guardrail_block(
                layer="policy",
                reason="execution_time_exceeded",
                user_input_hash=user_input_hash,
                details={"max_ms": self.settings.max_query_execution_time * 1000, "actual_ms": execution_time_ms},
            )
            return False, f"Query execution time exceeded {self.settings.max_query_execution_time} seconds"

        return True, "Execution time valid"

    def get_allowed_tools(self) -> List[str]:
        return self.settings.allowed_tools

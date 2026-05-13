import json
from typing import Any, Dict, List, Tuple
from config import get_settings
from guardrails.monitoring_layer import MonitoringLayer


class OutputLayer:
    def __init__(self, monitoring: MonitoringLayer):
        self.settings = get_settings()
        self.monitoring = monitoring
        self.sensitive_fields = {"password", "secret", "token", "api_key", "private_key"}

    def filter_output(self, data: Any, tools_used: List[str]) -> Tuple[Any, bool]:
        filtered = False

        if isinstance(data, list):
            if len(data) > self.settings.max_results_per_query:
                self.monitoring.log_event(
                    layer="output",
                    event_type="truncation",
                    action="truncated",
                    original_count=len(data),
                    truncated_count=self.settings.max_results_per_query,
                )
                data = data[:self.settings.max_results_per_query]
                filtered = True

            cleaned = []
            for item in data:
                if isinstance(item, dict):
                    cleaned_item = self._remove_sensitive_fields(item)
                    cleaned.append(cleaned_item)
                else:
                    cleaned.append(item)
            data = cleaned
            filtered = True

        elif isinstance(data, dict):
            data = self._remove_sensitive_fields(data)
            filtered = True

        output_size = len(json.dumps(data))
        if output_size > self.settings.max_output_length:
            self.monitoring.log_event(
                layer="output",
                event_type="truncation",
                action="summarized",
                original_size=output_size,
                truncated_size=self.settings.max_output_length,
            )
            filtered = True

        self.monitoring.log_response(
            output_size=output_size,
            tools_used=tools_used,
            execution_time_ms=0,
            filtered=filtered,
        )

        return data, filtered

    def _remove_sensitive_fields(self, obj: Dict) -> Dict:
        if not isinstance(obj, dict):
            return obj

        cleaned = {}
        for key, value in obj.items():
            if key.lower() in self.sensitive_fields:
                cleaned[key] = "***REDACTED***"
            elif isinstance(value, dict):
                cleaned[key] = self._remove_sensitive_fields(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._remove_sensitive_fields(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value
        return cleaned

    def validate_json_structure(self, data: Any, depth: int = 0) -> bool:
        if depth > self.settings.max_json_depth:
            self.monitoring.log_guardrail_block(
                layer="output",
                reason="json_depth_exceeded",
                details={"max_depth": self.settings.max_json_depth, "actual_depth": depth},
            )
            return False

        if isinstance(data, dict):
            for value in data.values():
                if not self.validate_json_structure(value, depth + 1):
                    return False

        elif isinstance(data, list):
            for item in data:
                if not self.validate_json_structure(item, depth + 1):
                    return False

        return True

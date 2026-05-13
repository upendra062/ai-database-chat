import hashlib
import time
from typing import Tuple, Dict, Any, Callable
from config import get_settings
from guardrails.monitoring_layer import MonitoringLayer


class ExecutionLayer:
    def __init__(self, monitoring: MonitoringLayer):
        self.settings = get_settings()
        self.monitoring = monitoring

    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        allowed_param_types = {str, int, float, bool, list, dict, type(None)}

        for key, value in parameters.items():
            if type(value) not in allowed_param_types:
                self.monitoring.log_guardrail_block(
                    layer="execution",
                    reason="invalid_parameter_type",
                    details={"tool": tool_name, "param": key, "type": str(type(value))},
                )
                return False, f"Invalid parameter type for {key}"

        return True, "Parameters valid"

    def execute_with_timeout(
        self,
        func: Callable,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout_seconds: int = None,
    ) -> Tuple[bool, Any, float]:
        timeout_seconds = timeout_seconds or self.settings.max_query_execution_time
        start_time = time.time()

        try:
            result = func(**parameters)
            execution_time = time.time() - start_time

            if execution_time > timeout_seconds:
                self.monitoring.log_guardrail_block(
                    layer="execution",
                    reason="execution_timeout",
                    details={"tool": tool_name, "timeout": timeout_seconds, "actual": execution_time},
                )
                return False, None, execution_time * 1000

            self.monitoring.log_tool_execution(
                tool_name=tool_name,
                parameters=parameters,
                execution_time_ms=execution_time * 1000,
                status="success",
            )
            return True, result, execution_time * 1000

        except Exception as e:
            execution_time = time.time() - start_time
            self.monitoring.log_tool_execution(
                tool_name=tool_name,
                parameters=parameters,
                execution_time_ms=execution_time * 1000,
                status="error",
            )
            return False, str(e), execution_time * 1000

    def enforce_read_only_mode(self) -> bool:
        return True

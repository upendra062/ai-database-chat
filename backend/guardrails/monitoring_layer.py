import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class MonitoringLayer:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("monitoring")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_dir / "audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_event(
        self,
        layer: str,
        event_type: str,
        action: str,
        reason: str = "",
        severity: str = "info",
        **kwargs
    ):
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "layer": layer,
            "event_type": event_type,
            "action": action,
            "reason": reason,
            "severity": severity,
        }
        event.update(kwargs)

        self.logger.info(json.dumps(event))

    def log_request(self, user_input: str, session_id: str = "unknown"):
        user_input_hash = hashlib.sha256(user_input.encode()).hexdigest()
        self.log_event(
            layer="input",
            event_type="request",
            action="received",
            user_input_hash=user_input_hash,
            session_id=session_id,
            input_length=len(user_input),
        )

    def log_guardrail_block(
        self,
        layer: str,
        reason: str,
        user_input_hash: str = "",
        details: Dict[str, Any] = None,
    ):
        self.log_event(
            layer=layer,
            event_type="block",
            action="blocked",
            reason=reason,
            severity="warning",
            user_input_hash=user_input_hash,
            details=details or {},
        )

    def log_tool_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        execution_time_ms: float,
        status: str = "success",
    ):
        self.log_event(
            layer="execution",
            event_type="tool_execution",
            action="executed",
            tool_name=tool_name,
            parameters=parameters,
            execution_time_ms=execution_time_ms,
            status=status,
        )

    def log_response(
        self,
        output_size: int,
        tools_used: list,
        execution_time_ms: float,
        filtered: bool = False,
    ):
        self.log_event(
            layer="output",
            event_type="response",
            action="sent",
            output_size=output_size,
            tools_used=tools_used,
            execution_time_ms=execution_time_ms,
            filtered=filtered,
        )

    def log_injection_attempt(self, pattern: str, user_input_hash: str):
        self.log_event(
            layer="instruction",
            event_type="injection_attempt",
            action="blocked",
            reason="prompt_injection_detected",
            severity="critical",
            pattern=pattern,
            user_input_hash=user_input_hash,
        )

    def get_audit_summary(self):
        audit_file = self.log_dir / "audit.log"
        if not audit_file.exists():
            return {"total_events": 0, "blocks": 0, "errors": 0}

        events = {"total": 0, "blocked": 0, "errors": 0, "by_layer": {}}

        with open(audit_file) as f:
            for line in f:
                try:
                    event = json.loads(line)
                    events["total"] += 1

                    layer = event.get("layer", "unknown")
                    if layer not in events["by_layer"]:
                        events["by_layer"][layer] = 0
                    events["by_layer"][layer] += 1

                    if event.get("action") == "blocked":
                        events["blocked"] += 1
                    if event.get("severity") == "critical":
                        events["errors"] += 1
                except json.JSONDecodeError:
                    continue

        return events

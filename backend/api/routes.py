import hashlib
import time
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse, ErrorResponse
from agent.agent import DatabaseAgent
from guardrails.monitoring_layer import MonitoringLayer
from guardrails.input_layer import InputLayer
from guardrails.policy_layer import PolicyLayer
from guardrails.instruction_layer import InstructionLayer
from guardrails.execution_layer import ExecutionLayer
from guardrails.output_layer import OutputLayer

router = APIRouter()

monitoring = MonitoringLayer()
input_layer = InputLayer(monitoring)
policy_layer = PolicyLayer(monitoring)
instruction_layer = InstructionLayer(monitoring)
execution_layer = ExecutionLayer(monitoring)
output_layer = OutputLayer(monitoring)

agent = None


def initialize_agent():
    global agent
    try:
        agent = DatabaseAgent()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_input_hash = hashlib.sha256(request.message.encode()).hexdigest()
    start_time = time.time()

    is_valid, sanitized_input = input_layer.validate_input(
        request.message,
        request.session_id
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=sanitized_input)

    is_safe, message = instruction_layer.check_prompt_injection(sanitized_input)
    if not is_safe:
        raise HTTPException(status_code=400, detail=message)

    if not agent:
        initialize_agent()

    try:
        response = agent.run(sanitized_input)

        output_data, filtered = output_layer.filter_output(
            {"response": response},
            tools_used=[]
        )

        execution_time = (time.time() - start_time) * 1000

        policy_layer.validate_execution_time(execution_time, user_input_hash)

        monitoring.log_response(
            output_size=len(response),
            tools_used=[],
            execution_time_ms=execution_time,
            filtered=filtered,
        )

        return ChatResponse(
            response=response,
            tools_used=[],
            execution_time_ms=execution_time,
            filtered=filtered,
            metadata={"session_id": request.session_id},
        )

    except Exception as e:
        monitoring.log_event(
            layer="execution",
            event_type="error",
            action="failed",
            reason=str(e),
            severity="critical",
        )
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/logs/summary")
async def get_logs_summary():
    return monitoring.get_audit_summary()

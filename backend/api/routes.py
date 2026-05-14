import hashlib
import time
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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
        print("✓ Agent initialized")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")


def _validate_request(message: str, session_id: str):
    is_valid, sanitized = input_layer.validate_input(message, session_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=sanitized)
    is_safe, msg = instruction_layer.check_prompt_injection(sanitized)
    if not is_safe:
        raise HTTPException(status_code=400, detail=msg)
    return sanitized


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_input_hash = hashlib.sha256(request.message.encode()).hexdigest()
    start_time = time.time()

    sanitized_input = _validate_request(request.message, request.session_id)

    if not agent:
        initialize_agent()

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: agent.run(sanitized_input, request.session_id)
        )

        output_data, filtered = output_layer.filter_output({"response": response}, tools_used=[])
        execution_time = (time.time() - start_time) * 1000
        policy_layer.validate_execution_time(execution_time, user_input_hash)
        monitoring.log_response(output_size=len(response), tools_used=[], execution_time_ms=execution_time, filtered=filtered)

        return ChatResponse(
            response=response,
            tools_used=[],
            execution_time_ms=execution_time,
            filtered=filtered,
            metadata={"session_id": request.session_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        monitoring.log_event(layer="execution", event_type="error", action="failed", reason=str(e), severity="critical")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    sanitized_input = _validate_request(request.message, request.session_id)

    if not agent:
        initialize_agent()

    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start'})}\n\n"

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: agent.run(sanitized_input, request.session_id)
            )

            # Stream response word by word for natural feel
            words = response.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                await asyncio.sleep(0.03)

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/logs/summary")
async def get_logs_summary():
    return monitoring.get_audit_summary()

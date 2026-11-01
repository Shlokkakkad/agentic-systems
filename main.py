import time
import uuid
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from pydantic import BaseModel
from agent_crew import run_orchestrated_crew, input_guardrail_mask_pii
from review_stage import execute_autogen_review_stage

app = FastAPI(title="Cred Banking Support Operations Core Engine", version="1.0.0")

class AskRequest(BaseModel):
    query: str
    session_id: str = "default-session"

class AskResponse(BaseModel):
    trace_id: str
    response: str
    requires_escalation: bool
    processing_time_ms: float

# Task 15 Compliance: Token / Cost Budget Matrix Limits Configuration
MAX_REQUEST_CHARACTER_BUDGET = 400

@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    """Task 12: ELK Structured Logging Layer enforcing strict PII protection disk metrics."""
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    
    # Capture and intercept stream safely
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8") if body_bytes else ""
    
    # Enforce PII filter constraints on log components completely
    clean_log_payload = input_guardrail_mask_pii(body_str)
    
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    
    log_entry = {
        "trace_id": trace_id,
        "timestamp": time.time(),
        "path": request.url.path,
        "duration_ms": round(duration, 2),
        "payload_snapshot": clean_log_payload
    }
    # Outputs a single structural JSON-Lines log line cleanly to sys.stdout/disk pipes
    print(json.dumps(log_entry))
    return response

@app.post("/ask", response_model=AskResponse)
async def handle_ask_endpoint(payload: AskRequest):
    """Core synchronous evaluation routing stage."""
    # Runtime Cost Budget Check
    if len(payload.query) > MAX_REQUEST_CHARACTER_BUDGET:
        raise HTTPException(status_code=400, detail="Payload Volume Exceeded: Cost token constraint budget violated.")
        
    start = time.time()
    crew_output = run_orchestrated_crew(payload.query)
    
    # Chain down verifying validation pipeline through AutoGen reviewer stage safely
    reviewed_verdict = execute_autogen_review_stage(crew_output.resolved_response, "Knowledge Core Verification")
    
    duration = (time.time() - start) * 1000
    return AskResponse(
        trace_id=str(uuid.uuid4()),
        response=reviewed_verdict.final_answer,
        requires_escalation=crew_output.requires_escalation,
        processing_time_ms=round(duration, 2)
    )

@app.websocket("/chat")
async def handle_websocket_conversational_loop(websocket: WebSocket):
    """Task 11: Real-time dual direction state engine sustaining connection disruptions."""
    await websocket.accept()
    session_history = []
    try:
        while True:
            data = await websocket.receive_text()
            input_data = json.loads(data)
            user_msg = input_data.get("query", "")
            
            crew_output = run_orchestrated_crew(user_msg, session_history=" ".join(session_history))
            session_history.append(f"User: {user_msg} Agent: {crew_output.resolved_response}")
            
            await websocket.send_json({
                "response": crew_output.resolved_response,
                "requires_escalation": crew_output.requires_escalation
            })
    except WebSocketDisconnect:
        # Gracefully handle network terminations without interrupting adjacent worker threads
        print("WebSocket disconnected successfully. Cleaning up allocations safely.")

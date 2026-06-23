import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.ingestion.pipeline import run_pipeline
from backend.rag.engine import ask
from backend.websocket.sentiment import score_message, check_escalation

load_dotenv()
import sys
import os
# Validate required env vars on startup
REQUIRED_ENV_VARS = ["GROQ_API_KEY", "CHROMA_DB_PATH"]
missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing:
    print(f"[ERROR] Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)

app = FastAPI(title="RAG Support Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
sessions = {}
active_connections = {}  # session_id -> WebSocket


class IngestRequest(BaseModel):
    source: str


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(request: IngestRequest):
    try:
        result = run_pipeline(request.source)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(request: AskRequest):
    try:
        result = ask(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
def get_sessions():
    escalated = {
        sid: data for sid, data in sessions.items()
        if data.get("escalated")
    }
    return {"escalated_sessions": escalated, "count": len(escalated)}


@app.post("/agent-reply/{session_id}")
async def agent_reply(session_id: str, request: AskRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[session_id]["history"].append({
        "role": "agent",
        "content": request.question,
    })

    # Push reply to user in real time if still connected
    if session_id in active_connections:
        ws = active_connections[session_id]
        try:
            await ws.send_text(json.dumps({
                "type": "agent_message",
                "answer": request.question,
            }))
        except Exception:
            pass

    return {"status": "reply sent", "session_id": session_id}


@app.websocket("/chat/{session_id}")
async def chat_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_connections[session_id] = websocket

    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "sentiment_scores": [],
            "escalated": False,
        }

    session = sessions[session_id]
    print(f"[WS] Session connected: {session_id}")

    try:
        while True:
            user_message = await websocket.receive_text()
            print(f"[WS] [{session_id}] User: {user_message}")

            if session["escalated"]:
                await websocket.send_text(json.dumps({
                    "type": "escalate",
                    "answer": "You are already connected to a human agent.",
                    "history": session["history"],
                }))
                continue

            # Score sentiment
            score = score_message(user_message)
            session["sentiment_scores"].append(score)

            session["history"].append({
                "role": "user",
                "content": user_message,
                "sentiment": score,
            })

            # Send typing indicator
            await websocket.send_text(json.dumps({"type": "typing"}))

            # Check escalation
            if check_escalation(session["sentiment_scores"], user_message):
                session["escalated"] = True
                print(f"[WS] ESCALATING session: {session_id}")
                await websocket.send_text(json.dumps({
                    "type": "escalate",
                    "answer": "I'm connecting you to a human agent now. Please hold on.",
                    "history": session["history"],
                }))
                continue

            # Get RAG response
            result = ask(user_message)

            session["history"].append({
                "role": "assistant",
                "content": result["answer"],
                "source": result.get("source"),
            })

            await websocket.send_text(json.dumps({
                "type": "message",
                "answer": result["answer"],
                "fallback": result["fallback"],
                "source": result.get("source"),
                "sentiment_score": round(score, 3),
                "session_id": session_id,
            }))

    except WebSocketDisconnect:
        print(f"[WS] Session disconnected: {session_id}")
        active_connections.pop(session_id, None)
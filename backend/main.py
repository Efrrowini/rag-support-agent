from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.ingestion.pipeline import run_pipeline
from backend.rag.engine import ask

load_dotenv()

app = FastAPI(title="RAG Support Agent")

# In-memory session store
sessions = {}


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


@app.websocket("/chat/{session_id}")
async def chat_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Initialize session history
    if session_id not in sessions:
        sessions[session_id] = []

    print(f"[WS] Session connected: {session_id}")

    try:
        while True:
            # Receive message from client
            user_message = await websocket.receive_text()
            print(f"[WS] [{session_id}] User: {user_message}")

            # Append to session history
            sessions[session_id].append({
                "role": "user",
                "content": user_message
            })

            # Get RAG response
            result = ask(user_message)

            # Append bot reply to history
            sessions[session_id].append({
                "role": "assistant",
                "content": result["answer"]
            })

            # Send response back to client
            import json
            await websocket.send_text(json.dumps({
                "type": "message",
                "answer": result["answer"],
                "fallback": result["fallback"],
                "source": result.get("source"),
                "session_id": session_id,
            }))

    except WebSocketDisconnect:
        print(f"[WS] Session disconnected: {session_id}")
        # Keep session history in memory after disconnect
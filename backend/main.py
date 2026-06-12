from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.ingestion.pipeline import run_pipeline
from backend.rag.engine import ask

load_dotenv()

app = FastAPI(title="RAG Support Agent")


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
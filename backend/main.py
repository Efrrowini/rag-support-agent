from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.ingestion.pipeline import run_pipeline

load_dotenv()

app = FastAPI(title="RAG Support Agent")


class IngestRequest(BaseModel):
    source: str


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
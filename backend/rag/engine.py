import os
import json
import time
from datetime import datetime
from groq import Groq
from backend.ingestion.embedder import embed
from backend.vectordb.store import query
from backend.rag.fallback import get_fallback_response

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.55"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

client = None

def get_client():
    global client
    if client is None:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return client

SYSTEM_PROMPT = """You are a customer support assistant for VortexIQ.
You MUST answer ONLY using the context provided below.
Do not use any outside knowledge or make anything up.
If the answer is not clearly found in the context, say you don't know.
Be concise, friendly, and helpful.
Always answer in 2-4 sentences maximum."""

LOG_PATH = "logs/rag.jsonl"


def log_interaction(entry: dict):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def ask(question: str) -> dict:
    start = time.time()

    # Step 1 - Embed the question
    question_embedding = embed([question])[0]

    # Step 2 - Retrieve relevant chunks
    results = query(question_embedding, n=3)

    # Step 3 - Check similarity threshold
    if not results or results[0]["score"] > SIMILARITY_THRESHOLD:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "fallback": True,
            "latency_ms": round((time.time() - start) * 1000),
        }
        log_interaction(entry)
        return get_fallback_response()

    # Step 4 - Build context
    context = "\n\n".join([r["text"] for r in results])

    # Step 5 - Call Groq with error handling
    try:
        response = get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            max_tokens=300,
        )
        answer = response.choices[0].message.content

    except Exception as e:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "error": str(e),
            "latency_ms": round((time.time() - start) * 1000),
        }
        log_interaction(entry)
        return {
            "answer": "I'm experiencing technical difficulties. Please try again in a moment.",
            "source": None,
            "fallback": True,
            "error": str(e),
        }

    latency = round((time.time() - start) * 1000)

    # Step 6 - Log interaction
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "source": results[0]["source"],
        "top_score": round(results[0]["score"], 4),
        "chunks_used": len(results),
        "fallback": False,
        "latency_ms": latency,
    }
    log_interaction(entry)

    return {
        "answer": answer,
        "source": results[0]["source"],
        "fallback": False,
        "chunks_used": len(results),
        "top_score": round(results[0]["score"], 4),
        "latency_ms": latency,
    }
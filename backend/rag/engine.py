import os
from groq import Groq
from backend.ingestion.embedder import embed
from backend.vectordb.store import query
from backend.rag.fallback import get_fallback_response

SIMILARITY_THRESHOLD = 0.55

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a customer support assistant for VortexIQ.
You MUST answer ONLY using the context provided below.
Do not use any outside knowledge or make anything up.
If the answer is not clearly found in the context, say you don't know.
Be concise, friendly, and helpful.
Always answer in 2-4 sentences maximum."""


def ask(question: str) -> dict:
    # Step 1 - Embed the question
    question_embedding = embed([question])[0]

    # Step 2 - Retrieve relevant chunks
    results = query(question_embedding, n=3)

    # Step 3 - Check similarity threshold
    if not results or results[0]["score"] > SIMILARITY_THRESHOLD:
        return get_fallback_response()

    # Step 4 - Build context
    context = "\n\n".join([r["text"] for r in results])

    # Step 5 - Call Groq
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        max_tokens=300,
    )

    return {
        "answer": response.choices[0].message.content,
        "source": results[0]["source"],
        "fallback": False,
        "chunks_used": len(results),
        "top_score": round(results[0]["score"], 4),
    }
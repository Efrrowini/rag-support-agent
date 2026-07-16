from dotenv import load_dotenv
load_dotenv()
from backend.ingestion.embedder import embed
from backend.vectordb.store import query

questions = [
    "What is the weather in Bangalore?",
    "Who won the IPL 2025?",
    "Write me a Python function to sort a list.",
    "What is the capital of France?",
    "Tell me a joke.",
]

for q in questions:
    emb = embed([q])[0]
    results = query(emb, n=1)
    print(f"{results[0]['score']:.4f} | {q}")
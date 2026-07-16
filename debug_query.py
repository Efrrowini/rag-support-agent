from backend.ingestion.embedder import embed
from backend.vectordb.store import query

q = "What does the Pro plan include?"
embedding = embed([q])[0]
results = query(embedding, n=3)

for i, r in enumerate(results):
    print(f"Result {i+1} | Score: {r['score']:.4f}")
    print(f"  {r['text'][:150]}")
    print()
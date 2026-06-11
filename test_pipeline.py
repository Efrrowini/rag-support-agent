from backend.ingestion.pipeline import run_pipeline
from backend.ingestion.embedder import embed
from backend.vectordb.store import query

# Step 1 - Run full pipeline
print("=" * 50)
result = run_pipeline("data/sample.pdf")
print(f"\nPipeline summary:")
print(f"  Characters : {result['characters']}")
print(f"  Chunks     : {result['chunks']}")
print(f"  Vectors    : {result['vectors']}")

# Step 2 - Test 3 different queries
print("\n" + "=" * 50)
test_queries = [
    "How do I reset my password?",
    "What are the pricing plans?",
    "How do I connect Slack integration?",
]

for q in test_queries:
    print(f"\nQuery: '{q}'")
    embedding = embed([q])[0]
    results = query(embedding, n=3)
    print(f"Top result (score {results[0]['score']:.4f}):")
    print(f"  {results[0]['text'][:200]}")

print("\n" + "=" * 50)
print("Pipeline test PASSED")
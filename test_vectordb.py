from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_text
from backend.ingestion.embedder import embed
from backend.vectordb.store import upsert, query

SOURCE = "data/sample.pdf"

# Step 1 - Load
print("=" * 50)
print("Step 1: Loading document...")
raw_text = load_document(SOURCE)
print(f"Loaded {len(raw_text)} characters")

# Step 2 - Chunk
print("\nStep 2: Chunking text...")
chunks = chunk_text(raw_text, source=SOURCE)
print(f"Created {len(chunks)} chunks")

# Step 3 - Embed
print("\nStep 3: Embedding chunks...")
texts = [c["text"] for c in chunks]
embeddings = embed(texts)
print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

# Step 4 - Upsert
print("\nStep 4: Storing in ChromaDB...")
upsert(chunks, embeddings)

# Step 5 - Query
print("\nStep 5: Running similarity search...")
test_query = "How do I reset my password?"
query_embedding = embed([test_query])[0]
results = query(query_embedding, n=2)

print(f"\nQuery: '{test_query}'")
print(f"Top {len(results)} results:\n")
for i, r in enumerate(results):
    print(f"Result {i+1}:")
    print(f"  Source : {r['source']}")
    print(f"  Score  : {r['score']:.4f}")
    print(f"  Text   : {r['text'][:200]}")
    print()

print("=" * 50)
print("Vector DB test PASSED")
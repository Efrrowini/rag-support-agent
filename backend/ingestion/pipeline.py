from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_text
from backend.ingestion.embedder import embed
from backend.vectordb.store import upsert


def run_pipeline(source: str) -> dict:
    print(f"\nRunning ingestion pipeline for: {source}")

    # Step 1 - Load
    raw_text = load_document(source)
    print(f"  Loaded: {len(raw_text)} characters")

    # Step 2 - Chunk
    chunks = chunk_text(raw_text, source=source)
    print(f"  Chunked: {len(chunks)} chunks")

    # Step 3 - Embed
    texts = [c["text"] for c in chunks]
    embeddings = embed(texts)
    print(f"  Embedded: {len(embeddings)} vectors")

    # Step 4 - Upsert
    upsert(chunks, embeddings)
    print(f"  Stored in ChromaDB.")

    return {
        "source": source,
        "characters": len(raw_text),
        "chunks": len(chunks),
        "vectors": len(embeddings),
    }

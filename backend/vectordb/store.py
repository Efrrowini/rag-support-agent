import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

def get_collection():
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_store")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(
        name="support_docs",
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def upsert(chunks: list[dict], embeddings: list[list[float]]):
    col = get_collection()
    col.upsert(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
    )
    print(f"Upserted {len(chunks)} chunks into ChromaDB.")


def query(query_embedding: list[float], n: int = 5) -> list[dict]:
    col = get_collection()
    results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(n, col.count()),
    )
    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "source": results["metadatas"][0][i]["source"],
            "score": results["distances"][0][i],
        })
    return chunks
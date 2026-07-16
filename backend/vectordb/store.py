import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue
)

load_dotenv()

COLLECTION_NAME = "support_docs"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output size


def get_client():
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    return QdrantClient(url=url, api_key=api_key)


def get_collection():
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    return client


def upsert(chunks: list[dict], embeddings: list[list[float]]):
    client = get_collection()
    points = [
        PointStruct(
            id=abs(hash(c["id"])) % (2**63),
            vector=embeddings[i],
            payload={
                "text": c["text"],
                "source": c["source"],
                "chunk_index": c["chunk_index"],
                "chunk_id": c["id"],
            }
        )
        for i, c in enumerate(chunks)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Upserted {len(chunks)} chunks into Qdrant.")


def query(query_embedding: list[float], n: int = 5) -> list[dict]:
    client = get_collection()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=n,
        with_payload=True,
    )
    chunks = []
    for r in results.points:
        chunks.append({
            "text": r.payload["text"],
            "source": r.payload["source"],
            "score": 1 - r.score,
        })
    return chunks
def count():
    client = get_collection()
    info = client.get_collection(COLLECTION_NAME)
    return info.points_count
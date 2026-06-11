from sentence_transformers import SentenceTransformer

model = None

def get_model():
    global model
    if model is None:
        print("Loading embedding model (first time only)...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded.")
    return model

def embed(texts: list[str]) -> list[list[float]]:
    m = get_model()
    embeddings = m.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()
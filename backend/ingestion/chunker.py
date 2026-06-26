from pathlib import Path


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 80,
    overlap: int = 15,
) -> list[dict]:
    words = text.split()
    chunks = []
    start = 0
    idx = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_content = " ".join(chunk_words)

        chunks.append({
            "id": f"{Path(source).stem}_chunk_{idx}",
            "text": chunk_content,
            "source": source,
            "chunk_index": idx,
        })

        idx += 1
        start += chunk_size - overlap

    return chunks
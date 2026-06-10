from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_text

SOURCE = "data/sample.pdf"

print("=" * 50)
print(f"Loading: {SOURCE}")
raw_text = load_document(SOURCE)
print(f"Raw text length: {len(raw_text)} characters")
print(f"\nText preview:\n{raw_text[:300]}")

print("\n" + "=" * 50)
chunks = chunk_text(raw_text, source=SOURCE)
print(f"Total chunks: {len(chunks)}")
print(f"\nChunk 0:")
print(f"  ID     : {chunks[0]['id']}")
print(f"  Source : {chunks[0]['source']}")
print(f"  Words  : {len(chunks[0]['text'].split())}")
print(f"  Text   : {chunks[0]['text'][:200]}")
print("=" * 50)
print("Ingestion test PASSED")
from dotenv import load_dotenv
load_dotenv()
from backend.rag.engine import ask, SIMILARITY_THRESHOLD

print(f"Threshold in engine: {SIMILARITY_THRESHOLD}")

result = ask("What is the weather in Bangalore?")
print(f"Fallback: {result['fallback']}")
print(f"Score: {result.get('top_score')}")
print(f"Answer: {result.get('answer')[:100]}")
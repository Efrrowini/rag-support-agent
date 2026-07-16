import requests
import time

BASE_URL = "https://web-production-215bcf.up.railway.app"

questions = [
    "What is the weather in Bangalore?",
    "Tell me a joke.",
    "How do I reset my password?",
]

for q in questions:
    r = requests.post(f"{BASE_URL}/ask", json={"question": q})
    data = r.json()
    print(f"Q: {q[:50]}")
    print(f"   fallback: {data.get('fallback')}")
    print(f"   score: {data.get('top_score')}")
    print(f"   answer: {str(data.get('answer',''))[:80]}")
    print()
    time.sleep(2)
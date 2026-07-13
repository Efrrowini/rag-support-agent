import requests
import time

BASE_URL = "https://web-production-215bcf.up.railway.app"

queries = [
    ("How do I reset my password?", False),
    ("What are the pricing plans?", False),
    ("Is VortexIQ SOC 2 certified?", False),
    ("What HTTP status code means rate limit exceeded?", False),
    ("How do I rename my workspace?", False),
    ("What is the weather in Bangalore?", True),
    ("Tell me a joke.", True),
]

print("Live server spot check — 7 queries")
print("=" * 50)
passed = 0

for q, expect_fallback in queries:
    r = requests.post(f"{BASE_URL}/ask", json={"question": q})
    time.sleep(1.5)
    data = r.json()
    ok = data.get("fallback", False) == expect_fallback
    print(f"[{'PASS' if ok else 'FAIL'}] {q[:55]}")
    if ok:
        passed += 1

print(f"\nLive server: {passed}/7 passed")
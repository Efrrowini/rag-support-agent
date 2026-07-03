import requests

BASE_URL = "http://localhost:8000"

in_scope = [
    # From sample.pdf — core support
    "How do I reset my password?",
    "What are the pricing plans?",
    "How do I invite a team member?",
    "How do I cancel my subscription?",
    "How do I connect Slack?",
    "What roles can I assign to users?",
    "How do I generate an API key?",
    "What happens after 5 failed login attempts?",
    "How do I export my data?",
    "How do I delete my account?",
    # From api_reference.pdf
    "What is the base URL for the VortexIQ API?",
    "What HTTP status code means I exceeded the rate limit?",
    "How do I create a new project using the API?",
    "What SDK is available for Python?",
    "How many API requests per hour does the Pro plan allow?",
    # From troubleshooting.pdf
    "What should I do if VortexIQ is loading slowly?",
    "Why am I not receiving email notifications?",
    "What file size limit does VortexIQ support for uploads?",
    "How do I fix Jira sync issues?",
    "Who do I contact for billing issues?",
]

out_of_scope = [
    "What is the weather in Bangalore?",
    "Who won the IPL 2025?",
    "Write me a Python function to sort a list.",
    "What is the capital of France?",
    "Tell me a joke.",
]

print("=" * 60)
print("EVALUATION SUITE — 25 queries across 3 documents")
print("=" * 60)

passed = 0
failed = 0

print("\n--- IN-SCOPE QUERIES (expect fallback: false) ---\n")
for q in in_scope:
    r = requests.post(f"{BASE_URL}/ask", json={"question": q})
    data = r.json()
    is_pass = not data.get("fallback", True)
    status = "PASS" if is_pass else "FAIL"
    if is_pass:
        passed += 1
    else:
        failed += 1
    print(f"[{status}] {q}")
    if not is_pass:
        print(f"       → triggered fallback unexpectedly")

print("\n--- OUT-OF-SCOPE QUERIES (expect fallback: true) ---\n")
for q in out_of_scope:
    r = requests.post(f"{BASE_URL}/ask", json={"question": q})
    data = r.json()
    is_pass = data.get("fallback", False)
    status = "PASS" if is_pass else "FAIL"
    if is_pass:
        passed += 1
    else:
        failed += 1
    print(f"[{status}] {q}")
    if not is_pass:
        print(f"       → should have triggered fallback, score: {data.get('top_score')}")

print("\n" + "=" * 60)
print(f"RESULTS: {passed}/25 passed | {failed} failed")
rate = round(passed / 25 * 100)
print(f"Pass rate: {rate}%")
print("=" * 60)
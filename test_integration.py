import pytest
import requests

BASE_URL = "http://localhost:8000"


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready():
    r = requests.get(f"{BASE_URL}/ready")
    assert r.status_code == 200
    data = r.json()
    assert "ready" in data
    assert "status" in data


def test_ask_in_scope():
    r = requests.post(f"{BASE_URL}/ask", json={"question": "How do I reset my password?"})
    assert r.status_code == 200
    data = r.json()
    assert data["fallback"] is False
    assert len(data["answer"]) > 10
    assert data["source"] is not None


def test_ask_out_of_scope():
    r = requests.post(f"{BASE_URL}/ask", json={"question": "What is the weather in Bangalore?"})
    assert r.status_code == 200
    data = r.json()
    assert data["fallback"] is True


def test_ask_pricing():
    r = requests.post(f"{BASE_URL}/ask", json={"question": "What are the pricing plans?"})
    assert r.status_code == 200
    data = r.json()
    assert data["fallback"] is False
    assert any(word in data["answer"].lower() for word in ["starter", "pro", "enterprise"])


def test_ingest():
    r = requests.post(f"{BASE_URL}/ingest", json={"source": "data/sample.pdf"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["result"]["chunks"] > 0


def test_sessions_endpoint():
    r = requests.get(f"{BASE_URL}/sessions")
    assert r.status_code == 200
    data = r.json()
    assert "escalated_sessions" in data
    assert "count" in data
import os
import time
import pytest
from fastapi.testclient import TestClient

# Ensure required minimal env vars are set for Settings loading (DATABASE_URL must be provided externally - no SQLite fallback)
os.environ.setdefault("SECRET_KEY", "dev-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
os.environ.setdefault("SMTP_SERVER", "smtp.example.com")
os.environ.setdefault("SMTP_PORT", "587")
os.environ.setdefault("EMAIL_USERNAME", "test@example.com")
os.environ.setdefault("EMAIL_PASSWORD", "password")

from app.main import app  # noqa E402

client = TestClient(app)

@pytest.mark.order(1)
def test_health_root():
    r = client.get("/api/v1/health/")
    assert r.status_code == 200
    data = r.json()
    assert data["message"].startswith("Welcome")

@pytest.mark.order(2)
def test_health_rag():
    r = client.get("/api/v1/rag/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

@pytest.mark.order(3)
def test_login_demo_user():
    # OAuth2PasswordRequestForm expects form fields 'username' and 'password'
    r = client.post("/api/v1/auth/login", data={"username": "demo@farmer.com", "password": "demo123"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token
    # store globally
    global AUTH_TOKEN
    AUTH_TOKEN = token

@pytest.mark.order(4)
def test_create_chat_session():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {"title": "Smoke Test Session", "language_preference": "english"}
    r = client.post("/api/v1/chat/sessions", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["id"]
    global SESSION_ID
    SESSION_ID = data["id"]

@pytest.mark.order(5)
def test_send_chat_message():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {"session_id": SESSION_ID, "content": "How to improve wheat yield?"}
    r = client.post("/api/v1/chat/messages", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list) and len(data) == 2
    roles = {msg["role"] for msg in data}
    assert "user" in roles and "assistant" in roles

@pytest.mark.order(6)
def test_rag_ask_basic():
    payload = {"query": "Best time to irrigate rice crop?"}
    r = client.post("/api/v1/rag/ask", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["success"] is True
    assert "response" in data
    assert "processing_time" in data

@pytest.mark.order(7)
def test_list_sessions():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get("/api/v1/chat/sessions", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "sessions" in data

@pytest.mark.order(8)
def test_get_session_messages():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get(f"/api/v1/chat/sessions/{SESSION_ID}/messages", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(msg["role"] == "assistant" for msg in data)


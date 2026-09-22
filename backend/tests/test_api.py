import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_session

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "vector_store" in data
    assert "llm_providers" in data

def test_session_lifecycle():
    # 1. Create session
    create_res = client.post("/api/sessions", json={"title": "Test PM Chat"})
    assert create_res.status_code == 200
    session_data = create_res.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Test PM Chat"

    # 2. Get session
    get_res = client.get(f"/api/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == session_id

    # 3. List sessions
    list_res = client.get("/api/sessions")
    assert list_res.status_code == 200
    assert any(s["id"] == session_id for s in list_res.json())

    # 4. Delete session
    del_res = client.delete(f"/api/sessions/{session_id}")
    assert del_res.status_code == 200

def test_artifact_creation_and_retrieval():
    # Create session first
    session = client.post("/api/sessions", json={"title": "Artifact Test"}).json()
    session_id = session["id"]

    # Create artifact
    art_payload = {
        "session_id": session_id,
        "title": "Onboarding Matrix",
        "type": "markdown",
        "content": "# Matrix\n- Step 1\n- Step 2"
    }
    art_res = client.post("/api/artifacts", json=art_payload)
    assert art_res.status_code == 200
    art_data = art_res.json()
    assert art_data["title"] == "Onboarding Matrix"
    assert art_data["type"] == "markdown"

    # Get artifact by id
    get_art = client.get(f"/api/artifacts/{art_data['id']}")
    assert get_art.status_code == 200
    assert get_art.json()["content"] == art_payload["content"]

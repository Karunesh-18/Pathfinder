import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, seed_initial_data
from backend.database import Base, engine

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    yield

def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    with TestClient(app) as client:
        payload = {"user_id": "test_user_001", "message": "I want to become a Data Scientist in 8 weeks"}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "asked_clarifying_question" in data

def test_get_profile():
    with TestClient(app) as client:
        client.post("/api/chat", json={"user_id": "test_user_001", "message": "Data science goal"})
        response = client.get("/api/profile/test_user_001")
        assert response.status_code == 200
        assert response.json()["user_id"] == "test_user_001"

def test_recommendations():
    with TestClient(app) as client:
        client.post("/api/chat", json={"user_id": "test_user_001", "message": "Data science goal"})
        response = client.get("/api/recommend/test_user_001")
        assert response.status_code == 200
        assert "recommendations" in response.json()

def test_dashboard():
    with TestClient(app) as client:
        client.post("/api/chat", json={"user_id": "test_user_001", "message": "Data science goal"})
        response = client.get("/api/dashboard/test_user_001")
        assert response.status_code == 200
        data = response.json()
        assert "career_readiness_pct" in data
        assert "skill_growth" in data


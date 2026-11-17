"""Tests API : health check maintenant, wiring complet en semaine 4."""
from fastapi.testclient import TestClient

from src.depute.api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

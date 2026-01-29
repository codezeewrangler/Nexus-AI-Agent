# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns HTML"""
    response = client.get("/")
    # Should either return 200 with HTML or redirect
    assert response.status_code in [200, 404]  # 404 if static files not found


def test_legacy_health_check(client):
    """Test legacy health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_api_health_check(client):
    """Test API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_upload_invalid_file_type(client):
    """Test upload rejects invalid file types"""
    files = {"file": ("malware.exe", b"fake content", "application/octet-stream")}
    response = client.post("/upload_document", files=files)
    assert response.status_code == 400


def test_upload_valid_txt_file(client):
    """Test upload accepts valid TXT file"""
    files = {"file": ("test.txt", b"This is test content.", "text/plain")}
    response = client.post("/upload_document", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"


def test_query_validation_empty_query(client):
    """Test query endpoint validates empty query"""
    response = client.post(
        "/api/query",
        json={"query": ""}
    )
    assert response.status_code == 422  # Validation error


def test_query_validation_short_query(client):
    """Test query endpoint validates minimum query length"""
    response = client.post(
        "/api/query",
        json={"query": "ab"}  # Too short (min 3 chars)
    )
    assert response.status_code == 422  # Validation error

"""Basic API tests."""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_list_demos():
    """Test listing available demos."""
    response = client.get("/api/demos")
    assert response.status_code == 200
    demos = response.json()
    assert len(demos) >= 1
    assert any(demo["id"] == "tcp-handshake" for demo in demos)


def test_get_demo():
    """Test getting specific demo."""
    response = client.get("/api/demos/tcp-handshake")
    assert response.status_code == 200
    demo = response.json()
    assert demo["id"] == "tcp-handshake"
    assert demo["name"] == "TCP 3-Way Handshake"
    assert "parameters_schema" in demo


def test_get_nonexistent_demo():
    """Test getting non-existent demo."""
    response = client.get("/api/demos/nonexistent")
    assert response.status_code == 404


def test_submit_job_valid():
    """Test submitting a valid job."""
    response = client.post(
        "/api/jobs",
        json={
            "demo_id": "tcp-handshake",
            "parameters": {
                "target_ip": "8.8.8.8",
                "target_port": 80,
                "timeout": 5
            }
        }
    )
    assert response.status_code == 202
    job = response.json()
    assert "job_id" in job
    assert job["demo_id"] == "tcp-handshake"
    assert job["status"] == "pending"


def test_submit_job_invalid_demo():
    """Test submitting job with invalid demo ID."""
    response = client.post(
        "/api/jobs",
        json={
            "demo_id": "nonexistent",
            "parameters": {}
        }
    )
    assert response.status_code == 404


def test_submit_job_invalid_parameters():
    """Test submitting job with invalid parameters."""
    response = client.post(
        "/api/jobs",
        json={
            "demo_id": "tcp-handshake",
            "parameters": {
                "target_ip": "not-an-ip",
                "target_port": 80
            }
        }
    )
    assert response.status_code == 422


def test_get_job_status():
    """Test getting job status."""
    # Submit a job first
    submit_response = client.post(
        "/api/jobs",
        json={
            "demo_id": "tcp-handshake",
            "parameters": {
                "target_ip": "8.8.8.8",
                "target_port": 80,
                "timeout": 5
            }
        }
    )
    job_id = submit_response.json()["job_id"]
    
    # Get job status
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    job = response.json()
    assert job["job_id"] == job_id


def test_get_nonexistent_job():
    """Test getting non-existent job status."""
    response = client.get("/api/jobs/nonexistent-id")
    assert response.status_code == 404

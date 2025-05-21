"""
End-to-end tests for the Agent Swarm API.
"""
import pytest
import json
import sys
import os
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_process_message_infinitepay_query(client):
    """Test processing an InfinitePay-related query."""
    # Mock the router agent's process method to avoid actual processing
    # This would typically be done with a patch, but for simplicity in this example
    # we're relying on the actual implementation with mocked dependencies
    
    payload = {
        "message": "What are the fees of the Maquininha Smart?",
        "user_id": "test_user_123"
    }
    
    response = client.post("/api/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure
    assert "response" in data
    assert "agent_workflow" in data
    assert isinstance(data["agent_workflow"], list)
    
    # Verify workflow includes expected agents
    agent_names = [step["agent_name"] for step in data["agent_workflow"]]
    assert "Router" in agent_names


def test_process_message_support_query(client):
    """Test processing a customer support query."""
    payload = {
        "message": "I can't sign in to my account.",
        "user_id": "test_user_456"
    }
    
    response = client.post("/api/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure
    assert "response" in data
    assert "agent_workflow" in data
    assert isinstance(data["agent_workflow"], list)
    
    # Verify workflow includes expected agents
    agent_names = [step["agent_name"] for step in data["agent_workflow"]]
    assert "Router" in agent_names


def test_process_message_general_query(client):
    """Test processing a general knowledge query."""
    payload = {
        "message": "Quais as principais notícias de São Paulo hoje?",
        "user_id": "test_user_789"
    }
    
    response = client.post("/api/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure
    assert "response" in data
    assert "agent_workflow" in data
    assert isinstance(data["agent_workflow"], list)
    
    # Verify workflow includes expected agents
    agent_names = [step["agent_name"] for step in data["agent_workflow"]]
    assert "Router" in agent_names


def test_process_message_invalid_request(client):
    """Test processing an invalid request."""
    # Missing required field
    payload = {
        "user_id": "test_user_123"
    }
    
    response = client.post("/api/message", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Empty message
    payload = {
        "message": "",
        "user_id": "test_user_123"
    }
    
    response = client.post("/api/message", json=payload)
    assert response.status_code == 200  # Should still process empty messages
    
    # Invalid JSON
    response = client.post(
        "/api/message", 
        headers={"Content-Type": "application/json"},
        content="invalid json"
    )
    assert response.status_code == 422  # Unprocessable Entity

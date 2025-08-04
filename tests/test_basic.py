"""
Basic tests for the MCP Memory Server.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_memory_server.main import app
from mcp_memory_server.database.base import Base


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides = {}


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "MCP Memory Server"
    assert data["version"] == "0.1.0"


def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mcp-memory-server"


def test_metrics_endpoint(client):
    """Test the metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "active_connections" in data
    assert data["service"] == "mcp-memory-server"


def test_register_agent(client):
    """Test agent registration."""
    agent_data = {
        "name": "test_agent",
        "agent_type": "chatgpt",
        "project_id": "test_project",
        "custom_metadata": {"test": "data"}
    }
    
    response = client.post("/api/v1/agents/register", json=agent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_agent"
    assert data["agent_type"] == "chatgpt"
    assert "id" in data


def test_push_memory(client):
    """Test memory push functionality."""
    # First register an agent
    agent_data = {
        "name": "test_agent_2",
        "agent_type": "chatgpt",
        "project_id": "test_project",
        "custom_metadata": {}
    }
    
    agent_response = client.post("/api/v1/agents/register", json=agent_data)
    agent_id = agent_response.json()["id"]
    
    # Push memory
    memory_data = {
        "agent_id": agent_id,
        "project_id": "test_project",
        "content": "This is a test memory",
        "memory_type": "fact",
        "tags": ["test", "memory"],
        "custom_metadata": {},
        "is_short_term": False
    }
    
    response = client.post("/api/v1/memory/push", json=memory_data)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is a test memory"
    assert data["memory_type"] == "fact"
    assert "id" in data


def test_fetch_memories(client):
    """Test memory fetch functionality."""
    # First register an agent and push memory
    agent_data = {
        "name": "test_agent_3",
        "agent_type": "chatgpt",
        "project_id": "test_project",
        "custom_metadata": {}
    }
    
    agent_response = client.post("/api/v1/agents/register", json=agent_data)
    agent_id = agent_response.json()["id"]
    
    # Push memory
    memory_data = {
        "agent_id": agent_id,
        "project_id": "test_project",
        "content": "This is a test memory for fetching",
        "memory_type": "fact",
        "tags": ["test", "fetch"],
        "custom_metadata": {},
        "is_short_term": False
    }
    
    client.post("/api/v1/memory/push", json=memory_data)
    
    # Fetch memories
    response = client.get(f"/api/v1/memory/fetch?agent_id={agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0 
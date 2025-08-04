"""
Main FastAPI application for the MCP Memory Server.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from mcp_memory_server.api.agents import router as agents_router
from mcp_memory_server.api.memory import router as memory_router
from mcp_memory_server.api.sessions import router as sessions_router
from mcp_memory_server.config import settings
from mcp_memory_server.core.embedding_service import EmbeddingService
from mcp_memory_server.core.memory_engine import MemoryEngine
from mcp_memory_server.database.base import create_tables, get_db


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        self.active_connections[agent_id] = websocket

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]

    async def send_personal_message(self, message: str, agent_id: str):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting MCP Memory Server...")
    create_tables()
    print("Database tables created successfully")

    yield

    # Shutdown
    print("Shutting down MCP Memory Server...")


# Create FastAPI app
app = FastAPI(
    title="MCP Memory Server",
    description="A robust Model Context Protocol server for long-term memory and context synchronization between AI agents",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(memory_router)
app.include_router(agents_router)
app.include_router(sessions_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MCP Memory Server",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-memory-server"}


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint."""
    return {
        "active_connections": len(manager.active_connections),
        "service": "mcp-memory-server",
    }


# WebSocket endpoint for real-time memory updates
@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time memory synchronization."""
    await manager.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(agent_id)


# MCP Tools - Commented out for now due to import issues
# These can be implemented as separate MCP server tools later
#
# async def push_memory(agent_id: str, content: str, memory_type: str = "fact", tags: str = "") -> str:
#     """Push memory to the MCP server."""
#     # Implementation would go here
#     pass
#
# async def fetch_memory(agent_id: str, query: str = "", limit: int = 10) -> str:
#     """Fetch relevant memory from the MCP server."""
#     # Implementation would go here
#     pass
#
# async def get_agent_stats(agent_id: str) -> str:
#     """Get memory statistics for an agent."""
#     # Implementation would go here
#     pass


def main():
    """Main entry point for the MCP server."""
    import uvicorn

    uvicorn.run(
        "mcp_memory_server.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()

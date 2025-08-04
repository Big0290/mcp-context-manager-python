"""
WebSocket API for real-time memory synchronization.
"""

from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


# WebSocket connection manager (imported from main.py)
manager = None


def set_manager(connection_manager):
    """Set the connection manager from main.py."""
    global manager
    manager = connection_manager


@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time memory synchronization."""
    if not manager:
        await websocket.close(code=1000, reason="Server not ready")
        return

    await manager.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            await handle_websocket_message(agent_id, data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(agent_id)


async def handle_websocket_message(agent_id: str, data: str, websocket: WebSocket):
    """Handle incoming WebSocket messages."""
    try:
        import json

        message = json.loads(data)

        message_type = message.get("type")

        if message_type == "ping":
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "pong",
                        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
                    }
                )
            )

        elif message_type == "memory_update":
            # Handle memory update notification
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "memory_updated",
                        "agent_id": agent_id,
                        "message": "Memory updated successfully",
                    }
                )
            )

        elif message_type == "subscribe":
            # Handle subscription to memory updates
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "subscribed",
                        "agent_id": agent_id,
                        "message": "Subscribed to memory updates",
                    }
                )
            )

        else:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    }
                )
            )

    except json.JSONDecodeError:
        await websocket.send_text(
            json.dumps({"type": "error", "message": "Invalid JSON format"})
        )
    except Exception as e:
        await websocket.send_text(
            json.dumps(
                {"type": "error", "message": f"Error processing message: {str(e)}"}
            )
        )


async def broadcast_memory_update(agent_id: str, memory_data: Dict[str, Any]):
    """Broadcast memory update to connected agents."""
    if not manager:
        return

    import json

    message = {
        "type": "memory_update",
        "agent_id": agent_id,
        "memory": memory_data,
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
    }

    await manager.send_personal_message(json.dumps(message), agent_id)


async def broadcast_system_message(message: str):
    """Broadcast system message to all connected agents."""
    if not manager:
        return

    import json

    system_message = {
        "type": "system_message",
        "message": message,
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
    }

    await manager.broadcast(json.dumps(system_message))

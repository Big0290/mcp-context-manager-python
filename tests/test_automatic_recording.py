#!/usr/bin/env python3
"""
Test script for automatic conversation recording functionality
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


def send_mcp_message(process: subprocess.Popen, message: dict) -> dict:
    """Send a message to the MCP server and get response."""
    try:
        # Send message
        message_str = json.dumps(message) + "\n"
        process.stdin.write(message_str)
        process.stdin.flush()

        # Read response, skipping log messages
        while True:
            response_line = process.stdout.readline().strip()
            if not response_line:
                print(f"❌ No response received from server")
                return {"error": "No response"}

            # Skip log messages (lines that don't start with {)
            if response_line.startswith("{"):
                print(f"📤 Sent: {message_str.strip()}")
                print(f"📥 Received: {response_line}")
                return json.loads(response_line)
            else:
                print(f"📝 Log: {response_line}")

    except Exception as e:
        print(f"❌ Error in send_mcp_message: {e}")
        return {"error": str(e)}


async def test_automatic_recording():
    """Test the automatic conversation recording functionality."""
    print("🧪 Testing Automatic Conversation Recording")
    print("=" * 50)

    # Start the MCP server
    server_path = Path(__file__).parent / "src" / "simple_mcp_server.py"
    process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Initialize the server
        print("1. Initializing MCP server...")
        init_response = send_mcp_message(
            process, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        print(
            f"✅ Server initialized: {init_response.get('result', {}).get('serverInfo', {}).get('name')}"
        )

        # Get available tools
        print("\n2. Getting available tools...")
        tools_response = send_mcp_message(
            process, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        tools = tools_response.get("result", {}).get("tools", [])
        tool_names = [tool["name"] for tool in tools]
        print(f"✅ Available tools: {', '.join(tool_names)}")

        # Test starting conversation recording
        print("\n3. Starting automatic conversation recording...")
        start_recording_response = send_mcp_message(
            process,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "start_conversation_recording",
                    "arguments": {
                        "project_id": "test-project",
                        "auto_record_user_messages": True,
                        "auto_record_ai_responses": True,
                    },
                },
            },
        )
        result = start_recording_response.get("result", {})
        if not result.get("isError", True):
            print(
                f"✅ {result.get('content', [{}])[0].get('text', 'Recording started')}"
            )
        else:
            print(f"❌ Failed to start recording: {result}")
            return

        # Simulate some conversation interactions
        print("\n4. Simulating conversation interactions...")

        # Simulate user requesting context summary
        print("   - User requests context summary...")
        context_response = send_mcp_message(
            process,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_context_summary",
                    "arguments": {"project_id": "test-project", "max_memories": 5},
                },
            },
        )

        # Simulate user adding a memory
        print("   - User adds a memory...")
        memory_response = send_mcp_message(
            process,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "push_memory",
                    "arguments": {
                        "content": "This is a test memory for automatic recording",
                        "memory_type": "fact",
                        "priority": "medium",
                        "tags": ["test", "automatic-recording"],
                        "project_id": "test-project",
                    },
                },
            },
        )

        # Simulate user checking agent stats
        print("   - User checks agent statistics...")
        stats_response = send_mcp_message(
            process,
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "get_agent_stats",
                    "arguments": {"agent_id": "test-project"},
                },
            },
        )

        # Wait a moment for async operations to complete
        await asyncio.sleep(2)

        # Check if memories were automatically created
        print("\n5. Checking for automatically created memories...")
        fetch_response = send_mcp_message(
            process,
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "fetch_memory",
                    "arguments": {"project_id": "test-project", "limit": 10},
                },
            },
        )

        memories = (
            fetch_response.get("result", {}).get("content", [{}])[0].get("text", "")
        )
        print(f"📝 Retrieved memories: {memories}")

        # Stop conversation recording
        print("\n6. Stopping conversation recording...")
        stop_response = send_mcp_message(
            process,
            {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "stop_conversation_recording",
                    "arguments": {"project_id": "test-project"},
                },
            },
        )

        result = stop_response.get("result", {})
        if not result.get("isError", True):
            print(
                f"✅ {result.get('content', [{}])[0].get('text', 'Recording stopped')}"
            )
        else:
            print(f"❌ Failed to stop recording: {result}")

        print("\n🎉 Automatic conversation recording test completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()


if __name__ == "__main__":
    asyncio.run(test_automatic_recording())

#!/usr/bin/env python3
"""
Test script to verify context injection functionality
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


def test_context_injection():
    """Test manual context injection to verify it works."""
    print("🧪 Testing Context Injection")
    print("=" * 50)

    # Test the MCP server directly
    project_path = Path(__file__).parent
    server_script = project_path / "src" / "simple_mcp_server.py"

    # Start the server
    process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={
            "PYTHONPATH": str(project_path),
            "MCP_PROJECT_ID": "mcp-context-manager-python",
        },
    )

    try:
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        # Send the message
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"Init Response: {response}")

        # Test context summary
        context_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "max_memories": 5,
                    "include_recent": True,
                    "focus_areas": ["python", "mcp", "development"],
                },
            },
        }

        process.stdin.write(json.dumps(context_message) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"Context Response: {response}")

        # Test AI prompt crafting
        prompt_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "user_message": "Continue helping with the project",
                    "prompt_type": "continuation",
                    "focus_areas": ["python", "mcp", "development"],
                },
            },
        }

        process.stdin.write(json.dumps(prompt_message) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"Prompt Response: {response}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        process.terminate()
        process.wait()
        print("✅ Test completed")


if __name__ == "__main__":
    test_context_injection()

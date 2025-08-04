#!/usr/bin/env python3
"""
Simple MCP Server Test
Test basic MCP server functionality
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def test_mcp_server():
    """Test basic MCP server functionality."""
    print("🧪 **Testing MCP Server**")
    print("=" * 50)

    project_path = Path(__file__).parent.parent
    server_script = project_path / "src" / "simple_mcp_server.py"

    print("1. Starting MCP server...")
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
        time.sleep(2)  # Wait for server to start

        print("2. Testing initialization...")
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

        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No initialization response")

        print("✅ Server initialized successfully")
        print(f"Response: {response.strip()}")

        print("\n3. Testing tools list...")
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        process.stdin.write(json.dumps(tools_message) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No tools list response")

        print("✅ Tools list retrieved")
        print(f"Response: {response.strip()}")

        print("\n4. Testing context summary...")
        context_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "max_memories": 5,
                    "include_recent": True,
                },
            },
        }

        process.stdin.write(json.dumps(context_message) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No context summary response")

        print("✅ Context summary retrieved")
        print(f"Response: {response.strip()}")

        # Parse the response
        try:
            result = json.loads(response)
            if "result" in result and "content" in result["result"]:
                context_text = result["result"]["content"][0]["text"]
                print("\n📋 **Context Summary:**")
                print(context_text)
            else:
                print("❌ Unexpected response format")
                print(f"Result: {result}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse response: {e}")
            print(f"Raw response: {response}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    test_mcp_server()

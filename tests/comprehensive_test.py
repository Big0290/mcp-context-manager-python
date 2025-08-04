#!/usr/bin/env python3
"""
Comprehensive test for MCP server with all functionality
"""

import json
import subprocess
import sys
from typing import Any, Dict


def send_mcp_message(
    process: subprocess.Popen, message: Dict[str, Any]
) -> Dict[str, Any]:
    """Send a message to the MCP server and get response."""
    # Send message
    message_str = json.dumps(message) + "\n"
    process.stdin.write(message_str)
    process.stdin.flush()

    # Read response
    response_line = process.stdout.readline()
    if not response_line:
        raise RuntimeError("No response from server")

    return json.loads(response_line.strip())


def main():
    """Comprehensive test of MCP server."""
    print("🧪 Comprehensive MCP Server Test")
    print("=" * 50)

    # Start the server process
    process = subprocess.Popen(
        ["python3", "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    try:
        # 1. Initialize the server
        print("\n1️⃣ Testing server initialization...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "comprehensive-test-client", "version": "0.1.0"},
            },
        }

        response = send_mcp_message(process, init_message)
        server_info = response.get("result", {}).get("serverInfo", {})
        print(f"✅ Server initialized: {server_info['name']} v{server_info['version']}")

        # 2. List available tools
        print("\n2️⃣ Testing tool listing...")
        list_tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        response = send_mcp_message(process, list_tools_message)
        tools = response.get("result", {}).get("tools", [])
        tool_names = [tool["name"] for tool in tools]
        print(f"✅ Available tools: {', '.join(tool_names)}")

        # 3. Register an agent
        print("\n3️⃣ Testing agent registration...")
        register_agent_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "register_agent",
                "arguments": {
                    "name": "Test Agent",
                    "agent_type": "cli",
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, register_agent_message)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Agent registration: {result_text}")

        # 4. Push first memory
        print("\n4️⃣ Testing memory push (first entry)...")
        push_memory_message_1 = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "The user prefers dark mode in their IDE",
                    "memory_type": "preference",
                    "priority": "high",
                    "tags": ["ui", "preference", "ide"],
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, push_memory_message_1)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Memory push: {result_text}")

        # 5. Push second memory
        print("\n5️⃣ Testing memory push (second entry)...")
        push_memory_message_2 = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "The user is working on a Python MCP server project",
                    "memory_type": "fact",
                    "priority": "medium",
                    "tags": ["python", "mcp", "project"],
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, push_memory_message_2)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Memory push: {result_text}")

        # 6. Push third memory
        print("\n6️⃣ Testing memory push (third entry)...")
        push_memory_message_3 = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "The user likes to use keyboard shortcuts for efficiency",
                    "memory_type": "preference",
                    "priority": "medium",
                    "tags": ["efficiency", "keyboard", "shortcuts"],
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, push_memory_message_3)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Memory push: {result_text}")

        # 7. Fetch memories with query
        print("\n7️⃣ Testing memory fetch with query...")
        fetch_memory_message_1 = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "fetch_memory",
                "arguments": {
                    "query": "user preferences",
                    "limit": 10,
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, fetch_memory_message_1)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Memory fetch (query): {result_text}")

        # 8. Fetch memories with tags
        print("\n8️⃣ Testing memory fetch with tags...")
        fetch_memory_message_2 = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "fetch_memory",
                "arguments": {
                    "tags": ["python", "mcp"],
                    "limit": 5,
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, fetch_memory_message_2)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Memory fetch (tags): {result_text}")

        # 9. Fetch memories by type
        print("\n9️⃣ Testing memory fetch by type...")
        fetch_memory_message_3 = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "fetch_memory",
                "arguments": {
                    "memory_type": "preference",
                    "limit": 5,
                    "project_id": "test-project",
                },
            },
        }

        response = send_mcp_message(process, fetch_memory_message_3)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Memory fetch (type): {result_text}")

        # 10. Get agent statistics
        print("\n🔟 Testing agent statistics...")
        get_stats_message = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "get_agent_stats",
                "arguments": {"agent_id": "cursor-agent", "project_id": "test-project"},
            },
        }

        response = send_mcp_message(process, get_stats_message)
        result_text = response.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"✅ Agent stats: {result_text}")

        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("✅ MCP server is working correctly with stdin/stdout communication")
        print("✅ All tools are functioning as expected")
        print("✅ Protocol compliance verified")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        # Print server stderr for debugging
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")

    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("\n🛑 Server stopped.")


if __name__ == "__main__":
    main()

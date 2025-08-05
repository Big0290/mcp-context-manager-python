#!/usr/bin/env python3
"""
Direct MCP Protocol Test
"""

import json
import subprocess
import sys
import time


def test_mcp_protocol():
    """Test MCP protocol directly."""
    print("🧠 Testing MCP Protocol Directly...")

    # Start the server
    print("📡 Starting MCP server...")
    process = subprocess.Popen(
        ["python3", "-m", "src.extensible_mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Wait a moment for server to start
        time.sleep(2)

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"📥 Initialize response: {response}")

        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        print("\n📤 Sending tools/list request...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print(f"📥 Tools response: {response}")

        # Parse tools
        try:
            tools_data = json.loads(response)
            tools = tools_data.get("result", {}).get("tools", [])
            print(f"\n📋 Found {len(tools)} tools:")

            brain_tools = [
                tool
                for tool in tools
                if tool["name"]
                in [
                    "get_brain_status",
                    "get_identity_summary",
                    "search_memories_with_brain",
                    "process_task_with_brain",
                    "get_emotional_learning_summary",
                    "get_cognitive_summary",
                    "add_emotional_tag",
                    "get_joyful_memories",
                    "update_emotional_state",
                ]
            ]

            print(f"🧠 Brain tools: {len(brain_tools)}")
            for tool in brain_tools:
                print(f"  - {tool['name']}: {tool['description']}")

            plugin_tools = [
                tool
                for tool in tools
                if tool["name"]
                in ["start_conversation_recording", "stop_conversation_recording"]
            ]

            print(f"🔌 Plugin tools: {len(plugin_tools)}")
            for tool in plugin_tools:
                print(f"  - {tool['name']}: {tool['description']}")

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing response: {e}")
            print(f"Raw response: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()


if __name__ == "__main__":
    test_mcp_protocol()

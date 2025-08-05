#!/usr/bin/env python3
"""
Test MCP protocol to see what tools are exposed
"""

import json
import sys


# Simulate MCP protocol messages
def test_mcp_protocol():
    print("🧠 Testing MCP Protocol...")

    # Initialize request
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
    print(json.dumps(init_request))

    # Tools list request
    tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

    print("\n📤 Sending tools/list request...")
    print(json.dumps(tools_request))

    print("\n📋 Expected brain tools:")
    expected_tools = [
        "mcp_brain-enhanced-mcp_get_brain_status",
        "mcp_brain-enhanced-mcp_get_identity_summary",
        "mcp_brain-enhanced-mcp_search_memories_with_brain",
        "mcp_brain-enhanced-mcp_process_task_with_brain",
        "mcp_brain-enhanced-mcp_get_emotional_learning_summary",
        "mcp_brain-enhanced-mcp_get_cognitive_summary",
        "mcp_brain-enhanced-mcp_add_emotional_tag",
        "mcp_brain-enhanced-mcp_get_joyful_memories",
        "mcp_brain-enhanced-mcp_update_emotional_state",
    ]

    for tool in expected_tools:
        print(f"  - {tool}")

    print("\n💡 To test manually:")
    print("1. Send the initialize request to the MCP server")
    print("2. Send the tools/list request")
    print("3. Check if the brain tools are in the response")


if __name__ == "__main__":
    test_mcp_protocol()

#!/usr/bin/env python3
"""
Debug script to check tool registration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.brain_enhancement_integration import BrainEnhancementIntegration
from src.extensible_mcp_server import ExtensibleMCPServer


async def debug_tools():
    """Debug tool registration."""
    print("🔍 Debugging Tool Registration...")

    # Test brain integration directly
    print("\n1. Testing Brain Integration Directly:")
    brain_integration = BrainEnhancementIntegration(enable_all_features=True)
    brain_tools = brain_integration.get_brain_enhancement_tools()
    print(f"   Brain tools count: {len(brain_tools)}")
    for tool in brain_tools:
        print(f"   - {tool['name']}: {tool['description']}")

    # Test server
    print("\n2. Testing Server Tool Registration:")
    server = ExtensibleMCPServer(enable_brain_features=True, enable_plugins=True)

    await server.start()

    tools = server.get_tools()
    print(f"   Total tools: {len(tools)}")

    # Check brain tools
    brain_tools_in_server = [
        tool
        for tool in tools
        if tool["name"]
        in ["get_brain_status", "get_identity_summary", "search_memories_with_brain"]
    ]
    print(f"   Brain tools in server: {len(brain_tools_in_server)}")
    for tool in brain_tools_in_server:
        print(f"   - {tool['name']}: {tool['description']}")

    # Check plugin tools
    plugin_tools = [
        tool
        for tool in tools
        if tool["name"]
        in ["start_conversation_recording", "stop_conversation_recording"]
    ]
    print(f"   Plugin tools: {len(plugin_tools)}")
    for tool in plugin_tools:
        print(f"   - {tool['name']}: {tool['description']}")

    # List all tools
    print("\n3. All Available Tools:")
    for i, tool in enumerate(tools):
        print(f"   {i+1}. {tool['name']}: {tool['description']}")

    await server.stop()


if __name__ == "__main__":
    asyncio.run(debug_tools())

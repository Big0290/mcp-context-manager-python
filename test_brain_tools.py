#!/usr/bin/env python3
"""
Test script for brain enhancement tools
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.extensible_mcp_server import ExtensibleMCPServer


async def test_brain_tools():
    """Test the brain enhancement tools."""
    print("🧠 Testing Brain Enhancement Tools...")

    # Create server
    server = ExtensibleMCPServer(enable_brain_features=True, enable_plugins=True)

    try:
        await server.start()
        print("✅ Server started successfully")

        # Get available tools
        tools = server.get_tools()
        print(f"📋 Available tools: {len(tools)}")

        # List brain tools
        brain_tools = [
            tool for tool in tools if tool["name"].startswith("mcp_brain-enhanced-mcp_")
        ]
        print(f"🧠 Brain tools: {len(brain_tools)}")
        for tool in brain_tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # Test brain status tool
        print("\n🔍 Testing brain status tool...")
        result = await server.execute_tool(
            "mcp_brain-enhanced-mcp_get_brain_status", {}
        )
        print(f"Brain status result: {result}")

        # Test identity summary tool
        print("\n👤 Testing identity summary tool...")
        result = await server.execute_tool(
            "mcp_brain-enhanced-mcp_get_identity_summary", {}
        )
        print(f"Identity summary result: {result}")

        print("\n✅ All tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(test_brain_tools())

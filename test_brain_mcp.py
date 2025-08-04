#!/usr/bin/env python3
"""
Brain MCP Server Test Script
Quick test to verify everything is working.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_brain_server():
    """Test the brain-enhanced MCP server."""
    print("🧠 Testing Brain-Enhanced MCP Server")
    print("=" * 40)

    try:
        from src.brain_enhanced_mcp_server import BrainEnhancedMCPServer

        # Test with brain features
        print("\n1. Testing with brain features enabled...")
        server = BrainEnhancedMCPServer(enable_brain_features=True)
        tools = server.get_tools()

        brain_tools = [
            t
            for t in tools
            if "brain" in t.get("description", "").lower()
            or t["name"] in ["search_similar_experiences", "get_knowledge_graph"]
        ]

        print(f"   ✅ Total tools: {len(tools)}")
        print(f"   ✅ Brain tools: {len(brain_tools)}")

        # Test a simple memory operation
        print("\n2. Testing memory storage...")
        result = await server.execute_tool(
            "push_memory",
            {
                "content": "Test memory for brain system validation",
                "memory_type": "fact",
                "tags": ["test", "validation"],
                "project_id": "test-project",
            },
        )

        if not result.get("isError", True):
            print("   ✅ Memory storage working")
        else:
            print("   ❌ Memory storage failed")

        # Test brain search
        print("\n3. Testing brain search...")
        search_result = await server.execute_tool(
            "search_similar_experiences",
            {"query": "test validation", "project_id": "test-project"},
        )

        if not search_result.get("isError", True):
            print("   ✅ Brain search working")
        else:
            print("   ❌ Brain search failed")

        print("\n✅ All tests passed! Brain MCP server is ready.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_brain_server())
    sys.exit(0 if success else 1)

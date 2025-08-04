#!/usr/bin/env python3
"""
Brain Memory System Usage Examples
Demonstrates advanced brain-like memory capabilities for MCP Context Manager.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brain_enhanced_mcp_server import BrainEnhancedMCPServer


async def example_basic_memory_enhancement():
    """Example: Basic memory storage with brain enhancements."""
    print("🧠 Example 1: Basic Memory Enhancement")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # Store memories that will be automatically enhanced
    memories = [
        {
            "content": "React useState hook manages component state",
            "memory_type": "fact",
            "tags": ["react", "hooks", "state"],
            "project_id": "react-project",
        },
        {
            "content": "Fixed performance issue by memoizing expensive calculation with useMemo",
            "memory_type": "task",
            "tags": ["react", "performance", "useMemo"],
            "project_id": "react-project",
        },
        {
            "content": "useEffect hook handles side effects in functional components",
            "memory_type": "fact",
            "tags": ["react", "hooks", "useEffect"],
            "project_id": "react-project",
        },
    ]

    # Push memories (they'll be enhanced automatically)
    for i, memory in enumerate(memories):
        result = await server.execute_tool("push_memory", memory)
        print(f"Memory {i+1}: {result['content'][0]['text']}")

    print("\n✅ Memories stored and automatically enhanced with:")
    print("• Hierarchical classification (Programming → Frontend → React)")
    print("• Memory layer assignment (semantic, procedural, etc.)")
    print("• Automatic connection creation between related memories")
    print("• Emotional weight calculation based on content importance")


async def example_similar_experience_search():
    """Example: Finding similar experiences and analogical reasoning."""
    print("\n🔍 Example 2: Similar Experience Search")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # Search for similar experiences
    search_query = "performance optimization React components"
    result = await server.execute_tool(
        "search_similar_experiences",
        {
            "query": search_query,
            "project_id": "react-project",
            "focus_areas": ["Performance", "React", "Optimization"],
            "include_analogies": True,
        },
    )

    print(f"Query: '{search_query}'")
    print("\nResults:")
    print(result["content"][0]["text"])

    print("\n✅ Brain search provides:")
    print("• Direct content matches with relevance scores")
    print("• Similar experiences from different contexts")
    print("• Connected knowledge through memory graph traversal")
    print("• Analogical patterns across different topics")


async def example_knowledge_graph():
    """Example: Building and visualizing knowledge graphs."""
    print("\n🕸️ Example 3: Knowledge Graph Generation")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # Generate knowledge graph
    result = await server.execute_tool(
        "get_knowledge_graph",
        {
            "center_topic": "React Hooks",
            "project_id": "react-project",
            "max_depth": 2,
            "connection_types": ["semantic", "functional", "contextual"],
        },
    )

    print("Knowledge Graph for 'React Hooks':")
    print(result["content"][0]["text"])

    print("\n✅ Knowledge graphs show:")
    print("• Memory nodes organized by layers (short-term, long-term, etc.)")
    print("• Connection strengths and types between related memories")
    print("• Knowledge distribution across different memory layers")
    print("• Visual representation of how concepts relate to each other")


async def example_memory_insights():
    """Example: Getting insights about knowledge patterns."""
    print("\n📊 Example 4: Memory System Insights")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # Get memory insights
    result = await server.execute_tool(
        "get_memory_insights",
        {"project_id": "react-project", "include_recommendations": True},
    )

    print("Memory System Analysis:")
    print(result["content"][0]["text"])

    print("\n✅ Insights provide:")
    print("• Memory distribution across layers and states")
    print("• Top knowledge areas and skill categories")
    print("• Connection patterns and relationship types")
    print("• AI-generated recommendations for knowledge management")


async def example_knowledge_path_tracing():
    """Example: Tracing knowledge flow between concepts."""
    print("\n🛤️ Example 5: Knowledge Path Tracing")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # Trace knowledge path
    result = await server.execute_tool(
        "trace_knowledge_path",
        {
            "from_concept": "useState",
            "to_concept": "performance optimization",
            "max_hops": 4,
            "project_id": "react-project",
        },
    )

    print("Knowledge Path Discovery:")
    print(result["content"][0]["text"])

    print("\n✅ Path tracing reveals:")
    print("• How knowledge flows from basic concepts to advanced topics")
    print("• Intermediate concepts that bridge different areas")
    print("• Learning paths for skill development")
    print("• Knowledge gaps where connections are missing")


async def example_memory_promotion():
    """Example: Manually promoting important memories."""
    print("\n⬆️ Example 6: Memory Promotion and Management")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # First, let's fetch some memories to get their IDs
    fetch_result = await server.execute_tool(
        "fetch_memory", {"query": "React", "project_id": "react-project", "limit": 3}
    )

    print("Available memories:")
    print(fetch_result["content"][0]["text"])

    # Note: In a real scenario, you'd extract actual memory IDs from the fetch result
    # For this example, we'll use placeholder IDs
    memory_ids = ["mem_1", "mem_2"]  # These would be real IDs in practice

    # Promote memories
    result = await server.execute_tool(
        "promote_memory_knowledge",
        {
            "memory_ids": memory_ids,
            "target_layer": "procedural",
            "emotional_weight": 0.9,
        },
    )

    print("\nMemory Promotion Result:")
    print(result["content"][0]["text"])

    print("\n✅ Memory promotion allows:")
    print("• Manual control over memory importance and layer assignment")
    print("• Boosting critical knowledge for better retrieval")
    print("• Converting experiences into reusable procedures")
    print("• Fine-tuning the brain's knowledge priorities")


async def example_enhanced_context_injection():
    """Example: Enhanced context injection with brain insights."""
    print("\n🎯 Example 7: Enhanced Context Injection")
    print("=" * 50)

    server = BrainEnhancedMCPServer(enable_brain_features=True)

    # Get enhanced context summary
    result = await server.execute_tool(
        "get_context_summary",
        {
            "project_id": "react-project",
            "max_memories": 10,
            "include_recent": True,
            "focus_areas": ["React", "Performance"],
        },
    )

    print("Enhanced Context Summary:")
    print(result["content"][0]["text"])

    print("\n✅ Enhanced context includes:")
    print("• Original project memories and summaries")
    print("• Brain insights about memory distribution and patterns")
    print("• Knowledge growth recommendations")
    print("• Connection patterns and relationship analysis")


async def example_backward_compatibility():
    """Example: Demonstrating full backward compatibility."""
    print("\n↩️ Example 8: Backward Compatibility")
    print("=" * 50)

    # Test with brain features enabled
    print("With Brain Features:")
    server_brain = BrainEnhancedMCPServer(enable_brain_features=True)
    tools_brain = server_brain.get_tools()
    print(f"Available tools: {len(tools_brain)} (includes brain tools)")

    # Test with brain features disabled
    print("\nWithout Brain Features:")
    server_original = BrainEnhancedMCPServer(enable_brain_features=False)
    tools_original = server_original.get_tools()
    print(f"Available tools: {len(tools_original)} (original tools only)")

    # Both should support original operations
    test_memory = {
        "content": "Test memory for compatibility",
        "memory_type": "fact",
        "project_id": "test-project",
    }

    result_brain = await server_brain.execute_tool("push_memory", test_memory)
    result_original = await server_original.execute_tool("push_memory", test_memory)

    print(f"\nBrain server result: {result_brain['content'][0]['text'][:50]}...")
    print(f"Original server result: {result_original['content'][0]['text'][:50]}...")

    print("\n✅ Backward compatibility ensures:")
    print("• All original functionality works unchanged")
    print("• Existing MCP configurations continue to work")
    print("• Optional brain features don't break existing workflows")
    print("• Gradual adoption possible (enable brain features when ready)")


async def run_all_examples():
    """Run all brain memory system examples."""
    print("🧠 BRAIN MEMORY SYSTEM EXAMPLES")
    print("=" * 60)
    print("Demonstrating advanced brain-like memory capabilities")
    print("for the MCP Context Manager\n")

    examples = [
        example_basic_memory_enhancement,
        example_similar_experience_search,
        example_knowledge_graph,
        example_memory_insights,
        example_knowledge_path_tracing,
        example_memory_promotion,
        example_enhanced_context_injection,
        example_backward_compatibility,
    ]

    for example_func in examples:
        try:
            await example_func()
            await asyncio.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {e}")

    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("• Try the brain-enhanced server with your own MCP configuration")
    print("• Explore the brain tools in your development workflow")
    print("• Build knowledge graphs for your project domains")
    print("• Use similar experience search for problem-solving")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run examples
    asyncio.run(run_all_examples())

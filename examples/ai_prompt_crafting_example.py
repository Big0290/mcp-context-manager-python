#!/usr/bin/env python3
"""
AI Prompt Crafting Example

This example demonstrates how to use the AI Prompt Crafter with the MCP Memory Server
to generate intelligent, contextual prompts for AI interactions.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict


def send_mcp_message(
    process: subprocess.Popen, message: Dict[str, Any]
) -> Dict[str, Any]:
    """Send a message to the MCP server and get response."""
    message_str = json.dumps(message) + "\n"
    process.stdin.write(message_str.encode())
    process.stdin.flush()

    response_line = process.stdout.readline()
    return json.loads(response_line.strip())


async def demonstrate_ai_prompt_crafting():
    """Demonstrate AI prompt crafting with different scenarios."""
    print("🎯 **AI Prompt Crafting Demonstration**")
    print("=" * 50)

    # Start MCP server
    print("\n🚀 **Starting MCP Server**")
    process = subprocess.Popen(
        ["python", "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait a moment for server to start
    await asyncio.sleep(2)

    try:
        # Test scenarios for AI prompt crafting
        scenarios = [
            {
                "name": "Task-Focused Prompt",
                "user_message": "I need to implement a new feature for user authentication",
                "prompt_type": "task_focused",
                "focus_areas": ["python", "authentication", "security"],
            },
            {
                "name": "Problem-Solving Prompt",
                "user_message": "I'm getting an error when trying to connect to the database",
                "prompt_type": "problem_solving",
                "focus_areas": ["database", "error", "debugging"],
            },
            {
                "name": "Explanation Prompt",
                "user_message": "Can you explain how the MCP memory system works?",
                "prompt_type": "explanation",
                "focus_areas": ["mcp", "memory", "context"],
            },
            {
                "name": "Code Review Prompt",
                "user_message": "Please review this code for best practices",
                "prompt_type": "code_review",
                "focus_areas": ["python", "code-quality", "best-practices"],
            },
            {
                "name": "Auto-Detected Prompt",
                "user_message": "How do I fix this bug in my React component?",
                "prompt_type": "general",  # Will be auto-detected as problem_solving
                "focus_areas": ["react", "javascript", "debugging"],
            },
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 **Scenario {i}: {scenario['name']}**")
            print("-" * 40)

            # Craft AI prompt
            prompt_message = {
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/call",
                "params": {
                    "name": "craft_ai_prompt",
                    "arguments": {
                        "project_id": "mcp-context-manager-python",
                        "user_message": scenario["user_message"],
                        "prompt_type": scenario["prompt_type"],
                        "focus_areas": scenario["focus_areas"],
                    },
                },
            }

            response = send_mcp_message(process, prompt_message)
            result = response.get("result", {})

            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                crafted_prompt = result.get("content", [{}])[0].get("text", "")
                print("🎯 **Crafted AI Prompt:**")
                print(crafted_prompt)
                print("\n" + "=" * 50)

        # Demonstrate intelligent prompt crafting with context
        print("\n🧠 **Intelligent Context-Aware Prompt Crafting**")
        print("-" * 50)

        # First, get context summary
        context_message = {
            "jsonrpc": "2.0",
            "id": "context",
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

        context_response = send_mcp_message(process, context_message)
        context_result = context_response.get("result", {})

        if "error" not in context_result:
            context_summary = context_result.get("content", [{}])[0].get("text", "")
            print("📋 **Current Context Summary:**")
            print(context_summary)
            print("\n" + "-" * 30)

            # Now craft a prompt that uses this context
            intelligent_prompt_message = {
                "jsonrpc": "2.0",
                "id": "intelligent",
                "method": "tools/call",
                "params": {
                    "name": "craft_ai_prompt",
                    "arguments": {
                        "project_id": "mcp-context-manager-python",
                        "user_message": "Based on our previous work, what should we focus on next?",
                        "prompt_type": "continuation",
                        "focus_areas": ["mcp", "python", "development"],
                    },
                },
            }

            intelligent_response = send_mcp_message(process, intelligent_prompt_message)
            intelligent_result = intelligent_response.get("result", {})

            if "error" not in intelligent_result:
                intelligent_prompt = intelligent_result.get("content", [{}])[0].get(
                    "text", ""
                )
                print("🧠 **Intelligent Context-Aware Prompt:**")
                print(intelligent_prompt)

        print("\n✅ **AI Prompt Crafting Demonstration Complete!**")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")

    finally:
        # Clean up
        process.terminate()
        process.wait()


async def demonstrate_prompt_types():
    """Demonstrate different prompt types and their characteristics."""
    print("\n🎭 **Prompt Types Demonstration**")
    print("=" * 40)

    prompt_types = [
        {
            "type": "continuation",
            "description": "For ongoing conversations",
            "example": "Continue helping with the project",
        },
        {
            "type": "task_focused",
            "description": "For implementation work",
            "example": "Help me implement a new feature",
        },
        {
            "type": "problem_solving",
            "description": "For debugging and issue resolution",
            "example": "I'm getting an error, can you help?",
        },
        {
            "type": "explanation",
            "description": "For educational content",
            "example": "Can you explain how this works?",
        },
        {
            "type": "code_review",
            "description": "For code quality assessment",
            "example": "Please review this code",
        },
        {
            "type": "debugging",
            "description": "For systematic debugging",
            "example": "Help me debug this issue",
        },
        {
            "type": "general",
            "description": "For general assistance",
            "example": "General help needed",
        },
    ]

    for prompt_type in prompt_types:
        print(f"\n📝 **{prompt_type['type'].replace('_', ' ').title()}**")
        print(f"Description: {prompt_type['description']}")
        print(f"Example: {prompt_type['example']}")


def main():
    """Main demonstration function."""
    print("🎯 **AI Prompt Crafting with MCP Memory Server**")
    print("=" * 60)

    # Show prompt types
    asyncio.run(demonstrate_prompt_types())

    # Run the main demonstration
    asyncio.run(demonstrate_ai_prompt_crafting())

    print("\n🎉 **Demonstration Complete!**")
    print("\n**Key Features Demonstrated:**")
    print("✅ Context-aware prompt generation")
    print("✅ Multiple prompt types for different scenarios")
    print("✅ Intelligent auto-detection of prompt type")
    print("✅ Integration with MCP Memory Server")
    print("✅ Focus area filtering")
    print("✅ User message incorporation")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Intelligent Context Injection Example

This example demonstrates how to use AI prompt crafting for intelligent
context injection instead of raw context summaries.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


def send_mcp_message(process: subprocess.Popen, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to the MCP server and get response."""
    message_str = json.dumps(message) + "\n"
    process.stdin.write(message_str.encode())
    process.stdin.flush()
    
    response_line = process.stdout.readline()
    return json.loads(response_line.strip())


async def demonstrate_intelligent_context_injection():
    """Demonstrate intelligent context injection with different scenarios."""
    print("🧠 **Intelligent Context Injection Demonstration**")
    print("=" * 60)
    
    # Start MCP server
    print("\n🚀 **Starting MCP Server**")
    process = subprocess.Popen(
        ["python", "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for server to start
    await asyncio.sleep(2)
    
    try:
        # Add some context first
        print("\n📝 **Adding Context for Demonstration**")
        
        memories = [
            {
                "content": "Working on MCP Memory Server with Python",
                "memory_type": "task",
                "priority": "high",
                "tags": ["python", "mcp", "memory", "server"],
                "project_id": "demo-project"
            },
            {
                "content": "Implemented context injection feature",
                "memory_type": "task", 
                "priority": "medium",
                "tags": ["context", "injection", "feature"],
                "project_id": "demo-project"
            },
            {
                "content": "User requested AI prompt crafting functionality",
                "memory_type": "task",
                "priority": "high", 
                "tags": ["ai", "prompt", "crafting"],
                "project_id": "demo-project"
            }
        ]
        
        for i, memory in enumerate(memories, 1):
            memory_message = {
                "jsonrpc": "2.0",
                "id": f"memory_{i}",
                "method": "tools/call",
                "params": {
                    "name": "push_memory",
                    "arguments": memory
                }
            }
            
            response = send_mcp_message(process, memory_message)
            print(f"✅ Added memory {i}: {memory['content'][:50]}...")
        
        # Demonstrate different types of intelligent context injection
        scenarios = [
            {
                "name": "General Continuation",
                "description": "Continue helping with the project",
                "prompt_type": "continuation",
                "focus_areas": ["python", "mcp", "development"],
                "user_message": "Continue helping with the project based on our previous work"
            },
            {
                "name": "Task-Focused Development",
                "description": "Focus on implementation work",
                "prompt_type": "task_focused",
                "focus_areas": ["python", "implementation", "features"],
                "user_message": "Help me implement new features for the MCP server"
            },
            {
                "name": "Problem-Solving Debugging",
                "description": "Focus on debugging and issues",
                "prompt_type": "problem_solving",
                "focus_areas": ["debugging", "errors", "python"],
                "user_message": "I'm having issues with the memory server, can you help debug?"
            },
            {
                "name": "Educational Explanation",
                "description": "Focus on explaining concepts",
                "prompt_type": "explanation",
                "focus_areas": ["mcp", "memory", "context"],
                "user_message": "Can you explain how the MCP memory system works?"
            },
            {
                "name": "Code Review Assessment",
                "description": "Focus on code quality",
                "prompt_type": "code_review",
                "focus_areas": ["python", "code-quality", "best-practices"],
                "user_message": "Please review my code for best practices"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎭 **Scenario {i}: {scenario['name']}**")
            print(f"Description: {scenario['description']}")
            print("-" * 50)
            
            # Craft intelligent context injection
            context_message = {
                "jsonrpc": "2.0",
                "id": f"context_{i}",
                "method": "tools/call",
                "params": {
                    "name": "craft_ai_prompt",
                    "arguments": {
                        "project_id": "demo-project",
                        "user_message": scenario["user_message"],
                        "prompt_type": scenario["prompt_type"],
                        "focus_areas": scenario["focus_areas"]
                    }
                }
            }
            
            response = send_mcp_message(process, context_message)
            result = response.get('result', {})
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                crafted_prompt = result.get('content', [{}])[0].get('text', '')
                print("🎯 **Intelligent Context Crafted:**")
                print(crafted_prompt)
                print("\n" + "="*60)
        
        # Compare with basic context injection
        print("\n📊 **Comparison: Intelligent vs Basic Context Injection**")
        print("-" * 50)
        
        # Basic context injection
        print("\n📋 **Basic Context Injection:**")
        basic_message = {
            "jsonrpc": "2.0",
            "id": "basic",
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "demo-project",
                    "max_memories": 5,
                    "include_recent": True
                }
            }
        }
        
        basic_response = send_mcp_message(process, basic_message)
        basic_result = basic_response.get('result', {})
        
        if 'error' not in basic_result:
            basic_context = basic_result.get('content', [{}])[0].get('text', '')
            print(basic_context)
        
        # Intelligent context injection
        print("\n🧠 **Intelligent Context Injection:**")
        intelligent_message = {
            "jsonrpc": "2.0",
            "id": "intelligent",
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "demo-project",
                    "user_message": "Continue helping with the project",
                    "prompt_type": "continuation",
                    "focus_areas": ["python", "mcp", "development"]
                }
            }
        }
        
        intelligent_response = send_mcp_message(process, intelligent_message)
        intelligent_result = intelligent_response.get('result', {})
        
        if 'error' not in intelligent_result:
            intelligent_context = intelligent_result.get('content', [{}])[0].get('text', '')
            print(intelligent_context)
        
        print("\n✅ **Intelligent Context Injection Demonstration Complete!**")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
    
    finally:
        # Clean up
        process.terminate()
        process.wait()


def show_benefits():
    """Show the benefits of intelligent context injection."""
    print("\n🎯 **Benefits of Intelligent Context Injection**")
    print("=" * 50)
    
    benefits = [
        {
            "benefit": "Context-Aware Responses",
            "description": "AI understands project history and can provide more relevant responses",
            "example": "References previous work and ongoing tasks"
        },
        {
            "benefit": "Intent-Specific Guidance",
            "description": "Different prompt types for different scenarios (task, debugging, explanation)",
            "example": "Task-focused prompts for implementation, problem-solving for debugging"
        },
        {
            "benefit": "Focus Area Filtering",
            "description": "Filter context by specific technologies or topics",
            "example": "Focus on Python, MCP, or specific features"
        },
        {
            "benefit": "Structured Guidelines",
            "description": "Provides specific response guidelines for the AI",
            "example": "Step-by-step guidance, code examples, best practices"
        },
        {
            "benefit": "Auto-Detection",
            "description": "Automatically determines the best prompt type based on content",
            "example": "Detects if user needs help with implementation vs debugging"
        },
        {
            "benefit": "Fallback Support",
            "description": "Gracefully falls back to basic context if AI crafting fails",
            "example": "Ensures context injection always works"
        }
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. **{benefit['benefit']}**")
        print(f"   Description: {benefit['description']}")
        print(f"   Example: {benefit['example']}")


def main():
    """Main demonstration function."""
    print("🧠 **Intelligent Context Injection with AI Prompt Crafting**")
    print("=" * 70)
    
    # Show benefits
    show_benefits()
    
    # Run the main demonstration
    asyncio.run(demonstrate_intelligent_context_injection())
    
    print("\n🎉 **Demonstration Complete!**")
    print("\n**Key Improvements:**")
    print("✅ Context-aware prompt generation")
    print("✅ Intent-specific guidance")
    print("✅ Focus area filtering")
    print("✅ Structured response guidelines")
    print("✅ Auto-detection of prompt type")
    print("✅ Graceful fallback support")
    print("✅ Better AI responses and user experience")


if __name__ == "__main__":
    main() 
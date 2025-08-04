#!/usr/bin/env python3
"""
Example demonstrating automatic context injection for chat sessions
"""

import json
import subprocess
import sys
from typing import Dict, Any


def send_mcp_message(process: subprocess.Popen, message: Dict[str, Any]) -> Dict[str, Any]:
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


def simulate_chat_session_start(process: subprocess.Popen, project_id: str = "cursor-chat"):
    """Simulate starting a new chat session with intelligent context injection."""
    print("🤖 **Starting New Chat Session**")
    print("=" * 50)
    
    # 1. Get intelligent context injection using AI prompt crafting
    print("\n🧠 **Intelligent Context Injection**")
    print("Crafting contextual prompt from conversation history...")
    
    intelligent_context_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "craft_ai_prompt",
            "arguments": {
                "project_id": project_id,
                "user_message": "Continue helping with the project based on our previous work",
                "prompt_type": "continuation",
                "focus_areas": ["python", "mcp", "development", "memory"]
            }
        }
    }
    
    response = send_mcp_message(process, intelligent_context_message)
    result = response.get('result', {})
    
    if 'error' in result:
        print("⚠️ AI prompt crafting failed, using basic context injection...")
        # Fallback to basic context summary
        summary_message = {
            "jsonrpc": "2.0",
            "id": "fallback",
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": project_id,
                    "max_memories": 5,
                    "include_recent": True
                }
            }
        }
        
        response = send_mcp_message(process, summary_message)
        context_summary = response.get('result', {}).get('content', [{}])[0].get('text', '')
        
        print("\n📋 **Basic Context Summary:**")
        print("-" * 40)
        print(context_summary)
        print("-" * 40)
    else:
        crafted_prompt = result.get('content', [{}])[0].get('text', '')
        
        print("\n🎯 **Intelligent Context Crafted:**")
        print("-" * 40)
        print(crafted_prompt)
        print("-" * 40)
    
    # 2. Simulate agent response with context
    print("\n🤖 **Agent Response (with context):**")
    print("Hello! I can see from our conversation history that:")
    
    # Parse the context and provide a natural response
    if "project cleanup" in context_summary.lower():
        print("• We've been working on organizing the MCP Memory Server project")
        print("• The project structure has been cleaned up and is now developer-friendly")
        print("• We've implemented stdin/stdout communication following MCP specifications")
    
    if "context injection" in context_summary.lower():
        print("• You requested automatic context injection for chat sessions")
        print("• This feature will provide continuity across conversations")
        print("• I'm now implementing this functionality")
    
    print("\nHow can I help you continue with the project today?")


def main():
    """Demonstrate automatic context injection."""
    print("🧪 Context Injection Demo")
    print("=" * 50)
    
    # Start the server process
    process = subprocess.Popen(
        ["python3", "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    try:
        # Initialize server
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "context-injection-demo",
                    "version": "0.1.0"
                }
            }
        }
        
        response = send_mcp_message(process, init_message)
        print("✅ Server initialized")
        
        # Simulate chat session start
        simulate_chat_session_start(process, "cursor-chat")
        
        print("\n✅ Context injection demo completed!")
        print("\n💡 **Benefits of this approach:**")
        print("• Automatic continuity across chat sessions")
        print("• No need to re-explain previous work")
        print("• Context-aware responses")
        print("• Improved user experience")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
    
    finally:
        process.terminate()
        process.wait()
        print("\n🛑 Server stopped.")


if __name__ == "__main__":
    main() 
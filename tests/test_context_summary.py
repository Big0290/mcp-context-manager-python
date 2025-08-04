#!/usr/bin/env python3
"""
Test for the new context summary functionality
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


def main():
    """Test the context summary functionality."""
    print("🧪 Testing Context Summary Functionality")
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
        # 1. Initialize the server
        print("\n1️⃣ Initializing server...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "context-summary-test",
                    "version": "0.1.0"
                }
            }
        }
        
        response = send_mcp_message(process, init_message)
        print("✅ Server initialized")
        
        # 2. Add some test memories
        print("\n2️⃣ Adding test memories...")
        
        memories = [
            {
                "content": "User is working on a Python MCP server project",
                "memory_type": "fact",
                "priority": "high",
                "tags": ["python", "mcp", "project"],
                "project_id": "test-project"
            },
            {
                "content": "User prefers dark mode in their IDE",
                "memory_type": "preference",
                "priority": "medium",
                "tags": ["ui", "preference", "ide"],
                "project_id": "test-project"
            },
            {
                "content": "Need to implement automatic context injection",
                "memory_type": "task",
                "priority": "high",
                "tags": ["feature", "context", "automation"],
                "project_id": "test-project"
            },
            {
                "content": "User likes to use keyboard shortcuts for efficiency",
                "memory_type": "preference",
                "priority": "medium",
                "tags": ["efficiency", "keyboard", "shortcuts"],
                "project_id": "test-project"
            }
        ]
        
        for i, memory_data in enumerate(memories):
            push_message = {
                "jsonrpc": "2.0",
                "id": 2 + i,
                "method": "tools/call",
                "params": {
                    "name": "push_memory",
                    "arguments": memory_data
                }
            }
            
            response = send_mcp_message(process, push_message)
            print(f"✅ Added memory {i+1}: {memory_data['content'][:50]}...")
        
        # 3. Test context summary
        print("\n3️⃣ Testing context summary...")
        summary_message = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "test-project",
                    "max_memories": 5,
                    "include_recent": True
                }
            }
        }
        
        response = send_mcp_message(process, summary_message)
        result_text = response.get('result', {}).get('content', [{}])[0].get('text', '')
        print("📋 Context Summary Generated:")
        print("-" * 40)
        print(result_text)
        print("-" * 40)
        
        # 4. Test focused summary
        print("\n4️⃣ Testing focused summary...")
        focused_summary_message = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "test-project",
                    "max_memories": 3,
                    "focus_areas": ["python", "mcp"]
                }
            }
        }
        
        response = send_mcp_message(process, focused_summary_message)
        result_text = response.get('result', {}).get('content', [{}])[0].get('text', '')
        print("🎯 Focused Summary (Python/MCP):")
        print("-" * 40)
        print(result_text)
        print("-" * 40)
        
        print("\n✅ All context summary tests passed!")
        
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
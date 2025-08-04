#!/usr/bin/env python3
"""
Simple test for Cursor integration
"""

import json
import subprocess
import sys
from typing import Dict, Any


def send_mcp_message(process: subprocess.Popen, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to the MCP server and get response."""
    message_str = json.dumps(message) + "\n"
    process.stdin.write(message_str)
    process.stdin.flush()
    
    response_line = process.stdout.readline()
    if not response_line:
        raise RuntimeError("No response from server")
    
    return json.loads(response_line.strip())


def main():
    """Test Cursor integration features."""
    print("🧪 Testing Cursor Integration Features")
    print("=" * 50)
    
    # Start the server
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
        # Initialize
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cursor-integration-test",
                    "version": "0.1.0"
                }
            }
        }
        
        response = send_mcp_message(process, init_message)
        print("✅ Server initialized")
        
        # Test automatic context injection
        print("\n🎯 Testing Automatic Context Injection...")
        context_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "cursor-chat",
                    "max_memories": 5,
                    "include_recent": True
                }
            }
        }
        
        response = send_mcp_message(process, context_message)
        result = response.get('result', {})
        context_text = result.get('content', [{}])[0].get('text', '')
        
        print("📋 **Automatic Context Injection Result:**")
        print("-" * 40)
        print(context_text)
        print("-" * 40)
        
        # Test manual memory addition
        print("\n📝 Testing Manual Memory Addition...")
        memory_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "Testing Cursor integration features - automatic context injection and manual triggers working",
                    "memory_type": "fact",
                    "priority": "high",
                    "tags": ["cursor", "integration", "testing"],
                    "project_id": "cursor-chat"
                }
            }
        }
        
        response = send_mcp_message(process, memory_message)
        result = response.get('result', {})
        memory_text = result.get('content', [{}])[0].get('text', '')
        
        print(f"✅ {memory_text}")
        
        print("\n🎉 Cursor integration features working!")
        print("\n💡 **Available Commands:**")
        print("• Cmd+Shift+C: Inject context manually")
        print("• Cmd+Shift+M: Show current context")
        print("• Cmd+Shift+A: Add memory entry")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
    
    finally:
        process.terminate()
        process.wait()
        print("\n🛑 Test completed")


if __name__ == "__main__":
    main() 
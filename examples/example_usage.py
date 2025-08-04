#!/usr/bin/env python3
"""
Example usage of the refactored MCP Memory Server
Demonstrates how to communicate with the server using stdin/stdout
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
    """Example usage of the MCP Memory Server."""
    print("Starting MCP Memory Server...")
    
    # Start the server process
    process = subprocess.Popen(
        ["python3", "src/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    try:
        # 1. Initialize the server
        print("\n1. Initializing server...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "example-client",
                    "version": "0.1.0"
                }
            }
        }
        
        response = send_mcp_message(process, init_message)
        print(f"Server initialized: {response['result']['serverInfo']}")
        
        # 2. List available tools
        print("\n2. Listing available tools...")
        list_tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_mcp_message(process, list_tools_message)
        tools = response['result']['tools']
        print(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # 3. Register an agent
        print("\n3. Registering an agent...")
        register_agent_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "register_agent",
                "arguments": {
                    "name": "Example Agent",
                    "agent_type": "cli",
                    "project_id": "example-project"
                }
            }
        }
        
        response = send_mcp_message(process, register_agent_message)
        print(f"Agent registration: {response['result']['content'][0]['text']}")
        
        # 4. Push a memory
        print("\n4. Pushing a memory...")
        push_memory_message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "The user prefers dark mode in their IDE",
                    "memory_type": "preference",
                    "priority": "high",
                    "tags": ["ui", "preference", "ide"],
                    "project_id": "example-project"
                }
            }
        }
        
        response = send_mcp_message(process, push_memory_message)
        print(f"Memory push: {response['result']['content'][0]['text']}")
        
        # 5. Push another memory
        print("\n5. Pushing another memory...")
        push_memory_message_2 = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "The user is working on a Python MCP server project",
                    "memory_type": "fact",
                    "priority": "medium",
                    "tags": ["python", "mcp", "project"],
                    "project_id": "example-project"
                }
            }
        }
        
        response = send_mcp_message(process, push_memory_message_2)
        print(f"Memory push: {response['result']['content'][0]['text']}")
        
        # 6. Fetch memories
        print("\n6. Fetching memories...")
        fetch_memory_message = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "fetch_memory",
                "arguments": {
                    "query": "user preferences",
                    "limit": 10,
                    "project_id": "example-project"
                }
            }
        }
        
        response = send_mcp_message(process, fetch_memory_message)
        print(f"Memory fetch: {response['result']['content'][0]['text']}")
        
        # 7. Get agent stats
        print("\n7. Getting agent statistics...")
        get_stats_message = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "get_agent_stats",
                "arguments": {
                    "agent_id": "cursor-agent",
                    "project_id": "example-project"
                }
            }
        }
        
        response = send_mcp_message(process, get_stats_message)
        print(f"Agent stats: {response['result']['content'][0]['text']}")
        
        print("\n✅ All operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Print server stderr for debugging
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
    
    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("\nServer stopped.")


if __name__ == "__main__":
    main() 
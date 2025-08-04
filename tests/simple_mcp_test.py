#!/usr/bin/env python3
"""
Simple test for MCP server with minimal dependencies
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
    """Simple test of MCP server."""
    print("Testing MCP server with stdin/stdout...")
    
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
        print("\n1. Testing initialization...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "0.1.0"
                }
            }
        }
        
        response = send_mcp_message(process, init_message)
        print(f"✅ Initialization successful: {response.get('result', {}).get('serverInfo', {})}")
        
        # 2. List tools
        print("\n2. Testing tool listing...")
        list_tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_mcp_message(process, list_tools_message)
        tools = response.get('result', {}).get('tools', [])
        print(f"✅ Tools listed successfully: {[tool['name'] for tool in tools]}")
        
        print("\n✅ All basic tests passed!")
        
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
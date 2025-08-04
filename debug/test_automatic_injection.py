#!/usr/bin/env python3
"""
Test Automatic Context Injection
Simulates Cursor's automatic context injection behavior
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_automatic_injection():
    """Test automatic context injection simulation."""
    print("🧪 **Testing Automatic Context Injection**")
    print("=" * 50)
    
    project_path = Path(__file__).parent.parent
    server_script = project_path / "src" / "simple_mcp_server.py"
    
    print("1. Starting MCP server...")
    process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={
            "PYTHONPATH": str(project_path),
            "MCP_PROJECT_ID": "mcp-context-manager-python"
        }
    )
    
    try:
        time.sleep(2)  # Wait for server to start
        
        print("2. Initializing server...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cursor-simulator",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No initialization response")
        
        print("3. Testing automatic context injection...")
        
        # Simulate Cursor's automatic injection call
        auto_injection_message = {
            "jsonrpc": "2.0",
            "id": "auto_injection",
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "user_message": "Continue helping with the project based on our previous work",
                    "prompt_type": "continuation",
                    "focus_areas": ["python", "mcp", "development", "memory"]
                }
            }
        }
        
        process.stdin.write(json.dumps(auto_injection_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No response from automatic injection")
        
        result = json.loads(response)
        
        if "result" in result and "content" in result["result"]:
            context_text = result["result"]["content"][0]["text"]
            print("✅ **Automatic Injection Test Successful!**")
            print("=" * 50)
            print(context_text)
            print("=" * 50)
            print("🎯 The MCP server is working correctly!")
            print("❌ The issue is with Cursor's integration")
        else:
            print("❌ Automatic injection test failed")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_automatic_injection()

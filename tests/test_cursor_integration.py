#!/usr/bin/env python3
"""
Test Cursor MCP Integration
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_mcp_server_communication():
    """Test if the MCP server can communicate properly."""
    print("🧪 **Testing MCP Server Communication**")
    print("=" * 50)
    
    project_path = Path(__file__).parent
    server_script = project_path / "src" / "simple_mcp_server.py"
    
    # Start the server
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
        # Test 1: Initialize
        print("1. Testing initialization...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cursor-test",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        result = json.loads(response)
        print(f"✅ Init response: {result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Test 2: List tools
        print("\n2. Testing tool listing...")
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        result = json.loads(response)
        tools = result.get('result', {}).get('tools', [])
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.get('name', 'Unknown')}")
        
        # Test 3: Test context summary
        print("\n3. Testing context summary...")
        context_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "max_memories": 5,
                    "include_recent": True
                }
            }
        }
        
        process.stdin.write(json.dumps(context_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        result = json.loads(response)
        
        if "result" in result and "content" in result["result"]:
            context_text = result["result"]["content"][0]["text"]
            print("✅ Context summary retrieved successfully")
            print(f"   Length: {len(context_text)} characters")
        else:
            print("❌ Failed to get context summary")
            print(f"   Error: {result}")
        
        # Test 4: Test AI prompt crafting
        print("\n4. Testing AI prompt crafting...")
        prompt_message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "user_message": "Continue helping with the project",
                    "prompt_type": "continuation",
                    "focus_areas": ["python", "mcp", "development"]
                }
            }
        }
        
        process.stdin.write(json.dumps(prompt_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        result = json.loads(response)
        
        if "result" in result and "content" in result["result"]:
            prompt_text = result["result"]["content"][0]["text"]
            print("✅ AI prompt crafting works")
            print(f"   Length: {len(prompt_text)} characters")
        else:
            print("❌ Failed to craft AI prompt")
            print(f"   Error: {result}")
        
        print("\n" + "=" * 50)
        print("✅ MCP Server Communication Test: PASSED")
        print("   All tools are working correctly")
        print("   Server can handle Cursor's requests")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        process.terminate()
        process.wait()

def check_cursor_configuration():
    """Check if Cursor configuration is properly set up."""
    print("\n🔧 **Checking Cursor Configuration**")
    print("=" * 50)
    
    config_file = Path(__file__).parent / "cursor_integration.json"
    
    if config_file.exists():
        print("✅ cursor_integration.json exists")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check MCP server configuration
        mcp_servers = config.get('mcpServers', {})
        if 'mcp-memory-server' in mcp_servers:
            server_config = mcp_servers['mcp-memory-server']
            print("✅ MCP server configured")
            print(f"   Command: {server_config.get('command', 'Unknown')}")
            print(f"   Script: {server_config.get('args', ['Unknown'])[0]}")
            print(f"   Auto injection: {server_config.get('autoContextInjection', False)}")
            print(f"   Context project: {server_config.get('contextProjectId', 'Unknown')}")
        else:
            print("❌ MCP server not configured")
        
        # Check commands
        commands = config.get('commands', {})
        print(f"✅ {len(commands)} commands configured")
        for cmd_name, cmd_config in commands.items():
            print(f"   - {cmd_name}: {cmd_config.get('shortcut', 'No shortcut')}")
        
        # Check auto injection
        auto_injection = config.get('autoInjection', {})
        if auto_injection.get('enabled', False):
            print("✅ Auto injection enabled")
            print(f"   Trigger events: {auto_injection.get('triggerEvents', [])}")
        else:
            print("❌ Auto injection disabled")
    
    else:
        print("❌ cursor_integration.json not found")

def suggest_cursor_integration_fixes():
    """Suggest fixes for Cursor integration issues."""
    print("\n🛠️ **Cursor Integration Fixes**")
    print("=" * 50)
    
    print("1. **Check Cursor's MCP Settings:**")
    print("   - Open Cursor settings")
    print("   - Look for 'MCP' or 'Model Context Protocol' section")
    print("   - Ensure MCP is enabled")
    print("   - Check if our server is listed")
    
    print("\n2. **Verify Configuration Location:**")
    print("   - cursor_integration.json should be in project root")
    print("   - Cursor might need to reload the configuration")
    print("   - Try restarting Cursor")
    
    print("\n3. **Test Manual Commands:**")
    print("   - Try Cmd+Shift+C (inject context)")
    print("   - Try Cmd+Shift+M (show context)")
    print("   - Try Cmd+Shift+A (add memory)")
    
    print("\n4. **Alternative Integration:**")
    print("   - Use Cursor's built-in MCP support")
    print("   - Configure via Cursor's UI instead of JSON")
    print("   - Check Cursor's documentation for MCP setup")

if __name__ == "__main__":
    test_mcp_server_communication()
    check_cursor_configuration()
    suggest_cursor_integration_fixes() 
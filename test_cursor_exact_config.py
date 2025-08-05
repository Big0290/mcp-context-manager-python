#!/usr/bin/env python3
"""
Test the exact configuration Cursor will use.
"""

import json
import os
import subprocess
import time


def test_cursor_exact_config():
    """Test the exact configuration Cursor will use."""
    print("🧪 Testing Cursor Exact Configuration")
    print("=" * 40)

    # Use the exact same configuration as Cursor
    command = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/venv/bin/python"
    args = [
        "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/mcp_server_protocol.py"
    ]
    cwd = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python"
    env = {
        "ENABLE_BRAIN_FEATURES": "true",
        "ENABLE_PLUGINS": "true",
        "BRAIN_ENHANCEMENT_LEVEL": "full",
        "EMOTIONAL_LEARNING_ENABLED": "true",
        "COGNITIVE_LOOP_ENABLED": "true",
        "PLUGIN_DIRS": "plugins,src/plugins,~/.mcp/plugins",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python",
    }

    print(f"Command: {command}")
    print(f"Args: {args}")
    print(f"CWD: {cwd}")
    print(f"ENV: {env}")

    # Start the server with exact Cursor config
    process = subprocess.Popen(
        [command] + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env=env,
    )

    # Wait for startup
    time.sleep(3)

    if process.poll() is not None:
        print("❌ Server failed to start")
        stderr = process.stderr.read()
        print(f"Error: {stderr}")
        return False

    print("✅ Server started successfully")

    # Test initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "cursor-test", "version": "1.0.0"},
        },
    }

    try:
        # Send request
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        if response:
            result = json.loads(response)
            print("✅ Initialize successful")
            print(f"   Server: {result['result']['serverInfo']['name']}")
            print(f"   Version: {result['result']['serverInfo']['version']}")

            # Test tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }

            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()

            tools_response = process.stdout.readline()
            if tools_response:
                tools_result = json.loads(tools_response)
                tools = tools_result["result"]["tools"]
                print(f"✅ Tools list successful - {len(tools)} tools available")

                # Show brain tools
                brain_tools = [t for t in tools if "brain" in t["name"].lower()]
                print(f"   Brain tools: {len(brain_tools)}")

                for i, tool in enumerate(brain_tools[:3], 1):
                    print(f"   {i}. {tool['name']}")

                return True
            else:
                print("❌ No tools response")
                return False
        else:
            print("❌ No initialize response")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except:
            process.kill()


if __name__ == "__main__":
    success = test_cursor_exact_config()

    if success:
        print("\n🎉 Configuration works correctly!")
        print("💡 The issue might be:")
        print("   1. Cursor needs a complete restart")
        print("   2. Cursor cache needs clearing")
        print("   3. Try restarting your computer")
    else:
        print("\n❌ Configuration has issues")
        print("🔧 Need to fix the server configuration")

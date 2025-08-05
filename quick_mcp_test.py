#!/usr/bin/env python3
"""
Quick test to verify MCP server is working.
"""

import json
import subprocess
import time


def test_mcp_server():
    """Quick test of MCP server."""
    print("🧪 Quick MCP Server Test")
    print("=" * 30)

    # Start server
    process = subprocess.Popen(
        ["python3", "mcp_server_protocol.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=".",
    )

    # Wait for startup
    time.sleep(3)

    if process.poll() is not None:
        print("❌ Server failed to start")
        return False

    print("✅ Server started successfully")

    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"},
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
    success = test_mcp_server()

    if success:
        print("\n🎉 MCP server is working correctly!")
        print("💡 The issue is likely in Cursor's configuration.")
        print("\nNext steps:")
        print("1. Copy cursor_mcp_config.json to ~/.cursor/mcp.json")
        print("2. Restart Cursor completely (Cmd+Q)")
        print("3. Check if the red status is gone")
    else:
        print("\n❌ MCP server has issues")

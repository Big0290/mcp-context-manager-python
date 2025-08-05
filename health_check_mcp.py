#!/usr/bin/env python3
"""
Quick Health Check for MCP Server
Tests if server responds fast enough for Cursor's health checks.
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path


async def health_check_mcp():
    """Quick health check for MCP server."""
    print("🏥 MCP Server Health Check")
    print("=" * 30)

    # Use Cursor's exact paths
    python_path = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/venv/bin/python"
    script_path = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/mcp_server_protocol.py"
    cwd = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python"

    # Start server
    process = subprocess.Popen(
        [python_path, script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env={
            "ENABLE_BRAIN_FEATURES": "true",
            "ENABLE_PLUGINS": "true",
            "PYTHONPATH": cwd,
        },
    )

    try:
        # Wait for startup
        await asyncio.sleep(2)

        # Quick initialize test
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "health-check", "version": "1.0.0"},
            },
        }

        start_time = time.time()
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response with short timeout
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, process.stdout.readline),
                timeout=2.0,
            )

            response_time = time.time() - start_time

            if response:
                print(f"✅ Health check passed! Response time: {response_time:.2f}s")
                print("✅ Server is responding quickly enough")
                return True
            else:
                print("❌ No response from server")
                return False

        except asyncio.TimeoutError:
            print("❌ Health check timeout - server too slow")
            print("💡 This might be why Cursor shows red status")
            return False

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


async def main():
    """Run health check."""
    success = await health_check_mcp()

    if success:
        print("\n💡 The server is healthy!")
        print("🔴 The red status in Cursor is likely due to:")
        print("   1. Cursor needs a full restart (Cmd+Q)")
        print("   2. Cursor cache issues")
        print("   3. Network/connection timing issues")
    else:
        print("\n❌ Server health check failed")
        print("🔧 This explains the red status - server needs fixing")


if __name__ == "__main__":
    asyncio.run(main())

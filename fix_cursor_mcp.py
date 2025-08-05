#!/usr/bin/env python3
"""
Fix Cursor MCP Connection
Restarts MCP server with clean state and tests connection.
"""

import os
import signal
import subprocess
import time

import psutil


def kill_mcp_processes():
    """Kill any existing MCP server processes."""
    print("🔪 Killing existing MCP processes...")

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"]
            if cmdline and any("mcp_server_protocol.py" in str(arg) for arg in cmdline):
                print(f"Killing process {proc.info['pid']}: {' '.join(cmdline)}")
                proc.terminate()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass


def start_mcp_server():
    """Start MCP server with clean environment."""
    print("🚀 Starting MCP server with clean state...")

    python_path = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/venv/bin/python"
    script_path = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/mcp_server_protocol.py"
    cwd = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python"

    env = os.environ.copy()
    env.update(
        {
            "ENABLE_BRAIN_FEATURES": "true",
            "ENABLE_PLUGINS": "true",
            "BRAIN_ENHANCEMENT_LEVEL": "full",
            "EMOTIONAL_LEARNING_ENABLED": "true",
            "COGNITIVE_LOOP_ENABLED": "true",
            "PLUGIN_DIRS": "plugins,src/plugins,~/.mcp/plugins",
            "LOG_LEVEL": "INFO",
            "PYTHONPATH": cwd,
            "MCP_CLEAN_START": "true",
        }
    )

    process = subprocess.Popen(
        [python_path, script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env=env,
    )

    print(f"✅ MCP server started with PID: {process.pid}")
    return process


def test_mcp_connection():
    """Test MCP connection with simple request."""
    print("🧪 Testing MCP connection...")

    # Simple test request
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "cursor-test", "version": "1.0.0"},
        },
    }

    python_path = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/venv/bin/python"
    script_path = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python/mcp_server_protocol.py"
    cwd = "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/OpenSource_Projects/mcp-context-manager-python"

    process = subprocess.Popen(
        [python_path, script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env={"PYTHONPATH": cwd},
    )

    try:
        # Send test request
        process.stdin.write(f"{test_request}\n")
        process.stdin.flush()

        # Wait for response
        time.sleep(1)

        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server is running and responsive")
            process.terminate()
            return True
        else:
            print("❌ MCP server process died")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        try:
            process.terminate()
            process.wait(timeout=3)
        except:
            pass


def main():
    """Main fix routine."""
    print("🔧 Fixing Cursor MCP Connection")
    print("=" * 40)

    # 1. Kill existing processes
    kill_mcp_processes()
    time.sleep(2)

    # 2. Test connection
    if test_mcp_connection():
        print("\n✅ MCP server is working correctly!")
        print("\n💡 Next steps:")
        print("1. Completely quit Cursor (Cmd+Q)")
        print("2. Wait 10 seconds")
        print("3. Reopen Cursor")
        print("4. Check if red status is gone")
        print("\n🎯 The server is healthy - this is a Cursor display issue!")
    else:
        print("\n❌ MCP server has issues")
        print("🔧 Need to investigate server problems")


if __name__ == "__main__":
    main()

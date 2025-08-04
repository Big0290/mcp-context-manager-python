#!/usr/bin/env python3
"""
Fixed Manual Context Injection Script
Use this to manually inject context when automatic injection isn't working
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def inject_context_manually():
    """Manually inject context for the current project."""
    print("🎯 **Manual Context Injection**")
    print("=" * 50)

    project_path = Path(__file__).parent.parent
    server_script = project_path / "src" / "simple_mcp_server.py"

    # Start the server with proper error handling
    try:
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={
                "PYTHONPATH": str(project_path),
                "MCP_PROJECT_ID": "mcp-context-manager-python",
            },
        )

        # Wait a moment for server to start
        time.sleep(1)

        # Initialize
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "manual-injector", "version": "1.0.0"},
            },
        }

        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()

        # Read init response with timeout
        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No response from server during initialization")

        # Get context summary
        context_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "max_memories": 10,
                    "include_recent": True,
                    "focus_areas": ["python", "mcp", "development"],
                },
            },
        }

        process.stdin.write(json.dumps(context_message) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No response from server for context summary")

        result = json.loads(response)

        if "result" in result and "content" in result["result"]:
            context_text = result["result"]["content"][0]["text"]
            print("📋 **Context Summary:**")
            print(context_text)
            print("\n" + "=" * 50)
            print("✅ Context injection ready!")
            print("Copy the context above and paste it into your chat session.")
        else:
            print("❌ Failed to get context summary")
            print(f"Response: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try running the server manually first:")
        print(f"   python3 {server_script}")

    finally:
        if "process" in locals():
            process.terminate()
            process.wait()


def craft_ai_prompt():
    """Craft an intelligent AI prompt with context."""
    print("🧠 **Intelligent Context Crafting**")
    print("=" * 50)

    project_path = Path(__file__).parent.parent
    server_script = project_path / "src" / "simple_mcp_server.py"

    try:
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={
                "PYTHONPATH": str(project_path),
                "MCP_PROJECT_ID": "mcp-context-manager-python",
            },
        )

        # Wait a moment for server to start
        time.sleep(1)

        # Initialize
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "prompt-crafter", "version": "1.0.0"},
            },
        }

        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No response from server during initialization")

        # Craft AI prompt
        prompt_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "mcp-context-manager-python",
                    "user_message": "Continue helping with the project based on our previous work",
                    "prompt_type": "continuation",
                    "focus_areas": ["python", "mcp", "development"],
                },
            },
        }

        process.stdin.write(json.dumps(prompt_message) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        if not response:
            raise RuntimeError("No response from server for AI prompt crafting")

        result = json.loads(response)

        if "result" in result and "content" in result["result"]:
            prompt_text = result["result"]["content"][0]["text"]
            print("🎯 **Crafted AI Prompt:**")
            print(prompt_text)
            print("\n" + "=" * 50)
            print("✅ Intelligent prompt ready!")
            print("Copy the prompt above and paste it into your chat session.")
        else:
            print("❌ Failed to craft AI prompt")
            print(f"Response: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try running the server manually first:")
        print(f"   python3 {server_script}")

    finally:
        if "process" in locals():
            process.terminate()
            process.wait()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "prompt":
        craft_ai_prompt()
    else:
        inject_context_manually()

#!/usr/bin/env python3
"""
Test Cursor MCP Communication
Comprehensive test to verify MCP server communication with Cursor.
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path


class MCPCommunicationTester:
    """Test MCP server communication."""

    def __init__(self):
        self.process = None
        self.cwd = Path(__file__).parent
        self.python_path = "python3"
        self.script_path = self.cwd / "mcp_server_protocol.py"

    async def start_server(self):
        """Start the MCP server."""
        print("🚀 Starting MCP server...")

        env = {
            "ENABLE_BRAIN_FEATURES": "true",
            "ENABLE_PLUGINS": "true",
            "BRAIN_ENHANCEMENT_LEVEL": "full",
            "EMOTIONAL_LEARNING_ENABLED": "true",
            "COGNITIVE_LOOP_ENABLED": "true",
            "PLUGIN_DIRS": "plugins,src/plugins,~/.mcp/plugins",
            "LOG_LEVEL": "INFO",
            "PYTHONPATH": str(self.cwd),
        }

        self.process = subprocess.Popen(
            [self.python_path, str(self.script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(self.cwd),
            env=env,
        )

        # Wait for server to start
        await asyncio.sleep(2)

        if self.process.poll() is None:
            print("✅ MCP server started successfully")
            return True
        else:
            print("❌ MCP server failed to start")
            return False

    async def send_request(self, request: dict) -> dict:
        """Send a request to the MCP server and get response."""
        if not self.process or self.process.poll() is not None:
            raise Exception("Server not running")

        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()

        # Read response
        response_line = await asyncio.get_event_loop().run_in_executor(
            None, self.process.stdout.readline
        )

        if response_line:
            return json.loads(response_line.strip())
        else:
            raise Exception("No response from server")

    async def test_initialize(self):
        """Test initialize request."""
        print("\n1️⃣ Testing Initialize...")

        request = {
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
            response = await self.send_request(request)
            print("✅ Initialize successful")
            print(f"   Server: {response['result']['serverInfo']['name']}")
            print(f"   Version: {response['result']['serverInfo']['version']}")
            return True
        except Exception as e:
            print(f"❌ Initialize failed: {e}")
            return False

    async def test_tools_list(self):
        """Test tools/list request."""
        print("\n2️⃣ Testing Tools List...")

        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        try:
            response = await self.send_request(request)
            tools = response["result"]["tools"]
            print(f"✅ Tools list successful - {len(tools)} tools available")

            # Show brain tools
            brain_tools = [tool for tool in tools if "brain" in tool["name"].lower()]
            for i, tool in enumerate(brain_tools[:5], 1):
                print(f"   {i}. {tool['name']}: {tool['description']}")

            return True
        except Exception as e:
            print(f"❌ Tools list failed: {e}")
            return False

    async def test_tool_call(self):
        """Test tool call."""
        print("\n3️⃣ Testing Tool Call...")

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "mcp_brain-enhanced-mcp_get_brain_status",
                "arguments": {},
            },
        }

        try:
            response = await self.send_request(request)
            print("✅ Tool call successful")
            print(f"   Result: {response['result']}")
            return True
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return False

    async def test_identity_summary(self):
        """Test identity summary tool."""
        print("\n4️⃣ Testing Identity Summary...")

        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "mcp_brain-enhanced-mcp_get_identity_summary",
                "arguments": {},
            },
        }

        try:
            response = await self.send_request(request)
            print("✅ Identity summary successful")
            identity = response["result"]
            print(f"   Name: {identity.get('name', 'Unknown')}")
            print(f"   Role: {identity.get('role', 'Unknown')}")
            print(f"   Emotional State: {identity.get('emotional_summary', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Identity summary failed: {e}")
            return False

    async def cleanup(self):
        """Clean up the server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()

    async def run_tests(self):
        """Run all tests."""
        print("🧪 Testing Cursor MCP Communication")
        print("=" * 50)

        try:
            # Start server
            if not await self.start_server():
                return False

            # Run tests
            tests = [
                self.test_initialize(),
                self.test_tools_list(),
                self.test_tool_call(),
                self.test_identity_summary(),
            ]

            results = await asyncio.gather(*tests, return_exceptions=True)

            # Check results
            success_count = sum(1 for result in results if result is True)
            total_tests = len(results)

            print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")

            if success_count == total_tests:
                print("🎉 All tests passed! MCP communication is working correctly.")
                print("\n💡 Next steps:")
                print("1. Copy cursor_mcp_config.json to ~/.cursor/mcp.json")
                print("2. Restart Cursor completely (Cmd+Q)")
                print("3. Check if the red status is gone")
                return True
            else:
                print("❌ Some tests failed. Check the server configuration.")
                return False

        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return False
        finally:
            await self.cleanup()


async def main():
    """Run the communication test."""
    tester = MCPCommunicationTester()
    success = await tester.run_tests()

    if success:
        print("\n✅ MCP server is ready for Cursor!")
    else:
        print("\n❌ MCP server needs configuration fixes")


if __name__ == "__main__":
    asyncio.run(main())

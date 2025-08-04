#!/usr/bin/env python3
"""
Simple test client for MCP Memory Server
Tests stdin/stdout communication
"""

import json
import subprocess
import sys
from typing import Any, Dict


class MCPTestClient:
    def __init__(self, server_command: str):
        self.server_command = server_command
        self.process = None

    def start_server(self):
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            self.server_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

    def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the server and get response."""
        if not self.process:
            raise RuntimeError("Server not started")

        # Send message
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str)
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        return json.loads(response_line.strip())

    def stop_server(self):
        """Stop the server process."""
        if self.process:
            self.process.terminate()
            self.process.wait()

    def test_initialization(self):
        """Test server initialization."""
        print("Testing server initialization...")

        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "0.1.0"},
            },
        }

        response = self.send_message(init_message)
        print(f"Initialization response: {json.dumps(response, indent=2)}")
        return response

    def test_list_tools(self):
        """Test listing tools."""
        print("\nTesting tool listing...")

        list_tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        response = self.send_message(list_tools_message)
        print(f"Tools response: {json.dumps(response, indent=2)}")
        return response

    def test_push_memory(self):
        """Test pushing a memory."""
        print("\nTesting memory push...")

        push_memory_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "This is a test memory from the MCP client",
                    "memory_type": "fact",
                    "priority": "medium",
                    "tags": ["test", "mcp"],
                    "project_id": "test-project",
                },
            },
        }

        response = self.send_message(push_memory_message)
        print(f"Push memory response: {json.dumps(response, indent=2)}")
        return response

    def test_fetch_memory(self):
        """Test fetching memories."""
        print("\nTesting memory fetch...")

        fetch_memory_message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "fetch_memory",
                "arguments": {
                    "query": "test memory",
                    "limit": 5,
                    "project_id": "test-project",
                },
            },
        }

        response = self.send_message(fetch_memory_message)
        print(f"Fetch memory response: {json.dumps(response, indent=2)}")
        return response

    def test_register_agent(self):
        """Test agent registration."""
        print("\nTesting agent registration...")

        register_agent_message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "register_agent",
                "arguments": {
                    "name": "Test Agent",
                    "agent_type": "cli",
                    "project_id": "test-project",
                },
            },
        }

        response = self.send_message(register_agent_message)
        print(f"Register agent response: {json.dumps(response, indent=2)}")
        return response

    def run_all_tests(self):
        """Run all tests."""
        try:
            self.start_server()
            print("Server started successfully")

            # Run tests
            self.test_initialization()
            self.test_list_tools()
            self.test_push_memory()
            self.test_fetch_memory()
            self.test_register_agent()

            print("\nAll tests completed successfully!")

        except Exception as e:
            print(f"Test failed: {e}")
            if self.process:
                stderr_output = self.process.stderr.read()
                if stderr_output:
                    print(f"Server stderr: {stderr_output}")
        finally:
            self.stop_server()


def main():
    """Main entry point."""
    # Use the refactored server
    server_command = "python3 src/mcp_server.py"

    client = MCPTestClient(server_command)
    client.run_all_tests()


if __name__ == "__main__":
    main()

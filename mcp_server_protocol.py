#!/usr/bin/env python3
"""
MCP Server with Protocol Implementation
Implements the Model Context Protocol for Cursor integration.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.extensible_mcp_server import ExtensibleMCPServer


class MCPProtocolServer:
    """MCP Server that implements the Model Context Protocol."""

    def __init__(self):
        self.extensible_server = ExtensibleMCPServer(
            enable_brain_features=True, enable_plugins=True
        )
        self.logger = logging.getLogger(__name__)
        self.tools = []
        self.initialized = False

    async def initialize(self):
        """Initialize the MCP server."""
        try:
            await self.extensible_server.start()
            self.tools = self.extensible_server.get_tools()
            self.initialized = True
            self.logger.info(f"MCP Server initialized with {len(self.tools)} tools")
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP server: {e}")
            raise

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return await self.handle_initialize(params, request_id)
            elif method == "tools/list":
                return await self.handle_tools_list(request_id)
            elif method == "tools/call":
                return await self.handle_tools_call(params, request_id)
            elif method == "resources/list":
                return await self.handle_resources_list(request_id)
            elif method == "resources/read":
                return await self.handle_resources_read(params, request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }

    async def handle_initialize(
        self, params: Dict[str, Any], request_id: Any
    ) -> Dict[str, Any]:
        """Handle initialize request."""
        await self.initialize()
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {
                    "name": "Brain-Enhanced Extensible MCP Server",
                    "version": "1.0.0",
                },
            },
        }

    async def handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = []
        for tool in self.tools:
            tools.append(
                {
                    "name": tool.get("name", "unknown"),
                    "description": tool.get("description", ""),
                    "inputSchema": tool.get("inputSchema", {}),
                }
            )

        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    async def handle_tools_call(
        self, params: Dict[str, Any], request_id: Any
    ) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Tool name is required"},
            }

        try:
            result = await self.extensible_server.execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}",
                },
            }

    async def handle_resources_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}

    async def handle_resources_read(
        self, params: Dict[str, Any], request_id: Any
    ) -> Dict[str, Any]:
        """Handle resources/read request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Resources not supported"},
        }

    async def run(self):
        """Run the MCP server."""
        try:
            # Set up logging
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

            self.logger.info("🧠 Brain-Enhanced MCP Server Starting...")
            self.logger.info("Features enabled:")
            self.logger.info("  ✅ Brain Enhancement")
            self.logger.info("  ✅ Plugin System")
            self.logger.info("  ✅ Emotional Learning")
            self.logger.info("  ✅ Cognitive Loop")
            self.logger.info("  ✅ Memory Management")
            self.logger.info("  ✅ Context Injection")

            # Initialize the server
            await self.initialize()

            # Start reading from stdin for MCP protocol
            self.logger.info("✅ MCP Server ready - listening for requests")

            while True:
                try:
                    # Read line from stdin
                    line = await asyncio.get_event_loop().run_in_executor(
                        None, sys.stdin.readline
                    )
                    if not line:
                        break

                    # Parse JSON request
                    request = json.loads(line.strip())
                    self.logger.debug(
                        f"Received request: {request.get('method', 'unknown')}"
                    )

                    # Handle request
                    response = await self.handle_request(request)

                    # Send response
                    print(json.dumps(response))
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing request: {e}")

        except KeyboardInterrupt:
            self.logger.info("🛑 Shutting down MCP server...")
        except Exception as e:
            self.logger.error(f"❌ Server error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            if self.initialized:
                await self.extensible_server.stop()
                self.logger.info("✅ MCP Server stopped")


async def main():
    """Main entry point."""
    server = MCPProtocolServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

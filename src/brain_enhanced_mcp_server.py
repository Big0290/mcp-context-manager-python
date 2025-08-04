#!/usr/bin/env python3
"""
Brain-Enhanced MCP Server
Extends the existing SimpleMCPServer with brain-like memory capabilities.
Maintains full backward compatibility while adding advanced memory features.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from src.brain_integration import BrainIntegration
from src.simple_mcp_server import SimpleMCPServer


class BrainEnhancedMCPServer:
    """
    Brain-enhanced MCP server that extends SimpleMCPServer with advanced memory capabilities.

    Features:
    - All original SimpleMCPServer functionality (100% backward compatible)
    - Multilayered memory architecture (short-term, long-term, episodic, procedural, semantic)
    - Neural-style interconnected memories with automatic connection discovery
    - Cross-referencing and similarity lookback for analogical reasoning
    - Growing knowledge flow with automatic memory promotion
    - Hierarchical classification system for knowledge organization
    - Memory insights and recommendations
    - Knowledge graph visualization and traversal
    """

    def __init__(self, enable_brain_features: bool = True):
        # Initialize the original MCP server
        self.original_server = SimpleMCPServer()

        # Initialize brain integration layer
        self.brain_integration = BrainIntegration(
            self.original_server, enable_brain_features=enable_brain_features
        )

        self.enable_brain_features = enable_brain_features
        self.logger = logging.getLogger(__name__)

        # Schedule periodic memory maintenance
        if enable_brain_features:
            self._schedule_maintenance()

        self.logger.info(
            f"Brain-Enhanced MCP Server initialized "
            f"(Brain features: {'enabled' if enable_brain_features else 'disabled'})"
        )

    def _schedule_maintenance(self):
        """Schedule periodic memory maintenance tasks."""

        async def maintenance_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # Run every hour
                    await self.brain_integration.run_memory_maintenance()
                except Exception as e:
                    self.logger.error(f"Error in maintenance loop: {e}")

        # Start maintenance task
        asyncio.create_task(maintenance_loop())

    def get_tools(self):
        """Get all available tools including brain enhancements."""
        return self.brain_integration.get_enhanced_tools()

    async def execute_tool(self, tool_name: str, arguments: dict):
        """Execute tools with brain enhancements."""
        return await self.brain_integration.execute_enhanced_tool(tool_name, arguments)

    @property
    def db_path(self):
        """Database path for compatibility."""
        return self.original_server.db_path

    @property
    def project_id(self):
        """Current project ID."""
        return self.original_server.project_id

    @property
    def conversation_recorder(self):
        """Conversation recorder for compatibility."""
        return self.original_server.conversation_recorder

    def setup_logging(self):
        """Setup logging (delegated to original server)."""
        return self.original_server.setup_logging()

    def get_db_connection(self):
        """Get database connection (delegated to original server)."""
        return self.original_server.get_db_connection()

    async def get_brain_status(self):
        """Get status of brain features."""
        if not self.enable_brain_features:
            return {"brain_enabled": False, "message": "Brain features are disabled"}

        try:
            brain_system = self.brain_integration.brain_system
            status = {
                "brain_enabled": True,
                "memory_nodes_count": len(brain_system.memory_nodes),
                "connections_count": sum(
                    len(conns) for conns in brain_system.connections.values()
                ),
                "topic_categories": len(brain_system.topic_hierarchy),
                "skill_categories": len(brain_system.skill_hierarchy),
                "last_maintenance": datetime.now().isoformat(),
            }

            # Get memory layer distribution
            layer_dist = {}
            for node in brain_system.memory_nodes.values():
                layer = node.metadata.memory_layer.value
                layer_dist[layer] = layer_dist.get(layer, 0) + 1

            status["layer_distribution"] = layer_dist
            return status

        except Exception as e:
            return {
                "brain_enabled": True,
                "error": f"Error getting brain status: {str(e)}",
            }


async def main():
    """
    Main entry point for Brain-Enhanced MCP server.
    Maintains full compatibility with original MCP protocol.
    """
    # Check if brain features should be enabled
    enable_brain = not ("--no-brain" in sys.argv)

    server = BrainEnhancedMCPServer(enable_brain_features=enable_brain)

    # Handle stdio communication following MCP protocol (same as original)
    while True:
        try:
            # Read from stdin
            line = sys.stdin.readline()
            if not line:
                break

            # Parse JSON message
            data = json.loads(line.strip())
            message_type = data.get("jsonrpc")
            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")

            # Auto-record incoming messages for conversation tracking
            if method and method != "initialize":
                # Extract user message from tool calls
                if method == "tools/call":
                    tool_name = params.get("name", "")
                    arguments = params.get("arguments", {})

                    # Record user intent based on tool calls
                    if tool_name == "push_memory":
                        content = arguments.get("content", "")
                        if content:
                            server.conversation_recorder.record_user_message(
                                f"User added memory: {content}"
                            )
                    elif tool_name == "fetch_memory":
                        server.conversation_recorder.record_user_message(
                            "User requested memory retrieval"
                        )
                    elif tool_name == "get_context_summary":
                        server.conversation_recorder.record_user_message(
                            "User requested context summary"
                        )
                    elif tool_name == "search_similar_experiences":
                        query = arguments.get("query", "")
                        server.conversation_recorder.record_user_message(
                            f"User searched similar experiences: {query}"
                        )
                    elif tool_name == "get_knowledge_graph":
                        topic = arguments.get("center_topic", "")
                        server.conversation_recorder.record_user_message(
                            f"User requested knowledge graph for: {topic}"
                        )
                    else:
                        server.conversation_recorder.record_user_message(
                            f"User called tool: {tool_name}"
                        )

            # Handle different MCP message types (same as original)
            if method == "initialize":
                # Initialize response
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "brain-enhanced-mcp-memory-server",
                            "version": "1.0.0",
                        },
                    },
                }
                print(json.dumps(response), flush=True)

            elif method == "tools/list":
                # List tools response (includes brain tools)
                tools = server.get_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools},
                }
                print(json.dumps(response), flush=True)

            elif method == "tools/call":
                # Call tool response (with brain enhancements)
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result = await server.execute_tool(tool_name, arguments)

                # Auto-record AI response based on tool results
                if result and not result.get("isError", True):
                    content = result.get("content", [{}])[0].get("text", "")
                    if content:
                        server.conversation_recorder.record_ai_response(
                            f"AI provided response: {content}"
                        )

                response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                print(json.dumps(response), flush=True)

            elif method == "notifications/cancel":
                # Handle cancellation
                response = {"jsonrpc": "2.0", "id": request_id, "result": None}
                print(json.dumps(response), flush=True)

        except EOFError:
            # End conversation when connection closes
            server.conversation_recorder.end_conversation()
            break
        except Exception as e:
            # Error response
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id if "request_id" in locals() else None,
                "error": {"code": -32603, "message": str(e)},
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    asyncio.run(main())

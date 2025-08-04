#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Memory Management
Uses stdin/stdout for communication as per MCP specifications
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import our memory server components
from mcp_memory_server.config import settings
from mcp_memory_server.core.agent_service import AgentService
from mcp_memory_server.core.memory_engine import MemoryEngine
from mcp_memory_server.database.base import create_tables, get_db
from mcp_memory_server.models.agent import AgentCreate, AgentType
from mcp_memory_server.models.memory import MemoryCreate, MemoryPriority, MemoryType


class MCPMemoryServer:
    def __init__(self):
        self.memory_engine = MemoryEngine()
        self.agent_service = AgentService()

        # Initialize database
        create_tables()

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for MCP protocol."""
        return [
            {
                "name": "push_memory",
                "description": "Push a memory entry to the server",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The memory content to store",
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["fact", "preference", "task", "thread"],
                            "description": "Type of memory entry",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Priority level of the memory",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorization",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "fetch_memory",
                "description": "Fetch memories based on search criteria",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for semantic search",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags",
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["fact", "preference", "task", "thread"],
                            "description": "Filter by memory type",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                    },
                },
            },
            {
                "name": "get_agent_stats",
                "description": "Get statistics for an agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent identifier",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                    },
                    "required": ["agent_id"],
                },
            },
            {
                "name": "register_agent",
                "description": "Register a new agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Agent name"},
                        "agent_type": {
                            "type": "string",
                            "enum": ["chatbot", "cli", "web", "mobile", "other"],
                            "description": "Type of agent",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                    },
                    "required": ["name"],
                },
            },
        ]

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        try:
            if tool_name == "push_memory":
                return await self._push_memory(arguments)
            elif tool_name == "fetch_memory":
                return await self._fetch_memory(arguments)
            elif tool_name == "get_agent_stats":
                return await self._get_agent_stats(arguments)
            elif tool_name == "register_agent":
                return await self._register_agent(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _push_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Push a memory entry."""
        content = args.get("content", "")
        memory_type = args.get("memory_type", "fact")
        priority = args.get("priority", "medium")
        tags = args.get("tags", [])
        project_id = args.get("project_id", "default")

        # Create memory entry
        memory_data = MemoryCreate(
            content=content,
            memory_type=MemoryType(memory_type),
            priority=MemoryPriority(priority),
            tags=tags,
            project_id=project_id,
            agent_id="cursor-agent",  # Default agent ID
            is_short_term=False,
        )

        memory = await self.memory_engine.create_memory(memory_data)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Memory stored successfully with ID: {memory.id}",
                }
            ],
            "isError": False,
        }

    async def _fetch_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch memories based on criteria."""
        query = args.get("query", "")
        tags = args.get("tags", [])
        memory_type = args.get("memory_type")
        limit = args.get("limit", 10)
        project_id = args.get("project_id", "default")

        # Search memories
        memories = await self.memory_engine.search_memories(
            query=query,
            tags=tags,
            memory_type=memory_type,
            limit=limit,
            project_id=project_id,
        )

        # Format results
        results = []
        for memory in memories:
            results.append(
                {
                    "id": str(memory.id),
                    "content": memory.content,
                    "type": memory.memory_type.value,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat(),
                }
            )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(results)} memories:\n"
                    + json.dumps(results, indent=2),
                }
            ],
            "isError": False,
        }

    async def _get_agent_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent statistics."""
        agent_id = args.get("agent_id", "cursor-agent")
        project_id = args.get("project_id", "default")

        # Get agent stats
        stats = await self.agent_service.get_agent_stats(agent_id, project_id)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Agent Statistics:\n"
                    + f"Total memories: {stats.get('total_memories', 0)}\n"
                    + f"Memory types: {stats.get('memory_types', {})}\n"
                    + f"Top tags: {stats.get('top_tags', [])}",
                }
            ],
            "isError": False,
        }

    async def _register_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent."""
        name = args.get("name", "Cursor Agent")
        agent_type = args.get("agent_type", "other")
        project_id = args.get("project_id", "default")

        # Create agent
        agent_data = AgentCreate(
            name=name, agent_type=AgentType(agent_type), project_id=project_id
        )

        agent = await self.agent_service.create_agent(agent_data)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Agent registered successfully with ID: {agent.id}",
                }
            ],
            "isError": False,
        }


async def main():
    """Main entry point for MCP server using stdin/stdout."""
    server = MCPMemoryServer()

    # Handle stdio communication following MCP protocol
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

            # Handle different MCP message types
            if method == "initialize":
                # Initialize response
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "mcp-memory-server", "version": "0.1.0"},
                    },
                }
                print(json.dumps(response), flush=True)

            elif method == "tools/list":
                # List tools response
                tools = server.get_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools},
                }
                print(json.dumps(response), flush=True)

            elif method == "tools/call":
                # Call tool response
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result = await server.execute_tool(tool_name, arguments)

                response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                print(json.dumps(response), flush=True)

            elif method == "notifications/cancel":
                # Handle cancellation (if needed)
                response = {"jsonrpc": "2.0", "id": request_id, "result": None}
                print(json.dumps(response), flush=True)

        except EOFError:
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

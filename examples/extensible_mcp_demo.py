#!/usr/bin/env python3
"""
Extensible MCP Server Demo
Demonstrates the plugin system and brain enhancement features.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from src.extensible_mcp_server import ExtensibleMCPServer, MCPPlugin, PluginMetadata


class DemoPlugin(MCPPlugin):
    """Demo plugin showcasing extensible MCP server capabilities."""

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="demo_plugin",
            version="1.0.0",
            description="Demo plugin for extensible MCP server",
            author="MCP Team",
            dependencies=[],
            tags=["demo", "example"],
            priority=1,
        )

    async def initialize(self) -> bool:
        """Initialize the plugin."""
        self.logger.info("Initializing Demo Plugin...")
        self.counter = 0
        return True

    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        self.logger.info("Shutting down Demo Plugin...")
        return True

    def get_tools(self) -> list[Dict[str, Any]]:
        """Get tools provided by this plugin."""
        return [
            {
                "name": "demo_counter",
                "description": "Increment and get counter value",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "increment": {
                            "type": "boolean",
                            "description": "Whether to increment the counter",
                            "default": True,
                        }
                    },
                },
            },
            {
                "name": "demo_echo",
                "description": "Echo back the input with plugin prefix",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message to echo"}
                    },
                    "required": ["message"],
                },
            },
        ]

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool provided by this plugin."""
        if tool_name == "demo_counter":
            if arguments.get("increment", True):
                self.counter += 1
            return {
                "counter": self.counter,
                "message": f"Counter value: {self.counter}",
            }
        elif tool_name == "demo_echo":
            message = arguments.get("message", "")
            return {"echo": f"[DEMO PLUGIN] {message}", "original_message": message}
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def get_hooks(self) -> Dict[str, callable]:
        """Get hooks provided by this plugin."""
        return {
            "on_server_start": self._on_server_start,
            "on_server_stop": self._on_server_stop,
            "on_tool_executed": self._on_tool_executed,
        }

    async def _on_server_start(self):
        """Called when the server starts."""
        self.logger.info("Demo Plugin: Server started!")

    async def _on_server_stop(self):
        """Called when the server stops."""
        self.logger.info("Demo Plugin: Server stopping!")

    async def _on_tool_executed(
        self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]
    ):
        """Called after a tool is executed."""
        self.logger.info(
            f"Demo Plugin: Tool {tool_name} executed with result: {result}"
        )


async def demo_extensible_mcp_server():
    """Demo the extensible MCP server capabilities."""
    print("🚀 Starting Extensible MCP Server Demo")
    print("=" * 50)

    # Create server with both brain features and plugins enabled
    server = ExtensibleMCPServer(enable_brain_features=True, enable_plugins=True)

    print("✅ Server created successfully")
    print(f"Brain features enabled: {server.enable_brain_features}")
    print(f"Plugin system enabled: {server.enable_plugins}")

    # Start the server
    await server.start()
    print("✅ Server started successfully")

    # Load our demo plugin
    print("\n📦 Loading Demo Plugin...")
    success = await server.load_plugin(DemoPlugin)
    if success:
        print("✅ Demo Plugin loaded successfully")
    else:
        print("❌ Failed to load Demo Plugin")

    # Get server status
    print("\n📊 Server Status:")
    status = server.get_server_status()
    print(json.dumps(status, indent=2))

    # Get available tools
    print("\n🛠️ Available Tools:")
    tools = server.get_tools()
    for i, tool in enumerate(tools, 1):
        print(
            f"{i}. {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
        )

    # Test plugin tools
    print("\n🧪 Testing Plugin Tools:")

    # Test demo_counter tool
    print("\n1. Testing demo_counter tool:")
    result = await server.execute_tool("demo_counter", {"increment": True})
    print(f"Result: {result}")

    result = await server.execute_tool("demo_counter", {"increment": False})
    print(f"Result: {result}")

    # Test demo_echo tool
    print("\n2. Testing demo_echo tool:")
    result = await server.execute_tool("demo_echo", {"message": "Hello from demo!"})
    print(f"Result: {result}")

    # Test brain enhancement tools
    print("\n🧠 Testing Brain Enhancement Tools:")

    # Test memory push
    print("\n1. Testing memory push:")
    result = await server.execute_tool(
        "mcp_mcp-brain-context-manager_push_memory",
        {
            "content": "This is a test memory from extensible MCP server demo",
            "memory_type": "fact",
            "priority": "medium",
            "tags": ["demo", "extensible-mcp", "test"],
        },
    )
    print(f"Result: {result}")

    # Test memory fetch
    print("\n2. Testing memory fetch:")
    result = await server.execute_tool(
        "mcp_mcp-brain-context-manager_fetch_memory",
        {"query": "demo extensible MCP server", "limit": 5},
    )
    print(f"Result: {result}")

    # Get plugin status
    print("\n📋 Plugin Status:")
    plugin_status = server.get_plugin_status()
    print(json.dumps(plugin_status, indent=2))

    # Stop the server
    print("\n🛑 Stopping server...")
    await server.stop()
    print("✅ Server stopped successfully")

    print("\n🎉 Extensible MCP Server Demo completed successfully!")


async def demo_plugin_lifecycle():
    """Demo plugin lifecycle management."""
    print("\n🔄 Plugin Lifecycle Demo")
    print("=" * 30)

    server = ExtensibleMCPServer(enable_plugins=True)
    await server.start()

    # Load plugin
    print("📦 Loading plugin...")
    success = await server.load_plugin(DemoPlugin)
    print(f"Load result: {success}")

    # Get plugin status
    status = server.get_plugin_status()
    print(f"Loaded plugins: {len(status.get('loaded_plugins', []))}")

    # Unload plugin
    print("📦 Unloading plugin...")
    success = await server.unload_plugin("demo_plugin")
    print(f"Unload result: {success}")

    # Get plugin status again
    status = server.get_plugin_status()
    print(f"Loaded plugins after unload: {len(status.get('loaded_plugins', []))}")

    await server.stop()
    print("✅ Plugin lifecycle demo completed")


async def main():
    """Main demo function."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Run demos
        await demo_extensible_mcp_server()
        await demo_plugin_lifecycle()

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

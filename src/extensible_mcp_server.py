#!/usr/bin/env python3
"""
Extensible MCP Server with Plugin System
Allows dynamic updates and extensions without breaking existing modules.
"""

import asyncio
import importlib.util
import inspect
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

import yaml


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""

    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    priority: int = 0  # Higher priority plugins load first
    enabled: bool = True
    loaded_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "priority": self.priority,
            "enabled": self.enabled,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "last_updated": self.last_updated.isoformat()
            if self.last_updated
            else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Create metadata from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True),
            loaded_at=datetime.fromisoformat(data["loaded_at"])
            if data.get("loaded_at")
            else None,
            last_updated=datetime.fromisoformat(data["last_updated"])
            if data.get("last_updated")
            else None,
        )


class MCPPlugin(ABC):
    """Base class for MCP server plugins."""

    def __init__(self, server_instance=None):
        self.server = server_instance
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        pass

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools provided by this plugin."""
        return []

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool provided by this plugin."""
        return {
            "error": f"Tool {tool_name} not implemented in plugin {self.metadata.name}"
        }

    def get_hooks(self) -> Dict[str, callable]:
        """Get hooks provided by this plugin."""
        return {}

    def get_extensions(self) -> Dict[str, Any]:
        """Get extensions provided by this plugin."""
        return {}

    async def on_server_start(self):
        """Called when the server starts."""
        pass

    async def on_server_stop(self):
        """Called when the server stops."""
        pass

    async def on_tool_executed(
        self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]
    ):
        """Called after a tool is executed."""
        pass

    async def on_memory_updated(
        self, memory_id: str, operation: str, data: Dict[str, Any]
    ):
        """Called when memory is updated."""
        pass


class PluginManager:
    """Manages plugin loading, unloading, and lifecycle."""

    def __init__(self, server_instance=None):
        self.server = server_instance
        self.logger = logging.getLogger(__name__)

        # Plugin registry
        self.plugins: Dict[str, MCPPlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_dependencies: Dict[str, Set[str]] = {}

        # Plugin directories
        self.plugin_dirs = [
            Path.cwd() / "plugins",
            Path.cwd() / "src" / "plugins",
            Path.home() / ".mcp" / "plugins",
        ]

        # Create plugin directories if they don't exist
        for plugin_dir in self.plugin_dirs:
            plugin_dir.mkdir(parents=True, exist_ok=True)

        # Load plugin registry
        self.registry_file = Path.cwd() / "data" / "plugin_registry.json"
        self._load_registry()

    def _load_registry(self):
        """Load plugin registry from file."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    for plugin_name, metadata_dict in data.items():
                        self.plugin_metadata[plugin_name] = PluginMetadata.from_dict(
                            metadata_dict
                        )
        except Exception as e:
            self.logger.error(f"Error loading plugin registry: {e}")

    def _save_registry(self):
        """Save plugin registry to file."""
        try:
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_file, "w") as f:
                data = {
                    name: metadata.to_dict()
                    for name, metadata in self.plugin_metadata.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin registry: {e}")

    def discover_plugins(self) -> List[PluginMetadata]:
        """Discover available plugins in plugin directories."""
        discovered_plugins = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue

            for plugin_file in plugin_dir.glob("*.py"):
                try:
                    # Import the plugin module
                    module_name = f"plugins.{plugin_file.stem}"
                    spec = importlib.util.spec_from_file_location(
                        module_name, plugin_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find plugin classes
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, MCPPlugin)
                            and obj != MCPPlugin
                        ):
                            # Create temporary instance to get metadata
                            temp_plugin = obj(self.server)
                            metadata = temp_plugin.get_metadata()
                            discovered_plugins.append(metadata)

                except Exception as e:
                    self.logger.error(f"Error discovering plugin {plugin_file}: {e}")

        return discovered_plugins

    async def load_plugin(self, plugin_class: Type[MCPPlugin]) -> bool:
        """Load a plugin by class."""
        try:
            # Create plugin instance
            plugin = plugin_class(self.server)
            metadata = plugin.get_metadata()

            # Check dependencies
            if not await self._check_dependencies(metadata.dependencies):
                self.logger.error(
                    f"Plugin {metadata.name} has unmet dependencies: {metadata.dependencies}"
                )
                return False

            # Initialize plugin
            if not await plugin.initialize():
                self.logger.error(f"Failed to initialize plugin {metadata.name}")
                return False

            # Register plugin
            self.plugins[metadata.name] = plugin
            self.plugin_metadata[metadata.name] = metadata
            self.plugin_dependencies[metadata.name] = set(metadata.dependencies)

            # Update metadata
            metadata.loaded_at = datetime.now()
            metadata.last_updated = datetime.now()

            # Save registry
            self._save_registry()

            # Call server start hook
            await plugin.on_server_start()

            self.logger.info(
                f"Successfully loaded plugin: {metadata.name} v{metadata.version}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_class.__name__}: {e}")
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin by name."""
        try:
            if plugin_name not in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} not found")
                return False

            plugin = self.plugins[plugin_name]

            # Call server stop hook
            await plugin.on_server_stop()

            # Shutdown plugin
            if not await plugin.shutdown():
                self.logger.error(f"Failed to shutdown plugin {plugin_name}")
                return False

            # Remove from registry
            del self.plugins[plugin_name]
            del self.plugin_metadata[plugin_name]
            if plugin_name in self.plugin_dependencies:
                del self.plugin_dependencies[plugin_name]

            # Save registry
            self._save_registry()

            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin by name."""
        try:
            # Unload first
            if plugin_name in self.plugins:
                await self.unload_plugin(plugin_name)

            # Find and reload
            for plugin_dir in self.plugin_dirs:
                plugin_file = plugin_dir / f"{plugin_name}.py"
                if plugin_file.exists():
                    # Import the plugin module
                    module_name = f"plugins.{plugin_name}"
                    spec = importlib.util.spec_from_file_location(
                        module_name, plugin_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find plugin class
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, MCPPlugin)
                            and obj != MCPPlugin
                        ):
                            return await self.load_plugin(obj)

            self.logger.error(f"Plugin {plugin_name} not found for reload")
            return False

        except Exception as e:
            self.logger.error(f"Error reloading plugin {plugin_name}: {e}")
            return False

    async def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if plugin dependencies are met."""
        for dep in dependencies:
            if dep not in self.plugins:
                return False
        return True

    def get_plugin_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all plugins."""
        tools = []
        for plugin in self.plugins.values():
            tools.extend(plugin.get_tools())
        return tools

    async def execute_plugin_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool from a plugin."""
        for plugin in self.plugins.values():
            tools = plugin.get_tools()
            tool_names = [tool.get("name") for tool in tools]
            if tool_name in tool_names:
                return await plugin.execute_tool(tool_name, arguments)

        return {"error": f"Tool {tool_name} not found in any plugin"}

    def get_plugin_hooks(self) -> Dict[str, callable]:
        """Get all hooks from all plugins."""
        hooks = {}
        for plugin in self.plugins.values():
            hooks.update(plugin.get_hooks())
        return hooks

    def get_plugin_extensions(self) -> Dict[str, Any]:
        """Get all extensions from all plugins."""
        extensions = {}
        for plugin in self.plugins.values():
            extensions.update(plugin.get_extensions())
        return extensions

    async def call_plugin_hooks(self, hook_name: str, *args, **kwargs):
        """Call a specific hook on all plugins."""
        for plugin in self.plugins.values():
            hooks = plugin.get_hooks()
            if hook_name in hooks:
                try:
                    await hooks[hook_name](*args, **kwargs)
                except Exception as e:
                    self.logger.error(
                        f"Error calling hook {hook_name} on plugin {plugin.metadata.name}: {e}"
                    )

    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins."""
        status = {
            "total_plugins": len(self.plugins),
            "loaded_plugins": [],
            "available_plugins": [],
        }

        # Get loaded plugins
        for name, plugin in self.plugins.items():
            status["loaded_plugins"].append(
                {
                    "name": name,
                    "version": plugin.metadata.version,
                    "description": plugin.metadata.description,
                    "author": plugin.metadata.author,
                    "enabled": plugin.metadata.enabled,
                    "loaded_at": plugin.metadata.loaded_at.isoformat()
                    if plugin.metadata.loaded_at
                    else None,
                    "tools_count": len(plugin.get_tools()),
                    "hooks_count": len(plugin.get_hooks()),
                    "extensions_count": len(plugin.get_extensions()),
                }
            )

        # Get available plugins
        discovered_plugins = self.discover_plugins()
        for metadata in discovered_plugins:
            if metadata.name not in self.plugins:
                status["available_plugins"].append(metadata.to_dict())

        return status


class ExtensibleMCPServer:
    """Extensible MCP server with plugin system."""

    def __init__(self, enable_brain_features: bool = True, enable_plugins: bool = True):
        self.logger = logging.getLogger(__name__)
        self.enable_brain_features = enable_brain_features
        self.enable_plugins = enable_plugins

        # Initialize brain enhancement integration
        if enable_brain_features:
            from .brain_enhancement_integration import BrainEnhancementIntegration

            self.brain_integration = BrainEnhancementIntegration(
                enable_all_features=True
            )
        else:
            self.brain_integration = None

        # Initialize plugin manager
        if enable_plugins:
            self.plugin_manager = PluginManager(self)
        else:
            self.plugin_manager = None

        # Server state
        self.is_running = False
        self.start_time = None

        self.logger.info(
            f"Extensible MCP Server initialized (Brain: {enable_brain_features}, Plugins: {enable_plugins})"
        )

    async def start(self):
        """Start the extensible MCP server."""
        self.is_running = True
        self.start_time = datetime.now()

        # Initialize brain features
        if self.brain_integration:
            self.logger.info("Initializing brain enhancement features...")

        # Load plugins
        if self.plugin_manager:
            self.logger.info("Loading plugins...")
            await self._load_default_plugins()

        # Call server start hooks
        if self.plugin_manager:
            await self.plugin_manager.call_plugin_hooks("on_server_start")

        self.logger.info("Extensible MCP Server started successfully")

    async def stop(self):
        """Stop the extensible MCP server."""
        self.is_running = False

        # Call server stop hooks
        if self.plugin_manager:
            await self.plugin_manager.call_plugin_hooks("on_server_stop")

        # Shutdown plugins
        if self.plugin_manager:
            for plugin_name in list(self.plugin_manager.plugins.keys()):
                await self.plugin_manager.unload_plugin(plugin_name)

        self.logger.info("Extensible MCP Server stopped")

    async def _load_default_plugins(self):
        """Load default plugins."""
        try:
            # Load conversation recording plugin
            from plugins.conversation_recording_plugin import (
                ConversationRecordingPlugin,
            )

            await self.plugin_manager.load_plugin(ConversationRecordingPlugin)
            self.logger.info("Loaded conversation recording plugin")
        except Exception as e:
            self.logger.error(f"Failed to load default plugins: {e}")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools including brain and plugin tools."""
        tools = []

        # Add brain enhancement tools
        if self.brain_integration:
            tools.extend(self.brain_integration.get_brain_enhancement_tools())

        # Add plugin tools
        if self.plugin_manager:
            tools.extend(self.plugin_manager.get_plugin_tools())

        return tools

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with extensible capabilities."""
        try:
            # Auto-record user interaction before tool execution
            if self.plugin_manager:
                # Find conversation recording plugin
                conversation_plugin = None
                for plugin in self.plugin_manager.plugins.values():
                    if hasattr(plugin, "record_user_message"):
                        conversation_plugin = plugin
                        break

                if conversation_plugin:
                    # Record user intent based on tool calls
                    if tool_name == "push_memory":
                        content = arguments.get("content", "")
                        if content:
                            conversation_plugin.record_user_message(
                                f"User added memory: {content}"
                            )
                    elif tool_name == "fetch_memory":
                        conversation_plugin.record_user_message(
                            "User requested memory retrieval"
                        )
                    elif tool_name == "get_context_summary":
                        conversation_plugin.record_user_message(
                            "User requested context summary"
                        )
                    elif tool_name == "get_agent_stats":
                        conversation_plugin.record_user_message(
                            "User requested agent statistics"
                        )
                    elif tool_name == "craft_ai_prompt":
                        conversation_plugin.record_user_message(
                            "User requested AI prompt crafting"
                        )
                    elif tool_name == "search_memories_with_brain":
                        query = arguments.get("query", "")
                        conversation_plugin.record_user_message(
                            f"User searched memories: {query}"
                        )
                    elif tool_name == "get_identity_summary":
                        conversation_plugin.record_user_message(
                            "User requested identity summary"
                        )
                    else:
                        # Record generic tool call as user interaction
                        conversation_plugin.record_user_message(
                            f"User called tool: {tool_name}"
                        )

            # Try brain enhancement tools first
            if self.brain_integration:
                try:
                    result = await self.brain_integration.execute_brain_tool(
                        tool_name, arguments
                    )
                    if "error" not in result:
                        # Call plugin hooks
                        if self.plugin_manager:
                            await self.plugin_manager.call_plugin_hooks(
                                "on_tool_executed", tool_name, arguments, result
                            )

                        # Auto-record AI response
                        if self.plugin_manager and conversation_plugin:
                            content = result.get("content", [{}])[0].get("text", "")
                            if content:
                                conversation_plugin.record_ai_response(
                                    f"AI provided response: {content}"
                                )

                        return result
                except Exception as e:
                    self.logger.debug(
                        f"Tool {tool_name} not found in brain integration: {e}"
                    )

            # Try plugin tools
            if self.plugin_manager:
                result = await self.plugin_manager.execute_plugin_tool(
                    tool_name, arguments
                )
                if "error" not in result:
                    # Call plugin hooks
                    await self.plugin_manager.call_plugin_hooks(
                        "on_tool_executed", tool_name, arguments, result
                    )

                    # Auto-record AI response
                    if conversation_plugin:
                        content = result.get("content", [{}])[0].get("text", "")
                        if content:
                            conversation_plugin.record_ai_response(
                                f"AI provided response: {content}"
                            )

                    return result

            return {"error": f"Tool {tool_name} not found"}

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    async def load_plugin(self, plugin_class: Type[MCPPlugin]) -> bool:
        """Load a plugin."""
        if not self.plugin_manager:
            return False

        return await self.plugin_manager.load_plugin(plugin_class)

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if not self.plugin_manager:
            return False

        return await self.plugin_manager.unload_plugin(plugin_name)

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if not self.plugin_manager:
            return False

        return await self.plugin_manager.reload_plugin(plugin_name)

    def get_plugin_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        if not self.plugin_manager:
            return {"error": "Plugin system is disabled"}

        return self.plugin_manager.get_plugin_status()

    def get_server_status(self) -> Dict[str, Any]:
        """Get comprehensive server status."""
        status = {
            "server_type": "Extensible MCP Server",
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "brain_features_enabled": self.enable_brain_features,
            "plugins_enabled": self.enable_plugins,
            "total_tools": len(self.get_tools()),
        }

        # Add brain integration status
        if self.brain_integration:
            status[
                "brain_integration"
            ] = self.brain_integration.get_brain_enhancement_status()

        # Add plugin status
        if self.plugin_manager:
            status["plugins"] = self.get_plugin_status()

        return status

    async def update_plugin(
        self, plugin_name: str, update_data: Dict[str, Any]
    ) -> bool:
        """Update a plugin with new data."""
        if not self.plugin_manager:
            return False

        try:
            # Reload the plugin to get updates
            success = await self.reload_plugin(plugin_name)
            if success:
                self.logger.info(f"Successfully updated plugin: {plugin_name}")
            return success
        except Exception as e:
            self.logger.error(f"Error updating plugin {plugin_name}: {e}")
            return False

    def get_extensions(self) -> Dict[str, Any]:
        """Get all extensions from plugins."""
        extensions = {}

        if self.plugin_manager:
            extensions.update(self.plugin_manager.get_plugin_extensions())

        return extensions


async def main():
    """Main entry point for the extensible MCP server."""
    import asyncio
    import json
    import logging
    import sys

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and start the server
    server = ExtensibleMCPServer(enable_brain_features=True, enable_plugins=True)

    try:
        await server.start()

        # Set up MCP protocol handling
        async def handle_mcp_request():
            while True:
                try:
                    # Read request from stdin
                    line = await asyncio.get_event_loop().run_in_executor(
                        None, sys.stdin.readline
                    )
                    if not line:
                        break

                    request = json.loads(line.strip())
                    method = request.get("method")
                    params = request.get("params", {})
                    request_id = request.get("id")

                    if method == "initialize":
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {"tools": {}},
                                "serverInfo": {
                                    "name": "brain-enhanced-mcp",
                                    "version": "1.0.0",
                                },
                            },
                        }

                    elif method == "tools/list":
                        tools = server.get_tools()
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {"tools": tools},
                        }

                    elif method == "tools/call":
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})

                        result = await server.execute_tool(tool_name, arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": result,
                        }

                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}",
                            },
                        }

                    # Send response to stdout
                    print(json.dumps(response), flush=True)

                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id if "request_id" in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}",
                        },
                    }
                    print(json.dumps(error_response), flush=True)

        await handle_mcp_request()

    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())

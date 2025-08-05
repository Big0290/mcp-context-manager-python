#!/usr/bin/env python3
"""
Example Plugin for Extensible MCP Server
Demonstrates how to create plugins that extend server functionality.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.extensible_mcp_server import MCPPlugin, PluginMetadata


class ExamplePlugin(MCPPlugin):
    """Example plugin that adds basic utility tools."""

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="example_plugin",
            version="1.0.0",
            description="Example plugin demonstrating extensible MCP server capabilities",
            author="MCP Team",
            dependencies=[],
            tags=["example", "utility", "demo"],
            priority=0,
        )

    async def initialize(self) -> bool:
        """Initialize the plugin."""
        try:
            self.logger.info("Initializing Example Plugin...")

            # Create plugin data directory
            self.data_dir = Path.cwd() / "data" / "plugins" / "example_plugin"
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Initialize plugin state
            self.state_file = self.data_dir / "state.json"
            self.plugin_state = self._load_state()

            self.logger.info("Example Plugin initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Example Plugin: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        try:
            self.logger.info("Shutting down Example Plugin...")

            # Save plugin state
            self._save_state()

            self.logger.info("Example Plugin shut down successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to shutdown Example Plugin: {e}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools provided by this plugin."""
        return [
            {
                "name": "example_hello",
                "description": "Say hello with plugin functionality",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name to greet"},
                        "language": {
                            "type": "string",
                            "description": "Language for greeting (en, es, fr)",
                            "default": "en",
                        },
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "example_calculator",
                "description": "Simple calculator with plugin functionality",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Mathematical operation (add, subtract, multiply, divide)",
                            "enum": ["add", "subtract", "multiply", "divide"],
                        },
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["operation", "a", "b"],
                },
            },
            {
                "name": "example_file_operations",
                "description": "File operations with plugin functionality",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "File operation (list, read, write)",
                            "enum": ["list", "read", "write"],
                        },
                        "path": {"type": "string", "description": "File path"},
                        "content": {
                            "type": "string",
                            "description": "Content to write (for write operation)",
                        },
                    },
                    "required": ["operation", "path"],
                },
            },
            {
                "name": "example_plugin_status",
                "description": "Get plugin status and statistics",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool provided by this plugin."""
        try:
            if tool_name == "example_hello":
                return await self._hello_tool(arguments)
            elif tool_name == "example_calculator":
                return await self._calculator_tool(arguments)
            elif tool_name == "example_file_operations":
                return await self._file_operations_tool(arguments)
            elif tool_name == "example_plugin_status":
                return await self._plugin_status_tool(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    async def _hello_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Hello tool implementation."""
        name = arguments.get("name", "World")
        language = arguments.get("language", "en")

        greetings = {
            "en": f"Hello, {name}!",
            "es": f"¡Hola, {name}!",
            "fr": f"Bonjour, {name}!",
        }

        greeting = greetings.get(language, greetings["en"])

        # Update plugin state
        self.plugin_state["greetings_count"] = (
            self.plugin_state.get("greetings_count", 0) + 1
        )
        self.plugin_state["last_greeting"] = {
            "name": name,
            "language": language,
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "greeting": greeting,
            "language": language,
            "greetings_count": self.plugin_state["greetings_count"],
        }

    async def _calculator_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Calculator tool implementation."""
        operation = arguments.get("operation")
        a = arguments.get("a")
        b = arguments.get("b")

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"error": "Division by zero"}
            result = a / b
        else:
            return {"error": f"Unknown operation: {operation}"}

        # Update plugin state
        self.plugin_state["calculations_count"] = (
            self.plugin_state.get("calculations_count", 0) + 1
        )
        self.plugin_state["last_calculation"] = {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
            "calculations_count": self.plugin_state["calculations_count"],
        }

    async def _file_operations_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """File operations tool implementation."""
        operation = arguments.get("operation")
        path = arguments.get("path")

        try:
            file_path = Path(path)

            if operation == "list":
                if file_path.is_dir():
                    files = [f.name for f in file_path.iterdir()]
                    return {"files": files, "directory": str(file_path)}
                else:
                    return {"error": f"Path is not a directory: {path}"}

            elif operation == "read":
                if file_path.exists():
                    content = file_path.read_text()
                    return {"content": content, "file": str(file_path)}
                else:
                    return {"error": f"File not found: {path}"}

            elif operation == "write":
                content = arguments.get("content", "")
                file_path.write_text(content)
                return {
                    "message": f"File written successfully: {path}",
                    "file": str(file_path),
                }

            else:
                return {"error": f"Unknown operation: {operation}"}

        except Exception as e:
            return {"error": f"File operation failed: {str(e)}"}

    async def _plugin_status_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Plugin status tool implementation."""
        return {
            "plugin_name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "loaded_at": self.metadata.loaded_at.isoformat()
            if self.metadata.loaded_at
            else None,
            "state": self.plugin_state,
            "tools_count": len(self.get_tools()),
            "hooks_count": len(self.get_hooks()),
            "extensions_count": len(self.get_extensions()),
        }

    def get_hooks(self) -> Dict[str, callable]:
        """Get hooks provided by this plugin."""
        return {
            "on_server_start": self._on_server_start,
            "on_server_stop": self._on_server_stop,
            "on_tool_executed": self._on_tool_executed,
        }

    def get_extensions(self) -> Dict[str, Any]:
        """Get extensions provided by this plugin."""
        return {
            "example_plugin_data_dir": str(self.data_dir),
            "example_plugin_state": self.plugin_state,
            "example_plugin_metadata": self.metadata.to_dict(),
        }

    async def _on_server_start(self):
        """Called when the server starts."""
        self.logger.info("Example Plugin: Server started")
        self.plugin_state["server_start_time"] = datetime.now().isoformat()

    async def _on_server_stop(self):
        """Called when the server stops."""
        self.logger.info("Example Plugin: Server stopping")

    async def _on_tool_executed(
        self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]
    ):
        """Called after a tool is executed."""
        self.logger.info(f"Example Plugin: Tool {tool_name} executed")

        # Track tool executions
        if "tool_executions" not in self.plugin_state:
            self.plugin_state["tool_executions"] = []

        self.plugin_state["tool_executions"].append(
            {
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Keep only last 10 executions
        if len(self.plugin_state["tool_executions"]) > 10:
            self.plugin_state["tool_executions"] = self.plugin_state["tool_executions"][
                -10:
            ]

    def _load_state(self) -> Dict[str, Any]:
        """Load plugin state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading plugin state: {e}")

        return {}

    def _save_state(self):
        """Save plugin state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.plugin_state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin state: {e}")


class AdvancedPlugin(MCPPlugin):
    """Advanced plugin with more sophisticated functionality."""

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="advanced_plugin",
            version="1.0.0",
            description="Advanced plugin with sophisticated features",
            author="MCP Team",
            dependencies=["example_plugin"],
            tags=["advanced", "sophisticated", "demo"],
            priority=1,
        )

    async def initialize(self) -> bool:
        """Initialize the plugin."""
        try:
            self.logger.info("Initializing Advanced Plugin...")

            # Check if example plugin is loaded
            if "example_plugin" not in self.server.plugin_manager.plugins:
                self.logger.error(
                    "Advanced Plugin requires example_plugin to be loaded"
                )
                return False

            self.logger.info("Advanced Plugin initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Advanced Plugin: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        try:
            self.logger.info("Shutting down Advanced Plugin...")
            self.logger.info("Advanced Plugin shut down successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to shutdown Advanced Plugin: {e}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools provided by this plugin."""
        return [
            {
                "name": "advanced_analysis",
                "description": "Advanced analysis with plugin functionality",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to analyze"},
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis (sentiment, complexity, pattern)",
                            "enum": ["sentiment", "complexity", "pattern"],
                        },
                    },
                    "required": ["data", "analysis_type"],
                },
            },
            {
                "name": "advanced_plugin_status",
                "description": "Get advanced plugin status",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool provided by this plugin."""
        try:
            if tool_name == "advanced_analysis":
                return await self._advanced_analysis_tool(arguments)
            elif tool_name == "advanced_plugin_status":
                return await self._advanced_plugin_status_tool(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    async def _advanced_analysis_tool(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Advanced analysis tool implementation."""
        data = arguments.get("data", "")
        analysis_type = arguments.get("analysis_type")

        if analysis_type == "sentiment":
            # Simple sentiment analysis
            positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]

            words = data.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)

            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            return {
                "analysis_type": "sentiment",
                "sentiment": sentiment,
                "positive_score": positive_count,
                "negative_score": negative_count,
                "confidence": min(
                    1.0, (positive_count + negative_count) / len(words) if words else 0
                ),
            }

        elif analysis_type == "complexity":
            # Simple complexity analysis
            words = data.split()
            sentences = data.split(".")
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / len(words) if words else 0

            complexity_score = (
                avg_sentence_length * 0.4 + vocabulary_diversity * 0.6
            ) * 10

            return {
                "analysis_type": "complexity",
                "complexity_score": min(10.0, complexity_score),
                "avg_sentence_length": avg_sentence_length,
                "vocabulary_diversity": vocabulary_diversity,
                "word_count": len(words),
                "sentence_count": len(sentences),
            }

        elif analysis_type == "pattern":
            # Simple pattern analysis
            patterns = {
                "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "url": r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
                "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                "date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            }

            import re

            found_patterns = {}
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, data)
                found_patterns[pattern_name] = len(matches)

            return {
                "analysis_type": "pattern",
                "found_patterns": found_patterns,
                "total_patterns": sum(found_patterns.values()),
            }

        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}

    async def _advanced_plugin_status_tool(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Advanced plugin status tool implementation."""
        return {
            "plugin_name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "dependencies": self.metadata.dependencies,
            "loaded_at": self.metadata.loaded_at.isoformat()
            if self.metadata.loaded_at
            else None,
            "tools_count": len(self.get_tools()),
            "hooks_count": len(self.get_hooks()),
            "extensions_count": len(self.get_extensions()),
            "dependency_status": {
                "example_plugin": "example_plugin" in self.server.plugin_manager.plugins
            },
        }

    def get_hooks(self) -> Dict[str, callable]:
        """Get hooks provided by this plugin."""
        return {
            "on_server_start": self._on_server_start,
            "on_server_stop": self._on_server_stop,
        }

    def get_extensions(self) -> Dict[str, Any]:
        """Get extensions provided by this plugin."""
        return {
            "advanced_analysis_capabilities": ["sentiment", "complexity", "pattern"],
            "advanced_plugin_metadata": self.metadata.to_dict(),
        }

    async def _on_server_start(self):
        """Called when the server starts."""
        self.logger.info("Advanced Plugin: Server started")

    async def _on_server_stop(self):
        """Called when the server stops."""
        self.logger.info("Advanced Plugin: Server stopping")

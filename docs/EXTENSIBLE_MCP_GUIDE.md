# Extensible MCP Server Guide

## Overview

The Extensible MCP Server is a powerful, plugin-based Model Context Protocol (MCP) server that combines brain-like enhancement features with a dynamic plugin system. It allows for real-time extensions and updates without breaking existing functionality.

## Key Features

### 🧠 Brain Enhancement Integration

- **Identity Memory**: Maintains agent identity and emotional state
- **Session Memory**: Per-session personal data management
- **Experience Logger**: Tracks learning experiences and patterns
- **Memory Query Engine**: Advanced memory search and retrieval
- **Emotional Learning**: Emotional intelligence and adaptation
- **Cognitive Loop**: Continuous learning and improvement

### 🔌 Plugin System

- **Dynamic Loading**: Load plugins at runtime without restart
- **Dependency Management**: Handle plugin dependencies automatically
- **Lifecycle Management**: Proper initialization and shutdown
- **Hook System**: Event-driven plugin interactions
- **Tool Extensions**: Add new tools dynamically
- **Plugin Registry**: Persistent plugin state management

### 🛠️ Extensibility

- **Hot Reloading**: Update plugins without server restart
- **Tool Integration**: Seamless tool execution across plugins
- **Event Hooks**: Plugin interaction with server events
- **State Management**: Persistent plugin state
- **Error Handling**: Graceful error recovery

## Architecture

```
ExtensibleMCPServer
├── Brain Enhancement Integration
│   ├── Identity Memory
│   ├── Session Memory
│   ├── Experience Logger
│   ├── Memory Query Engine
│   ├── Emotional Learning
│   └── Cognitive Loop
├── Plugin Manager
│   ├── Plugin Registry
│   ├── Dependency Resolver
│   ├── Lifecycle Manager
│   └── Hook Dispatcher
└── Tool Execution Engine
    ├── Brain Tools
    ├── Plugin Tools
    └── Integration Layer
```

## Quick Start

### 1. Basic Server Setup

```python
from src.extensible_mcp_server import ExtensibleMCPServer

# Create server with all features enabled
server = ExtensibleMCPServer(
    enable_brain_features=True,
    enable_plugins=True
)

# Start the server
await server.start()

# Get server status
status = server.get_server_status()
print(f"Server running: {status['is_running']}")
print(f"Total tools: {status['total_tools']}")

# Stop the server
await server.stop()
```

### 2. Creating a Plugin

```python
from src.extensible_mcp_server import MCPPlugin, PluginMetadata

class MyPlugin(MCPPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
            dependencies=[],
            tags=["custom", "example"],
            priority=0
        )

    async def initialize(self) -> bool:
        self.logger.info("Initializing My Plugin...")
        return True

    async def shutdown(self) -> bool:
        self.logger.info("Shutting down My Plugin...")
        return True

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "my_tool",
                "description": "My custom tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "my_tool":
            input_text = arguments.get("input", "")
            return {"result": f"Processed: {input_text}"}
        return {"error": f"Unknown tool: {tool_name}"}
```

### 3. Loading and Using Plugins

```python
# Load a plugin
success = await server.load_plugin(MyPlugin)
print(f"Plugin loaded: {success}")

# Execute plugin tool
result = await server.execute_tool("my_tool", {"input": "Hello World"})
print(f"Tool result: {result}")

# Get plugin status
plugin_status = server.get_plugin_status()
print(f"Loaded plugins: {len(plugin_status['loaded_plugins'])}")

# Unload plugin
success = await server.unload_plugin("my_plugin")
print(f"Plugin unloaded: {success}")
```

## Plugin System Details

### Plugin Metadata

The `PluginMetadata` class defines plugin properties:

```python
@dataclass
class PluginMetadata:
    name: str                    # Unique plugin name
    version: str                 # Plugin version
    description: str             # Plugin description
    author: str                  # Plugin author
    dependencies: List[str]      # Required plugins
    tags: List[str]             # Plugin tags
    priority: int               # Load priority (higher = first)
    enabled: bool               # Plugin enabled state
    loaded_at: Optional[datetime]  # When plugin was loaded
    last_updated: Optional[datetime]  # Last update time
```

### Plugin Lifecycle

1. **Discovery**: Server discovers available plugins
2. **Loading**: Plugin is instantiated and initialized
3. **Registration**: Plugin is registered with the server
4. **Execution**: Plugin tools are available for use
5. **Unloading**: Plugin is shut down and removed

### Plugin Hooks

Plugins can implement hooks for server events:

```python
def get_hooks(self) -> Dict[str, callable]:
    return {
        "on_server_start": self._on_server_start,
        "on_server_stop": self._on_server_stop,
        "on_tool_executed": self._on_tool_executed,
        "on_memory_updated": self._on_memory_updated
    }

async def _on_server_start(self):
    """Called when server starts"""
    pass

async def _on_server_stop(self):
    """Called when server stops"""
    pass

async def _on_tool_executed(self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]):
    """Called after tool execution"""
    pass
```

### Plugin Dependencies

Plugins can depend on other plugins:

```python
def get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="dependent_plugin",
        version="1.0.0",
        description="Plugin that depends on another",
        author="Your Name",
        dependencies=["base_plugin"],  # Requires base_plugin
        tags=["dependent"],
        priority=1
    )
```

## Brain Enhancement Features

### Available Brain Tools

The server provides brain enhancement tools:

- `get_brain_status`: Get comprehensive brain status
- `process_task_with_brain`: Process tasks with brain system
- `get_identity_summary`: Get agent identity and emotional state
- `search_memories_with_brain`: Search memories with brain enhancement
- `get_emotional_learning_summary`: Get emotional learning status
- `get_cognitive_summary`: Get cognitive loop status
- `add_emotional_tag`: Add emotional tags to memories
- `get_joyful_memories`: Get memories with joyful tags
- `update_emotional_state`: Update agent emotional state

### Brain Integration Example

```python
# Get brain status
brain_status = await server.execute_tool("get_brain_status", {})
print(f"Brain enabled: {brain_status['enabled']}")

# Process task with brain
task_result = await server.execute_tool("process_task_with_brain", {
    "task_description": "Analyze user preferences",
    "task_type": "analysis",
    "priority": 0.8
})

# Get emotional state
identity = await server.execute_tool("get_identity_summary", {})
print(f"Emotional state: {identity['emotional_summary']}")
```

## Plugin Development Best Practices

### 1. Error Handling

```python
async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if tool_name == "my_tool":
            # Tool implementation
            return {"result": "success"}
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        self.logger.error(f"Tool execution error: {e}")
        return {"error": str(e)}
```

### 2. State Management

```python
async def initialize(self) -> bool:
    try:
        # Create plugin data directory
        self.data_dir = Path.cwd() / "data" / "plugins" / self.metadata.name
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load plugin state
        self.state_file = self.data_dir / "state.json"
        self.plugin_state = self._load_state()

        return True
    except Exception as e:
        self.logger.error(f"Initialization failed: {e}")
        return False

def _load_state(self) -> Dict[str, Any]:
    if self.state_file.exists():
        with open(self.state_file, 'r') as f:
            return json.load(f)
    return {}

def _save_state(self):
    with open(self.state_file, 'w') as f:
        json.dump(self.plugin_state, f, indent=2)
```

### 3. Tool Schema Design

```python
def get_tools(self) -> List[Dict[str, Any]]:
    return [
        {
            "name": "well_designed_tool",
            "description": "Clear description of what the tool does",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "required_param": {
                        "type": "string",
                        "description": "Required parameter description"
                    },
                    "optional_param": {
                        "type": "integer",
                        "description": "Optional parameter description",
                        "default": 0
                    }
                },
                "required": ["required_param"]
            }
        }
    ]
```

## Server Configuration

### Environment Variables

```bash
# Enable/disable features
ENABLE_BRAIN_FEATURES=true
ENABLE_PLUGINS=true

# Plugin directories
PLUGIN_DIRS=plugins,src/plugins,~/.mcp/plugins

# Brain enhancement settings
BRAIN_ENHANCEMENT_LEVEL=full
EMOTIONAL_LEARNING_ENABLED=true
COGNITIVE_LOOP_ENABLED=true
```

### Configuration File

Create `config.py` for server configuration:

```python
# Server configuration
SERVER_CONFIG = {
    "enable_brain_features": True,
    "enable_plugins": True,
    "plugin_directories": [
        "plugins",
        "src/plugins",
        "~/.mcp/plugins"
    ],
    "brain_enhancement": {
        "enable_identity_memory": True,
        "enable_session_memory": True,
        "enable_experience_logger": True,
        "enable_memory_query_engine": True,
        "enable_emotional_learning": True,
        "enable_cognitive_loop": True
    }
}
```

## Advanced Usage

### Plugin Discovery

```python
# Discover available plugins
if server.plugin_manager:
    discovered_plugins = server.plugin_manager.discover_plugins()
    for plugin in discovered_plugins:
        print(f"Found plugin: {plugin.name} v{plugin.version}")
```

### Plugin Reloading

```python
# Reload a plugin (useful for development)
success = await server.reload_plugin("my_plugin")
print(f"Plugin reloaded: {success}")
```

### Plugin Updates

```python
# Update plugin with new data
success = await server.update_plugin("my_plugin", {
    "new_feature": "dynamic_update",
    "timestamp": "2024-01-01T00:00:00"
})
```

### Extension System

```python
def get_extensions(self) -> Dict[str, Any]:
    return {
        "custom_extension": {
            "type": "data_processor",
            "version": "1.0.0",
            "capabilities": ["transform", "validate"]
        }
    }
```

## Troubleshooting

### Common Issues

1. **Plugin Loading Failures**

   - Check plugin dependencies
   - Verify plugin metadata
   - Check for import errors

2. **Tool Execution Errors**

   - Validate tool schemas
   - Check argument types
   - Review error handling

3. **Brain Integration Issues**
   - Verify brain features are enabled
   - Check memory database
   - Review emotional state configuration

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Create server with debug info
server = ExtensibleMCPServer(enable_brain_features=True, enable_plugins=True)
```

## Examples

See the `examples/` directory for complete working examples:

- `extensible_mcp_demo.py`: Complete demo of server capabilities
- `plugin_development_example.py`: Plugin development guide
- `brain_integration_example.py`: Brain enhancement usage

## Contributing

When contributing to the extensible MCP server:

1. Follow the plugin development guidelines
2. Add comprehensive tests for new features
3. Update documentation for new capabilities
4. Ensure backward compatibility
5. Follow the existing code style

## License

This project is licensed under the MIT License. See LICENSE file for details.

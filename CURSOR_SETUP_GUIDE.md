# 🚀 Cursor Setup Guide for Brain-Enhanced MCP Server

## Overview

This guide will help you set up the brain-enhanced extensible MCP server with Cursor to get access to advanced AI capabilities including emotional learning, memory management, and plugin extensibility.

## 📋 Prerequisites

- ✅ Python 3.8+ installed
- ✅ Cursor IDE installed
- ✅ Virtual environment set up
- ✅ All dependencies installed

## 🔧 Setup Steps

### 1. Environment Setup

First, ensure your environment is properly set up:

```bash
# Activate virtual environment
source venv/bin/activate

# Verify dependencies are installed
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|pydantic)"
```

### 2. MCP Configuration

The `mcp.json` file is already configured for Cursor. It includes:

```json
{
  "mcpServers": {
    "brain-enhanced-mcp": {
      "command": "python",
      "args": ["mcp_server_protocol.py"],
      "env": {
        "ENABLE_BRAIN_FEATURES": "true",
        "ENABLE_PLUGINS": "true",
        "BRAIN_ENHANCEMENT_LEVEL": "full",
        "EMOTIONAL_LEARNING_ENABLED": "true",
        "COGNITIVE_LOOP_ENABLED": "true",
        "PLUGIN_DIRS": "plugins,src/plugins,~/.mcp/plugins",
        "LOG_LEVEL": "INFO"
      },
      "cwd": ".",
      "description": "Brain-Enhanced Extensible MCP Server with Plugin System"
    }
  }
}
```

### 3. Cursor Configuration

#### Option A: Use the provided mcp.json

1. Copy the `mcp.json` file to your Cursor configuration directory:

   ```bash
   cp mcp.json ~/.cursor/mcp.json
   ```

2. Restart Cursor to load the new MCP configuration.

#### Option B: Add to existing Cursor MCP configuration

If you already have an MCP configuration in Cursor:

1. Open Cursor
2. Go to Settings → Extensions → MCP
3. Add the brain-enhanced-mcp server configuration

### 4. Test the Setup

Run the test script to verify everything is working:

```bash
# Test the MCP protocol server
python test_mcp_protocol.py
```

You should see output like:

```
🧪 Testing MCP Protocol Server
========================================

1️⃣ Testing Initialize...
✅ Initialize successful
   Server: Brain-Enhanced Extensible MCP Server
   Version: 1.0.0

2️⃣ Testing Tools List...
✅ Tools list successful - 9 tools available
   1. get_brain_status: Get comprehensive status of brain enhancement modules
   2. process_task_with_brain: Process a task using the complete brain-like system
   3. get_identity_summary: Get current identity and emotional state summary
   4. search_memories_with_brain: Search memories using brain-enhanced query engine
   5. get_emotional_learning_summary: Get emotional learning summary
   ... and 4 more tools

3️⃣ Testing Tool Call...
✅ Tool call successful for 'get_brain_status'
   Result: {"enabled": true, "modules": {...}}

🎉 All MCP protocol tests passed!

✅ MCP Protocol Server is working correctly!
   Cursor should now be able to connect and use the tools.
```

## 🧠 Available Brain Tools

Once connected, you'll have access to these brain enhancement tools:

### Core Brain Tools

1. **`get_brain_status`** - Get comprehensive brain status
2. **`process_task_with_brain`** - Process tasks with brain system
3. **`get_identity_summary`** - Get agent identity and emotional state
4. **`search_memories_with_brain`** - Brain-enhanced memory search
5. **`get_emotional_learning_summary`** - Emotional learning status
6. **`get_cognitive_summary`** - Cognitive loop status
7. **`add_emotional_tag`** - Add emotional tags to memories
8. **`get_joyful_memories`** - Get memories with joyful tags
9. **`update_emotional_state`** - Update agent emotional state

### Plugin Tools

1. **`demo_counter`** - Simple counter tool
2. **`demo_echo`** - Echo tool with plugin prefix
3. **`example_hello`** - Hello tool with language support
4. **`example_calculator`** - Simple calculator
5. **`example_file_operations`** - File operations
6. **`example_plugin_status`** - Plugin status tool
7. **`advanced_analysis`** - Advanced text analysis
8. **`advanced_plugin_status`** - Advanced plugin status

### Context Management Tools

1. **`mcp_mcp-brain-context-manager_push_memory`** - Push memory to brain
2. **`mcp_mcp-brain-context-manager_fetch_memory`** - Fetch memories
3. **`mcp_mcp-brain-context-manager_get_context_summary`** - Get context summary
4. **`mcp_mcp-brain-context-manager_auto_inject_context`** - Auto-inject context
5. **`mcp_mcp-brain-context-manager_craft_ai_prompt`** - Craft AI prompts
6. **`mcp_mcp-brain-context-manager_search_similar_experiences`** - Search experiences
7. **`mcp_mcp-brain-context-manager_get_knowledge_graph`** - Get knowledge graph
8. **`mcp_mcp-brain-context-manager_get_memory_insights`** - Get memory insights

## 🎯 Usage Examples

### 1. Get Brain Status

Ask Cursor: "What's the current status of the brain enhancement system?"

### 2. Process a Task with Brain

Ask Cursor: "Process this task with the brain system: Analyze the code structure and suggest improvements"

### 3. Get Emotional State

Ask Cursor: "What's my current emotional state and learning progress?"

### 4. Search Memories

Ask Cursor: "Search my memories for similar coding patterns or solutions"

### 5. Update Emotional State

Ask Cursor: "Update my emotional state to reflect excitement about this new project"

### 6. Use Plugin Tools

Ask Cursor: "Use the demo counter tool to track my progress"

## 🔌 Plugin Development

### Creating Custom Plugins

1. Create a new plugin file in the `plugins/` directory:

```python
from src.extensible_mcp_server import MCPPlugin, PluginMetadata

class MyCustomPlugin(MCPPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_custom_plugin",
            version="1.0.0",
            description="My custom plugin for Cursor",
            author="Your Name",
            dependencies=[],
            tags=["custom", "cursor"],
            priority=0
        )

    async def initialize(self) -> bool:
        self.logger.info("My Custom Plugin: Initializing...")
        return True

    async def shutdown(self) -> bool:
        self.logger.info("My Custom Plugin: Shutting down...")
        return True

    def get_tools(self) -> list[Dict[str, Any]]:
        return [
            {
                "name": "my_custom_tool",
                "description": "My custom tool for Cursor",
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
        if tool_name == "my_custom_tool":
            input_text = arguments.get("input", "")
            return {"result": f"Processed: {input_text}"}
        return {"error": f"Unknown tool: {tool_name}"}
```

2. The plugin will be automatically discovered and loaded by the MCP server.

## 🛠️ Troubleshooting

### Common Issues

1. **Server won't start**

   ```bash
   # Check if virtual environment is activated
   source venv/bin/activate

   # Check if dependencies are installed
   pip install -r requirements.txt
   ```

2. **Cursor can't connect to MCP server**

   - Verify the `mcp.json` file is in the correct location
   - Check that the server is running: `python mcp_server_entry.py`
   - Restart Cursor after configuration changes

3. **Tools not available**

   - Check server logs for errors
   - Verify plugins are loaded: `python examples/extensible_mcp_demo.py`

4. **Performance issues**
   - Check memory usage: `ps aux | grep python`
   - Restart the MCP server if needed

### Debug Mode

Enable debug logging by modifying the environment variables in `mcp.json`:

```json
"env": {
  "LOG_LEVEL": "DEBUG",
  "ENABLE_BRAIN_FEATURES": "true",
  "ENABLE_PLUGINS": "true"
}
```

## 📊 Monitoring

### Server Status

Check server status with:

```bash
python examples/extensible_mcp_demo.py
```

### Logs

Server logs are written to:

- Console output (when running directly)
- `logs/mcp_server.log` (if file logging is enabled)

### Performance

Monitor performance with:

```bash
# Check memory usage
ps aux | grep mcp_server_entry

# Check CPU usage
top -p $(pgrep -f mcp_server_entry)
```

## 🚀 Advanced Configuration

### Customizing Brain Enhancement

Modify the brain enhancement settings in `mcp.json`:

```json
"env": {
  "BRAIN_ENHANCEMENT_LEVEL": "full",
  "EMOTIONAL_LEARNING_ENABLED": "true",
  "COGNITIVE_LOOP_ENABLED": "true",
  "EMOTIONAL_DECAY_RATE": "0.1",
  "EMOTIONAL_LEARNING_RATE": "0.05"
}
```

### Plugin Configuration

Configure plugin directories:

```json
"env": {
  "PLUGIN_DIRS": "plugins,src/plugins,~/.mcp/plugins,/path/to/custom/plugins"
}
```

### Performance Tuning

Optimize performance with:

```json
"env": {
  "MAX_MEMORY_USAGE": "512MB",
  "CACHE_SIZE": "1000",
  "CACHE_EXPIRATION": "3600"
}
```

## 🎉 Success!

Once configured, you'll have access to:

- ✅ **Brain-enhanced AI** with emotional learning
- ✅ **Memory management** with persistent storage
- ✅ **Plugin system** for extensibility
- ✅ **Context injection** for better conversations
- ✅ **Cognitive loop** for continuous improvement
- ✅ **Emotional intelligence** for adaptive responses

Your Cursor experience will now be enhanced with brain-like capabilities! 🧠✨

## 📚 Additional Resources

- [Extensible MCP Guide](docs/EXTENSIBLE_MCP_GUIDE.md)
- [Integration Summary](INTEGRATION_SUMMARY.md)
- [Brain Enhancement Guide](docs/BRAIN_ENHANCEMENT_GUIDE.md)
- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT_GUIDE.md)

---

**🎯 Ready to use your brain-enhanced MCP server with Cursor!**

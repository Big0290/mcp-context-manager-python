# MCP Memory Server - Refactored for stdin/stdout

This project has been refactored to use stdin/stdout communication according to the [Model Context Protocol (MCP) specifications](https://modelcontextprotocol.io/docs/getting-started/intro).

## Overview

The MCP Memory Server provides long-term memory and context synchronization between AI agents. It has been refactored to follow the official MCP protocol using stdin/stdout for communication, making it compatible with any MCP-compliant client.

## Key Changes

### 1. Removed MCP SDK Dependency
- Removed `mcp[cli]>=1.2.0` dependency
- Implemented direct stdin/stdout communication
- Uses JSON-RPC 2.0 protocol over stdin/stdout

### 2. Protocol Compliance
- Follows MCP specification for message format
- Implements proper JSON-RPC 2.0 messages
- Handles initialization, tool listing, and tool calls
- Supports error handling and cancellation

### 3. Simplified Architecture
- Direct communication without transport layer abstraction
- Cleaner message handling
- Better error reporting

## Files

### Core Server
- `mcp_server.py` - Main MCP server implementation using stdin/stdout
- `cursor_mcp_server.py` - Original Cursor-specific implementation (kept for reference)

### Testing and Examples
- `test_mcp_client.py` - Test client to verify server functionality
- `example_usage.py` - Example showing how to use the server

## Usage

### Running the Server

```bash
python mcp_server.py
```

The server will start and listen for JSON-RPC messages on stdin, responding on stdout.

### Testing the Server

```bash
python test_mcp_client.py
```

This will run a comprehensive test suite to verify all functionality.

### Example Usage

```bash
python example_usage.py
```

This demonstrates how to communicate with the server programmatically.

## MCP Protocol Messages

### Initialization
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "client-name",
      "version": "0.1.0"
    }
  }
}
```

### List Tools
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### Call Tool
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "push_memory",
    "arguments": {
      "content": "Memory content",
      "memory_type": "fact",
      "priority": "medium",
      "tags": ["tag1", "tag2"],
      "project_id": "project-1"
    }
  }
}
```

## Available Tools

### 1. push_memory
Store a memory entry for context persistence.

**Parameters:**
- `content` (required): The memory content to store
- `memory_type`: Type of memory entry (fact, preference, task, thread)
- `priority`: Priority level (low, medium, high, critical)
- `tags`: Tags for categorization
- `project_id`: Project identifier

### 2. fetch_memory
Retrieve memories based on search criteria.

**Parameters:**
- `query`: Search query for semantic search
- `tags`: Filter by tags
- `memory_type`: Filter by memory type
- `limit`: Maximum number of results
- `project_id`: Project identifier

### 3. get_agent_stats
Get statistics for an agent.

**Parameters:**
- `agent_id` (required): Agent identifier
- `project_id`: Project identifier

### 4. register_agent
Register a new agent.

**Parameters:**
- `name` (required): Agent name
- `agent_type`: Type of agent (chatbot, cli, web, mobile, other)
- `project_id`: Project identifier

## Error Handling

The server implements proper error handling according to JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error description"
  }
}
```

## Benefits of Refactoring

1. **Standard Compliance**: Follows official MCP specifications
2. **Simplified Dependencies**: No external MCP SDK required
3. **Better Control**: Direct control over protocol implementation
4. **Easier Debugging**: Clear message flow through stdin/stdout
5. **Portability**: Works with any MCP-compliant client
6. **Flexibility**: Easy to extend and modify

## Integration with MCP Clients

The refactored server can be integrated with any MCP-compliant client by:

1. Starting the server process
2. Sending JSON-RPC messages to stdin
3. Reading responses from stdout
4. Handling errors appropriately

This makes it compatible with the broader MCP ecosystem while maintaining the specific memory management functionality.

## Development

To extend the server:

1. Add new tools to the `get_tools()` method
2. Implement tool execution in `execute_tool()`
3. Add corresponding private methods for tool logic
4. Update tests and examples

The refactored implementation provides a clean, standards-compliant foundation for MCP memory management. 
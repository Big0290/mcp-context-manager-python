#!/bin/bash
# Brain-Enhanced MCP Server Startup Script

echo "🧠 Starting Brain-Enhanced MCP Context Manager..."
echo "📍 Project: /Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/mcp-context-manager-python"
echo "🐍 Python: /Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/mcp-context-manager-python/.venv/bin/python"
echo ""

export PYTHONPATH="/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/mcp-context-manager-python"
export MCP_PROJECT_ID="cursor-workspace"
export MCP_LOG_LEVEL="INFO"
export MCP_PERFORMANCE_MONITORING="true"

cd "/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/mcp-context-manager-python"

# Test mode - shows server info and exits
if [ "$1" = "--test" ]; then
    echo "🧪 Running in test mode..."
    /Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/mcp-context-manager-python/.venv/bin/python test_brain_mcp.py
    exit $?
fi

# Normal mode - starts MCP server
echo "🚀 Starting MCP server..."
echo "   Use Ctrl+C to stop"
echo "   Logs will be written to logs/mcp_server.log"
echo ""

/Users/jonathanmorand/Documents/ProjectsFolder/MCP_FOLDER/mcp-context-manager-python/.venv/bin/python src/brain_enhanced_mcp_server.py

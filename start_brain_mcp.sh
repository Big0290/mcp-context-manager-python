#!/bin/bash

# Brain-Enhanced Extensible MCP Server Startup Script
# This script starts the extensible MCP server with brain enhancement features

echo "🧠 Starting Brain-Enhanced Extensible MCP Server..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Set environment variables
export ENABLE_BRAIN_FEATURES=true
export ENABLE_PLUGINS=true
export BRAIN_ENHANCEMENT_LEVEL=full
export EMOTIONAL_LEARNING_ENABLED=true
export COGNITIVE_LOOP_ENABLED=true
export PLUGIN_DIRS="plugins,src/plugins,~/.mcp/plugins"
export LOG_LEVEL=INFO

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/plugins
mkdir -p data/experience_logs
mkdir -p logs
mkdir -p ~/.mcp/plugins

# Start the extensible MCP server
echo "🚀 Starting Extensible MCP Server..."
echo "Features enabled:"
echo "  ✅ Brain Enhancement"
echo "  ✅ Plugin System"
echo "  ✅ Emotional Learning"
echo "  ✅ Cognitive Loop"
echo "  ✅ Memory Management"
echo "  ✅ Context Injection"
echo ""

# Run the extensible MCP server
python -m src.extensible_mcp_server

echo ""
echo "🛑 Brain-Enhanced Extensible MCP Server stopped."

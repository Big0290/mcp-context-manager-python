# 🚀 Quick Cursor Setup for Brain MCP

## Automated Setup (Recommended)

Run the automated setup script:

```bash
cd /path/to/mcp-context-manager-python
python scripts/setup_cursor_brain_mcp.py
```

This script will:
- ✅ Check all prerequisites
- ✅ Test the brain server
- ✅ Create MCP configuration
- ✅ Install Cursor configuration
- ✅ Create startup scripts

## Manual Setup (If Needed)

### 1. Copy this MCP configuration:

**For Cursor MCP Settings** (copy to your Cursor MCP settings):

```json
{
  "mcpServers": {
    "mcp-brain-context-manager": {
      "command": "/path/to/mcp-context-manager-python/.venv/bin/python",
      "args": [
        "/path/to/mcp-context-manager-python/src/brain_enhanced_mcp_server.py"
      ],
      "cwd": "/path/to/mcp-context-manager-python",
      "env": {
        "MCP_PROJECT_ID": "cursor-workspace",
        "MCP_LOG_LEVEL": "INFO",
        "MCP_PERFORMANCE_MONITORING": "true",
        "PYTHONPATH": "/path/to/mcp-context-manager-python"
      }
    }
  }
}
```

### 2. Where to add this configuration:

**Option A: Cursor Settings (Preferred)**
1. Open Cursor
2. Go to Settings (Cmd+,)
3. Search for "MCP"
4. Paste the configuration above

**Option B: Manual File Placement**
Add to one of these locations:
- `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.cursor-mcp/settings.json`
- `~/.cursor/mcp_settings.json`
- `~/.config/cursor/mcp_settings.json`

## 🧪 Testing

### Quick Test
```bash
cd /path/to/mcp-context-manager-python

# Test the server
python test_brain_mcp.py

# Or use the startup script
./start_brain_mcp.sh --test
```

### Manual Server Test
```bash
cd /path/to/mcp-context-manager-python
.venv/bin/python src/brain_enhanced_mcp_server.py
```

## 🎯 Using Brain Tools in Cursor

Once connected, try these in Cursor chat:

### Basic Memory Operations
- "Store this as a memory: React hooks are powerful for state management"
- "Fetch memories about React performance"
- "Get context summary for this project"

### Brain-Enhanced Operations
- **Similar Experiences**: "Search for similar experiences with database optimization"
- **Knowledge Graph**: "Show me the knowledge graph for React hooks"
- **Memory Insights**: "Get memory insights with recommendations"
- **Knowledge Path**: "Trace knowledge path from useState to useCallback"
- **Promote Knowledge**: "Promote important memories about API design patterns"

## 🔧 Troubleshooting

### Connection Issues
1. **Restart Cursor completely** (quit and reopen)
2. Check that Python virtual environment is activated
3. Verify paths in the configuration are correct
4. Look for errors in: `logs/mcp_server.log`

### Server Issues
```bash
# Check Python and dependencies
.venv/bin/python --version
.venv/bin/python -c "import sqlite3; print('SQLite OK')"

# Test server manually
.venv/bin/python src/brain_enhanced_mcp_server.py
```

### Permission Issues
```bash
# Fix script permissions
chmod +x start_brain_mcp.sh
chmod +x scripts/setup_cursor_brain_mcp.py
```

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Cursor shows MCP connection indicator
- ✅ You can use brain tools in chat
- ✅ Memory operations work and get enhanced with brain features
- ✅ Knowledge graphs and similar experience search work

## 📞 Getting Help

If you encounter issues:
1. Check `logs/mcp_server.log` for detailed error information
2. Run `python test_brain_mcp.py` to diagnose problems
3. Try the automated setup script again
4. Verify all file paths in the configuration are correct

---

**Ready to use your brain-enhanced MCP Context Manager!** 🧠✨

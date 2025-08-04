---
name: 🐛 Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## 🐛 **Bug Description**

A clear and concise description of what the bug is.

## 🔄 **Steps to Reproduce**

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ **Expected Behavior**

A clear and concise description of what you expected to happen.

## ❌ **Actual Behavior**

A clear and concise description of what actually happened.

## 📸 **Screenshots**

If applicable, add screenshots to help explain your problem.

## 🖥️ **Environment Information**

### **System Details**

- **OS**: [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
- **Python Version**: [e.g., 3.10.12]
- **MCP Client**: [e.g., Cursor, VS Code, Custom]
- **MCP Client Version**: [e.g., 0.1.0]

### **Project Configuration**

```json
{
  "project_id": "your-project-name",
  "mcp_server": "brain_enhanced_mcp_server.py",
  "log_level": "INFO"
}
```

### **Dependencies**

```bash
# Output of: pip freeze | grep -E "(mcp|brain|memory)"
```

## 📋 **Additional Context**

- **Error Messages**: Copy the full error message if any
- **Log Files**: Relevant log entries (anonymized if needed)
- **Related Issues**: Links to related issues or discussions
- **Recent Changes**: Any recent changes that might have caused this

## 🔍 **Debugging Information**

### **Server Logs**

```bash
# Run with debug logging and paste relevant output
export MCP_LOG_LEVEL=DEBUG
python src/brain_enhanced_mcp_server.py
```

### **Memory System Status**

```python
# Run this diagnostic script
python -c "
from src.brain_memory_system import BrainMemorySystem
import asyncio

async def diagnose():
    brain = BrainMemorySystem(':memory:')
    print('Memory system initialized successfully')
    # Add your specific test case here

asyncio.run(diagnose())
"
```

### **MCP Protocol Test**

```bash
# Test basic MCP communication
python test_brain_mcp.py
```

## 🎯 **Severity**

- [ ] **Critical** - System completely unusable
- [ ] **High** - Major functionality broken
- [ ] **Medium** - Minor functionality affected
- [ ] **Low** - Cosmetic or minor issue

## 🏷️ **Labels**

- [ ] `brain-system` - Related to brain memory features
- [ ] `mcp-protocol` - MCP compliance or protocol issues
- [ ] `performance` - Performance-related issue
- [ ] `documentation` - Documentation-related issue
- [ ] `good first issue` - Suitable for new contributors

## 📝 **Additional Notes**

Add any other context about the problem here.

---

**Thank you for helping improve the MCP Context Manager!** 🧠✨

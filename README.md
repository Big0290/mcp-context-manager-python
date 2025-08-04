# 🧠 MCP Context Manager with Brain-Enhanced Memory

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A sophisticated **Model Context Protocol (MCP) server** that provides human brain-like memory management for AI agents. Features multilayered memory architecture, neural-style interconnections, and intelligent knowledge growth.

## 🎯 **What This Solves**

- **Context Loss**: AI agents forgetting previous conversations and learned patterns
- **Knowledge Fragmentation**: Scattered information across different sessions
- **Pattern Recognition**: Missing connections between similar problems and solutions
- **Learning Efficiency**: Inability to build upon past experiences and insights
- **Knowledge Management**: No systematic way to organize and retrieve relevant context

## ⭐ **Key Features**

### 🧠 **Brain-Like Memory System**

- **Multilayered Architecture**: Short-term, long-term, episodic, procedural, and semantic memory
- **Neural Connections**: Automatic relationship discovery between memories
- **Memory Promotion**: Frequently used knowledge becomes more accessible
- **Analogical Reasoning**: Find similar solutions from different contexts

### 🔗 **Intelligent Connections**

- **6 Connection Types**: Semantic, temporal, causal, contextual, functional, analogical
- **Auto-Discovery**: Finds relationships between memories automatically
- **Knowledge Graphs**: Visualize how concepts interconnect
- **Learning Paths**: Trace knowledge flow between concepts

### 📊 **Advanced Features**

- **MCP Protocol Compliant**: Full compatibility with Cursor and other MCP clients
- **Performance Monitoring**: Built-in analytics and optimization
- **Project Isolation**: Separate memory contexts by project
- **Semantic Search**: Vector-based similarity matching
- **Context Injection**: Automatic relevant memory retrieval

## 🚀 **Quick Start**

### **1. Installation**

```bash
git clone https://github.com/yourusername/mcp-context-manager-python.git
cd mcp-context-manager-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Automated Setup (Recommended)**

```bash
# Run the automated setup script
python scripts/setup_cursor_brain_mcp.py
```

This will:

- ✅ Test all components
- ✅ Create MCP configuration
- ✅ Install Cursor integration
- ✅ Set up startup scripts

### **3. Manual Setup**

#### Start the Brain-Enhanced Server

```bash
# With brain features (recommended)
python src/brain_enhanced_mcp_server.py

# Or simple server (basic features only)
python src/simple_mcp_server.py
```

#### Test the Server

```bash
python test_brain_mcp.py
```

#### Configure Your MCP Client

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "mcp-brain-context-manager": {
      "command": "python",
      "args": ["src/brain_enhanced_mcp_server.py"],
      "cwd": "/path/to/mcp-context-manager-python",
      "env": {
        "MCP_PROJECT_ID": "your-project",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🛠️ **Usage Examples**

### **Basic Memory Operations**

```python
# Store memories (automatically enhanced with brain features)
await mcp_server.push_memory({
    "content": "React useEffect handles side effects in functional components",
    "memory_type": "fact",
    "tags": ["react", "hooks", "javascript"],
    "project_id": "my-web-app"
})

# Retrieve memories with semantic search
result = await mcp_server.fetch_memory({
    "query": "React performance optimization",
    "project_id": "my-web-app"
})
```

### **Brain-Enhanced Operations**

#### **🔍 Similar Experience Search**

```python
# Find analogous past experiences
result = await mcp_server.search_similar_experiences({
    "query": "API rate limiting errors",
    "focus_areas": ["Error Handling", "APIs", "Performance"],
    "include_analogies": True
})
```

#### **🕸️ Knowledge Graph**

```python
# Build knowledge maps
graph = await mcp_server.get_knowledge_graph({
    "center_topic": "Database Optimization",
    "max_depth": 3
})
```

#### **🛤️ Knowledge Path Tracing**

```python
# Discover learning paths
path = await mcp_server.trace_knowledge_path({
    "from_concept": "Basic SQL",
    "to_concept": "Advanced Query Optimization"
})
```

#### **📊 Memory Insights**

```python
# Analyze knowledge patterns
insights = await mcp_server.get_memory_insights({
    "project_id": "my-project",
    "include_recommendations": True
})
```

## 🏗️ **Architecture**

```
mcp-context-manager-python/
├── 🎯 Core Components
│   ├── src/
│   │   ├── brain_enhanced_mcp_server.py    # Main brain-enhanced server
│   │   ├── brain_memory_system.py          # Multilayered memory system
│   │   ├── brain_integration.py            # Integration layer
│   │   ├── simple_mcp_server.py            # Basic MCP server
│   │   └── performance_monitor.py          # Performance tracking
│   └── mcp_memory_server/                  # Full-featured server components
│       ├── core/                           # Core services
│       ├── models/                         # Data models
│       └── api/                            # API endpoints
│
├── 🧪 Testing & Examples
│   ├── tests/                              # Comprehensive test suite
│   ├── examples/                           # Usage examples
│   └── test_brain_mcp.py                   # Quick server test
│
├── 🔧 Configuration & Scripts
│   ├── scripts/                            # Setup and utility scripts
│   ├── config.py                           # Main configuration
│   └── cursor_mcp_config.json              # MCP client configuration
│
├── 📚 Documentation
│   └── guides/                             # Detailed guides and documentation
│       ├── BRAIN_MEMORY_SYSTEM_GUIDE.md    # Comprehensive user guide
│       ├── BRAIN_ARCHITECTURE_SUMMARY.md   # Technical architecture
│       └── QUICK_CURSOR_SETUP.md           # Quick setup guide
│
└── 💾 Data & Logs
    ├── data/                               # Database files
    └── logs/                               # Application logs
```

## 🧠 **Brain Memory System**

### **Memory Layers**

- **Short-term**: Working memory for temporary information (≤50 items)
- **Long-term**: Persistent knowledge and facts
- **Episodic**: Specific events and experiences ("I learned X while doing Y")
- **Procedural**: Skills and learned patterns ("How to debug React performance")
- **Semantic**: Conceptual knowledge and relationships

### **Connection Types**

- **Semantic**: Related concepts (`useState` ↔ `useReducer`)
- **Temporal**: Time-based sequences (`Step 1` → `Step 2`)
- **Causal**: Cause-effect relationships (`Performance issue` → `Solution`)
- **Contextual**: Same project/context
- **Functional**: Similar tools/techniques
- **Analogical**: Similar patterns across domains

### **Example Memory Insights**

```
📊 Memory System Analysis

Memory Layer Distribution:
• Long-term: 45 memories
• Procedural: 23 memories
• Episodic: 15 memories
• Short-term: 8 memories

Connection Patterns:
• Semantic: 45 connections (related concepts)
• Contextual: 32 connections (same projects)
• Functional: 15 connections (similar techniques)

💡 Recommendations:
• Strong React knowledge - consider creating procedural guides
• Review dormant Python memories for valuable insights
• Consider consolidating short-term memories
```

## 🎨 **Available Tools**

### **Core MCP Tools**

| Tool                  | Description                          | Key Parameters                                 |
| --------------------- | ------------------------------------ | ---------------------------------------------- |
| `push_memory`         | Store memory with brain enhancement  | `content`, `memory_type`, `tags`, `project_id` |
| `fetch_memory`        | Retrieve with brain-enhanced search  | `query`, `tags`, `memory_type`, `limit`        |
| `get_context_summary` | Generate context with brain insights | `project_id`, `max_memories`, `focus_areas`    |

### **Brain-Enhanced Tools**

| Tool                         | Description                         | Key Parameters                                   |
| ---------------------------- | ----------------------------------- | ------------------------------------------------ |
| `search_similar_experiences` | Find analogous past experiences     | `query`, `focus_areas`, `include_analogies`      |
| `get_knowledge_graph`        | Build interconnected knowledge maps | `center_topic`, `max_depth`, `connection_types`  |
| `get_memory_insights`        | Analyze knowledge patterns          | `project_id`, `include_recommendations`          |
| `trace_knowledge_path`       | Discover learning paths             | `from_concept`, `to_concept`, `max_hops`         |
| `promote_memory_knowledge`   | Boost important memories            | `memory_ids`, `target_layer`, `emotional_weight` |

## ⚡ **Performance & Scalability**

- **Semantic Search**: Vector embeddings with similarity thresholds
- **Connection Pruning**: Automatic cleanup of weak relationships
- **Memory Limits**: Configurable limits per memory layer
- **Batch Operations**: Efficient bulk processing
- **Performance Monitoring**: Built-in analytics and recommendations

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Core settings
MCP_PROJECT_ID=your-project-name
MCP_LOG_LEVEL=INFO
MCP_PERFORMANCE_MONITORING=true

# Brain system settings
BRAIN_SHORT_TERM_LIMIT=50
BRAIN_SIMILARITY_THRESHOLD=0.7
BRAIN_CONNECTION_STRENGTH_THRESHOLD=0.3
```

### **Advanced Configuration**

```python
# Customize brain system parameters
brain_system.config.update({
    "short_term_limit": 30,
    "similarity_threshold": 0.8,
    "memory_promotion_threshold": 5,
    "consolidation_threshold": 10
})

# Add custom hierarchies
brain_system.topic_hierarchy["YourDomain"] = [
    "Subdomain1", "Subdomain2", "Subdomain3"
]
```

## 🧪 **Testing**

### **Run All Tests**

```bash
python -m pytest tests/
```

### **Quick Server Test**

```bash
python test_brain_mcp.py
```

### **Comprehensive Test**

```bash
python tests/comprehensive_test.py
```

### **Performance Test**

```bash
python tests/test_performance_monitoring.py
```

## 🤝 **Contributing**

We welcome contributions from developers of all skill levels! This project thrives on community collaboration.

### **🚀 Quick Start for Contributors**

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/mcp-context-manager-python.git
cd mcp-context-manager-python

# Set up development environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run development setup
python scripts/setup_dev.py

# Test your setup
python test_brain_mcp.py
```

### **📋 Contribution Process**

1. **🍴 Fork the repository**
2. **🌿 Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **✍️ Make your changes** with tests and documentation
4. **✅ Run the test suite**: `python -m pytest tests/`
5. **📝 Update documentation** as needed
6. **🚀 Submit a Pull Request** with a clear description

### **🎯 Areas for Contribution**

#### **🧠 Brain System Enhancements**

- **New Memory Connection Types**: Emotional, spatial, hierarchical connections
- **Advanced Memory Algorithms**: Consolidation, decay, forgetting mechanisms
- **Knowledge Transfer**: Cross-project memory sharing
- **Memory Classification**: Improved categorization and tagging

#### **🎨 Visualization & UI**

- **Web-based Knowledge Graph**: Interactive memory exploration
- **Real-time Analytics Dashboard**: Live memory system insights
- **Memory Timeline**: Historical view of knowledge growth
- **Learning Path Visualizations**: Visual knowledge flow diagrams

#### **🔌 Integrations & Extensions**

- **VS Code Extension**: Native IDE integration
- **JetBrains Plugins**: IntelliJ, PyCharm support
- **Obsidian/Roam Connectors**: Knowledge base integration
- **Slack/Discord Bots**: Team collaboration features

#### **📊 Analytics & Insights**

- **Advanced Pattern Analysis**: Memory usage analytics
- **Learning Recommendations**: Personalized knowledge suggestions
- **Knowledge Gap Detection**: Identify missing knowledge areas
- **Performance Optimization**: Memory system tuning

#### **🌍 Accessibility & Internationalization**

- **Multi-language Support**: Localized memory content
- **Accessibility Improvements**: Screen reader support, keyboard navigation
- **Documentation Translations**: Help translate guides and docs
- **Cultural Context**: Domain-specific memory hierarchies

#### **⚡ Performance & Scalability**

- **Database Optimization**: Query performance improvements
- **Distributed Systems**: Multi-node memory sharing
- **Caching Strategies**: Memory access optimization
- **Cloud Deployment**: AWS, GCP, Azure support

### **🏷️ Issue Labels**

We use these labels to help contributors find suitable tasks:

- `good first issue` - Perfect for new contributors
- `help wanted` - Looking for contributors
- `brain-system` - Brain memory system features
- `visualization` - UI and visualization work
- `integration` - External system integrations
- `performance` - Performance optimization
- `documentation` - Documentation improvements
- `testing` - Test coverage and quality

### **📚 Resources for Contributors**

- **[Contributing Guide](CONTRIBUTING.md)** - Complete contribution guidelines
- **[Brain Memory System Guide](docs/guides/BRAIN_MEMORY_SYSTEM_GUIDE.md)** - Understanding the core system
- **[Quick Setup Guide](docs/guides/QUICK_CURSOR_SETUP.md)** - Development environment setup
- **[Architecture Summary](docs/guides/BRAIN_ARCHITECTURE_SUMMARY.md)** - Technical architecture overview

### **🎉 Recognition & Rewards**

- **First Contribution Badge**: Special recognition for first-time contributors
- **README Credits**: All contributors listed in acknowledgments
- **Release Notes**: Major contributions highlighted in releases
- **Maintainer Invitation**: Active contributors invited to be maintainers

### **🤝 Community Support**

- **GitHub Discussions**: Ask questions and share ideas
- **Code Reviews**: Get feedback on your contributions
- **Pair Programming**: Arrange coding sessions with maintainers
- **Mentorship**: Get guidance from experienced contributors

**Ready to contribute? Pick an issue, fork the repo, and let's build the future of AI memory together!** 🧠✨

## 📋 **Roadmap**

### **Near Term**

- [ ] Web-based knowledge graph visualization
- [ ] Export/import knowledge structures
- [ ] Multi-user collaboration features
- [ ] Enhanced embedding models

### **Medium Term**

- [ ] LLM integration for memory summarization
- [ ] Domain-specific memory hierarchies
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard

### **Long Term**

- [ ] Distributed memory systems
- [ ] Cross-project knowledge sharing
- [ ] AI-powered memory curation
- [ ] Enterprise deployment options

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Server Won't Start**

```bash
# Check Python version
python --version  # Should be 3.10+

# Test imports
python -c "from src.brain_enhanced_mcp_server import BrainEnhancedMCPServer"

# Check logs
tail -f logs/mcp_server.log
```

#### **MCP Connection Issues**

1. Restart your MCP client completely
2. Verify configuration paths are correct
3. Check that Python virtual environment is activated
4. Review client-specific MCP setup guides

#### **Performance Issues**

```bash
# Check performance metrics
python -c "
from src.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor('data/mcp_performance.db')
print(monitor.get_performance_report())
"
```

#### **Memory Search Not Working**

- Ensure embeddings are generated (check logs)
- Verify similarity thresholds in configuration
- Test with different query terms

### **Getting Help**

- 📖 Read the [comprehensive guide](docs/guides/BRAIN_MEMORY_SYSTEM_GUIDE.md)
- 🔧 Check the [setup guide](docs/guides/QUICK_CURSOR_SETUP.md)
- 🏗️ Review the [architecture summary](docs/guides/BRAIN_ARCHITECTURE_SUMMARY.md)
- 🔍 Check [existing issues](https://github.com/yourusername/mcp-context-manager-python/issues)
- 💬 Start a [discussion](https://github.com/yourusername/mcp-context-manager-python/discussions)
- 🐛 Report [new issues](https://github.com/yourusername/mcp-context-manager-python/issues/new)

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - For the excellent protocol specification
- **[Anthropic](https://anthropic.com/)** - For Claude and MCP development
- **[Cursor](https://cursor.sh/)** - For MCP integration and development tools
- **Community Contributors** - For feedback, testing, and improvements

## 📊 **Project Status**

- ✅ **Core Functionality**: Complete and stable
- ✅ **Brain Features**: Fully implemented and tested
- ✅ **MCP Compliance**: Full protocol support
- ✅ **Documentation**: Comprehensive guides available
- ✅ **Testing**: Extensive test coverage
- 🚀 **Production Ready**: Stable and performant

---

**Transform your AI agent from a simple chatbot into an intelligent partner with human-like memory and reasoning capabilities.** 🧠✨

_Built with ❤️ for the AI development community_

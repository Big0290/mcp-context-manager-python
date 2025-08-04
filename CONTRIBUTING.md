# 🤝 Contributing to MCP Context Manager

Thank you for your interest in contributing to the MCP Context Manager with Brain-Enhanced Memory! This project thrives on community contributions and we welcome developers of all skill levels.

## 🚀 **Quick Start for Contributors**

### **1. Development Setup**

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/mcp-context-manager-python.git
cd mcp-context-manager-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development setup
python scripts/setup_dev.py

# Test the installation
python test_brain_mcp.py
```

### **2. Run Tests**

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_brain_memory.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 🎯 **Areas for Contribution**

We're looking for contributions in these areas:

### **🧠 Core Brain System**
- New memory connection types (analogical, taxonomic, etc.)
- Enhanced memory classification algorithms
- Memory consolidation and summarization features
- Performance optimizations for large memory graphs

### **🎨 Visualization & UI**
- Web-based knowledge graph visualization
- Interactive memory exploration tools
- Real-time memory analytics dashboards
- Export formats for knowledge graphs

### **🔌 Integrations**
- Additional MCP client support (VS Code, IntelliJ, etc.)
- API integrations with external knowledge bases
- Import/export to popular formats (Obsidian, Roam, etc.)
- Cloud storage backends

### **📊 Analytics & Insights**
- Advanced memory pattern analysis
- Learning path recommendations
- Knowledge gap detection
- Usage analytics and reporting

### **🌍 Accessibility & Internationalization**
- Multi-language support
- Accessibility improvements
- Documentation translations
- Localized memory hierarchies

### **⚡ Performance & Scalability**
- Database optimization
- Distributed memory systems
- Caching strategies
- Memory cleanup algorithms

## 📋 **Contribution Process**

### **1. Planning Your Contribution**

1. **Check existing issues** - Look for open issues that match your interests
2. **Discuss large changes** - Open an issue for major features or architectural changes
3. **Start small** - Consider beginning with documentation, tests, or small bug fixes

### **2. Making Changes**

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow coding standards**
   - Use descriptive variable and function names
   - Add docstrings to new functions and classes
   - Follow PEP 8 style guidelines
   - Add type hints where appropriate

3. **Write tests**
   - Add unit tests for new functionality
   - Update integration tests as needed
   - Ensure all tests pass

4. **Update documentation**
   - Update docstrings and comments
   - Add examples for new features
   - Update README if needed

### **3. Code Quality Standards**

#### **Python Code Style**
```python
# Good: Clear, descriptive names with type hints
async def search_similar_memories(
    self,
    query: str,
    similarity_threshold: float = 0.7
) -> List[MemoryNode]:
    """
    Search for memories similar to the given query.

    Args:
        query: The search query string
        similarity_threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
        List of memory nodes matching the criteria
    """
    # Implementation here
    pass

# Bad: Unclear names, no type hints or documentation
def search(q, t=0.7):
    pass
```

#### **Documentation Standards**
- All public functions must have docstrings
- Include parameter descriptions and return types
- Add usage examples for complex functions
- Update README for new features

#### **Testing Standards**
```python
import pytest
from src.brain_memory_system import BrainMemorySystem

class TestBrainMemorySystem:
    """Test suite for brain memory system functionality."""

    @pytest.fixture
    def brain_system(self):
        """Create a test brain memory system."""
        return BrainMemorySystem(":memory:")  # Use in-memory DB for tests

    async def test_memory_creation(self, brain_system):
        """Test that memories are created correctly."""
        memory_data = {
            "content": "Test memory content",
            "memory_type": "fact",
            "tags": ["test"]
        }

        result = await brain_system.enhance_existing_memory("test_id", memory_data)

        assert result.content == "Test memory content"
        assert result.memory_type == "fact"
        assert "test" in result.tags
```

### **4. Submitting Your Contribution**

1. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what your changes do and why
   - Include screenshots for UI changes

3. **Respond to feedback**
   - Address review comments promptly
   - Be open to suggestions and changes
   - Ask questions if feedback is unclear

## 🧪 **Testing Guidelines**

### **Test Structure**
```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_brain_memory.py
│   ├── test_connections.py
│   └── test_classification.py
├── integration/            # Integration tests
│   ├── test_mcp_protocol.py
│   └── test_full_workflow.py
└── fixtures/               # Test data and fixtures
    ├── sample_memories.json
    └── test_configs.py
```

### **Running Tests**
```bash
# Run all tests
python -m pytest

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage report
python -m pytest --cov=src --cov-report=html

# Run performance tests (longer running)
python -m pytest tests/performance/ -m slow
```

### **Writing Good Tests**
- Test one thing at a time
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies
- Use fixtures for common test data

## 📝 **Documentation Guidelines**

### **Code Documentation**
- All public APIs must have docstrings
- Use Google or NumPy docstring format
- Include examples for complex functions
- Document performance characteristics for critical paths

### **User Documentation**
- Update README for new features
- Add usage examples
- Create guides for complex workflows
- Include troubleshooting information

### **Architecture Documentation**
- Document design decisions
- Include diagrams for complex systems
- Explain trade-offs and alternatives considered
- Update architecture docs for structural changes

## 🐛 **Bug Reports**

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Operating system
   - MCP client being used

2. **Steps to reproduce**
   - Minimal code example
   - Configuration used
   - Expected vs actual behavior

3. **Additional context**
   - Log files (anonymized)
   - Screenshots if relevant
   - Related issues or discussions

## 💡 **Feature Requests**

For feature requests:

1. **Describe the problem** you're trying to solve
2. **Explain your proposed solution** in detail
3. **Consider alternatives** and why your approach is best
4. **Discuss implementation** complexity and requirements

## 🎨 **Design Principles**

When contributing, please keep these principles in mind:

### **Brain-Like Architecture**
- Memory should feel natural and human-like
- Connections should emerge organically
- Knowledge should grow and evolve over time

### **Developer Experience**
- APIs should be intuitive and well-documented
- Error messages should be helpful and actionable
- Setup and configuration should be minimal

### **Performance**
- Memory operations should be fast and efficient
- Large memory graphs should remain responsive
- Resource usage should be predictable

### **Extensibility**
- New features should integrate cleanly
- Plugin architecture should be maintained
- Backward compatibility should be preserved

## 🏷️ **Issue Labels**

We use these labels to organize issues:

- `good first issue` - Great for new contributors
- `help wanted` - Looking for contributors
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation updates needed
- `performance` - Performance optimization
- `brain-system` - Related to brain memory features
- `mcp-protocol` - MCP compliance and protocol issues

## 🎉 **Recognition**

Contributors are recognized in several ways:

- **README Credits** - All contributors listed in acknowledgments
- **Release Notes** - Major contributions highlighted in releases
- **Contributor Badge** - Special recognition for ongoing contributors
- **Maintainer Invitation** - Active contributors invited to be maintainers

## 📞 **Getting Help**

If you need help with your contribution:

1. **Check the documentation** - README, guides, and code comments
2. **Search existing issues** - Someone may have had the same question
3. **Join discussions** - Use GitHub Discussions for questions
4. **Contact maintainers** - Open an issue tagged with `question`

## ⚖️ **Code of Conduct**

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 🙏 **Thank You**

Every contribution, no matter how small, helps make this project better. Whether you're fixing a typo, adding a feature, or helping others in discussions, your efforts are appreciated!

---

**Ready to contribute? Pick an issue, fork the repo, and let's build the future of AI memory together!** 🧠✨

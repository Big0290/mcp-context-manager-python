#!/usr/bin/env python3
"""
Developer setup script for MCP Memory Server
"""

import shutil
import subprocess
import sys
from pathlib import Path

from config import Config


def run_command(command: str, description: str) -> bool:
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def setup_directories():
    """Create necessary directories."""
    print("📁 Setting up directories...")

    directories = [
        Config.DATA_DIR,
        Config.LOGS_DIR,
        Path("examples"),
        Path("tests"),
        Path("docs"),
    ]

    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def setup_database():
    """Initialize database files."""
    print("🗄️ Setting up databases...")

    # Move existing database files to data directory
    db_files = [
        ("simple_mcp_memory.db", Config.SIMPLE_DB_PATH),
        ("mcp_memory.db", Config.FULL_DB_PATH),
        ("mcp_performance.db", Config.PERFORMANCE_DB_PATH),
    ]

    for old_path, new_path in db_files:
        old_file = Path(old_path)
        if old_file.exists():
            shutil.move(str(old_file), str(new_path))
            print(f"✅ Moved {old_path} to {new_path}")


def create_env_example():
    """Create environment example file."""
    env_example = """# MCP Memory Server Environment Configuration

# Project settings
MCP_PROJECT_ID=workspace
MCP_AGENT_ID=cursor-chat

# Logging
MCP_LOG_LEVEL=INFO

# Performance monitoring
MCP_PERFORMANCE_MONITORING=true

# Database settings
MCP_DB_TYPE=simple  # simple or full

# Context injection
MCP_AUTO_CONTEXT_INJECTION=true
MCP_SHOW_CONTEXT_SUMMARY=true
"""

    env_file = Path(".env.example")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_example)
        print("✅ Created .env.example file")


def test_server():
    """Test if the server can start."""
    print("🧪 Testing server startup...")

    try:
        # Test simple server
        result = subprocess.run(
            [sys.executable, "src/simple_mcp_server.py"],
            timeout=5,
            capture_output=True,
            text=True,
        )
        print("✅ Simple server test completed")
        return True
    except subprocess.TimeoutExpired:
        print("✅ Simple server started successfully (timeout expected)")
        return True
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False


def create_quick_start_guide():
    """Create a quick start guide for developers."""
    guide = """# Quick Start Guide

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Start the server:**
   ```bash
   python src/simple_mcp_server.py
   ```

3. **Test context injection:**
   ```bash
   python examples/context_injection_example.py
   ```

4. **Configure Cursor:**
   Copy `cursor_integration.json` to your Cursor MCP configuration.

## 📁 Project Structure

- `src/` - Server implementations
- `data/` - Database files
- `logs/` - Log files
- `examples/` - Usage examples
- `tests/` - Test files
- `docs/` - Documentation

## 🔧 Configuration

Edit `config.py` or set environment variables:
- `MCP_PROJECT_ID` - Default project ID
- `MCP_LOG_LEVEL` - Logging level
- `MCP_PERFORMANCE_MONITORING` - Enable/disable monitoring

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/
```

## 📊 Monitoring

Performance data is stored in `data/mcp_performance.db`
"""

    guide_file = Path("QUICK_START.md")
    with open(guide_file, "w") as f:
        f.write(guide)
    print("✅ Created QUICK_START.md")


def main():
    """Main setup function."""
    print("🚀 MCP Memory Server - Developer Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Setup directories
    setup_directories()

    # Setup database
    setup_database()

    # Create environment example
    create_env_example()

    # Create quick start guide
    create_quick_start_guide()

    # Test server
    if test_server():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env and configure")
        print("2. Run: python src/simple_mcp_server.py")
        print("3. Test with: python examples/context_injection_example.py")
        print("4. Configure Cursor with cursor_integration.json")
    else:
        print("\n⚠️ Setup completed with warnings. Check the output above.")


if __name__ == "__main__":
    main()

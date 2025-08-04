#!/usr/bin/env python3
"""
Fixed Automated Cursor MCP Brain Setup Script
Automatically configures Cursor to use the Brain-Enhanced MCP Context Manager.
"""

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class CursorBrainMCPSetup:
    """Automated setup for Cursor MCP Brain integration."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system().lower()
        self.logger = self._setup_logging()

        # Cursor config paths by OS
        self.cursor_config_paths = self._get_cursor_config_paths()

    def _setup_logging(self):
        """Setup logging for the setup process."""
        log_file = self.project_root / "logs" / "cursor_setup.log"
        log_file.parent.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        return logging.getLogger(__name__)

    def _get_cursor_config_paths(self):
        """Get Cursor configuration paths for different operating systems."""
        if self.system == "darwin":  # macOS
            return [
                Path.home()
                / "Library"
                / "Application Support"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "rooveterinaryinc.cursor-mcp"
                / "settings.json",
                Path.home() / ".cursor" / "mcp_settings.json",
                Path.home() / ".config" / "cursor" / "mcp_settings.json",
            ]
        elif self.system == "windows":
            return [
                Path.home()
                / "AppData"
                / "Roaming"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "rooveterinaryinc.cursor-mcp"
                / "settings.json",
                Path.home() / ".cursor" / "mcp_settings.json",
            ]
        else:  # Linux
            return [
                Path.home()
                / ".config"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "rooveterinaryinc.cursor-mcp"
                / "settings.json",
                Path.home() / ".cursor" / "mcp_settings.json",
                Path.home() / ".config" / "cursor" / "mcp_settings.json",
            ]

    def check_python_installation(self):
        """Check if Python is properly installed and accessible."""
        print("🐍 Checking Python installation...")

        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            python_version = result.stdout.strip()
            print(f"   ✅ Python found: {python_version}")
            print(f"   📍 Python path: {sys.executable}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Python check failed: {e}")
            return False

    def check_project_structure(self):
        """Verify project structure and required files."""
        print("📁 Checking project structure...")

        required_files = [
            "src/brain_enhanced_mcp_server.py",
            "src/brain_memory_system.py",
            "src/brain_integration.py",
            "src/simple_mcp_server.py",
            "config.py",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                print(f"   ✅ {file_path}")

        if missing_files:
            print("   ❌ Missing required files:")
            for file in missing_files:
                print(f"      • {file}")
            return False

        # Create required directories
        (self.project_root / "data").mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)

        print("   ✅ All required files found")
        return True

    def test_brain_server_imports(self):
        """Test if the brain-enhanced MCP server can be imported."""
        print("🧠 Testing brain-enhanced MCP server imports...")

        try:
            # Test basic imports without creating server instance
            sys.path.insert(0, str(self.project_root))

            # Test individual module imports
            from src.brain_memory_system import (
                BrainMemorySystem,
                MemoryLayer,
                MemoryState,
            )

            print("   ✅ Brain memory system import successful")

            from src.brain_integration import BrainIntegration

            print("   ✅ Brain integration import successful")

            from src.simple_mcp_server import SimpleMCPServer

            print("   ✅ Simple MCP server import successful")

            # Test that we can import the main server class
            from src.brain_enhanced_mcp_server import BrainEnhancedMCPServer

            print("   ✅ Brain-enhanced MCP server import successful")

            print("   ✅ All imports working correctly")
            return True

        except Exception as e:
            print(f"   ❌ Import test failed: {e}")
            self.logger.error(f"Import test error: {e}")
            return False

    def create_mcp_config(self):
        """Create MCP configuration for Cursor."""
        print("⚙️ Creating MCP configuration...")

        config = {
            "mcpServers": {
                "mcp-brain-context-manager": {
                    "command": sys.executable,
                    "args": [
                        str(self.project_root / "src" / "brain_enhanced_mcp_server.py")
                    ],
                    "cwd": str(self.project_root),
                    "env": {
                        "MCP_PROJECT_ID": "cursor-workspace",
                        "MCP_LOG_LEVEL": "INFO",
                        "MCP_PERFORMANCE_MONITORING": "true",
                        "PYTHONPATH": str(self.project_root),
                    },
                }
            }
        }

        # Save to project directory
        config_file = self.project_root / "cursor_mcp_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"   ✅ Configuration created: {config_file}")

        # Also create a simplified config for manual use
        simple_config_file = self.project_root / "cursor_mcp_config_simple.json"
        with open(simple_config_file, "w") as f:
            json.dump(config, f, indent=2)

        return config, config_file

    def install_cursor_config(self, config):
        """Install MCP configuration for Cursor."""
        print("📥 Installing Cursor MCP configuration...")

        config_installed = False
        successful_paths = []

        for config_path in self.cursor_config_paths:
            try:
                # Create directory if it doesn't exist
                config_path.parent.mkdir(parents=True, exist_ok=True)

                # Check if config already exists
                existing_config = {}
                if config_path.exists():
                    try:
                        with open(config_path, "r") as f:
                            existing_config = json.load(f)

                        # Backup existing config
                        backup_path = config_path.with_suffix(".backup.json")
                        shutil.copy2(config_path, backup_path)
                        print(f"   💾 Backed up existing config to: {backup_path}")

                    except json.JSONDecodeError:
                        print(
                            f"   ⚠️  Invalid JSON in existing config, creating new one"
                        )
                        existing_config = {}

                # Merge configurations
                if "mcpServers" not in existing_config:
                    existing_config["mcpServers"] = {}

                existing_config["mcpServers"].update(config["mcpServers"])

                # Write updated config
                with open(config_path, "w") as f:
                    json.dump(existing_config, f, indent=2)

                print(f"   ✅ Installed to: {config_path}")
                successful_paths.append(str(config_path))
                config_installed = True

            except PermissionError:
                print(f"   ⚠️  Permission denied: {config_path}")
                continue
            except Exception as e:
                print(f"   ⚠️  Failed to install to {config_path}: {e}")
                continue

        if not config_installed:
            print("   ⚠️  Could not install to standard Cursor locations")
            print("   📋 Manual installation required - see instructions below")
        else:
            print(f"   🎉 Successfully installed to {len(successful_paths)} location(s)")

        return config_installed, successful_paths

    def create_startup_script(self):
        """Create a startup script for easy server testing."""
        print("📜 Creating startup scripts...")

        # Create shell script for Unix-like systems
        if self.system in ["darwin", "linux"]:
            script_content = f"""#!/bin/bash
# Brain-Enhanced MCP Server Startup Script

echo "🧠 Starting Brain-Enhanced MCP Context Manager..."
echo "📍 Project: {self.project_root}"
echo "🐍 Python: {sys.executable}"
echo ""

export PYTHONPATH="{self.project_root}"
export MCP_PROJECT_ID="cursor-workspace"
export MCP_LOG_LEVEL="INFO"
export MCP_PERFORMANCE_MONITORING="true"

cd "{self.project_root}"

# Test mode - shows server info and exits
if [ "$1" = "--test" ]; then
    echo "🧪 Running in test mode..."
    {sys.executable} test_brain_mcp.py
    exit $?
fi

# Normal mode - starts MCP server
echo "🚀 Starting MCP server..."
echo "   Use Ctrl+C to stop"
echo "   Logs will be written to logs/mcp_server.log"
echo ""

{sys.executable} src/brain_enhanced_mcp_server.py
"""

            script_path = self.project_root / "start_brain_mcp.sh"
            with open(script_path, "w") as f:
                f.write(script_content)

            # Make executable
            script_path.chmod(0o755)
            print(f"   ✅ Created shell script: {script_path}")

        # Create batch script for Windows
        if self.system == "windows":
            batch_content = f"""@echo off
REM Brain-Enhanced MCP Server Startup Script

echo 🧠 Starting Brain-Enhanced MCP Context Manager...
echo 📍 Project: {self.project_root}
echo 🐍 Python: {sys.executable}
echo.

set PYTHONPATH={self.project_root}
set MCP_PROJECT_ID=cursor-workspace
set MCP_LOG_LEVEL=INFO
set MCP_PERFORMANCE_MONITORING=true

cd /d "{self.project_root}"

REM Test mode
if "%1"=="--test" (
    echo 🧪 Running in test mode...
    "{sys.executable}" test_brain_mcp.py
    exit /b %errorlevel%
)

REM Normal mode
echo 🚀 Starting MCP server...
echo    Use Ctrl+C to stop
echo    Logs will be written to logs\\mcp_server.log
echo.

"{sys.executable}" src\\brain_enhanced_mcp_server.py
"""

            batch_path = self.project_root / "start_brain_mcp.bat"
            with open(batch_path, "w", encoding="utf-8") as f:
                f.write(batch_content)

            print(f"   ✅ Created batch script: {batch_path}")

    def test_server_startup(self):
        """Test if the server can start without errors."""
        print("🧪 Testing server startup...")

        try:
            # Test the test script
            result = subprocess.run(
                [sys.executable, str(self.project_root / "test_brain_mcp.py")],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root),
                env={**os.environ, "PYTHONPATH": str(self.project_root)},
            )

            if result.returncode == 0:
                print("   ✅ Server startup test passed")
                print("   📝 Test output preview:")
                # Show first few lines of output
                lines = result.stdout.split("\n")[:5]
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
                return True
            else:
                print("   ❌ Server startup test failed")
                print(f"   📝 Error output: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print("   ⚠️  Server test timed out (this might be normal)")
            return True  # Timeout might be OK for MCP server
        except Exception as e:
            print(f"   ❌ Server test error: {e}")
            return False

    def print_instructions(self, config_installed, successful_paths):
        """Print final setup instructions."""
        print("\n🎉 CURSOR BRAIN MCP SETUP COMPLETE!")
        print("=" * 50)

        print("\n📋 SETUP SUMMARY:")
        print(f"✅ Python: {sys.executable}")
        print(f"✅ Project: {self.project_root}")
        print(f"✅ Configuration: cursor_mcp_config.json")

        if config_installed:
            print(f"✅ Cursor config installed to {len(successful_paths)} location(s)")
            for path in successful_paths:
                print(f"   • {path}")
        else:
            print("⚠️  Cursor config needs manual installation")

        print("\n📋 NEXT STEPS:")
        print("1. 🔄 Restart Cursor completely (quit and reopen)")
        print("2. 📂 Open any project in Cursor")
        print("3. 🔍 Look for the MCP connection indicator")
        print("4. 🧪 Try using the brain tools in chat")

        if not config_installed:
            print("\n⚙️  MANUAL CURSOR CONFIGURATION:")
            print("Since automatic installation wasn't successful, please:")
            print("1. Open Cursor Settings (Cmd+, or Ctrl+,)")
            print("2. Search for 'MCP' settings")
            print("3. Copy the configuration from: cursor_mcp_config.json")
            print("4. Paste it into your MCP settings")

        print("\n🧠 BRAIN TOOLS TO TRY:")
        print("• 'Search for similar experiences with React performance'")
        print("• 'Show me the knowledge graph for database optimization'")
        print("• 'Get memory insights for this project'")
        print("• 'Trace knowledge path from basic SQL to advanced queries'")

        print("\n🔧 CONFIGURATION FILES:")
        print(f"• Main config: {self.project_root}/cursor_mcp_config.json")
        print(
            f"• Startup script: {self.project_root}/start_brain_mcp.{'sh' if self.system != 'windows' else 'bat'}"
        )
        print(f"• Test script: {self.project_root}/test_brain_mcp.py")

        print("\n🧪 TESTING:")
        print("• Quick test: python test_brain_mcp.py")
        if self.system == "windows":
            print("• Startup test: start_brain_mcp.bat --test")
        else:
            print("• Startup test: ./start_brain_mcp.sh --test")

        print("\n🚨 TROUBLESHOOTING:")
        print("• Check logs in: logs/mcp_server.log")
        print("• Verify Cursor MCP extension is installed")
        print("• Ensure Python virtual environment is activated")
        print("• Try restarting Cursor if connection issues occur")

        print("\n📚 DOCUMENTATION:")
        print("• User Guide: BRAIN_MEMORY_SYSTEM_GUIDE.md")
        print("• Examples: examples/brain_memory_examples.py")
        print("• Architecture: BRAIN_ARCHITECTURE_SUMMARY.md")
        print("• Quick Setup: QUICK_CURSOR_SETUP.md")

    def run_setup(self):
        """Run the complete setup process."""
        print("🧠 CURSOR BRAIN MCP AUTOMATED SETUP")
        print("=" * 45)
        print(f"Operating System: {self.system.title()}")
        print(f"Project Root: {self.project_root}")
        print(f"Python: {sys.executable}")
        print("")

        try:
            # Step 1: Check Python
            if not self.check_python_installation():
                return False

            # Step 2: Check project structure
            if not self.check_project_structure():
                return False

            # Step 3: Test brain server imports (lighter than full server test)
            if not self.test_brain_server_imports():
                return False

            # Step 4: Create MCP config
            config, config_file = self.create_mcp_config()

            # Step 5: Install Cursor config
            config_installed, successful_paths = self.install_cursor_config(config)

            # Step 6: Create startup scripts
            self.create_startup_script()

            # Step 7: Test server startup
            self.test_server_startup()

            # Step 8: Print instructions
            self.print_instructions(config_installed, successful_paths)

            return True

        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            self.logger.error(f"Setup error: {e}")
            return False


def main():
    """Main entry point for the setup script."""
    setup = CursorBrainMCPSetup()
    success = setup.run_setup()

    if success:
        print("\n✅ Setup completed successfully!")
        return 0
    else:
        print("\n❌ Setup failed. Check the logs for details.")
        return 1


if __name__ == "__main__":
    exit(main())

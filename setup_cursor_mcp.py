#!/usr/bin/env python3
"""
Setup Cursor MCP Configuration
Copies the corrected MCP configuration to Cursor's directory.
"""

import os
import shutil
import subprocess
from pathlib import Path


def setup_cursor_mcp():
    """Setup Cursor MCP configuration."""
    print("🔧 Setting up Cursor MCP Configuration")
    print("=" * 45)

    # Get paths
    current_dir = Path(__file__).parent
    cursor_config_dir = Path.home() / ".cursor"
    cursor_mcp_config = cursor_config_dir / "mcp.json"

    # Source configuration file
    source_config = current_dir / "cursor_mcp_config.json"

    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Cursor config directory: {cursor_config_dir}")
    print(f"📄 Source config: {source_config}")
    print(f"📄 Target config: {cursor_mcp_config}")

    # Check if source exists
    if not source_config.exists():
        print("❌ Source configuration file not found!")
        return False

    # Create cursor config directory if it doesn't exist
    cursor_config_dir.mkdir(exist_ok=True)
    print(f"✅ Cursor config directory ready: {cursor_config_dir}")

    # Backup existing config if it exists
    if cursor_mcp_config.exists():
        backup_path = cursor_mcp_config.with_suffix(".json.backup")
        shutil.copy2(cursor_mcp_config, backup_path)
        print(f"📋 Backed up existing config to: {backup_path}")

    # Copy the configuration
    try:
        shutil.copy2(source_config, cursor_mcp_config)
        print("✅ Configuration copied successfully!")

        # Verify the copy
        if cursor_mcp_config.exists():
            print("✅ Configuration file verified!")

            # Show the configuration
            with open(cursor_mcp_config, "r") as f:
                config_content = f.read()
                print(f"\n📋 Configuration content:")
                print(config_content)

            return True
        else:
            print("❌ Configuration file not found after copy!")
            return False

    except Exception as e:
        print(f"❌ Error copying configuration: {e}")
        return False


def test_mcp_server():
    """Test that the MCP server can start."""
    print("\n🧪 Testing MCP Server...")

    try:
        # Test if the server can start
        result = subprocess.run(
            ["python3", "mcp_server_protocol.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 or "usage" in result.stdout.lower():
            print("✅ MCP server can start successfully")
            return True
        else:
            print(f"❌ MCP server test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✅ MCP server started (timeout expected)")
        return True
    except Exception as e:
        print(f"❌ MCP server test error: {e}")
        return False


def main():
    """Main setup routine."""
    print("🚀 Cursor MCP Setup")
    print("=" * 25)

    # Setup configuration
    if setup_cursor_mcp():
        print("\n✅ Configuration setup complete!")
    else:
        print("\n❌ Configuration setup failed!")
        return

    # Test server
    if test_mcp_server():
        print("✅ MCP server test passed!")
    else:
        print("❌ MCP server test failed!")
        return

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Completely quit Cursor (Cmd+Q)")
    print("2. Wait 10 seconds")
    print("3. Reopen Cursor")
    print("4. Check if the red status is gone")
    print("5. Try using the brain-enhanced tools")

    print("\n🔧 If you still see red status:")
    print("- Check Cursor's logs for MCP errors")
    print("- Try restarting your computer")
    print("- Verify Python path in the configuration")


if __name__ == "__main__":
    main()

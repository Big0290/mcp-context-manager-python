#!/usr/bin/env python3
"""
Quick start script for the MCP Memory Server
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run the MCP server with proper path handling."""
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()

    # Add the project root to Python path
    sys.path.insert(0, str(script_dir))

    # Determine which server to run
    server_type = "simple"  # Default to simple server

    if len(sys.argv) > 1:
        server_type = sys.argv[1].lower()

    if server_type == "full":
        server_path = script_dir / "src" / "mcp_server.py"
        print("🚀 Starting full MCP Memory Server...")
    else:
        server_path = script_dir / "src" / "simple_mcp_server.py"
        print("🚀 Starting simple MCP Memory Server...")

    if not server_path.exists():
        print(f"❌ Error: Server file not found at {server_path}")
        sys.exit(1)

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(script_dir)

    try:
        # Run the server
        subprocess.run(["python3", str(server_path)], env=env, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

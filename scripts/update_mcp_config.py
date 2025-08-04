#!/usr/bin/env python3
"""
Script to update MCP configuration with detected project name
"""

import json
import os
from pathlib import Path

from src.project_detector import detect_project_name, sanitize_project_name


def update_mcp_config():
    """Update the MCP configuration with the detected project name."""

    # Detect project name
    project_name = detect_project_name()
    project_id = sanitize_project_name(project_name)

    print(f"Detected project: {project_name}")
    print(f"Using project ID: {project_id}")

    # Get the path to the user's MCP config
    cursor_config_path = Path.home() / ".cursor" / "mcp.json"

    if not cursor_config_path.exists():
        print(f"❌ MCP config not found at {cursor_config_path}")
        return

    # Read current config
    with open(cursor_config_path, "r") as f:
        config = json.load(f)

    # Update the contextProjectId
    if "mcpServers" in config and "mcp-memory-server" in config["mcpServers"]:
        server_config = config["mcpServers"]["mcp-memory-server"]

        # Update contextProjectId
        old_project_id = server_config.get("contextProjectId", "cursor-chat")
        server_config["contextProjectId"] = project_id

        # Also update environment variable if present
        if "env" in server_config:
            server_config["env"]["MCP_PROJECT_ID"] = project_id
        else:
            server_config["env"] = {"MCP_PROJECT_ID": project_id}

        print(f"✅ Updated contextProjectId from '{old_project_id}' to '{project_id}'")
    else:
        print("❌ Could not find mcp-memory-server configuration")
        return

    # Write updated config
    with open(cursor_config_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"✅ MCP configuration updated successfully!")
    print(f"📁 Project: {project_name}")
    print(f"🆔 Project ID: {project_id}")
    print(f"📄 Config file: {cursor_config_path}")


if __name__ == "__main__":
    update_mcp_config()

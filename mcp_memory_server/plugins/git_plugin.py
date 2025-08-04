"""
Git plugin for the MCP Memory Server.
This plugin can extract Git-related information from memories.
"""

import re
from typing import Any, Dict, List

from mcp_memory_server.models.memory import Memory

from .base import BasePlugin


class GitPlugin(BasePlugin):
    """Plugin for extracting and processing Git-related memories."""

    def __init__(self):
        super().__init__(
            name="git_plugin",
            description="Extracts Git commits, branches, and repository information from memories",
        )
        self.git_patterns = {
            "commit_hash": r"\b[a-f0-9]{7,40}\b",
            "branch_name": r"\b(main|master|develop|feature|bugfix|hotfix)/[\w-]+\b",
            "repository": r"\b(github\.com|gitlab\.com|bitbucket\.org)/[\w-]+/[\w-]+\b",
            "git_commands": r"\b(git add|git commit|git push|git pull|git merge|git branch)\b",
        }

    def process_memory(self, memory: Memory) -> Memory:
        """Extract Git information from memory content."""
        if not self.enabled:
            return memory

        # Extract Git-related information
        git_data = {}
        for key, pattern in self.git_patterns.items():
            matches = re.findall(pattern, memory.content, re.IGNORECASE)
            if matches:
                git_data[key] = list(set(matches))

        if git_data:
            # Add Git metadata
            git_data["processed_by"] = self.name

            # Update memory metadata
            if not memory.custom_metadata:
                memory.custom_metadata = {}

            memory.custom_metadata["git"] = git_data

            # Add Git tags
            if "git" not in memory.tags:
                memory.tags.append("git")

            # Add specific tags based on content
            if "commit_hash" in git_data:
                memory.tags.append("commit")
            if "branch_name" in git_data:
                memory.tags.append("branch")
            if "git_commands" in git_data:
                memory.tags.append("git_command")

        return memory

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        info = super().get_plugin_info()
        info.update(
            {
                "git_patterns": len(self.git_patterns),
                "supported_patterns": list(self.git_patterns.keys()),
            }
        )
        return info

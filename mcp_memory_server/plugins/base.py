"""
Base plugin class for the MCP Memory Server.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from mcp_memory_server.models.memory import Memory


class BasePlugin(ABC):
    """Base class for all memory server plugins."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.enabled = True

    @abstractmethod
    def process_memory(self, memory: Memory) -> Memory:
        """Process a memory before it's stored."""
        return memory

    @abstractmethod
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
        }

    def enable(self):
        """Enable the plugin."""
        self.enabled = True

    def disable(self):
        """Disable the plugin."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if the plugin is enabled."""
        return self.enabled

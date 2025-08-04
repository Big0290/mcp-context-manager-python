"""
Plugin system for the MCP Memory Server.
"""

from .base import BasePlugin
from .calendar_plugin import CalendarPlugin
from .git_plugin import GitPlugin

__all__ = [
    "BasePlugin",
    "CalendarPlugin", 
    "GitPlugin"
] 
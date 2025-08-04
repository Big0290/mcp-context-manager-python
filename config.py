#!/usr/bin/env python3
"""
Configuration management for MCP Context Manager Python
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Centralized configuration for MCP Context Manager Python."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    SRC_DIR = PROJECT_ROOT / "src"
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Database configuration
    SIMPLE_DB_PATH = PROJECT_ROOT / "data" / "simple_mcp_memory.db"
    FULL_DB_PATH = PROJECT_ROOT / "data" / "mcp_memory.db"
    PERFORMANCE_DB_PATH = PROJECT_ROOT / "data" / "mcp_performance.db"

    # Server configuration
    DEFAULT_PROJECT_ID = "workspace"
    DEFAULT_AGENT_ID = "cursor-chat"
    MAX_MEMORIES_DEFAULT = 10
    CONTEXT_SUMMARY_LIMIT = 5

    # Performance monitoring
    ENABLE_PERFORMANCE_MONITORING = True
    PERFORMANCE_LOG_INTERVAL = 60  # seconds

    # Context injection settings
    AUTO_CONTEXT_INJECTION = True
    CONTEXT_INJECTION_ENABLED = True
    SHOW_CONTEXT_SUMMARY = True

    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "mcp_server.log"

    # MCP Protocol settings
    MCP_PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "mcp-context-manager-python"
    SERVER_VERSION = "1.0.0"

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_database_path(cls, server_type: str = "simple") -> Path:
        """Get database path for specified server type."""
        if server_type == "simple":
            return cls.SIMPLE_DB_PATH
        elif server_type == "full":
            return cls.FULL_DB_PATH
        else:
            raise ValueError(f"Unknown server type: {server_type}")

    @classmethod
    def get_cursor_config_path(cls) -> Path:
        """Get path to Cursor integration configuration."""
        return PROJECT_ROOT / "cursor_integration.json"


# Environment-specific overrides
def load_env_config():
    """Load configuration from environment variables."""
    Config.DEFAULT_PROJECT_ID = os.getenv("MCP_PROJECT_ID", Config.DEFAULT_PROJECT_ID)
    Config.DEFAULT_AGENT_ID = os.getenv("MCP_AGENT_ID", Config.DEFAULT_AGENT_ID)
    Config.LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", Config.LOG_LEVEL)
    Config.ENABLE_PERFORMANCE_MONITORING = (
        os.getenv("MCP_PERFORMANCE_MONITORING", "true").lower() == "true"
    )


# Initialize configuration
Config.ensure_directories()
load_env_config()

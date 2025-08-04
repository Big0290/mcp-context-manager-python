#!/usr/bin/env python3
"""
Project name detection utilities for MCP Memory Server
"""

import os
from pathlib import Path
from typing import Optional


def detect_project_name(workspace_path: Optional[str] = None) -> str:
    """
    Detect the project name from the workspace.
    
    Args:
        workspace_path: Optional path to workspace, defaults to current directory
        
    Returns:
        The detected project name
    """
    if workspace_path is None:
        workspace_path = os.getcwd()
    
    workspace = Path(workspace_path)
    
    # Method 1: Check for pyproject.toml
    pyproject_path = workspace / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                if 'project' in data and 'name' in data['project']:
                    return data['project']['name']
        except Exception:
            pass
    
    # Method 2: Check for package.json
    package_json_path = workspace / "package.json"
    if package_json_path.exists():
        try:
            import json
            with open(package_json_path, 'r') as f:
                data = json.load(f)
                if 'name' in data:
                    return data['name']
        except Exception:
            pass
    
    # Method 3: Use directory name as fallback
    return workspace.name


def get_project_id_from_env() -> str:
    """
    Get project ID from environment variable or detect from workspace.
    
    Returns:
        The project ID to use
    """
    # Check environment variable first
    env_project_id = os.environ.get('MCP_PROJECT_ID')
    if env_project_id:
        return env_project_id
    
    # Detect from workspace
    return detect_project_name()


def sanitize_project_name(name: str) -> str:
    """
    Sanitize project name for use as project ID.
    
    Args:
        name: Raw project name
        
    Returns:
        Sanitized project ID
    """
    # Replace spaces and special characters with hyphens
    import re
    sanitized = re.sub(r'[^\w\-]', '-', name.lower())
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    return sanitized or 'default-project'


if __name__ == "__main__":
    # Test the detection
    project_name = detect_project_name()
    project_id = sanitize_project_name(project_name)
    print(f"Detected project name: {project_name}")
    print(f"Sanitized project ID: {project_id}") 
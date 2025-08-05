#!/usr/bin/env python3
"""
Session Memory Module for Brain-Like MCP Server
Stores per-session personal data with secure access and session isolation.
"""

import json
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class SessionData:
    """Represents session-specific personal data."""

    # Session identification
    session_id: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None

    # Environment and system data
    environment_variables: Dict[str, str] = field(default_factory=dict)
    system_info: Dict[str, Any] = field(default_factory=dict)

    # User preferences and settings
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    interface_settings: Dict[str, Any] = field(default_factory=dict)

    # Authentication and tokens
    auth_tokens: Dict[str, str] = field(default_factory=dict)
    api_keys: Dict[str, str] = field(default_factory=dict)

    # Session state
    current_working_directory: Optional[str] = None
    active_files: List[str] = field(default_factory=list)
    recent_commands: List[str] = field(default_factory=list)

    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert session data to dictionary (excluding sensitive data)."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "environment_variables": self._sanitize_env_vars(),
            "system_info": self.system_info,
            "user_preferences": self.user_preferences,
            "interface_settings": self.interface_settings,
            "current_working_directory": self.current_working_directory,
            "active_files": self.active_files,
            "recent_commands": self.recent_commands,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def _sanitize_env_vars(self) -> Dict[str, str]:
        """Sanitize environment variables to remove sensitive data."""
        sensitive_keys = {
            "PASSWORD",
            "SECRET",
            "KEY",
            "TOKEN",
            "AUTH",
            "CREDENTIAL",
            "API_KEY",
            "PRIVATE",
            "SENSITIVE",
            "PWD",
            "SSH_",
        }

        sanitized = {}
        for key, value in self.environment_variables.items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def update_access(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.now()


class SessionMemory:
    """Manages session-specific personal data with secure access."""

    def __init__(self, storage_path: str = None, session_timeout_hours: int = 24):
        self.logger = logging.getLogger(__name__)
        self.session_timeout_hours = session_timeout_hours

        if storage_path is None:
            storage_path = Path.cwd() / "data" / "session_memory"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Active sessions cache
        self.active_sessions: Dict[str, SessionData] = {}

        # Load existing sessions
        self._load_sessions()

    def _load_sessions(self):
        """Load existing sessions from storage."""
        try:
            for session_file in self.storage_path.glob("session_*.json"):
                try:
                    with open(session_file, "r") as f:
                        data = json.load(f)
                        session = self._create_session_from_data(data)

                        if not session.is_expired():
                            self.active_sessions[session.session_id] = session
                        else:
                            # Clean up expired session
                            session_file.unlink()
                            self.logger.info(
                                f"Removed expired session: {session.session_id}"
                            )

                except Exception as e:
                    self.logger.error(f"Error loading session {session_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error loading sessions: {e}")

    def _create_session_from_data(self, data: Dict[str, Any]) -> SessionData:
        """Create session data from dictionary."""
        session = SessionData(
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            project_id=data.get("project_id"),
            environment_variables=data.get("environment_variables", {}),
            system_info=data.get("system_info", {}),
            user_preferences=data.get("user_preferences", {}),
            interface_settings=data.get("interface_settings", {}),
            current_working_directory=data.get("current_working_directory"),
            active_files=data.get("active_files", []),
            recent_commands=data.get("recent_commands", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
        )

        # Load sensitive data from separate secure storage
        session.auth_tokens = self._load_sensitive_data(
            session.session_id, "auth_tokens"
        )
        session.api_keys = self._load_sensitive_data(session.session_id, "api_keys")

        return session

    def _load_sensitive_data(self, session_id: str, data_type: str) -> Dict[str, str]:
        """Load sensitive data from secure storage."""
        secure_file = self.storage_path / f"{session_id}_{data_type}.secure"
        if secure_file.exists():
            try:
                with open(secure_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading sensitive data {data_type}: {e}")
        return {}

    def _save_sensitive_data(
        self, session_id: str, data_type: str, data: Dict[str, str]
    ):
        """Save sensitive data to secure storage."""
        secure_file = self.storage_path / f"{session_id}_{data_type}.secure"
        try:
            with open(secure_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving sensitive data {data_type}: {e}")

    def create_session(self, user_id: str = None, project_id: str = None) -> str:
        """Create a new session and return session ID."""
        session_id = secrets.token_urlsafe(32)

        # Collect current environment
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("_")}

        # Get system information
        system_info = {
            "platform": os.name,
            "cwd": os.getcwd(),
            "user": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
        }

        # Create session data
        session = SessionData(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            environment_variables=env_vars,
            system_info=system_info,
            expires_at=datetime.now() + timedelta(hours=self.session_timeout_hours),
        )

        self.active_sessions[session_id] = session
        self._save_session(session)

        self.logger.info(f"Created new session: {session_id}")
        return session_id

    def _save_session(self, session: SessionData):
        """Save session data to storage."""
        try:
            # Save main session data
            session_file = self.storage_path / f"session_{session.session_id}.json"
            with open(session_file, "w") as f:
                json.dump(session.to_dict(), f, indent=2)

            # Save sensitive data separately
            self._save_sensitive_data(
                session.session_id, "auth_tokens", session.auth_tokens
            )
            self._save_sensitive_data(session.session_id, "api_keys", session.api_keys)

        except Exception as e:
            self.logger.error(f"Error saving session {session.session_id}: {e}")

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data by ID."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if not session.is_expired():
                session.update_access()
                return session
            else:
                # Remove expired session
                del self.active_sessions[session_id]
                self._cleanup_session(session_id)

        return None

    def update_session(self, session_id: str, **updates):
        """Update session data."""
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found or expired")

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.update_access()
        self._save_session(session)
        self.logger.info(f"Updated session {session_id}: {list(updates.keys())}")

    def add_auth_token(self, session_id: str, service: str, token: str):
        """Add authentication token to session."""
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found or expired")

        session.auth_tokens[service] = token
        session.update_access()
        self._save_session(session)
        self.logger.info(f"Added auth token for {service} to session {session_id}")

    def add_api_key(self, session_id: str, service: str, key: str):
        """Add API key to session."""
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found or expired")

        session.api_keys[service] = key
        session.update_access()
        self._save_session(session)
        self.logger.info(f"Added API key for {service} to session {session_id}")

    def get_auth_token(self, session_id: str, service: str) -> Optional[str]:
        """Get authentication token for service."""
        session = self.get_session(session_id)
        if session is None:
            return None

        return session.auth_tokens.get(service)

    def get_api_key(self, session_id: str, service: str) -> Optional[str]:
        """Get API key for service."""
        session = self.get_session(session_id)
        if session is None:
            return None

        return session.api_keys.get(service)

    def end_session(self, session_id: str):
        """End a session and clean up data."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        self._cleanup_session(session_id)
        self.logger.info(f"Ended session: {session_id}")

    def _cleanup_session(self, session_id: str):
        """Clean up session files."""
        try:
            # Remove main session file
            session_file = self.storage_path / f"session_{session_id}.json"
            if session_file.exists():
                session_file.unlink()

            # Remove sensitive data files
            for data_type in ["auth_tokens", "api_keys"]:
                secure_file = self.storage_path / f"{session_id}_{data_type}.secure"
                if secure_file.exists():
                    secure_file.unlink()

        except Exception as e:
            self.logger.error(f"Error cleaning up session {session_id}: {e}")

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        expired_sessions = []
        for session_id, session in self.active_sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            self._cleanup_session(session_id)

        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self.active_sessions.keys())

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session data (excluding sensitive information)."""
        session = self.get_session(session_id)
        if session is None:
            return {"error": "Session not found or expired"}

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "project_id": session.project_id,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "expires_at": session.expires_at.isoformat()
            if session.expires_at
            else None,
            "active_files_count": len(session.active_files),
            "recent_commands_count": len(session.recent_commands),
            "auth_services": list(session.auth_tokens.keys()),
            "api_services": list(session.api_keys.keys()),
        }

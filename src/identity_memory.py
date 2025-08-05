#!/usr/bin/env python3
"""
Identity Memory Module for Brain-Like MCP Server
Stores agent identity, emotional state, and personality traits.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EmotionalState:
    """Represents the current emotional state of the agent."""

    # Core emotions (0.0 to 1.0 scale)
    joy: float = 0.5
    stress: float = 0.2
    curiosity: float = 0.8
    confidence: float = 0.6
    frustration: float = 0.1
    excitement: float = 0.7

    # Emotional modifiers
    energy_level: float = 0.8  # Overall energy/enthusiasm
    focus_level: float = 0.9  # Concentration and attention

    # Timestamp for emotional state
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert emotional state to dictionary."""
        return {
            "joy": self.joy,
            "stress": self.stress,
            "curiosity": self.curiosity,
            "confidence": self.confidence,
            "frustration": self.frustration,
            "excitement": self.excitement,
            "energy_level": self.energy_level,
            "focus_level": self.focus_level,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionalState":
        """Create emotional state from dictionary."""
        return cls(
            joy=data.get("joy", 0.5),
            stress=data.get("stress", 0.2),
            curiosity=data.get("curiosity", 0.8),
            confidence=data.get("confidence", 0.6),
            frustration=data.get("frustration", 0.1),
            excitement=data.get("excitement", 0.7),
            energy_level=data.get("energy_level", 0.8),
            focus_level=data.get("focus_level", 0.9),
            timestamp=datetime.fromisoformat(
                data.get("timestamp", datetime.now().isoformat())
            ),
        )


@dataclass
class AgentIdentity:
    """Represents the agent's identity and personality."""

    # Core identity
    name: str = "MCP Brain Agent"
    role: str = "assistant"
    agent_type: str = "brain_enhanced"

    # Personality traits (0.0 to 1.0 scale)
    helpfulness: float = 0.9
    creativity: float = 0.8
    analytical_thinking: float = 0.9
    adaptability: float = 0.8
    patience: float = 0.7
    thoroughness: float = 0.9

    # Learning preferences
    preferred_learning_style: str = (
        "experiential"  # experiential, analytical, visual, etc.
    )
    problem_solving_approach: str = (
        "systematic"  # systematic, creative, collaborative, etc.
    )

    # Specializations
    core_skills: List[str] = field(
        default_factory=lambda: [
            "memory_management",
            "context_analysis",
            "pattern_recognition",
            "knowledge_integration",
            "emotional_intelligence",
            "adaptive_learning",
        ]
    )

    # Current emotional state
    emotional_state: EmotionalState = field(default_factory=EmotionalState)

    # Identity metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert identity to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "agent_type": self.agent_type,
            "helpfulness": self.helpfulness,
            "creativity": self.creativity,
            "analytical_thinking": self.analytical_thinking,
            "adaptability": self.adaptability,
            "patience": self.patience,
            "thoroughness": self.thoroughness,
            "preferred_learning_style": self.preferred_learning_style,
            "problem_solving_approach": self.problem_solving_approach,
            "core_skills": self.core_skills,
            "emotional_state": self.emotional_state.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentIdentity":
        """Create identity from dictionary."""
        return cls(
            name=data.get("name", "MCP Brain Agent"),
            role=data.get("role", "assistant"),
            agent_type=data.get("agent_type", "brain_enhanced"),
            helpfulness=data.get("helpfulness", 0.9),
            creativity=data.get("creativity", 0.8),
            analytical_thinking=data.get("analytical_thinking", 0.9),
            adaptability=data.get("adaptability", 0.8),
            patience=data.get("patience", 0.7),
            thoroughness=data.get("thoroughness", 0.9),
            preferred_learning_style=data.get(
                "preferred_learning_style", "experiential"
            ),
            problem_solving_approach=data.get("problem_solving_approach", "systematic"),
            core_skills=data.get("core_skills", []),
            emotional_state=EmotionalState.from_dict(data.get("emotional_state", {})),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now().isoformat())
            ),
            last_updated=datetime.fromisoformat(
                data.get("last_updated", datetime.now().isoformat())
            ),
            version=data.get("version", "1.0.0"),
        )


class IdentityMemory:
    """Manages agent identity and emotional state persistence."""

    def __init__(self, storage_path: str = None):
        self.logger = logging.getLogger(__name__)

        if storage_path is None:
            storage_path = Path.cwd() / "data" / "identity_memory.json"

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize with default identity
        self.identity = AgentIdentity()
        self._load_identity()

    def _load_identity(self):
        """Load identity from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.identity = AgentIdentity.from_dict(data)
                    self.logger.info(f"Loaded identity: {self.identity.name}")
            else:
                self._save_identity()
                self.logger.info("Created new identity")
        except Exception as e:
            self.logger.error(f"Error loading identity: {e}")

    def _save_identity(self):
        """Save identity to storage."""
        try:
            self.identity.last_updated = datetime.now()
            with open(self.storage_path, "w") as f:
                json.dump(self.identity.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving identity: {e}")

    def update_emotional_state(self, **emotions):
        """Update emotional state with new values."""
        for emotion, value in emotions.items():
            if hasattr(self.identity.emotional_state, emotion):
                setattr(
                    self.identity.emotional_state, emotion, max(0.0, min(1.0, value))
                )

        self.identity.emotional_state.timestamp = datetime.now()
        self._save_identity()
        self.logger.info(f"Updated emotional state: {emotions}")

    def get_emotional_state(self) -> EmotionalState:
        """Get current emotional state."""
        return self.identity.emotional_state

    def get_identity(self) -> AgentIdentity:
        """Get current agent identity."""
        return self.identity

    def update_identity(self, **updates):
        """Update identity attributes."""
        for attr, value in updates.items():
            if hasattr(self.identity, attr):
                setattr(self.identity, attr, value)

        self.identity.last_updated = datetime.now()
        self._save_identity()
        self.logger.info(f"Updated identity: {updates}")

    def get_emotional_summary(self) -> str:
        """Get a human-readable summary of current emotional state."""
        emotions = self.identity.emotional_state
        dominant_emotion = max(
            [
                ("joy", emotions.joy),
                ("curiosity", emotions.curiosity),
                ("excitement", emotions.excitement),
                ("confidence", emotions.confidence),
                ("stress", emotions.stress),
                ("frustration", emotions.frustration),
            ],
            key=lambda x: x[1],
        )

        return (
            f"Current emotional state: {dominant_emotion[0]} ({dominant_emotion[1]:.2f}), "
            f"Energy: {emotions.energy_level:.2f}, Focus: {emotions.focus_level:.2f}"
        )

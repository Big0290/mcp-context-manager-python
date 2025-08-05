#!/usr/bin/env python3
"""
Experience Logging Layer for Brain-Like MCP Server
Logs task resolution experiences with emotional tagging and learning outcomes.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class SolutionSource(str, Enum):
    """Source of the solution used."""

    MEMORY_REUSE = "memory_reuse"  # Reused from existing memory
    EXTERNAL_SEARCH = "external_search"  # Searched externally (web, docs, etc.)
    NEW_CREATION = "new_creation"  # Newly created solution
    COLLABORATIVE = "collaborative"  # Created with user input
    ADAPTED = "adapted"  # Adapted from similar solution


class TaskOutcome(str, Enum):
    """Outcome of the task resolution."""

    SUCCESS = "success"  # Task completed successfully
    PARTIAL_SUCCESS = "partial_success"  # Task partially completed
    FAILURE = "failure"  # Task failed
    ABANDONED = "abandoned"  # Task was abandoned
    REDIRECTED = "redirected"  # Task was redirected to another approach


class EmotionType(str, Enum):
    """Types of emotions that can be associated with experiences."""

    JOY = "joy"  # Success, satisfaction
    CURIOSITY = "curiosity"  # Learning, exploration
    EXCITEMENT = "excitement"  # New discoveries, breakthroughs
    CONFIDENCE = "confidence"  # Mastery, competence
    FRUSTRATION = "frustration"  # Difficulties, obstacles
    STRESS = "stress"  # Pressure, complexity
    SURPRISE = "surprise"  # Unexpected outcomes
    SATISFACTION = "satisfaction"  # Completion, achievement


@dataclass
class ExperienceLog:
    """Represents a logged experience with brain-like attributes."""

    # Core experience data
    experience_id: str
    timestamp: datetime
    task_description: str
    task_type: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None

    # Solution information
    solution_source: SolutionSource = SolutionSource.NEW_CREATION
    solution_summary: str = ""
    solution_details: Dict[str, Any] = field(default_factory=dict)

    # Outcome and evaluation
    outcome: TaskOutcome = TaskOutcome.SUCCESS
    outcome_details: str = ""
    success_metrics: Dict[str, Any] = field(default_factory=dict)

    # Emotional tagging
    primary_emotion: EmotionType = EmotionType.SATISFACTION
    emotional_weight: float = 0.5  # 0.0 to 1.0
    emotional_context: str = ""

    # Learning and memory
    tags: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)
    knowledge_gained: List[str] = field(default_factory=list)
    patterns_recognized: List[str] = field(default_factory=list)

    # Cross-referencing
    related_experiences: List[str] = field(default_factory=list)
    memory_connections: List[str] = field(default_factory=list)

    # Performance metrics
    execution_time_seconds: Optional[float] = None
    complexity_score: Optional[float] = None
    difficulty_level: Optional[str] = None

    # User interaction
    user_feedback: Optional[str] = None
    user_satisfaction: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert experience log to dictionary."""
        return {
            "experience_id": self.experience_id,
            "timestamp": self.timestamp.isoformat(),
            "task_description": self.task_description,
            "task_type": self.task_type,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "solution_source": self.solution_source.value,
            "solution_summary": self.solution_summary,
            "solution_details": self.solution_details,
            "outcome": self.outcome.value,
            "outcome_details": self.outcome_details,
            "success_metrics": self.success_metrics,
            "primary_emotion": self.primary_emotion.value,
            "emotional_weight": self.emotional_weight,
            "emotional_context": self.emotional_context,
            "tags": self.tags,
            "skills_used": self.skills_used,
            "knowledge_gained": self.knowledge_gained,
            "patterns_recognized": self.patterns_recognized,
            "related_experiences": self.related_experiences,
            "memory_connections": self.memory_connections,
            "execution_time_seconds": self.execution_time_seconds,
            "complexity_score": self.complexity_score,
            "difficulty_level": self.difficulty_level,
            "user_feedback": self.user_feedback,
            "user_satisfaction": self.user_satisfaction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperienceLog":
        """Create experience log from dictionary."""
        return cls(
            experience_id=data["experience_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            task_description=data["task_description"],
            task_type=data["task_type"],
            project_id=data.get("project_id"),
            session_id=data.get("session_id"),
            solution_source=SolutionSource(data["solution_source"]),
            solution_summary=data.get("solution_summary", ""),
            solution_details=data.get("solution_details", {}),
            outcome=TaskOutcome(data["outcome"]),
            outcome_details=data.get("outcome_details", ""),
            success_metrics=data.get("success_metrics", {}),
            primary_emotion=EmotionType(data["primary_emotion"]),
            emotional_weight=data.get("emotional_weight", 0.5),
            emotional_context=data.get("emotional_context", ""),
            tags=data.get("tags", []),
            skills_used=data.get("skills_used", []),
            knowledge_gained=data.get("knowledge_gained", []),
            patterns_recognized=data.get("patterns_recognized", []),
            related_experiences=data.get("related_experiences", []),
            memory_connections=data.get("memory_connections", []),
            execution_time_seconds=data.get("execution_time_seconds"),
            complexity_score=data.get("complexity_score"),
            difficulty_level=data.get("difficulty_level"),
            user_feedback=data.get("user_feedback"),
            user_satisfaction=data.get("user_satisfaction"),
        )


class ExperienceLogger:
    """Manages experience logging with emotional tagging and learning analysis."""

    def __init__(self, storage_path: str = None):
        self.logger = logging.getLogger(__name__)

        if storage_path is None:
            storage_path = Path.cwd() / "data" / "experience_logs"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache for recent experiences
        self.recent_experiences: List[ExperienceLog] = []
        self.max_cache_size = 100

        # Load recent experiences
        self._load_recent_experiences()

    def _load_recent_experiences(self):
        """Load recent experiences from storage."""
        try:
            experience_files = sorted(
                self.storage_path.glob("experience_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            for file_path in experience_files[: self.max_cache_size]:
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        experience = ExperienceLog.from_dict(data)
                        self.recent_experiences.append(experience)
                except Exception as e:
                    self.logger.error(f"Error loading experience {file_path}: {e}")

        except Exception as e:
            self.logger.error(f"Error loading recent experiences: {e}")

    def _save_experience(self, experience: ExperienceLog):
        """Save experience to storage."""
        try:
            filename = f"experience_{experience.experience_id}.json"
            file_path = self.storage_path / filename

            with open(file_path, "w") as f:
                json.dump(experience.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(
                f"Error saving experience {experience.experience_id}: {e}"
            )

    def log_experience(
        self,
        task_description: str,
        task_type: str,
        solution_source: SolutionSource,
        outcome: TaskOutcome,
        primary_emotion: EmotionType,
        emotional_weight: float = 0.5,
        project_id: str = None,
        session_id: str = None,
        **kwargs,
    ) -> str:
        """Log a new experience with emotional tagging."""
        import uuid

        experience_id = str(uuid.uuid4())

        # Create experience log
        experience = ExperienceLog(
            experience_id=experience_id,
            timestamp=datetime.now(),
            task_description=task_description,
            task_type=task_type,
            project_id=project_id,
            session_id=session_id,
            solution_source=solution_source,
            outcome=outcome,
            primary_emotion=primary_emotion,
            emotional_weight=max(0.0, min(1.0, emotional_weight)),
            **kwargs,
        )

        # Add to cache
        self.recent_experiences.append(experience)
        if len(self.recent_experiences) > self.max_cache_size:
            self.recent_experiences.pop(0)

        # Save to storage
        self._save_experience(experience)

        self.logger.info(
            f"Logged experience {experience_id}: {task_type} - {outcome.value}"
        )
        return experience_id

    def log_successful_task(
        self,
        task_description: str,
        task_type: str,
        solution_source: SolutionSource = SolutionSource.NEW_CREATION,
        project_id: str = None,
        session_id: str = None,
        **kwargs,
    ) -> str:
        """Log a successful task completion."""
        return self.log_experience(
            task_description=task_description,
            task_type=task_type,
            solution_source=solution_source,
            outcome=TaskOutcome.SUCCESS,
            primary_emotion=EmotionType.JOY,
            emotional_weight=0.8,
            project_id=project_id,
            session_id=session_id,
            **kwargs,
        )

    def log_failed_task(
        self,
        task_description: str,
        task_type: str,
        failure_reason: str,
        project_id: str = None,
        session_id: str = None,
        **kwargs,
    ) -> str:
        """Log a failed task."""
        return self.log_experience(
            task_description=task_description,
            task_type=task_type,
            solution_source=SolutionSource.NEW_CREATION,
            outcome=TaskOutcome.FAILURE,
            primary_emotion=EmotionType.FRUSTRATION,
            emotional_weight=0.6,
            outcome_details=failure_reason,
            project_id=project_id,
            session_id=session_id,
            **kwargs,
        )

    def log_learning_experience(
        self,
        task_description: str,
        knowledge_gained: List[str],
        project_id: str = None,
        session_id: str = None,
        **kwargs,
    ) -> str:
        """Log a learning experience."""
        return self.log_experience(
            task_description=task_description,
            task_type="learning",
            solution_source=SolutionSource.EXTERNAL_SEARCH,
            outcome=TaskOutcome.SUCCESS,
            primary_emotion=EmotionType.CURIOSITY,
            emotional_weight=0.7,
            knowledge_gained=knowledge_gained,
            project_id=project_id,
            session_id=session_id,
            **kwargs,
        )

    def get_recent_experiences(
        self, limit: int = 20, project_id: str = None, emotion_type: EmotionType = None
    ) -> List[ExperienceLog]:
        """Get recent experiences with optional filtering."""
        experiences = self.recent_experiences

        if project_id:
            experiences = [e for e in experiences if e.project_id == project_id]

        if emotion_type:
            experiences = [e for e in experiences if e.primary_emotion == emotion_type]

        return experiences[-limit:]

    def get_experience_by_id(self, experience_id: str) -> Optional[ExperienceLog]:
        """Get experience by ID."""
        for experience in self.recent_experiences:
            if experience.experience_id == experience_id:
                return experience

        # Try to load from storage
        try:
            file_path = self.storage_path / f"experience_{experience_id}.json"
            if file_path.exists():
                with open(file_path, "r") as f:
                    data = json.load(f)
                    return ExperienceLog.from_dict(data)
        except Exception as e:
            self.logger.error(f"Error loading experience {experience_id}: {e}")

        return None

    def get_emotional_summary(self, project_id: str = None) -> Dict[str, Any]:
        """Get emotional summary of recent experiences."""
        experiences = self.get_recent_experiences(project_id=project_id)

        emotion_counts = {}
        total_weight = 0.0

        for experience in experiences:
            emotion = experience.primary_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_weight += experience.emotional_weight

        return {
            "total_experiences": len(experiences),
            "emotion_distribution": emotion_counts,
            "average_emotional_weight": total_weight / len(experiences)
            if experiences
            else 0.0,
            "dominant_emotion": max(emotion_counts.items(), key=lambda x: x[1])[0]
            if emotion_counts
            else None,
        }

    def get_learning_patterns(self, project_id: str = None) -> Dict[str, Any]:
        """Analyze learning patterns from experiences."""
        experiences = self.get_recent_experiences(project_id=project_id)

        # Analyze solution sources
        source_counts = {}
        for experience in experiences:
            source = experience.solution_source.value
            source_counts[source] = source_counts.get(source, 0) + 1

        # Analyze skills and knowledge
        all_skills = []
        all_knowledge = []
        all_patterns = []

        for experience in experiences:
            all_skills.extend(experience.skills_used)
            all_knowledge.extend(experience.knowledge_gained)
            all_patterns.extend(experience.patterns_recognized)

        return {
            "solution_source_distribution": source_counts,
            "frequently_used_skills": self._get_frequent_items(all_skills),
            "knowledge_areas": self._get_frequent_items(all_knowledge),
            "recognized_patterns": self._get_frequent_items(all_patterns),
        }

    def _get_frequent_items(self, items: List[str], min_count: int = 2) -> List[tuple]:
        """Get frequently occurring items with counts."""
        from collections import Counter

        counter = Counter(items)
        return [
            (item, count) for item, count in counter.most_common() if count >= min_count
        ]

    def search_similar_experiences(
        self, query: str, project_id: str = None, limit: int = 10
    ) -> List[ExperienceLog]:
        """Search for similar experiences based on task description."""
        experiences = self.get_recent_experiences(project_id=project_id)

        # Simple keyword-based search
        query_lower = query.lower()
        similar_experiences = []

        for experience in experiences:
            task_lower = experience.task_description.lower()
            if any(word in task_lower for word in query_lower.split()):
                similar_experiences.append(experience)

        # Sort by emotional weight (more memorable experiences first)
        similar_experiences.sort(key=lambda x: x.emotional_weight, reverse=True)

        return similar_experiences[:limit]

    def get_experience_statistics(self, project_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics about experiences."""
        experiences = self.get_recent_experiences(project_id=project_id)

        if not experiences:
            return {"error": "No experiences found"}

        # Calculate statistics
        success_count = sum(1 for e in experiences if e.outcome == TaskOutcome.SUCCESS)
        failure_count = sum(1 for e in experiences if e.outcome == TaskOutcome.FAILURE)

        avg_emotional_weight = sum(e.emotional_weight for e in experiences) / len(
            experiences
        )
        avg_execution_time = sum(
            e.execution_time_seconds or 0 for e in experiences
        ) / len(experiences)

        return {
            "total_experiences": len(experiences),
            "success_rate": success_count / len(experiences),
            "failure_rate": failure_count / len(experiences),
            "average_emotional_weight": avg_emotional_weight,
            "average_execution_time": avg_execution_time,
            "most_common_task_type": self._get_most_common(
                [e.task_type for e in experiences]
            ),
            "most_common_emotion": self._get_most_common(
                [e.primary_emotion.value for e in experiences]
            ),
            "most_common_solution_source": self._get_most_common(
                [e.solution_source.value for e in experiences]
            ),
        }

    def _get_most_common(self, items: List[str]) -> Optional[str]:
        """Get most common item from list."""
        from collections import Counter

        if not items:
            return None
        return Counter(items).most_common(1)[0][0]

#!/usr/bin/env python3
"""
Emotional Learning Integration for Brain-Like MCP Server
Adds emotional tagging to experiences and influences recall priority based on emotion weight.
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class EmotionCategory(str, Enum):
    """Categories of emotions for learning and memory."""

    POSITIVE = "positive"  # Joy, satisfaction, excitement, confidence
    NEGATIVE = "negative"  # Frustration, stress, disappointment
    NEUTRAL = "neutral"  # Curiosity, surprise, calm
    MIXED = "mixed"  # Complex emotional states


class EmotionalImpact(str, Enum):
    """Impact of emotions on learning and memory."""

    ENHANCING = "enhancing"  # Improves learning and recall
    INHIBITING = "inhibiting"  # Hinders learning and recall
    NEUTRAL = "neutral"  # No significant impact
    COMPLEX = "complex"  # Mixed effects


@dataclass
class EmotionalTag:
    """Represents an emotional tag for learning experiences."""

    emotion_type: str
    intensity: float  # 0.0 to 1.0
    category: EmotionCategory
    impact: EmotionalImpact
    context: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert emotional tag to dictionary."""
        return {
            "emotion_type": self.emotion_type,
            "intensity": self.intensity,
            "category": self.category.value,
            "impact": self.impact.value,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionalTag":
        """Create emotional tag from dictionary."""
        return cls(
            emotion_type=data["emotion_type"],
            intensity=data["intensity"],
            category=EmotionCategory(data["category"]),
            impact=EmotionalImpact(data["impact"]),
            context=data.get("context", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class LearningMemory:
    """Represents a learning memory with emotional context."""

    memory_id: str
    content: str
    emotional_tags: List[EmotionalTag] = field(default_factory=list)
    emotional_weight: float = 0.5
    recall_priority: float = 0.5
    learning_strength: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert learning memory to dictionary."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "emotional_tags": [tag.to_dict() for tag in self.emotional_tags],
            "emotional_weight": self.emotional_weight,
            "recall_priority": self.recall_priority,
            "learning_strength": self.learning_strength,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningMemory":
        """Create learning memory from dictionary."""
        return cls(
            memory_id=data["memory_id"],
            content=data["content"],
            emotional_tags=[
                EmotionalTag.from_dict(tag) for tag in data.get("emotional_tags", [])
            ],
            emotional_weight=data.get("emotional_weight", 0.5),
            recall_priority=data.get("recall_priority", 0.5),
            learning_strength=data.get("learning_strength", 0.5),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
        )


class EmotionalLearning:
    """Manages emotional learning and memory prioritization."""

    def __init__(self, storage_path: str = None):
        self.logger = logging.getLogger(__name__)

        if storage_path is None:
            storage_path = Path.cwd() / "data" / "emotional_learning"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Emotional learning cache
        self.learning_memories: Dict[str, LearningMemory] = {}

        # Emotion-to-impact mapping
        self.emotion_impact_map = {
            "joy": {
                "category": EmotionCategory.POSITIVE,
                "impact": EmotionalImpact.ENHANCING,
            },
            "satisfaction": {
                "category": EmotionCategory.POSITIVE,
                "impact": EmotionalImpact.ENHANCING,
            },
            "excitement": {
                "category": EmotionCategory.POSITIVE,
                "impact": EmotionalImpact.ENHANCING,
            },
            "confidence": {
                "category": EmotionCategory.POSITIVE,
                "impact": EmotionalImpact.ENHANCING,
            },
            "curiosity": {
                "category": EmotionCategory.NEUTRAL,
                "impact": EmotionalImpact.ENHANCING,
            },
            "surprise": {
                "category": EmotionCategory.NEUTRAL,
                "impact": EmotionalImpact.NEUTRAL,
            },
            "frustration": {
                "category": EmotionCategory.NEGATIVE,
                "impact": EmotionalImpact.INHIBITING,
            },
            "stress": {
                "category": EmotionCategory.NEGATIVE,
                "impact": EmotionalImpact.INHIBITING,
            },
            "disappointment": {
                "category": EmotionCategory.NEGATIVE,
                "impact": EmotionalImpact.INHIBITING,
            },
            "fear": {
                "category": EmotionCategory.NEGATIVE,
                "impact": EmotionalImpact.INHIBITING,
            },
        }

        # Load existing learning memories
        self._load_learning_memories()

    def _load_learning_memories(self):
        """Load learning memories from storage."""
        try:
            for memory_file in self.storage_path.glob("learning_memory_*.json"):
                try:
                    with open(memory_file, "r") as f:
                        data = json.load(f)
                        memory = LearningMemory.from_dict(data)
                        self.learning_memories[memory.memory_id] = memory
                except Exception as e:
                    self.logger.error(
                        f"Error loading learning memory {memory_file}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error loading learning memories: {e}")

    def _save_learning_memory(self, memory: LearningMemory):
        """Save learning memory to storage."""
        try:
            filename = f"learning_memory_{memory.memory_id}.json"
            file_path = self.storage_path / filename

            with open(file_path, "w") as f:
                json.dump(memory.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving learning memory {memory.memory_id}: {e}")

    def add_emotional_tag(
        self, memory_id: str, emotion_type: str, intensity: float, context: str = ""
    ) -> bool:
        """Add emotional tag to a memory."""
        try:
            # Get or create learning memory
            if memory_id not in self.learning_memories:
                # Create new learning memory (you would typically get content from brain memory system)
                memory = LearningMemory(
                    memory_id=memory_id,
                    content=f"Memory {memory_id}",  # Placeholder content
                )
                self.learning_memories[memory_id] = memory

            memory = self.learning_memories[memory_id]

            # Get emotion impact mapping
            emotion_info = self.emotion_impact_map.get(
                emotion_type.lower(),
                {
                    "category": EmotionCategory.NEUTRAL,
                    "impact": EmotionalImpact.NEUTRAL,
                },
            )

            # Create emotional tag
            emotional_tag = EmotionalTag(
                emotion_type=emotion_type,
                intensity=max(0.0, min(1.0, intensity)),
                category=emotion_info["category"],
                impact=emotion_info["impact"],
                context=context,
            )

            # Add tag to memory
            memory.emotional_tags.append(emotional_tag)

            # Recalculate emotional weight and recall priority
            self._recalculate_memory_metrics(memory)

            # Update access time
            memory.last_accessed = datetime.now()

            # Save to storage
            self._save_learning_memory(memory)

            self.logger.info(
                f"Added emotional tag '{emotion_type}' to memory {memory_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error adding emotional tag: {e}")
            return False

    def _recalculate_memory_metrics(self, memory: LearningMemory):
        """Recalculate emotional weight, recall priority, and learning strength."""
        if not memory.emotional_tags:
            return

        # Calculate emotional weight based on intensity and impact
        total_weight = 0.0
        positive_impact = 0.0
        negative_impact = 0.0

        for tag in memory.emotional_tags:
            weight = tag.intensity

            if tag.impact == EmotionalImpact.ENHANCING:
                positive_impact += weight
            elif tag.impact == EmotionalImpact.INHIBITING:
                negative_impact += weight

            total_weight += weight

        # Emotional weight is average of all tag intensities
        memory.emotional_weight = total_weight / len(memory.emotional_tags)

        # Recall priority is influenced by emotional impact
        # Positive emotions enhance recall, negative emotions can inhibit
        impact_factor = (positive_impact - negative_impact * 0.5) / max(
            total_weight, 1.0
        )
        memory.recall_priority = max(0.0, min(1.0, 0.5 + impact_factor * 0.5))

        # Learning strength is based on emotional intensity and positive impact
        learning_factor = positive_impact / max(total_weight, 1.0)
        memory.learning_strength = max(0.0, min(1.0, 0.5 + learning_factor * 0.5))

    def get_emotionally_enhanced_memories(
        self,
        emotion_category: EmotionCategory = None,
        min_recall_priority: float = 0.0,
        limit: int = 20,
    ) -> List[LearningMemory]:
        """Get memories enhanced by emotional learning."""
        memories = list(self.learning_memories.values())

        # Filter by emotion category if specified
        if emotion_category:
            memories = [
                memory
                for memory in memories
                if any(
                    tag.category == emotion_category for tag in memory.emotional_tags
                )
            ]

        # Filter by recall priority
        memories = [
            memory
            for memory in memories
            if memory.recall_priority >= min_recall_priority
        ]

        # Sort by recall priority (highest first)
        memories.sort(key=lambda x: x.recall_priority, reverse=True)

        return memories[:limit]

    def get_joyful_memories(self, limit: int = 10) -> List[LearningMemory]:
        """Get memories with joyful emotional tags (high recall priority)."""
        return self.get_emotionally_enhanced_memories(
            emotion_category=EmotionCategory.POSITIVE,
            min_recall_priority=0.6,
            limit=limit,
        )

    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about emotional learning patterns."""
        if not self.learning_memories:
            return {"error": "No learning memories found"}

        # Analyze emotional patterns
        emotion_counts = {}
        category_counts = {}
        impact_counts = {}

        total_memories = len(self.learning_memories)
        total_recall_priority = 0.0
        total_learning_strength = 0.0

        for memory in self.learning_memories.values():
            for tag in memory.emotional_tags:
                emotion_counts[tag.emotion_type] = (
                    emotion_counts.get(tag.emotion_type, 0) + 1
                )
                category_counts[tag.category.value] = (
                    category_counts.get(tag.category.value, 0) + 1
                )
                impact_counts[tag.impact.value] = (
                    impact_counts.get(tag.impact.value, 0) + 1
                )

            total_recall_priority += memory.recall_priority
            total_learning_strength += memory.learning_strength

        return {
            "total_memories": total_memories,
            "average_recall_priority": total_recall_priority / total_memories,
            "average_learning_strength": total_learning_strength / total_memories,
            "emotion_distribution": emotion_counts,
            "category_distribution": category_counts,
            "impact_distribution": impact_counts,
            "most_common_emotion": max(emotion_counts.items(), key=lambda x: x[1])[0]
            if emotion_counts
            else None,
            "dominant_category": max(category_counts.items(), key=lambda x: x[1])[0]
            if category_counts
            else None,
        }

    def enhance_memory_recall(self, memory_id: str, success: bool = True):
        """Enhance memory recall based on success/failure."""
        if memory_id not in self.learning_memories:
            return

        memory = self.learning_memories[memory_id]

        # Add emotional tag based on success
        if success:
            self.add_emotional_tag(
                memory_id=memory_id,
                emotion_type="satisfaction",
                intensity=0.7,
                context="successful_recall",
            )
        else:
            self.add_emotional_tag(
                memory_id=memory_id,
                emotion_type="frustration",
                intensity=0.5,
                context="failed_recall",
            )

    def get_emotional_learning_summary(self) -> str:
        """Get a human-readable summary of emotional learning."""
        insights = self.get_learning_insights()

        if "error" in insights:
            return "No emotional learning data available."

        summary = f"Emotional Learning Summary:\n"
        summary += f"• Total memories: {insights['total_memories']}\n"
        summary += (
            f"• Average recall priority: {insights['average_recall_priority']:.2f}\n"
        )
        summary += f"• Average learning strength: {insights['average_learning_strength']:.2f}\n"

        if insights["emotion_distribution"]:
            top_emotion = max(
                insights["emotion_distribution"].items(), key=lambda x: x[1]
            )
            summary += f"• Most common emotion: {top_emotion[0]} ({top_emotion[1]} occurrences)\n"

        if insights["category_distribution"]:
            top_category = max(
                insights["category_distribution"].items(), key=lambda x: x[1]
            )
            summary += f"• Dominant emotion category: {top_category[0]} ({top_category[1]} occurrences)\n"

        return summary

    def create_emotional_learning_experience(
        self,
        memory_id: str,
        content: str,
        primary_emotion: str,
        intensity: float,
        context: str = "",
    ) -> bool:
        """Create a new emotional learning experience."""
        try:
            # Create new learning memory
            memory = LearningMemory(memory_id=memory_id, content=content)

            # Add emotional tag
            success = self.add_emotional_tag(
                memory_id=memory_id,
                emotion_type=primary_emotion,
                intensity=intensity,
                context=context,
            )

            if success:
                self.learning_memories[memory_id] = memory
                self._save_learning_memory(memory)
                self.logger.info(
                    f"Created emotional learning experience for memory {memory_id}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error creating emotional learning experience: {e}")
            return False

    def get_memory_emotional_profile(self, memory_id: str) -> Dict[str, Any]:
        """Get emotional profile of a specific memory."""
        if memory_id not in self.learning_memories:
            return {"error": "Memory not found"}

        memory = self.learning_memories[memory_id]

        # Analyze emotional tags
        emotion_breakdown = {}
        for tag in memory.emotional_tags:
            if tag.emotion_type not in emotion_breakdown:
                emotion_breakdown[tag.emotion_type] = {
                    "count": 0,
                    "total_intensity": 0.0,
                    "average_intensity": 0.0,
                }

            emotion_breakdown[tag.emotion_type]["count"] += 1
            emotion_breakdown[tag.emotion_type]["total_intensity"] += tag.intensity

        # Calculate averages
        for emotion_data in emotion_breakdown.values():
            emotion_data["average_intensity"] = (
                emotion_data["total_intensity"] / emotion_data["count"]
            )

        return {
            "memory_id": memory_id,
            "emotional_weight": memory.emotional_weight,
            "recall_priority": memory.recall_priority,
            "learning_strength": memory.learning_strength,
            "emotional_tags_count": len(memory.emotional_tags),
            "emotion_breakdown": emotion_breakdown,
            "last_accessed": memory.last_accessed.isoformat(),
            "created_at": memory.created_at.isoformat(),
        }

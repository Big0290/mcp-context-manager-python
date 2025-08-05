#!/usr/bin/env python3
"""
Human-Like Decision Loop for Brain-Like MCP Server
Implements pseudo-behavior for memory-based decision making and learning.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DecisionType(str, Enum):
    """Types of decisions the cognitive loop can make."""

    MEMORY_REUSE = "memory_reuse"  # Reuse existing solution
    EXTERNAL_SEARCH = "external_search"  # Search externally for solution
    NEW_CREATION = "new_creation"  # Create new solution
    COLLABORATIVE = "collaborative"  # Work with user
    ADAPTATION = "adaptation"  # Adapt existing solution
    LEARNING = "learning"  # Learn new information


class CognitiveState(str, Enum):
    """States of the cognitive loop."""

    IDLE = "idle"  # Waiting for input
    ANALYZING = "analyzing"  # Analyzing task
    SEARCHING = "searching"  # Searching for solutions
    LEARNING = "learning"  # Learning new information
    CREATING = "creating"  # Creating solution
    REFLECTING = "reflecting"  # Reflecting on experience


@dataclass
class CognitiveTask:
    """Represents a cognitive task with decision-making context."""

    task_id: str
    description: str
    task_type: str
    priority: float = 0.5
    complexity: float = 0.5
    emotional_context: str = ""

    # Decision-making data
    decision_type: Optional[DecisionType] = None
    confidence_level: float = 0.0
    reasoning: str = ""

    # Memory and learning
    similar_memories: List[str] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)
    emotional_tags: List[str] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert cognitive task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority,
            "complexity": self.complexity,
            "emotional_context": self.emotional_context,
            "decision_type": self.decision_type.value if self.decision_type else None,
            "confidence_level": self.confidence_level,
            "reasoning": self.reasoning,
            "similar_memories": self.similar_memories,
            "learning_outcomes": self.learning_outcomes,
            "emotional_tags": self.emotional_tags,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }


class CognitiveLoop:
    """Human-like decision loop for brain-like MCP server."""

    def __init__(
        self,
        brain_memory_system=None,
        memory_query_engine=None,
        experience_logger=None,
        emotional_learning=None,
        identity_memory=None,
    ):
        self.logger = logging.getLogger(__name__)

        # Core systems
        self.brain_memory_system = brain_memory_system
        self.memory_query_engine = memory_query_engine
        self.experience_logger = experience_logger
        self.emotional_learning = emotional_learning
        self.identity_memory = identity_memory

        # Cognitive state
        self.current_state = CognitiveState.IDLE
        self.current_task: Optional[CognitiveTask] = None

        # Decision thresholds
        self.memory_reuse_threshold = 0.7
        self.external_search_threshold = 0.5
        self.learning_threshold = 0.3

        # Performance tracking
        self.task_history: List[CognitiveTask] = []
        self.decision_statistics = {
            "memory_reuse": 0,
            "external_search": 0,
            "new_creation": 0,
            "collaborative": 0,
            "adaptation": 0,
            "learning": 0,
        }

    async def process_task(
        self,
        task_description: str,
        task_type: str = "general",
        priority: float = 0.5,
        project_id: str = None,
        session_id: str = None,
    ) -> Dict[str, Any]:
        """Process a task using human-like cognitive decision making."""
        import uuid

        # Create cognitive task
        task_id = str(uuid.uuid4())
        task = CognitiveTask(
            task_id=task_id,
            description=task_description,
            task_type=task_type,
            priority=priority,
        )

        self.current_task = task
        self.current_state = CognitiveState.ANALYZING

        try:
            # Step 1: Analyze task and search for similar memories
            self.logger.info(f"Analyzing task: {task_description[:50]}...")
            similar_memories = await self._search_similar_memories(
                task_description, project_id
            )
            task.similar_memories = [m.memory_id for m in similar_memories]

            # Step 2: Make decision based on available information
            decision = await self._make_decision(task, similar_memories)
            task.decision_type = decision["type"]
            task.confidence_level = decision["confidence"]
            task.reasoning = decision["reasoning"]

            # Step 3: Execute decision
            result = await self._execute_decision(task, decision)

            # Step 4: Learn from experience
            await self._learn_from_experience(task, result)

            # Step 5: Update emotional state
            await self._update_emotional_state(task, result)

            # Complete task
            task.completed_at = datetime.now()
            self.task_history.append(task)
            self.decision_statistics[decision["type"].value] += 1

            self.current_state = CognitiveState.IDLE
            self.current_task = None

            return {
                "task_id": task_id,
                "decision": decision,
                "result": result,
                "similar_memories_count": len(similar_memories),
                "processing_time": (
                    task.completed_at - task.created_at
                ).total_seconds(),
            }

        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            self.current_state = CognitiveState.IDLE
            self.current_task = None
            return {"error": str(e)}

    async def _search_similar_memories(
        self, task_description: str, project_id: str = None
    ) -> List[Any]:
        """Search for similar memories using the query engine."""
        if not self.memory_query_engine:
            return []

        try:
            # Extract potential tags from task description
            tags = self._extract_tags_from_description(task_description)

            # Query for similar memories
            results = self.memory_query_engine.query_memories(
                query=task_description,
                project_id=project_id,
                search_tags=tags,
                max_results=10,
            )

            self.logger.info(f"Found {len(results)} similar memories")
            return results

        except Exception as e:
            self.logger.error(f"Error searching similar memories: {e}")
            return []

    def _extract_tags_from_description(self, description: str) -> List[str]:
        """Extract potential tags from task description."""
        # Simple keyword extraction - in a real implementation, you might use NLP
        keywords = description.lower().split()

        # Common programming and technical tags
        technical_tags = [
            "python",
            "javascript",
            "react",
            "node",
            "api",
            "database",
            "debug",
            "error",
            "fix",
            "optimize",
            "test",
            "deploy",
            "git",
            "docker",
            "aws",
            "cloud",
            "frontend",
            "backend",
        ]

        extracted_tags = []
        for keyword in keywords:
            if keyword in technical_tags:
                extracted_tags.append(keyword)

        return extracted_tags

    async def _make_decision(
        self, task: CognitiveTask, similar_memories: List[Any]
    ) -> Dict[str, Any]:
        """Make a decision about how to handle the task."""

        # Calculate confidence based on similar memories
        confidence = 0.0
        reasoning = ""

        if similar_memories:
            # Calculate average relevance score
            avg_relevance = sum(m.relevance_score for m in similar_memories) / len(
                similar_memories
            )
            confidence = avg_relevance

            if confidence > self.memory_reuse_threshold:
                decision_type = DecisionType.MEMORY_REUSE
                reasoning = f"Found {len(similar_memories)} highly relevant memories (confidence: {confidence:.2f})"
            elif confidence > self.external_search_threshold:
                decision_type = DecisionType.ADAPTATION
                reasoning = f"Found {len(similar_memories)} moderately relevant memories, will adapt (confidence: {confidence:.2f})"
            else:
                decision_type = DecisionType.EXTERNAL_SEARCH
                reasoning = f"Found {len(similar_memories)} memories but relevance is low (confidence: {confidence:.2f}), will search externally"
        else:
            # No similar memories found
            if task.task_type in ["learning", "research"]:
                decision_type = DecisionType.LEARNING
                reasoning = (
                    "No similar memories found, treating as learning opportunity"
                )
            elif task.priority > 0.8:
                decision_type = DecisionType.NEW_CREATION
                reasoning = (
                    "High priority task with no similar memories, creating new solution"
                )
            else:
                decision_type = DecisionType.EXTERNAL_SEARCH
                reasoning = "No similar memories found, will search externally"

        return {
            "type": decision_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "similar_memories_count": len(similar_memories),
        }

    async def _execute_decision(
        self, task: CognitiveTask, decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the decided course of action."""

        decision_type = decision["type"]
        task.started_at = datetime.now()

        if decision_type == DecisionType.MEMORY_REUSE:
            return await self._reuse_solution(task)
        elif decision_type == DecisionType.EXTERNAL_SEARCH:
            return await self._search_externally(task)
        elif decision_type == DecisionType.NEW_CREATION:
            return await self._create_new_solution(task)
        elif decision_type == DecisionType.ADAPTATION:
            return await self._adapt_solution(task)
        elif decision_type == DecisionType.LEARNING:
            return await self._learn_new_information(task)
        elif decision_type == DecisionType.COLLABORATIVE:
            return await self._collaborate_with_user(task)
        else:
            return {"error": f"Unknown decision type: {decision_type}"}

    async def _reuse_solution(self, task: CognitiveTask) -> Dict[str, Any]:
        """Reuse an existing solution from memory."""
        self.current_state = CognitiveState.ANALYZING

        # Get the most relevant memory
        if task.similar_memories and self.memory_query_engine:
            similar_memories = self.memory_query_engine.query_memories(
                query=task.description, max_results=1
            )

            if similar_memories:
                best_memory = similar_memories[0]

                # Log the experience
                if self.experience_logger:
                    self.experience_logger.log_successful_task(
                        task_description=task.description,
                        task_type=task.task_type,
                        solution_source="memory_reuse",
                        project_id=getattr(self, "project_id", None),
                        session_id=getattr(self, "session_id", None),
                        solution_summary=f"Reused solution from memory: {best_memory.memory_id}",
                        skills_used=["memory_recall", "pattern_recognition"],
                        patterns_recognized=["solution_reuse"],
                    )

                return {
                    "action": "memory_reuse",
                    "memory_id": best_memory.memory_id,
                    "content": best_memory.content,
                    "relevance_score": best_memory.relevance_score,
                    "success": True,
                }

        return {
            "action": "memory_reuse",
            "success": False,
            "reason": "No suitable memory found for reuse",
        }

    async def _search_externally(self, task: CognitiveTask) -> Dict[str, Any]:
        """Search externally for solutions."""
        self.current_state = CognitiveState.SEARCHING

        # Simulate external search
        await asyncio.sleep(0.1)  # Simulate search time

        # Log the experience
        if self.experience_logger:
            self.experience_logger.log_experience(
                task_description=task.description,
                task_type=task.task_type,
                solution_source="external_search",
                outcome="success",
                primary_emotion="curiosity",
                emotional_weight=0.6,
                knowledge_gained=["external_research", "information_gathering"],
                skills_used=["research", "information_synthesis"],
            )

        return {
            "action": "external_search",
            "success": True,
            "search_results": "External search completed",
            "knowledge_gained": ["external_research", "information_gathering"],
        }

    async def _create_new_solution(self, task: CognitiveTask) -> Dict[str, Any]:
        """Create a new solution."""
        self.current_state = CognitiveState.CREATING

        # Simulate solution creation
        await asyncio.sleep(0.2)  # Simulate creation time

        # Log the experience
        if self.experience_logger:
            self.experience_logger.log_successful_task(
                task_description=task.description,
                task_type=task.task_type,
                solution_source="new_creation",
                primary_emotion="excitement",
                emotional_weight=0.8,
                skills_used=["problem_solving", "creativity"],
                patterns_recognized=["new_solution_creation"],
            )

        return {
            "action": "new_creation",
            "success": True,
            "solution": "New solution created",
            "skills_used": ["problem_solving", "creativity"],
        }

    async def _adapt_solution(self, task: CognitiveTask) -> Dict[str, Any]:
        """Adapt an existing solution."""
        self.current_state = CognitiveState.CREATING

        # Simulate adaptation
        await asyncio.sleep(0.15)  # Simulate adaptation time

        # Log the experience
        if self.experience_logger:
            self.experience_logger.log_experience(
                task_description=task.description,
                task_type=task.task_type,
                solution_source="adapted",
                outcome="success",
                primary_emotion="confidence",
                emotional_weight=0.7,
                skills_used=["adaptation", "modification"],
                patterns_recognized=["solution_adaptation"],
            )

        return {
            "action": "adaptation",
            "success": True,
            "adapted_solution": "Solution adapted from existing memory",
            "skills_used": ["adaptation", "modification"],
        }

    async def _learn_new_information(self, task: CognitiveTask) -> Dict[str, Any]:
        """Learn new information."""
        self.current_state = CognitiveState.LEARNING

        # Simulate learning process
        await asyncio.sleep(0.1)  # Simulate learning time

        # Log the learning experience
        if self.experience_logger:
            self.experience_logger.log_learning_experience(
                task_description=task.description,
                knowledge_gained=["new_knowledge", "skill_development"],
                primary_emotion="curiosity",
                emotional_weight=0.7,
            )

        return {
            "action": "learning",
            "success": True,
            "knowledge_gained": ["new_knowledge", "skill_development"],
            "learning_outcomes": ["understanding", "skill_improvement"],
        }

    async def _collaborate_with_user(self, task: CognitiveTask) -> Dict[str, Any]:
        """Collaborate with the user."""
        self.current_state = CognitiveState.ANALYZING

        # Log the collaborative experience
        if self.experience_logger:
            self.experience_logger.log_experience(
                task_description=task.description,
                task_type=task.task_type,
                solution_source="collaborative",
                outcome="success",
                primary_emotion="satisfaction",
                emotional_weight=0.6,
                skills_used=["collaboration", "communication"],
            )

        return {
            "action": "collaboration",
            "success": True,
            "collaboration_type": "user_interaction",
            "skills_used": ["collaboration", "communication"],
        }

    async def _learn_from_experience(self, task: CognitiveTask, result: Dict[str, Any]):
        """Learn from the completed task experience."""
        if not self.experience_logger:
            return

        # Determine emotional context based on result
        if result.get("success", False):
            primary_emotion = "satisfaction"
            emotional_weight = 0.7
        else:
            primary_emotion = "frustration"
            emotional_weight = 0.5

        # Log the complete experience
        self.experience_logger.log_experience(
            task_description=task.description,
            task_type=task.task_type,
            solution_source=result.get("action", "unknown"),
            outcome="success" if result.get("success", False) else "failure",
            primary_emotion=primary_emotion,
            emotional_weight=emotional_weight,
            project_id=getattr(self, "project_id", None),
            session_id=getattr(self, "session_id", None),
            skills_used=result.get("skills_used", []),
            knowledge_gained=result.get("knowledge_gained", []),
            patterns_recognized=result.get("patterns_recognized", []),
        )

    async def _update_emotional_state(
        self, task: CognitiveTask, result: Dict[str, Any]
    ):
        """Update emotional state based on task outcome."""
        if not self.identity_memory:
            return

        # Determine emotional impact based on result
        if result.get("success", False):
            if result.get("action") == "memory_reuse":
                self.identity_memory.update_emotional_state(confidence=0.8, joy=0.7)
            elif result.get("action") == "new_creation":
                self.identity_memory.update_emotional_state(
                    excitement=0.8, confidence=0.6
                )
            elif result.get("action") == "learning":
                self.identity_memory.update_emotional_state(
                    curiosity=0.8, satisfaction=0.6
                )
            else:
                self.identity_memory.update_emotional_state(satisfaction=0.7)
        else:
            self.identity_memory.update_emotional_state(frustration=0.5, stress=0.3)

    def get_cognitive_statistics(self) -> Dict[str, Any]:
        """Get statistics about cognitive decision making."""
        total_tasks = len(self.task_history)

        if total_tasks == 0:
            return {"error": "No tasks processed yet"}

        # Calculate decision distribution
        decision_distribution = {}
        for decision_type, count in self.decision_statistics.items():
            decision_distribution[decision_type] = count / total_tasks

        # Calculate average processing time
        processing_times = []
        for task in self.task_history:
            if task.completed_at and task.started_at:
                processing_times.append(
                    (task.completed_at - task.started_at).total_seconds()
                )

        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        return {
            "total_tasks_processed": total_tasks,
            "decision_distribution": decision_distribution,
            "average_processing_time": avg_processing_time,
            "current_state": self.current_state.value,
            "most_common_decision": max(
                self.decision_statistics.items(), key=lambda x: x[1]
            )[0]
            if self.decision_statistics
            else None,
        }

    def get_cognitive_summary(self) -> str:
        """Get a human-readable summary of cognitive performance."""
        stats = self.get_cognitive_statistics()

        if "error" in stats:
            return "No cognitive data available."

        summary = f"Cognitive Loop Summary:\n"
        summary += f"• Total tasks processed: {stats['total_tasks_processed']}\n"
        summary += (
            f"• Average processing time: {stats['average_processing_time']:.3f}s\n"
        )
        summary += f"• Current state: {stats['current_state']}\n"
        summary += f"• Most common decision: {stats['most_common_decision']}\n"

        summary += f"\nDecision Distribution:\n"
        for decision, percentage in stats["decision_distribution"].items():
            summary += f"• {decision}: {percentage:.1%}\n"

        return summary

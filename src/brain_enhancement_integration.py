#!/usr/bin/env python3
"""
Brain Enhancement Integration for MCP Server
Integrates all brain-like enhancement modules into a unified system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .cognitive_loop import CognitiveLoop
from .emotional_learning import EmotionalLearning
from .experience_logger import ExperienceLogger
from .identity_memory import IdentityMemory
from .memory_query_engine import MemoryQueryEngine
from .session_memory import SessionMemory


class BrainEnhancementIntegration:
    """
    Integrates all brain-like enhancement modules into a unified system.
    Provides a single interface for brain-enhanced MCP server functionality.
    """

    def __init__(self, brain_memory_system=None, enable_all_features: bool = True):
        self.logger = logging.getLogger(__name__)
        self.enable_all_features = enable_all_features

        # Initialize all brain enhancement modules
        if enable_all_features:
            self.identity_memory = IdentityMemory()
            self.session_memory = SessionMemory()
            self.experience_logger = ExperienceLogger()
            self.memory_query_engine = MemoryQueryEngine(
                brain_memory_system=brain_memory_system,
                experience_logger=self.experience_logger,
            )
            self.emotional_learning = EmotionalLearning()
            self.cognitive_loop = CognitiveLoop(
                brain_memory_system=brain_memory_system,
                memory_query_engine=self.memory_query_engine,
                experience_logger=self.experience_logger,
                emotional_learning=self.emotional_learning,
                identity_memory=self.identity_memory,
            )
        else:
            # Disable brain features
            self.identity_memory = None
            self.session_memory = None
            self.experience_logger = None
            self.memory_query_engine = None
            self.emotional_learning = None
            self.cognitive_loop = None

        self.logger.info(
            f"Brain Enhancement Integration initialized (Features: {'enabled' if enable_all_features else 'disabled'})"
        )

    async def process_task_with_brain(
        self,
        task_description: str,
        task_type: str = "general",
        priority: float = 0.5,
        project_id: str = None,
        session_id: str = None,
    ) -> Dict[str, Any]:
        """Process a task using the complete brain-like system."""
        if not self.enable_all_features:
            return {"error": "Brain features are disabled"}

        try:
            # Process task through cognitive loop
            result = await self.cognitive_loop.process_task(
                task_description=task_description,
                task_type=task_type,
                priority=priority,
                project_id=project_id,
                session_id=session_id,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing task with brain: {e}")
            return {"error": str(e)}

    def get_identity_summary(self) -> Dict[str, Any]:
        """Get current identity and emotional state summary."""
        if not self.identity_memory:
            return {"error": "Identity memory is disabled"}

        identity = self.identity_memory.get_identity()
        emotional_state = self.identity_memory.get_emotional_state()

        return {
            "name": identity.name,
            "role": identity.role,
            "agent_type": identity.agent_type,
            "emotional_summary": self.identity_memory.get_emotional_summary(),
            "emotional_state": emotional_state.to_dict(),
            "personality_traits": {
                "helpfulness": identity.helpfulness,
                "creativity": identity.creativity,
                "analytical_thinking": identity.analytical_thinking,
                "adaptability": identity.adaptability,
                "patience": identity.patience,
                "thoroughness": identity.thoroughness,
            },
            "core_skills": identity.core_skills,
            "preferred_learning_style": identity.preferred_learning_style,
            "problem_solving_approach": identity.problem_solving_approach,
        }

    def create_session(self, user_id: str = None, project_id: str = None) -> str:
        """Create a new session with brain-enhanced tracking."""
        if not self.session_memory:
            return "session_disabled"

        session_id = self.session_memory.create_session(
            user_id=user_id, project_id=project_id
        )

        # Log session creation experience
        if self.experience_logger:
            self.experience_logger.log_experience(
                task_description=f"Created new session for user {user_id}",
                task_type="session_management",
                solution_source="new_creation",
                outcome="success",
                primary_emotion="satisfaction",
                emotional_weight=0.6,
                project_id=project_id,
                session_id=session_id,
            )

        return session_id

    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data with brain-enhanced context."""
        if not self.session_memory:
            return {"error": "Session memory is disabled"}

        session_data = self.session_memory.get_session(session_id)
        if not session_data:
            return {"error": "Session not found or expired"}

        # Get emotional context for the session
        emotional_context = {}
        if self.experience_logger:
            emotional_summary = self.experience_logger.get_emotional_summary(
                project_id=session_data.project_id
            )
            emotional_context = emotional_summary

        return {
            "session_id": session_id,
            "user_id": session_data.user_id,
            "project_id": session_data.project_id,
            "created_at": session_data.created_at.isoformat(),
            "last_accessed": session_data.last_accessed.isoformat(),
            "expires_at": session_data.expires_at.isoformat()
            if session_data.expires_at
            else None,
            "active_files_count": len(session_data.active_files),
            "recent_commands_count": len(session_data.recent_commands),
            "auth_services": list(session_data.auth_tokens.keys()),
            "api_services": list(session_data.api_keys.keys()),
            "emotional_context": emotional_context,
        }

    async def search_memories_with_brain(
        self,
        query: str,
        project_id: str = None,
        search_tags: List[str] = None,
        goal_type: str = None,
        max_results: int = 20,
    ) -> Dict[str, Any]:
        """Search memories using brain-enhanced query engine."""
        if not self.memory_query_engine:
            return {"error": "Memory query engine is disabled"}

        try:
            # Perform brain-enhanced search
            results = self.memory_query_engine.query_memories(
                query=query,
                project_id=project_id,
                search_tags=search_tags,
                goal_type=goal_type,
                max_results=max_results,
            )

            # Get emotional context for results
            emotional_context = {}
            if self.emotional_learning:
                learning_insights = self.emotional_learning.get_learning_insights()
                emotional_context = learning_insights

            return {
                "query": query,
                "results_count": len(results),
                "results": [result.to_dict() for result in results],
                "emotional_context": emotional_context,
                "query_statistics": self.memory_query_engine.get_query_statistics(),
            }

        except Exception as e:
            self.logger.error(f"Error searching memories with brain: {e}")
            return {"error": str(e)}

    def get_emotional_learning_summary(self) -> str:
        """Get emotional learning summary."""
        if not self.emotional_learning:
            return "Emotional learning is disabled"

        return self.emotional_learning.get_emotional_learning_summary()

    def get_cognitive_summary(self) -> str:
        """Get cognitive loop summary."""
        if not self.cognitive_loop:
            return "Cognitive loop is disabled"

        return self.cognitive_loop.get_cognitive_summary()

    def get_experience_summary(self, project_id: str = None) -> Dict[str, Any]:
        """Get experience logging summary."""
        if not self.experience_logger:
            return {"error": "Experience logger is disabled"}

        return {
            "emotional_summary": self.experience_logger.get_emotional_summary(
                project_id=project_id
            ),
            "learning_patterns": self.experience_logger.get_learning_patterns(
                project_id=project_id
            ),
            "experience_statistics": self.experience_logger.get_experience_statistics(
                project_id=project_id
            ),
        }

    async def add_emotional_tag(
        self, memory_id: str, emotion_type: str, intensity: float, context: str = ""
    ) -> bool:
        """Add emotional tag to a memory."""
        if not self.emotional_learning:
            return False

        return self.emotional_learning.add_emotional_tag(
            memory_id=memory_id,
            emotion_type=emotion_type,
            intensity=intensity,
            context=context,
        )

    def get_joyful_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories with joyful emotional tags."""
        if not self.emotional_learning:
            return []

        memories = self.emotional_learning.get_joyful_memories(limit=limit)
        return [memory.to_dict() for memory in memories]

    def update_emotional_state(self, **emotions):
        """Update the agent's emotional state."""
        if not self.identity_memory:
            return False

        self.identity_memory.update_emotional_state(**emotions)
        return True

    def get_brain_enhancement_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all brain enhancement modules."""
        status = {
            "enabled": self.enable_all_features,
            "modules": {
                "identity_memory": self.identity_memory is not None,
                "session_memory": self.session_memory is not None,
                "experience_logger": self.experience_logger is not None,
                "memory_query_engine": self.memory_query_engine is not None,
                "emotional_learning": self.emotional_learning is not None,
                "cognitive_loop": self.cognitive_loop is not None,
            },
        }

        if self.enable_all_features:
            # Add detailed status for each module
            if self.identity_memory:
                status["identity"] = self.get_identity_summary()

            if self.cognitive_loop:
                status["cognitive"] = self.cognitive_loop.get_cognitive_statistics()

            if self.memory_query_engine:
                status["query_engine"] = self.memory_query_engine.get_query_statistics()

            if self.emotional_learning:
                status[
                    "emotional_learning"
                ] = self.emotional_learning.get_learning_insights()

        return status

    async def run_brain_maintenance(self):
        """Run maintenance tasks for brain enhancement modules."""
        if not self.enable_all_features:
            return

        self.logger.info("Running brain enhancement maintenance...")

        try:
            # Clean up expired sessions
            if self.session_memory:
                self.session_memory.cleanup_expired_sessions()

            # Clear query cache if needed
            if self.memory_query_engine:
                # Only clear cache if it's getting too large
                cache_size = len(self.memory_query_engine.query_cache)
                if cache_size > 100:
                    self.memory_query_engine.clear_cache()
                    self.logger.info("Cleared memory query cache")

            # Preload frequent queries
            if self.memory_query_engine:
                self.memory_query_engine.preload_frequent_queries()

            self.logger.info("Brain enhancement maintenance completed")

        except Exception as e:
            self.logger.error(f"Error during brain maintenance: {e}")

    def get_brain_enhancement_tools(self) -> List[Dict[str, Any]]:
        """Get tools list with brain enhancement capabilities."""
        if not self.enable_all_features:
            return []

        tools = [
            {
                "name": "get_brain_status",
                "description": "Get comprehensive status of brain enhancement modules",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "process_task_with_brain",
                "description": "Process a task using the complete brain-like system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task to process",
                        },
                        "task_type": {
                            "type": "string",
                            "description": "Type of task (general, learning, debugging, etc.)",
                        },
                        "priority": {
                            "type": "number",
                            "description": "Task priority (0.0 to 1.0)",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["task_description"],
                },
            },
            {
                "name": "get_identity_summary",
                "description": "Get current identity and emotional state summary",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "search_memories_with_brain",
                "description": "Search memories using brain-enhanced query engine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                        "search_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags to search for",
                        },
                        "goal_type": {
                            "type": "string",
                            "description": "Type of goal (debugging, optimization, learning, etc.)",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_emotional_learning_summary",
                "description": "Get emotional learning summary",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_cognitive_summary",
                "description": "Get cognitive loop summary",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "add_emotional_tag",
                "description": "Add emotional tag to a memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "Memory identifier",
                        },
                        "emotion_type": {
                            "type": "string",
                            "description": "Type of emotion",
                        },
                        "intensity": {
                            "type": "number",
                            "description": "Emotional intensity (0.0 to 1.0)",
                        },
                        "context": {
                            "type": "string",
                            "description": "Context for the emotional tag",
                        },
                    },
                    "required": ["memory_id", "emotion_type", "intensity"],
                },
            },
            {
                "name": "get_joyful_memories",
                "description": "Get memories with joyful emotional tags",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of memories to return",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "update_emotional_state",
                "description": "Update the agent's emotional state",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "joy": {"type": "number"},
                        "confidence": {"type": "number"},
                        "frustration": {"type": "number"},
                        "excitement": {"type": "number"},
                        "energy_level": {"type": "number"},
                        "focus_level": {"type": "number"},
                    },
                    "required": [],
                },
            },
        ]

        return tools

    async def execute_brain_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute brain enhancement tools."""
        try:
            # Strip the MCP prefix if present
            if tool_name.startswith("mcp_brain-enhanced-mcp_"):
                tool_name = tool_name[len("mcp_brain-enhanced-mcp_") :]

            if tool_name == "get_brain_status":
                return self.get_brain_enhancement_status()

            elif tool_name == "process_task_with_brain":
                return await self.process_task_with_brain(
                    task_description=arguments["task_description"],
                    task_type=arguments.get("task_type", "general"),
                    priority=arguments.get("priority", 0.5),
                    project_id=arguments.get("project_id"),
                    session_id=arguments.get("session_id"),
                )

            elif tool_name == "get_identity_summary":
                return self.get_identity_summary()

            elif tool_name == "search_memories_with_brain":
                return await self.search_memories_with_brain(
                    query=arguments["query"],
                    project_id=arguments.get("project_id"),
                    search_tags=arguments.get("search_tags"),
                    goal_type=arguments.get("goal_type"),
                    max_results=arguments.get("max_results", 20),
                )

            elif tool_name == "get_emotional_learning_summary":
                return {"summary": self.get_emotional_learning_summary()}

            elif tool_name == "get_cognitive_summary":
                return {"summary": self.get_cognitive_summary()}

            elif tool_name == "add_emotional_tag":
                success = await self.add_emotional_tag(
                    memory_id=arguments["memory_id"],
                    emotion_type=arguments["emotion_type"],
                    intensity=arguments["intensity"],
                    context=arguments.get("context", ""),
                )
                return {"success": success}

            elif tool_name == "get_joyful_memories":
                memories = self.get_joyful_memories(limit=arguments.get("limit", 10))
                return {"memories": memories}

            elif tool_name == "update_emotional_state":
                success = self.update_emotional_state(**arguments)
                return {"success": success}

            else:
                return {"error": f"Unknown brain tool: {tool_name}"}

        except Exception as e:
            self.logger.error(f"Error executing brain tool {tool_name}: {e}")
            return {"error": str(e)}

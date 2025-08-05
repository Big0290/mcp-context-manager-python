#!/usr/bin/env python3
"""
Conversation Recording Plugin for Extensible MCP Server
Adds automatic conversation tracking and memory creation.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.extensible_mcp_server import MCPPlugin, PluginMetadata


class ConversationRecordingPlugin(MCPPlugin):
    """Plugin that adds conversation recording functionality."""

    def __init__(self, server_instance=None):
        super().__init__(server_instance)
        self.conversation_buffer = []
        self.last_user_message = ""
        self.last_ai_response = ""
        self.conversation_start_time = None
        self.project_id = "workspace"
        self.auto_record_user = True
        self.auto_record_ai = True
        self.logger = logging.getLogger(__name__)

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="conversation_recording",
            version="1.0.0",
            description="Automatic conversation recording and memory creation",
            author="MCP Team",
            tags=["conversation", "memory", "recording"],
            priority=10,  # High priority to ensure it loads early
        )

    async def initialize(self) -> bool:
        """Initialize the conversation recording plugin."""
        try:
            self.conversation_start_time = datetime.now()
            self.logger.info("Conversation recording plugin initialized")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to initialize conversation recording plugin: {e}"
            )
            return False

    async def shutdown(self) -> bool:
        """Shutdown the conversation recording plugin."""
        try:
            await self.end_conversation()
            self.logger.info("Conversation recording plugin shutdown")
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down conversation recording plugin: {e}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools provided by this plugin."""
        return [
            {
                "name": "start_conversation_recording",
                "description": "Start automatic conversation recording for a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier for conversation tracking",
                        },
                        "auto_record_user_messages": {
                            "type": "boolean",
                            "description": "Automatically record user messages",
                        },
                        "auto_record_ai_responses": {
                            "type": "boolean",
                            "description": "Automatically record AI responses",
                        },
                    },
                },
            },
            {
                "name": "stop_conversation_recording",
                "description": "Stop automatic conversation recording and create summary",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        }
                    },
                },
            },
        ]

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute conversation recording tools."""
        if tool_name == "start_conversation_recording":
            return await self._start_conversation_recording(arguments)
        elif tool_name == "stop_conversation_recording":
            return await self._stop_conversation_recording(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def _start_conversation_recording(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start automatic conversation recording."""
        try:
            project_id = args.get("project_id", "workspace")
            auto_record_user = args.get("auto_record_user_messages", True)
            auto_record_ai = args.get("auto_record_ai_responses", True)

            # Start conversation recording
            self.start_conversation(project_id)
            self.auto_record_user = auto_record_user
            self.auto_record_ai = auto_record_ai

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ Automatic conversation recording started for project: {project_id}\n"
                        f"User message recording: {'Enabled' if auto_record_user else 'Disabled'}\n"
                        f"AI response recording: {'Enabled' if auto_record_ai else 'Disabled'}",
                    }
                ],
                "isError": False,
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error starting conversation recording: {str(e)}",
                    }
                ],
                "isError": True,
            }

    async def _stop_conversation_recording(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stop automatic conversation recording."""
        try:
            project_id = args.get("project_id", "workspace")

            # End conversation and create summary
            await self.end_conversation()

            # Get conversation statistics
            buffer_size = len(self.conversation_buffer)
            user_messages = len(
                [msg for msg in self.conversation_buffer if msg["type"] == "user"]
            )
            ai_responses = len(
                [msg for msg in self.conversation_buffer if msg["type"] == "ai"]
            )

            summary_text = (
                f"✅ Conversation recording stopped for project: {project_id}\n"
                f"📊 Conversation Statistics:\n"
                f"  • Total interactions: {buffer_size}\n"
                f"  • User messages: {user_messages}\n"
                f"  • AI responses: {ai_responses}\n"
                f"  • Conversation summary created and stored"
            )

            return {
                "content": [{"type": "text", "text": summary_text}],
                "isError": False,
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error stopping conversation recording: {str(e)}",
                    }
                ],
                "isError": True,
            }

    def start_conversation(self, project_id: str = "workspace"):
        """Start tracking a new conversation."""
        self.conversation_start_time = datetime.now()
        self.project_id = project_id
        self.conversation_buffer = []
        self.logger.info(f"Started conversation tracking for project: {project_id}")

    def record_user_message(self, message: str):
        """Record a user message for automatic memory creation."""
        self.last_user_message = message.strip()
        self.conversation_buffer.append(
            {
                "type": "user",
                "content": self.last_user_message,
                "timestamp": datetime.now(),
            }
        )

        # Auto-create memory for significant user messages if enabled
        if self.auto_record_user and self._is_significant_message(message):
            asyncio.create_task(self._auto_record_memory("user_message", message))

    def record_ai_response(self, response: str):
        """Record an AI response for automatic memory creation."""
        self.last_ai_response = response.strip()
        self.conversation_buffer.append(
            {
                "type": "ai",
                "content": self.last_ai_response,
                "timestamp": datetime.now(),
            }
        )

        # Auto-create memory for significant AI responses if enabled
        if self.auto_record_ai and self._is_significant_response(response):
            asyncio.create_task(self._auto_record_memory("ai_response", response))

    def _is_significant_message(self, message: str) -> bool:
        """Determine if a user message is significant enough to record."""
        # Skip very short messages
        if len(message.strip()) < 10:
            return False

        # Skip simple greetings
        greetings = ["hello", "hi", "hey", "thanks", "thank you", "ok", "okay"]
        if message.lower().strip() in greetings:
            return False

        # Skip simple confirmations
        confirmations = ["yes", "no", "yep", "nope", "sure", "ok", "okay"]
        if message.lower().strip() in confirmations:
            return False

        return True

    def _is_significant_response(self, response: str) -> bool:
        """Determine if an AI response is significant enough to record."""
        # Skip very short responses
        if len(response.strip()) < 20:
            return False

        # Skip simple acknowledgments
        acknowledgments = ["ok", "okay", "got it", "understood", "sure"]
        if response.lower().strip() in acknowledgments:
            return False

        return True

    async def _auto_record_memory(self, interaction_type: str, content: str):
        """Automatically record a memory entry."""
        try:
            # Determine memory type and priority based on content
            memory_type = self._determine_memory_type(content)
            priority = self._determine_priority(content)
            tags = self._extract_tags(content)

            # Create memory entry
            memory_args = {
                "content": f"[{interaction_type.upper()}] {content}",
                "memory_type": memory_type,
                "priority": priority,
                "tags": tags,
                "project_id": self.project_id,
            }

            # Use the server's memory system to store the memory
            if self.server and hasattr(self.server, "brain_integration"):
                # Try to use brain integration if available
                result = await self.server.brain_integration.execute_brain_tool(
                    "push_memory", memory_args
                )
                if not result.get("isError", True):
                    self.logger.info(
                        f"Auto-recorded memory: {memory_type} - {content[:50]}..."
                    )
                else:
                    self.logger.warning(f"Failed to auto-record memory: {result}")

        except Exception as e:
            self.logger.error(f"Error auto-recording memory: {e}")

    def _determine_memory_type(self, content: str) -> str:
        """Determine the appropriate memory type based on content."""
        content_lower = content.lower()

        # Check for task-related content
        task_keywords = [
            "implement",
            "create",
            "build",
            "fix",
            "debug",
            "add",
            "remove",
            "update",
        ]
        if any(keyword in content_lower for keyword in task_keywords):
            return "task"

        # Check for question content
        question_keywords = ["how", "what", "why", "when", "where", "?"]
        if any(keyword in content_lower for keyword in question_keywords):
            return "question"

        # Check for feedback content
        feedback_keywords = [
            "good",
            "bad",
            "great",
            "terrible",
            "like",
            "dislike",
            "thanks",
        ]
        if any(keyword in content_lower for keyword in feedback_keywords):
            return "feedback"

        # Check for configuration content
        config_keywords = ["config", "setup", "install", "configure", "settings"]
        if any(keyword in content_lower for keyword in config_keywords):
            return "configuration"

        return "general"

    def _determine_priority(self, content: str) -> str:
        """Determine the priority level based on content."""
        content_lower = content.lower()

        # High priority keywords
        high_priority = [
            "urgent",
            "critical",
            "important",
            "fix",
            "error",
            "bug",
            "broken",
        ]
        if any(keyword in content_lower for keyword in high_priority):
            return "high"

        # Medium priority keywords
        medium_priority = ["implement", "create", "build", "add", "update", "improve"]
        if any(keyword in content_lower for keyword in medium_priority):
            return "medium"

        return "low"

    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content."""
        tags = []
        content_lower = content.lower()

        # Technology tags
        tech_keywords = {
            "python": ["python", "py", "pip", "venv"],
            "javascript": ["javascript", "js", "node", "npm"],
            "typescript": ["typescript", "ts"],
            "react": ["react", "jsx"],
            "vue": ["vue"],
            "angular": ["angular"],
            "docker": ["docker", "container"],
            "kubernetes": ["kubernetes", "k8s"],
            "aws": ["aws", "amazon", "lambda", "s3"],
            "azure": ["azure", "microsoft"],
            "gcp": ["gcp", "google", "cloud"],
            "database": ["database", "db", "sql", "mysql", "postgresql", "mongodb"],
            "api": ["api", "rest", "graphql"],
            "testing": ["test", "testing", "unit", "integration"],
            "ci_cd": ["ci", "cd", "pipeline", "jenkins", "github actions"],
        }

        for tag, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)

        return tags

    async def end_conversation(self):
        """End conversation and create summary."""
        if not self.conversation_buffer:
            return

        try:
            # Create conversation summary
            summary = self._create_conversation_summary()

            # Store conversation summary as memory
            summary_memory = {
                "content": f"Conversation Summary: {summary}",
                "memory_type": "conversation_summary",
                "priority": "medium",
                "tags": ["conversation", "summary", self.project_id],
                "project_id": self.project_id,
            }

            # Store the summary using the server's memory system
            if self.server and hasattr(self.server, "brain_integration"):
                await self.server.brain_integration.execute_brain_tool(
                    "push_memory", summary_memory
                )

            self.logger.info(
                f"Conversation ended. Summary created for project: {self.project_id}"
            )

        except Exception as e:
            self.logger.error(f"Error ending conversation: {e}")

    def _create_conversation_summary(self) -> str:
        """Create a summary of the conversation."""
        if not self.conversation_buffer:
            return "No conversation recorded."

        user_messages = [
            msg for msg in self.conversation_buffer if msg["type"] == "user"
        ]
        ai_responses = [msg for msg in self.conversation_buffer if msg["type"] == "ai"]

        summary = f"Conversation with {len(user_messages)} user messages and {len(ai_responses)} AI responses. "

        if user_messages:
            # Extract key topics from user messages
            topics = []
            for msg in user_messages[-3:]:  # Last 3 user messages
                content = msg["content"].lower()
                if "name" in content:
                    topics.append("identity/name")
                if "memory" in content or "remember" in content:
                    topics.append("memory")
                if "conversation" in content or "recording" in content:
                    topics.append("conversation_recording")
                if "tool" in content or "function" in content:
                    topics.append("tools")
                if "project" in content or "code" in content:
                    topics.append("project")

            if topics:
                summary += f"Key topics: {', '.join(set(topics))}. "

        return summary

    async def on_tool_executed(
        self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]
    ):
        """Hook called when a tool is executed."""
        # Record user intent based on tool calls
        if tool_name == "push_memory":
            content = arguments.get("content", "")
            if content:
                self.record_user_message(f"User added memory: {content}")
        elif tool_name == "fetch_memory":
            self.record_user_message("User requested memory retrieval")
        elif tool_name == "get_context_summary":
            self.record_user_message("User requested context summary")
        elif tool_name == "get_agent_stats":
            self.record_user_message("User requested agent statistics")
        elif tool_name == "craft_ai_prompt":
            self.record_user_message("User requested AI prompt crafting")
        else:
            # Record generic tool call as user interaction
            self.record_user_message(f"User called tool: {tool_name}")

        # Record AI response based on tool results
        if result and not result.get("isError", True):
            content = result.get("content", [{}])[0].get("text", "")
            if content:
                self.record_ai_response(f"AI provided response: {content}")

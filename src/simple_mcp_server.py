#!/usr/bin/env python3
"""
Simplified MCP Server for testing stdin/stdout communication
Follows MCP specifications without complex dependencies
"""

import asyncio
import json
import sys
import time
import sqlite3
import os
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from src.performance_monitor import PerformanceMonitor, ContextInjectionMonitor
from src.ai_prompt_crafter import AIPromptCrafter, PromptContext, PromptType
from src.project_detector import get_project_id_from_env, sanitize_project_name


class ConversationRecorder:
    """Automatically records conversation interactions for memory storage."""
    
    def __init__(self, memory_server):
        self.memory_server = memory_server
        self.conversation_buffer = []
        self.last_user_message = ""
        self.last_ai_response = ""
        self.conversation_start_time = None
        # Detect project ID dynamically
        detected_project = get_project_id_from_env()
        self.project_id = sanitize_project_name(detected_project)
        self.auto_record_user = True
        self.auto_record_ai = True
        
    def start_conversation(self, project_id: str = "workspace"):
        """Start tracking a new conversation."""
        self.conversation_start_time = datetime.now()
        self.project_id = project_id
        self.conversation_buffer = []
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Started conversation tracking for project: {project_id}")
    
    def record_user_message(self, message: str):
        """Record a user message for automatic memory creation."""
        self.last_user_message = message.strip()
        self.conversation_buffer.append({
            "type": "user",
            "content": self.last_user_message,
            "timestamp": datetime.now()
        })
        
        # Auto-create memory for significant user messages if enabled
        if self.auto_record_user and self._is_significant_message(message):
            asyncio.create_task(self._auto_record_memory("user_message", message))
    
    def record_ai_response(self, response: str):
        """Record an AI response for automatic memory creation."""
        self.last_ai_response = response.strip()
        self.conversation_buffer.append({
            "type": "ai",
            "content": self.last_ai_response,
            "timestamp": datetime.now()
        })
        
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
                "project_id": self.project_id
            }
            
            # Use the memory server to store the memory
            result = await self.memory_server._push_memory(memory_args)
            
            if not result.get("isError", True):
                self.logger.info(f"Auto-recorded memory: {memory_type} - {content[:50]}...")
            else:
                self.logger.warning(f"Failed to auto-record memory: {result}")
                
        except Exception as e:
            self.logger.error(f"Error auto-recording memory: {e}")
    
    def _determine_memory_type(self, content: str) -> str:
        """Determine the appropriate memory type based on content."""
        content_lower = content.lower()
        
        # Check for task-related content
        task_keywords = ["implement", "create", "build", "add", "fix", "update", "refactor", "write", "code"]
        if any(keyword in content_lower for keyword in task_keywords):
            return "task"
        
        # Check for preference-related content
        preference_keywords = ["prefer", "like", "want", "need", "should", "must", "always", "never"]
        if any(keyword in content_lower for keyword in preference_keywords):
            return "preference"
        
        # Check for fact-related content
        fact_keywords = ["is", "are", "was", "were", "has", "have", "does", "do", "explain", "describe"]
        if any(keyword in content_lower for keyword in fact_keywords):
            return "fact"
        
        # Default to thread for ongoing conversations
        return "thread"
    
    def _determine_priority(self, content: str) -> str:
        """Determine the priority based on content analysis."""
        content_lower = content.lower()
        
        # High priority keywords
        high_priority = ["urgent", "critical", "important", "must", "need", "error", "bug", "fix", "broken"]
        if any(keyword in content_lower for keyword in high_priority):
            return "high"
        
        # Medium priority keywords
        medium_priority = ["should", "would", "could", "implement", "create", "add", "update"]
        if any(keyword in content_lower for keyword in medium_priority):
            return "medium"
        
        # Default to low priority
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
            "react": ["react", "jsx", "tsx"],
            "mcp": ["mcp", "memory", "context"],
            "database": ["database", "sql", "sqlite", "postgres", "mysql"],
            "api": ["api", "rest", "http", "endpoint"],
            "testing": ["test", "testing", "unit", "integration"],
            "deployment": ["deploy", "docker", "kubernetes", "aws", "azure"]
        }
        
        for tag, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        # Add conversation tags
        if "?" in content:
            tags.append("question")
        if "!" in content:
            tags.append("exclamation")
        if len(content.split()) > 20:
            tags.append("detailed")
        
        return tags
    
    def end_conversation(self):
        """End the current conversation and create a summary memory."""
        if self.conversation_buffer:
            # Create a summary of the conversation
            summary = self._create_conversation_summary()
            asyncio.create_task(self._auto_record_memory("conversation_summary", summary))
            
            self.logger.info(f"Ended conversation tracking. Summary created.")
    
    def _create_conversation_summary(self) -> str:
        """Create a summary of the conversation."""
        if not self.conversation_buffer:
            return "Empty conversation"
        
        user_messages = [msg["content"] for msg in self.conversation_buffer if msg["type"] == "user"]
        ai_responses = [msg["content"] for msg in self.conversation_buffer if msg["type"] == "ai"]
        
        summary_parts = []
        
        if user_messages:
            summary_parts.append(f"User messages: {len(user_messages)}")
            # Include the most significant user message
            longest_user_msg = max(user_messages, key=len)
            summary_parts.append(f"Key user input: {longest_user_msg[:100]}...")
        
        if ai_responses:
            summary_parts.append(f"AI responses: {len(ai_responses)}")
            # Include the most significant AI response
            longest_ai_msg = max(ai_responses, key=len)
            summary_parts.append(f"Key AI output: {longest_ai_msg[:100]}...")
        
        return " | ".join(summary_parts)


class SimpleMCPServer:
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Initialize SQLite database for persistent storage
        self.db_path = Config.SIMPLE_DB_PATH
        self.init_database()
        
        # Initialize performance monitoring
        if Config.ENABLE_PERFORMANCE_MONITORING:
            self.performance_monitor = PerformanceMonitor(Config.PERFORMANCE_DB_PATH)
            self.context_monitor = ContextInjectionMonitor(self.performance_monitor)
            self.performance_monitor.start_monitoring()
        else:
            self.performance_monitor = None
            self.context_monitor = None
        
        # Get detected project ID
        detected_project = get_project_id_from_env()
        self.project_id = sanitize_project_name(detected_project)
        
        # Initialize conversation recorder
        self.conversation_recorder = ConversationRecorder(self)
        self.conversation_recorder.start_conversation(self.project_id)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Simple MCP Server initialized for project: {self.project_id}")
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'fact',
                priority TEXT DEFAULT 'medium',
                tags TEXT,  -- JSON string
                project_id TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                agent_type TEXT DEFAULT 'chatbot',
                project_id TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_db_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for MCP protocol."""
        return [
            {
                "name": "push_memory",
                "description": "Push a memory entry to the server",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The memory content to store"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["fact", "preference", "task", "thread"],
                            "description": "Type of memory entry"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Priority level of the memory"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorization"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "fetch_memory",
                "description": "Fetch memories based on search criteria",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for semantic search"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["fact", "preference", "task", "thread"],
                            "description": "Filter by memory type"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        }
                    }
                }
            },
            {
                "name": "get_agent_stats",
                "description": "Get statistics for an agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent identifier"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "register_agent",
                "description": "Register a new agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Agent name"
                        },
                        "agent_type": {
                            "type": "string",
                            "enum": ["chatbot", "cli", "web", "mobile", "other"],
                            "description": "Type of agent"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_context_summary",
                "description": "Generate a context summary for chat session injection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier to summarize context for"
                        },
                        "max_memories": {
                            "type": "integer",
                            "description": "Maximum number of memories to include in summary"
                        },
                        "include_recent": {
                            "type": "boolean",
                            "description": "Include recent memories in summary"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to focus on in summary"
                        }
                    }
                }
            },
            {
                "name": "auto_inject_context",
                "description": "Automatically inject context for new conversation sessions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (auto-detected if not provided)"
                        },
                        "max_memories": {
                            "type": "integer",
                            "description": "Maximum number of memories to include"
                        },
                        "include_recent": {
                            "type": "boolean",
                            "description": "Include recent memories"
                        },
                        "use_ai_crafting": {
                            "type": "boolean",
                            "description": "Use AI prompt crafting for intelligent context"
                        },
                        "show_notification": {
                            "type": "boolean",
                            "description": "Show injection notification"
                        }
                    }
                }
            },
            {
                "name": "start_conversation_recording",
                "description": "Start automatic conversation recording for a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier to record conversations for"
                        },
                        "auto_record_user_messages": {
                            "type": "boolean",
                            "description": "Automatically record user messages"
                        },
                        "auto_record_ai_responses": {
                            "type": "boolean",
                            "description": "Automatically record AI responses"
                        }
                    }
                }
            },
            {
                "name": "stop_conversation_recording",
                "description": "Stop automatic conversation recording and create summary",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        }
                    }
                }
            },
            {
                "name": "get_performance_report",
                "description": "Get performance metrics and recommendations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze (default: 7)"
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "description": "Include AI recommendations (default: true)"
                        }
                    }
                }
            },
            {
                "name": "record_feedback",
                "description": "Record user feedback about context injection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rating": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                            "description": "User rating (1-5)"
                        },
                        "comment": {
                            "type": "string",
                            "description": "Optional feedback comment"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        },
                        "context_summary": {
                            "type": "string",
                            "description": "Context summary that was provided"
                        }
                    },
                    "required": ["rating"]
                }
            },
            {
                "name": "craft_ai_prompt",
                "description": "Craft an intelligent AI prompt using context summary and user input",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier"
                        },
                        "user_message": {
                            "type": "string",
                            "description": "User message to incorporate into the prompt"
                        },
                        "prompt_type": {
                            "type": "string",
                            "enum": ["continuation", "task_focused", "problem_solving", "explanation", "code_review", "debugging", "general"],
                            "description": "Type of prompt to craft"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to focus on"
                        }
                    },
                    "required": ["project_id"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        start_time = time.time()
        
        try:
            if tool_name == "push_memory":
                result = await self._push_memory(arguments)
            elif tool_name == "fetch_memory":
                result = await self._fetch_memory(arguments)
            elif tool_name == "get_agent_stats":
                result = await self._get_agent_stats(arguments)
            elif tool_name == "register_agent":
                result = await self._register_agent(arguments)
            elif tool_name == "get_context_summary":
                result = await self._get_context_summary(arguments)
            elif tool_name == "get_performance_report":
                result = await self._get_performance_report(arguments)
            elif tool_name == "record_feedback":
                result = await self._record_feedback(arguments)
            elif tool_name == "start_conversation_recording":
                result = await self._start_conversation_recording(arguments)
            elif tool_name == "stop_conversation_recording":
                result = await self._stop_conversation_recording(arguments)
            elif tool_name == "craft_ai_prompt":
                result = await self._craft_ai_prompt(arguments)
            elif tool_name == "auto_inject_context":
                result = await self._auto_inject_context(arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            # Track performance if monitoring is enabled
            if self.context_monitor:
                duration_ms = (time.time() - start_time) * 1000
                project_id = arguments.get("project_id", "unknown")
                
                if tool_name == "get_context_summary":
                    context_length = len(result.get("content", [{}])[0].get("text", ""))
                    self.context_monitor.track_context_injection(
                        project_id=project_id,
                        context_length=context_length,
                        duration_ms=duration_ms,
                        success=not result.get("isError", False),
                        manual_trigger=arguments.get("manual_trigger", False)
                    )
                else:
                    self.context_monitor.track_memory_operation(
                        operation_type=tool_name,
                        project_id=project_id,
                        duration_ms=duration_ms,
                        success=not result.get("isError", False)
                    )
            
            return result
        except Exception as e:
            if self.context_monitor:
                duration_ms = (time.time() - start_time) * 1000
                self.context_monitor.track_memory_operation(
                    operation_type=tool_name,
                    project_id=arguments.get("project_id", "unknown"),
                    duration_ms=duration_ms,
                    success=False
                )
            return {"error": str(e)}
    
    async def _push_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Push a memory entry."""
        content = args.get("content", "")
        memory_type = args.get("memory_type", "fact")
        priority = args.get("priority", "medium")
        tags = args.get("tags", [])
        project_id = args.get("project_id", "default")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO memories (content, memory_type, priority, tags, project_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (content, memory_type, priority, json.dumps(tags), project_id))
            conn.commit()
            
            memory_id = cursor.lastrowid
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Memory stored successfully with ID: {memory_id}"
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            conn.rollback()
            return {"error": f"Error storing memory: {e}"}
        finally:
            conn.close()
    
    async def _fetch_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch memories based on criteria."""
        query = args.get("query", "")
        tags = args.get("tags", [])
        memory_type = args.get("memory_type")
        limit = args.get("limit", 10)
        project_id = args.get("project_id", "default")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Construct SQL query
            sql_query = "SELECT id, content, memory_type, priority, tags, project_id, created_at FROM memories WHERE project_id = ?"
            params = [project_id]
            
            if memory_type:
                sql_query += " AND memory_type = ?"
                params.append(memory_type)
            
            if tags:
                sql_query += " AND tags LIKE ?"
                params.append(f"%{json.dumps(tags)[1:-1]}%") # Escape JSON tags for LIKE
            
            if query:
                sql_query += " AND content LIKE ?"
                params.append(f"%{query}%")
            
            sql_query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql_query, params)
            memories = cursor.fetchall()
            
            results = []
            for memory in memories:
                memory_dict = {
                    "id": memory[0],
                    "content": memory[1],
                    "memory_type": memory[2],
                    "priority": memory[3],
                    "tags": json.loads(memory[4]),
                    "project_id": memory[5],
                    "created_at": memory[6]
                }
                results.append(memory_dict)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Found {len(results)} memories:\n" + 
                               json.dumps(results, indent=2)
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            return {"error": f"Error fetching memories: {e}"}
        finally:
            conn.close()
    
    async def _get_agent_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent statistics."""
        agent_id = args.get("agent_id", "cursor-agent")
        project_id = args.get("project_id", "default")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM agents WHERE project_id = ?
            ''', (project_id,))
            total_agents = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT memory_type, COUNT(*) FROM memories WHERE project_id = ? GROUP BY memory_type
            ''', (project_id,))
            memory_types = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Agent Statistics:\n" +
                               f"Total memories: {total_agents}\n" +
                               f"Memory types: {memory_types}\n" +
                               f"Agent ID: {agent_id}"
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            return {"error": f"Error getting agent stats: {e}"}
        finally:
            conn.close()
    
    async def _register_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent."""
        name = args.get("name", "Test Agent")
        agent_type = args.get("agent_type", "other")
        project_id = args.get("project_id", "default")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO agents (name, agent_type, project_id)
                VALUES (?, ?, ?)
            ''', (name, agent_type, project_id))
            conn.commit()
            
            agent_id = cursor.lastrowid
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Agent registered successfully with ID: {agent_id}"
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            conn.rollback()
            return {"error": f"Error registering agent: {e}"}
        finally:
            conn.close()
    
    async def _get_context_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a context summary for chat session injection."""
        project_id = args.get("project_id", "default")
        max_memories = args.get("max_memories", 10)
        include_recent = args.get("include_recent", True)
        focus_areas = args.get("focus_areas", [])
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get all memories for the project
            cursor.execute('''
                SELECT id, content, memory_type, priority, tags, project_id, created_at FROM memories
                WHERE project_id = ? ORDER BY created_at DESC
            ''', (project_id,))
            project_memories = cursor.fetchall()
            
            if not project_memories:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No previous context found for this project. Starting fresh conversation."
                        }
                    ],
                    "isError": False
                }
            
            # Sort by creation time (most recent first)
            project_memories.sort(key=lambda x: x[6], reverse=True) # Sort by created_at
            
            # Filter by focus areas if specified
            if focus_areas:
                filtered_memories = []
                for memory in project_memories:
                    memory_tags = json.loads(memory[4]) # tags is JSON string
                    if any(area.lower() in [tag.lower() for tag in memory_tags] for area in focus_areas):
                        filtered_memories.append(memory)
                project_memories = filtered_memories
            
            # Limit to max_memories
            project_memories = project_memories[:max_memories]
            
            # Generate summary
            summary_parts = []
            summary_parts.append(f"📋 **Context Summary for Project: {project_id}**")
            summary_parts.append(f"Found {len(project_memories)} relevant memories:")
            summary_parts.append("")
            
            # Group by memory type
            by_type = {}
            for memory in project_memories:
                mem_type = memory[2] # memory_type
                if mem_type not in by_type:
                    by_type[mem_type] = []
                by_type[mem_type].append(memory)
            
            # Add each type to summary
            for mem_type, memories in by_type.items():
                summary_parts.append(f"**{mem_type.title()}s:**")
                for memory in memories:
                    priority = memory[3] # priority
                    tags = json.loads(memory[4]) # tags
                    content = memory[1] # content
                    
                    # Truncate content if too long
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    summary_parts.append(f"• [{priority.upper()}] {content}")
                    if tags:
                        summary_parts.append(f"  Tags: {', '.join(tags)}")
                summary_parts.append("")
            
            # Add key insights
            if project_memories:
                high_priority = [m for m in project_memories if m[3] == "high"] # priority
                if high_priority:
                    summary_parts.append("**🎯 Key Priorities:**")
                    for memory in high_priority[:3]:
                        summary_parts.append(f"• {memory[1][:150]}...") # content
                    summary_parts.append("")
            
            summary_text = "\n".join(summary_parts)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": summary_text
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            return {"error": f"Error generating context summary: {e}"}
        finally:
            conn.close()
    
    async def _get_performance_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics and recommendations."""
        days = args.get("days", 7)
        include_recommendations = args.get("include_recommendations", True)
        
        try:
            report = self.performance_monitor.get_performance_report(days=days)
            
            # Format the report
            report_text = f"📊 **Performance Report (Last {days} days)**\n\n"
            
            # Overall stats
            stats = report["overall_stats"]
            report_text += f"**Overall Statistics:**\n"
            report_text += f"• Total Events: {stats['total_events']}\n"
            report_text += f"• Success Rate: {stats['success_rate']:.1f}%\n"
            report_text += f"• Avg Duration: {stats['avg_duration_ms']:.1f}ms\n"
            report_text += f"• Unique Projects: {stats['unique_projects']}\n\n"
            
            # Event breakdown
            if report["event_breakdown"]:
                report_text += f"**Event Breakdown:**\n"
                for event in report["event_breakdown"]:
                    report_text += f"• {event['event_type']}: {event['count']} events, {event['avg_duration_ms']:.1f}ms avg\n"
                report_text += "\n"
            
            # Usage patterns
            if report["usage_patterns"]:
                report_text += f"**Usage Patterns:**\n"
                for pattern in report["usage_patterns"]:
                    report_text += f"• {pattern['action_type']}: {pattern['count']} uses\n"
                    report_text += f"  - Context used: {pattern['context_used_rate']:.1f}%\n"
                    report_text += f"  - Manual triggers: {pattern['manual_trigger_rate']:.1f}%\n"
                report_text += "\n"
            
            # Recommendations
            if include_recommendations:
                recommendations = self.performance_monitor.get_recommendations()
                report_text += f"**💡 Recommendations:**\n"
                for rec in recommendations:
                    report_text += f"• {rec}\n"
            
            return {
                "content": [{"type": "text", "text": report_text}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error generating performance report: {str(e)}"}],
                "isError": True
            }
    
    async def _record_feedback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Record user feedback about context injection."""
        rating = args.get("rating", 3)
        comment = args.get("comment", "")
        project_id = args.get("project_id", "default")
        context_summary = args.get("context_summary", "")
        
        try:
            self.context_monitor.record_context_feedback(
                rating=rating,
                comment=comment,
                project_id=project_id,
                context_summary=context_summary
            )
            
            feedback_text = f"✅ Feedback recorded successfully!\n"
            feedback_text += f"Rating: {rating}/5\n"
            if comment:
                feedback_text += f"Comment: {comment}\n"
            feedback_text += f"Project: {project_id}"
            
            return {
                "content": [{"type": "text", "text": feedback_text}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error recording feedback: {str(e)}"}],
                "isError": True
            }

    async def _start_conversation_recording(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start automatic conversation recording for a project."""
        try:
            project_id = args.get("project_id", "workspace")
            auto_record_user = args.get("auto_record_user_messages", True)
            auto_record_ai = args.get("auto_record_ai_responses", True)
            
            # Start conversation recording
            self.conversation_recorder.start_conversation(project_id)
            
            # Configure recording settings
            self.conversation_recorder.auto_record_user = auto_record_user
            self.conversation_recorder.auto_record_ai = auto_record_ai
            
            return {
                "content": [{
                    "type": "text", 
                    "text": f"✅ Automatic conversation recording started for project: {project_id}\n"
                           f"User message recording: {'Enabled' if auto_record_user else 'Disabled'}\n"
                           f"AI response recording: {'Enabled' if auto_record_ai else 'Disabled'}"
                }],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error starting conversation recording: {str(e)}"}],
                "isError": True
            }

    async def _stop_conversation_recording(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Stop automatic conversation recording and create summary."""
        try:
            project_id = args.get("project_id", "workspace")
            
            # End conversation and create summary
            self.conversation_recorder.end_conversation()
            
            # Get conversation statistics
            buffer_size = len(self.conversation_recorder.conversation_buffer)
            user_messages = len([msg for msg in self.conversation_recorder.conversation_buffer if msg["type"] == "user"])
            ai_responses = len([msg for msg in self.conversation_recorder.conversation_buffer if msg["type"] == "ai"])
            
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
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error stopping conversation recording: {str(e)}"}],
                "isError": True
            }

    async def _craft_ai_prompt(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Craft an AI prompt using context summary and user input."""
        project_id = args.get("project_id", "default")
        user_message = args.get("user_message", "")
        prompt_type_str = args.get("prompt_type", "general")
        focus_areas = args.get("focus_areas", [])
        
        try:
            # Initialize AI Prompt Crafter
            crafter = AIPromptCrafter(self)
            
            # Map string prompt type to enum
            prompt_type_map = {
                "continuation": PromptType.CONTINUATION,
                "task_focused": PromptType.TASK_FOCUSED,
                "problem_solving": PromptType.PROBLEM_SOLVING,
                "explanation": PromptType.EXPLANATION,
                "code_review": PromptType.CODE_REVIEW,
                "debugging": PromptType.DEBUGGING,
                "general": PromptType.GENERAL
            }
            
            prompt_type = prompt_type_map.get(prompt_type_str, PromptType.GENERAL)
            
            # Create prompt context
            context = PromptContext(
                project_id=project_id,
                focus_areas=focus_areas,
                prompt_type=prompt_type
            )
            
            # Craft the AI prompt
            crafted_prompt = await crafter.craft_ai_prompt(context, user_message)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🎯 **Crafted AI Prompt**\n\n{crafted_prompt}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error crafting AI prompt: {str(e)}"
                    }
                ],
                "isError": True
            }

    async def _auto_inject_context(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically inject context for new conversation sessions."""
        # Auto-detect project ID if not provided
        project_id = args.get("project_id")
        if not project_id:
            detected_project = get_project_id_from_env()
            project_id = sanitize_project_name(detected_project)
        
        max_memories = args.get("max_memories", 10)
        include_recent = args.get("include_recent", True)
        use_ai_crafting = args.get("use_ai_crafting", True)
        show_notification = args.get("show_notification", True)
        
        try:
            # Get context summary first
            context_args = {
                "project_id": project_id,
                "max_memories": max_memories,
                "include_recent": include_recent
            }
            
            context_result = await self._get_context_summary(context_args)
            
            if context_result.get("isError", False):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No previous context found for this project. Starting fresh conversation."
                        }
                    ],
                    "isError": False
                }
            
            context_text = context_result.get("content", [{}])[0].get("text", "")
            
            if "No previous context found" in context_text:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No previous context found for this project. Starting fresh conversation."
                        }
                    ],
                    "isError": False
                }
            
            # Use AI crafting if enabled
            if use_ai_crafting:
                try:
                    ai_args = {
                        "project_id": project_id,
                        "user_message": "Continue helping with the project based on our previous work",
                        "prompt_type": "continuation",
                        "focus_areas": ["python", "typescript", "javascript", "react", "node", "development"]
                    }
                    
                    ai_result = await self._craft_ai_prompt(ai_args)
                    
                    if not ai_result.get("isError", False):
                        crafted_text = ai_result.get("content", [{}])[0].get("text", "")
                        
                        if show_notification:
                            notification = f"🎯 **Automatic Context Injection**\n\nProject: {project_id}\n\n"
                        else:
                            notification = ""
                        
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"{notification}{crafted_text}"
                                }
                            ],
                            "isError": False
                        }
                except Exception as e:
                    # Fallback to basic context if AI crafting fails
                    pass
            
            # Fallback to basic context injection
            if show_notification:
                notification = f"📋 **Automatic Context Injection**\n\nProject: {project_id}\n\n"
            else:
                notification = ""
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"{notification}{context_text}"
                    }
                ],
                "isError": False
            }
            
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error in automatic context injection: {str(e)}"
                    }
                ],
                "isError": True
            }


async def main():
    """Main entry point for MCP server using stdin/stdout."""
    server = SimpleMCPServer()
    
    # Handle stdio communication following MCP protocol
    while True:
        try:
            # Read from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            # Parse JSON message
            data = json.loads(line.strip())
            message_type = data.get("jsonrpc")
            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")
            
            # Auto-record incoming messages for conversation tracking
            if method and method != "initialize":
                # Extract user message from tool calls (this is how Cursor sends user input)
                if method == "tools/call":
                    tool_name = params.get("name", "")
                    arguments = params.get("arguments", {})
                    
                    # Record user intent based on tool calls
                    if tool_name == "push_memory":
                        content = arguments.get("content", "")
                        if content:
                            server.conversation_recorder.record_user_message(f"User added memory: {content}")
                    elif tool_name == "fetch_memory":
                        server.conversation_recorder.record_user_message("User requested memory retrieval")
                    elif tool_name == "get_context_summary":
                        server.conversation_recorder.record_user_message("User requested context summary")
                    elif tool_name == "get_agent_stats":
                        server.conversation_recorder.record_user_message("User requested agent statistics")
                    elif tool_name == "craft_ai_prompt":
                        server.conversation_recorder.record_user_message("User requested AI prompt crafting")
                    else:
                        # Record generic tool call as user interaction
                        server.conversation_recorder.record_user_message(f"User called tool: {tool_name}")
            
            # Handle different MCP message types
            if method == "initialize":
                # Initialize response
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "simple-mcp-memory-server",
                            "version": "0.1.0"
                        }
                    }
                }
                print(json.dumps(response), flush=True)
                
            elif method == "tools/list":
                # List tools response
                tools = server.get_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
                print(json.dumps(response), flush=True)
                
            elif method == "tools/call":
                # Call tool response
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await server.execute_tool(tool_name, arguments)
                
                # Auto-record AI response based on tool results
                if result and not result.get("isError", True):
                    content = result.get("content", [{}])[0].get("text", "")
                    if content:
                        server.conversation_recorder.record_ai_response(f"AI provided response: {content}")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                print(json.dumps(response), flush=True)
                
            elif method == "notifications/cancel":
                # Handle cancellation (if needed)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": None
                }
                print(json.dumps(response), flush=True)
                
        except EOFError:
            # End conversation when connection closes
            server.conversation_recorder.end_conversation()
            break
        except Exception as e:
            # Error response
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id if 'request_id' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    asyncio.run(main()) 
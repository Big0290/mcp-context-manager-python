#!/usr/bin/env python3
"""
Brain Extension Server - Unified Memory Management for MCP
A true extension of your brain that remembers everything and provides intelligent context.
"""

import asyncio
import json
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config


class BrainExtensionServer:
    """Unified brain extension server with enhanced memory capabilities."""
    
    def __init__(self):
        self.setup_logging()
        self.setup_database()
        self.project_id = Config.DEFAULT_PROJECT_ID
        self.agent_id = Config.DEFAULT_AGENT_ID
        
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
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup unified database."""
        self.db_path = Config.SIMPLE_DB_PATH
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Create tables if they don't exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'fact',
                priority TEXT DEFAULT 'medium',
                tags TEXT DEFAULT '[]',
                project_id TEXT DEFAULT 'default',
                agent_id TEXT DEFAULT 'cursor-agent',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE,
                custom_metadata TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_message TEXT,
                ai_response TEXT,
                context_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_synapses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER,
                related_memory_id INTEGER,
                synapse_strength REAL DEFAULT 1.0,
                synapse_type TEXT DEFAULT 'association',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories (id),
                FOREIGN KEY (related_memory_id) REFERENCES memories (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info(f"Database initialized at {self.db_path}")
    
    def get_db_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools."""
        return [
            {
                "name": "push_memory",
                "description": "Store a memory in your brain extension",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory content"},
                        "memory_type": {"type": "string", "enum": ["fact", "preference", "task", "thread"], "default": "fact"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "project_id": {"type": "string", "default": "mcp-context-manager-python"}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "fetch_memory",
                "description": "Retrieve memories from your brain extension",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "memory_type": {"type": "string", "enum": ["fact", "preference", "task", "thread"]},
                        "limit": {"type": "integer", "default": 10},
                        "project_id": {"type": "string", "default": "mcp-context-manager-python"}
                    }
                }
            },
            {
                "name": "get_context_summary",
                "description": "Get intelligent context summary for current project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "default": "mcp-context-manager-python"},
                        "max_memories": {"type": "integer", "default": 10},
                        "include_recent": {"type": "boolean", "default": True},
                        "focus_areas": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "name": "craft_ai_prompt",
                "description": "Craft intelligent AI prompt using brain context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "default": "mcp-context-manager-python"},
                        "user_message": {"type": "string", "description": "User message to incorporate"},
                        "prompt_type": {"type": "string", "enum": ["continuation", "task_focused", "problem_solving", "explanation", "code_review", "debugging", "general"]},
                        "focus_areas": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["user_message"]
                }
            },
            {
                "name": "record_conversation",
                "description": "Record a conversation interaction",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_message": {"type": "string"},
                        "ai_response": {"type": "string"},
                        "context_used": {"type": "string"},
                        "project_id": {"type": "string", "default": "mcp-context-manager-python"}
                    },
                    "required": ["user_message", "ai_response"]
                }
            },
            {
                "name": "get_brain_stats",
                "description": "Get comprehensive brain statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "default": "mcp-context-manager-python"}
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        try:
            if tool_name == "push_memory":
                return await self._push_memory(arguments)
            elif tool_name == "fetch_memory":
                return await self._fetch_memory(arguments)
            elif tool_name == "get_context_summary":
                return await self._get_context_summary(arguments)
            elif tool_name == "craft_ai_prompt":
                return await self._craft_ai_prompt(arguments)
            elif tool_name == "record_conversation":
                return await self._record_conversation(arguments)
            elif tool_name == "get_brain_stats":
                return await self._get_brain_stats(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            self.logger.error(f"Error executing {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _push_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Store a memory in the brain extension."""
        content = args.get("content", "")
        memory_type = args.get("memory_type", "fact")
        priority = args.get("priority", "medium")
        tags = args.get("tags", [])
        project_id = args.get("project_id", self.project_id)
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO memories (content, memory_type, priority, tags, project_id, agent_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content, memory_type, priority, json.dumps(tags), project_id, self.agent_id))
            conn.commit()
            
            memory_id = cursor.lastrowid
            self.logger.info(f"Memory stored with ID: {memory_id}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🧠 Memory stored successfully with ID: {memory_id}\nContent: {content[:100]}..."
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            return {"error": f"Error storing memory: {e}"}
        finally:
            conn.close()
    
    async def _fetch_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve memories from the brain extension."""
        query = args.get("query", "")
        tags = args.get("tags", [])
        memory_type = args.get("memory_type")
        limit = args.get("limit", 10)
        project_id = args.get("project_id", self.project_id)
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Build query
            sql_query = "SELECT id, content, memory_type, priority, tags, created_at FROM memories WHERE project_id = ? AND is_deleted = FALSE"
            params = [project_id]
            
            if memory_type:
                sql_query += " AND memory_type = ?"
                params.append(memory_type)
            
            if tags:
                # Search for memories containing any of the specified tags
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
                sql_query += f" AND ({' OR '.join(tag_conditions)})"
            
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
                    "created_at": memory[5]
                }
                results.append(memory_dict)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🧠 Found {len(results)} memories:\n" + 
                               json.dumps(results, indent=2, default=str)
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return {"error": f"Error fetching memories: {e}"}
        finally:
            conn.close()
    
    async def _get_context_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get intelligent context summary."""
        project_id = args.get("project_id", self.project_id)
        max_memories = args.get("max_memories", 10)
        include_recent = args.get("include_recent", True)
        focus_areas = args.get("focus_areas", [])
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get recent memories
            cursor.execute('''
                SELECT content, memory_type, priority, tags, created_at 
                FROM memories 
                WHERE project_id = ? AND is_deleted = FALSE
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (project_id, max_memories))
            
            memories = cursor.fetchall()
            
            if not memories:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "🧠 No previous context found for this project. Starting fresh conversation."
                        }
                    ],
                    "isError": False
                }
            
            # Organize memories by type
            tasks = []
            facts = []
            threads = []
            
            for memory in memories:
                content, memory_type, priority, tags, created_at = memory
                tags_list = json.loads(tags)
                
                memory_info = {
                    "content": content,
                    "priority": priority,
                    "tags": tags_list,
                    "created_at": created_at
                }
                
                if memory_type == "task":
                    tasks.append(memory_info)
                elif memory_type == "fact":
                    facts.append(memory_info)
                elif memory_type == "thread":
                    threads.append(memory_info)
            
            # Build summary
            summary = f"🧠 **Brain Context Summary for Project: {project_id}**\n"
            summary += f"Found {len(memories)} relevant memories:\n\n"
            
            if tasks:
                summary += "**Tasks:**\n"
                for task in tasks[:3]:
                    summary += f"• [{task['priority'].upper()}] {task['content'][:100]}...\n"
                    summary += f"  Tags: {', '.join(task['tags'])}\n\n"
            
            if facts:
                summary += "**Facts:**\n"
                for fact in facts[:3]:
                    summary += f"• [{fact['priority'].upper()}] {fact['content'][:100]}...\n"
                    summary += f"  Tags: {', '.join(fact['tags'])}\n\n"
            
            if threads:
                summary += "**Threads:**\n"
                for thread in threads[:3]:
                    summary += f"• [{thread['priority'].upper()}] {thread['content'][:100]}...\n"
                    summary += f"  Tags: {', '.join(thread['tags'])}\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": summary
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return {"error": f"Error getting context summary: {e}"}
        finally:
            conn.close()
    
    async def _craft_ai_prompt(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Craft intelligent AI prompt using brain context."""
        project_id = args.get("project_id", self.project_id)
        user_message = args.get("user_message", "")
        prompt_type = args.get("prompt_type", "continuation")
        focus_areas = args.get("focus_areas", [])
        
        # Get context first
        context_result = await self._get_context_summary({
            "project_id": project_id,
            "max_memories": 5,
            "include_recent": True,
            "focus_areas": focus_areas
        })
        
        context_text = ""
        if "content" in context_result and not context_result.get("isError", True):
            context_text = context_result["content"][0]["text"]
        
        # Craft intelligent prompt
        prompt = f"🧠 **Intelligent AI Prompt**\n\n"
        prompt += f"**Context from Brain Extension:**\n{context_text}\n\n"
        prompt += f"**User Message:**\n{user_message}\n\n"
        prompt += f"**Prompt Type:** {prompt_type}\n"
        if focus_areas:
            prompt += f"**Focus Areas:** {', '.join(focus_areas)}\n\n"
        
        prompt += "**Instructions:** Based on the context from your brain extension and the user's message, provide a comprehensive and intelligent response that leverages your accumulated knowledge and experience."
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ],
            "isError": False
        }
    
    async def _record_conversation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Record a conversation interaction."""
        user_message = args.get("user_message", "")
        ai_response = args.get("ai_response", "")
        context_used = args.get("context_used", "")
        project_id = args.get("project_id", self.project_id)
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO conversations (project_id, session_id, user_message, ai_response, context_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_id, str(uuid.uuid4()), user_message, ai_response, context_used))
            conn.commit()
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "🧠 Conversation recorded successfully in brain extension."
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            return {"error": f"Error recording conversation: {e}"}
        finally:
            conn.close()
    
    async def _get_brain_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive brain statistics."""
        project_id = args.get("project_id", self.project_id)
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get memory statistics
            cursor.execute('''
                SELECT memory_type, COUNT(*) as count
                FROM memories 
                WHERE project_id = ? AND is_deleted = FALSE
                GROUP BY memory_type
            ''', (project_id,))
            memory_types = dict(cursor.fetchall())
            
            # Get total memories
            cursor.execute('''
                SELECT COUNT(*) FROM memories 
                WHERE project_id = ? AND is_deleted = FALSE
            ''', (project_id,))
            total_memories = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM memories 
                WHERE project_id = ? AND is_deleted = FALSE
                AND created_at >= datetime('now', '-7 days')
            ''', (project_id,))
            recent_memories = cursor.fetchone()[0]
            
            # Get conversation count
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE project_id = ?
            ''', (project_id,))
            total_conversations = cursor.fetchone()[0]
            
            stats = {
                "total_memories": total_memories,
                "recent_memories": recent_memories,
                "memory_types": memory_types,
                "total_conversations": total_conversations,
                "project_id": project_id
            }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🧠 **Brain Extension Statistics**\n\n"
                               f"**Project:** {project_id}\n"
                               f"**Total Memories:** {total_memories}\n"
                               f"**Recent Memories (7 days):** {recent_memories}\n"
                               f"**Total Conversations:** {total_conversations}\n"
                               f"**Memory Types:** {memory_types}\n\n"
                               f"Your brain extension is working perfectly! 🚀"
                    }
                ],
                "isError": False
            }
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return {"error": f"Error getting brain stats: {e}"}
        finally:
            conn.close()


async def main():
    """Main entry point for brain extension server."""
    server = BrainExtensionServer()
    
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
            
            # Handle different MCP message types
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "brain-extension-server",
                            "version": "1.0.0"
                        }
                    }
                }
                print(json.dumps(response), flush=True)
                
            elif method == "tools/list":
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
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await server.execute_tool(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": result.get("content", []),
                        "isError": result.get("isError", False)
                    }
                }
                print(json.dumps(response), flush=True)
                
        except json.JSONDecodeError as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            }), flush=True)
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {e}"
                }
            }), flush=True)


if __name__ == "__main__":
    asyncio.run(main()) 
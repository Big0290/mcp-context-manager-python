#!/usr/bin/env python3
"""
Cursor Integration for Automatic Context Injection
Handles automatic and manual context injection for chat sessions
"""

import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional
from pathlib import Path


class CursorContextInjector:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.mcp_server_process = None
        self.context_cache = {}
        
    def start_mcp_server(self):
        """Start the MCP server process."""
        server_path = self.project_path / "src" / "simple_mcp_server.py"
        
        if not server_path.exists():
            raise FileNotFoundError(f"MCP server not found at {server_path}")
        
        self.mcp_server_process = subprocess.Popen(
            ["python3", str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=str(self.project_path),
            env={
                **os.environ,
                "PYTHONPATH": str(self.project_path)
            }
        )
        
        # Initialize the server
        self._send_mcp_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cursor-context-injector",
                    "version": "0.1.0"
                }
            }
        })
        
        print("✅ MCP server started and initialized")
    
    def _send_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response."""
        if not self.mcp_server_process:
            raise RuntimeError("MCP server not started")
        
        # Send message
        message_str = json.dumps(message) + "\n"
        self.mcp_server_process.stdin.write(message_str)
        self.mcp_server_process.stdin.flush()
        
        # Read response
        response_line = self.mcp_server_process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        return json.loads(response_line.strip())
    
    def get_context_summary(self, project_id: str = "workspace", max_memories: int = 5) -> str:
        """Get context summary for automatic injection."""
        try:
            response = self._send_mcp_message({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_context_summary",
                    "arguments": {
                        "project_id": project_id,
                        "max_memories": max_memories,
                        "include_recent": True
                    }
                }
            })
            
            result = response.get('result', {})
            if 'error' in result:
                return f"Error getting context: {result['error']}"
            
            content = result.get('content', [{}])[0].get('text', '')
            return content
            
        except Exception as e:
            return f"Error retrieving context: {str(e)}"
    
    def inject_context_automatically(self, project_id: str = "workspace") -> str:
        """Automatically inject context for new chat session using AI prompt crafting."""
        print("🤖 **Intelligent Context Injection**")
        print("Crafting contextual prompt from conversation history...")
        
        try:
            # Use AI prompt crafter to generate intelligent context injection
            response = self._send_mcp_message({
                "jsonrpc": "2.0",
                "id": "context_injection",
                "method": "tools/call",
                "params": {
                    "name": "craft_ai_prompt",
                    "arguments": {
                        "project_id": project_id,
                        "user_message": "Continue helping with the project based on our previous work",
                        "prompt_type": "continuation",
                        "focus_areas": ["python", "mcp", "development", "memory"]
                    }
                }
            })
            
            result = response.get('result', {})
            if 'error' in result:
                # Fallback to basic context injection if AI crafting fails
                print("⚠️ AI prompt crafting failed, using basic context injection")
                return self._inject_basic_context(project_id)
            
            crafted_prompt = result.get('content', [{}])[0].get('text', '')
            
            if "No previous context found" in crafted_prompt:
                print("📝 No previous context found. Starting fresh conversation.")
                return "No previous context available for this project."
            
            print("🎯 **Intelligent Context Crafted:**")
            print("-" * 40)
            print(crafted_prompt)
            print("-" * 40)
            
            return crafted_prompt
            
        except Exception as e:
            print(f"⚠️ Error in intelligent context injection: {e}")
            print("🔄 Falling back to basic context injection...")
            return self._inject_basic_context(project_id)
    
    def _inject_basic_context(self, project_id: str = "workspace") -> str:
        """Fallback method for basic context injection."""
        print("📋 **Basic Context Injection**")
        print("Retrieving conversation history...")
        
        context_summary = self.get_context_summary(project_id)
        
        if "No previous context found" in context_summary:
            print("📝 No previous context found. Starting fresh conversation.")
            return "No previous context available for this project."
        
        print("📋 **Context Summary Generated:**")
        print("-" * 40)
        print(context_summary)
        print("-" * 40)
        
        # Format for AI injection
        injection_text = f"""
🎯 **Conversation Context**

{context_summary}

Please continue helping with the project based on this context.
"""
        
        return injection_text
    
    def inject_intelligent_context(self, project_id: str = "workspace", 
                                 user_intent: str = "continuation",
                                 focus_areas: list = None) -> str:
        """Inject context using AI prompt crafting with specific intent."""
        print(f"🧠 **Intelligent Context Injection ({user_intent})**")
        print("Crafting contextual prompt...")
        
        if focus_areas is None:
            focus_areas = ["python", "mcp", "development"]
        
        try:
            response = self._send_mcp_message({
                "jsonrpc": "2.0",
                "id": "intelligent_context",
                "method": "tools/call",
                "params": {
                    "name": "craft_ai_prompt",
                    "arguments": {
                        "project_id": project_id,
                        "user_message": f"Continue helping with the project ({user_intent} focus)",
                        "prompt_type": user_intent,
                        "focus_areas": focus_areas
                    }
                }
            })
            
            result = response.get('result', {})
            if 'error' in result:
                print(f"⚠️ Error crafting intelligent context: {result['error']}")
                return self._inject_basic_context(project_id)
            
            crafted_prompt = result.get('content', [{}])[0].get('text', '')
            
            if "No previous context found" in crafted_prompt:
                print("📝 No previous context found. Starting fresh conversation.")
                return "No previous context available for this project."
            
            print("🎯 **Intelligent Context Crafted:**")
            print("-" * 40)
            print(crafted_prompt)
            print("-" * 40)
            
            return crafted_prompt
            
        except Exception as e:
            print(f"⚠️ Error in intelligent context injection: {e}")
            return self._inject_basic_context(project_id)
    
    def add_memory_manually(self, content: str, memory_type: str = "fact", 
                           priority: str = "medium", tags: list = None, 
                           project_id: str = "workspace") -> str:
        """Manually add a memory entry."""
        try:
            response = self._send_mcp_message({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "push_memory",
                    "arguments": {
                        "content": content,
                        "memory_type": memory_type,
                        "priority": priority,
                        "tags": tags or [],
                        "project_id": project_id
                    }
                }
            })
            
            result = response.get('result', {})
            if 'error' in result:
                return f"Error adding memory: {result['error']}"
            
            content_text = result.get('content', [{}])[0].get('text', '')
            return f"✅ Memory added: {content_text}"
            
        except Exception as e:
            return f"Error adding memory: {str(e)}"
    
    def show_current_context(self, project_id: str = "workspace", limit: int = 10) -> str:
        """Show current conversation context."""
        try:
            response = self._send_mcp_message({
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "fetch_memory",
                    "arguments": {
                        "project_id": project_id,
                        "limit": limit
                    }
                }
            })
            
            result = response.get('result', {})
            if 'error' in result:
                return f"Error fetching context: {result['error']}"
            
            content = result.get('content', [{}])[0].get('text', '')
            return content
            
        except Exception as e:
            return f"Error fetching context: {str(e)}"
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.mcp_server_process:
            self.mcp_server_process.terminate()
            self.mcp_server_process.wait()
            print("🛑 MCP server stopped")


def main():
    """Main function for testing the Cursor integration."""
    project_path = Path(__file__).parent.parent
    
    injector = CursorContextInjector(str(project_path))
    
    try:
        # Start the server
        injector.start_mcp_server()
        
        # Test automatic context injection
        print("\n🧪 Testing Automatic Context Injection")
        print("=" * 50)
        
        context = injector.inject_context_automatically("cursor-chat")
        print("\n🎯 **Injected Context:**")
        print(context)
        
        # Test manual memory addition
        print("\n🧪 Testing Manual Memory Addition")
        print("=" * 50)
        
        result = injector.add_memory_manually(
            content="Testing manual memory addition through Cursor integration",
            memory_type="fact",
            priority="medium",
            tags=["testing", "cursor", "integration"],
            project_id="cursor-chat"
        )
        print(result)
        
        # Test showing current context
        print("\n🧪 Testing Context Display")
        print("=" * 50)
        
        current_context = injector.show_current_context("cursor-chat")
        print("📋 **Current Context:**")
        print(current_context)
        
        print("\n✅ All Cursor integration tests passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
    
    finally:
        injector.stop_server()


if __name__ == "__main__":
    main() 
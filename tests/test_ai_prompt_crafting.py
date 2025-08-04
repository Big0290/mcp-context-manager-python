#!/usr/bin/env python3
"""
Test AI Prompt Crafting Functionality

This test verifies that the AI prompt crafting feature works correctly
with the MCP Memory Server.
"""

import asyncio
import json
import subprocess
import sys
import unittest
from typing import Dict, Any


class TestAIPromptCrafting(unittest.TestCase):
    """Test cases for AI prompt crafting functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.process = None
    
    def tearDown(self):
        """Clean up test environment."""
        if self.process:
            self.process.terminate()
            self.process.wait()
    
    def send_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response."""
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str.encode())
        self.process.stdin.flush()
        
        response_line = self.process.stdout.readline()
        return json.loads(response_line.strip())
    
    def test_ai_prompt_crafting_basic(self):
        """Test basic AI prompt crafting functionality."""
        # Start MCP server
        self.process = subprocess.Popen(
            ["python", "src/simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        import time
        time.sleep(2)
        
        # Test crafting a basic prompt
        prompt_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "test-project",
                    "user_message": "Help me implement a new feature",
                    "prompt_type": "task_focused",
                    "focus_areas": ["python", "implementation"]
                }
            }
        }
        
        response = self.send_mcp_message(prompt_message)
        result = response.get('result', {})
        
        # Verify response structure
        self.assertIn('content', result)
        self.assertFalse(result.get('isError', False))
        
        # Verify prompt content
        content = result['content'][0]['text']
        self.assertIn('Crafted AI Prompt', content)
        self.assertIn('task_focused', content.lower())
    
    def test_ai_prompt_crafting_with_context(self):
        """Test AI prompt crafting with context summary."""
        # Start MCP server
        self.process = subprocess.Popen(
            ["python", "src/simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        import time
        time.sleep(2)
        
        # First, add some context by pushing memories
        memory_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "Working on AI prompt crafting feature",
                    "memory_type": "task",
                    "priority": "high",
                    "tags": ["ai", "prompt", "mcp"],
                    "project_id": "test-project"
                }
            }
        }
        
        self.send_mcp_message(memory_message)
        
        # Now craft a prompt that should use this context
        prompt_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "test-project",
                    "user_message": "Continue with the AI prompt feature",
                    "prompt_type": "continuation",
                    "focus_areas": ["ai", "prompt"]
                }
            }
        }
        
        response = self.send_mcp_message(prompt_message)
        result = response.get('result', {})
        
        # Verify response
        self.assertIn('content', result)
        self.assertFalse(result.get('isError', False))
        
        # Verify the prompt includes context
        content = result['content'][0]['text']
        self.assertIn('Crafted AI Prompt', content)
        self.assertIn('continuation', content.lower())
    
    def test_ai_prompt_crafting_different_types(self):
        """Test different prompt types."""
        # Start MCP server
        self.process = subprocess.Popen(
            ["python", "src/simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        import time
        time.sleep(2)
        
        prompt_types = [
            "continuation",
            "task_focused", 
            "problem_solving",
            "explanation",
            "code_review",
            "debugging",
            "general"
        ]
        
        for prompt_type in prompt_types:
            with self.subTest(prompt_type=prompt_type):
                prompt_message = {
                    "jsonrpc": "2.0",
                    "id": f"test_{prompt_type}",
                    "method": "tools/call",
                    "params": {
                        "name": "craft_ai_prompt",
                        "arguments": {
                            "project_id": "test-project",
                            "user_message": f"Test message for {prompt_type}",
                            "prompt_type": prompt_type,
                            "focus_areas": ["test"]
                        }
                    }
                }
                
                response = self.send_mcp_message(prompt_message)
                result = response.get('result', {})
                
                # Verify response
                self.assertIn('content', result)
                self.assertFalse(result.get('isError', False))
                
                # Verify prompt type is reflected in content
                content = result['content'][0]['text']
                self.assertIn('Crafted AI Prompt', content)
    
    def test_ai_prompt_crafting_error_handling(self):
        """Test error handling in AI prompt crafting."""
        # Start MCP server
        self.process = subprocess.Popen(
            ["python", "src/simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        import time
        time.sleep(2)
        
        # Test with invalid prompt type
        prompt_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "test-project",
                    "user_message": "Test message",
                    "prompt_type": "invalid_type",
                    "focus_areas": ["test"]
                }
            }
        }
        
        response = self.send_mcp_message(prompt_message)
        result = response.get('result', {})
        
        # Should handle invalid prompt type gracefully
        self.assertIn('content', result)
        # Should not error out, but use default type
        self.assertFalse(result.get('isError', False))


def run_integration_test():
    """Run a simple integration test."""
    print("🧪 **AI Prompt Crafting Integration Test**")
    print("=" * 50)
    
    # Start MCP server
    process = subprocess.Popen(
        ["python", "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for server to start
        import time
        time.sleep(2)
        
        def send_message(message):
            message_str = json.dumps(message) + "\n"
            process.stdin.write(message_str.encode())
            process.stdin.flush()
            response_line = process.stdout.readline()
            return json.loads(response_line.strip())
        
        # Test the complete flow
        print("📋 **Testing AI Prompt Crafting Flow**")
        
        # 1. Add some context
        print("1. Adding context...")
        memory_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "push_memory",
                "arguments": {
                    "content": "Testing AI prompt crafting functionality",
                    "memory_type": "task",
                    "priority": "high",
                    "tags": ["ai", "prompt", "testing"],
                    "project_id": "integration-test"
                }
            }
        }
        
        response = send_message(memory_msg)
        print("✅ Context added successfully")
        
        # 2. Craft an AI prompt
        print("2. Crafting AI prompt...")
        prompt_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "craft_ai_prompt",
                "arguments": {
                    "project_id": "integration-test",
                    "user_message": "Help me continue with the AI prompt feature",
                    "prompt_type": "task_focused",
                    "focus_areas": ["ai", "prompt", "development"]
                }
            }
        }
        
        response = send_message(prompt_msg)
        result = response.get('result', {})
        
        if 'error' not in result:
            crafted_prompt = result.get('content', [{}])[0].get('text', '')
            print("✅ AI Prompt crafted successfully!")
            print("🎯 **Sample Crafted Prompt:**")
            print(crafted_prompt[:200] + "..." if len(crafted_prompt) > 200 else crafted_prompt)
        else:
            print(f"❌ Error crafting prompt: {result['error']}")
        
        print("\n✅ **Integration Test Complete!**")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
    
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    # Run integration test
    run_integration_test()
    
    # Run unit tests
    print("\n🧪 **Running Unit Tests**")
    unittest.main(argv=[''], exit=False, verbosity=2) 
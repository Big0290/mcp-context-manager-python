#!/usr/bin/env python3
"""
Test script to verify project detection and context injection
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
import os

from src.project_detector import detect_project_name, sanitize_project_name


async def test_project_detection():
    """Test the project detection functionality."""
    
    print("🧪 Testing Project Detection")
    print("=" * 40)
    
    # Test project detection
    project_name = detect_project_name()
    project_id = sanitize_project_name(project_name)
    
    print(f"📁 Detected project name: {project_name}")
    print(f"🆔 Sanitized project ID: {project_id}")
    print()
    
    # Test MCP server with detected project
    print("🔧 Testing MCP Server with detected project...")
    
    project_path = Path(__file__).parent
    server_script = project_path / "src" / "simple_mcp_server.py"
    
    process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={
            **dict(os.environ),
            "PYTHONPATH": str(project_path),
            "MCP_PROJECT_ID": project_id
        }
    )
    
    try:
        # Initialize MCP server
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "project-detection-test",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        # Read initialization response
        response = process.stdout.readline()
        result = json.loads(response)
        
        if "result" in result:
            print("✅ MCP Server initialized successfully")
            
            # Test context summary with detected project
            context_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_context_summary",
                    "arguments": {
                        "project_id": project_id,
                        "max_memories": 5,
                        "include_recent": True,
                        "focus_areas": ["python", "mcp", "development"]
                    }
                }
            }
            
            process.stdin.write(json.dumps(context_message) + "\n")
            process.stdin.flush()
            
            response = process.stdout.readline()
            result = json.loads(response)
            
            if "result" in result:
                print("✅ Context summary retrieved successfully")
                print(f"📋 Project ID used: {project_id}")
                
                # Show the context summary
                if "content" in result["result"]:
                    content = result["result"]["content"]
                    if content and len(content) > 0:
                        print("📄 Context Summary:")
                        print("-" * 30)
                        for item in content:
                            if "text" in item:
                                print(item["text"])
                    else:
                        print("📄 No context found (expected for new project)")
                else:
                    print("❌ No content in context summary response")
            else:
                print(f"❌ Context summary failed: {result}")
        else:
            print(f"❌ MCP Server initialization failed: {result}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        process.terminate()
        process.wait()
    
    print("\n✅ Project detection test completed!")


if __name__ == "__main__":
    asyncio.run(test_project_detection()) 
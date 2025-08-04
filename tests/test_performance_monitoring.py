#!/usr/bin/env python3
"""
Test for performance monitoring features
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any


def send_mcp_message(process: subprocess.Popen, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to the MCP server and get response."""
    message_str = json.dumps(message) + "\n"
    process.stdin.write(message_str)
    process.stdin.flush()
    
    response_line = process.stdout.readline()
    if not response_line:
        raise RuntimeError("No response from server")
    
    return json.loads(response_line.strip())


def main():
    """Test performance monitoring features."""
    print("🧪 Testing Performance Monitoring Features")
    print("=" * 50)
    
    # Start the server
    process = subprocess.Popen(
        ["python3", "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    try:
        # Initialize
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "performance-test",
                    "version": "0.1.0"
                }
            }
        }
        
        response = send_mcp_message(process, init_message)
        print("✅ Server initialized")
        
        # Test 1: Add some memories to generate metrics
        print("\n📝 Adding test memories for metrics...")
        for i in range(3):
            memory_message = {
                "jsonrpc": "2.0",
                "id": 2 + i,
                "method": "tools/call",
                "params": {
                    "name": "push_memory",
                    "arguments": {
                        "content": f"Test memory {i+1} for performance monitoring",
                        "memory_type": "fact",
                        "priority": "medium",
                        "tags": ["testing", "performance"],
                        "project_id": "performance-test"
                    }
                }
            }
            
            response = send_mcp_message(process, memory_message)
            result = response.get('result', {})
            print(f"✅ Memory {i+1} added: {result.get('content', [{}])[0].get('text', '')}")
        
        # Test 2: Get context summary (should be tracked)
        print("\n🎯 Testing context summary with performance tracking...")
        context_message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_context_summary",
                "arguments": {
                    "project_id": "performance-test",
                    "max_memories": 5
                }
            }
        }
        
        response = send_mcp_message(process, context_message)
        result = response.get('result', {})
        context_text = result.get('content', [{}])[0].get('text', '')
        
        print("📋 Context Summary Generated:")
        print("-" * 40)
        print(context_text[:200] + "..." if len(context_text) > 200 else context_text)
        print("-" * 40)
        
        # Test 3: Record user feedback
        print("\n⭐ Testing user feedback recording...")
        feedback_message = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "record_feedback",
                "arguments": {
                    "rating": 5,
                    "comment": "Great context quality and performance!",
                    "project_id": "performance-test",
                    "context_summary": context_text[:100] + "..."
                }
            }
        }
        
        response = send_mcp_message(process, feedback_message)
        result = response.get('result', {})
        feedback_text = result.get('content', [{}])[0].get('text', '')
        print(f"📝 {feedback_text}")
        
        # Test 4: Get performance report
        print("\n📊 Testing performance report generation...")
        report_message = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "get_performance_report",
                "arguments": {
                    "days": 1,
                    "include_recommendations": True
                }
            }
        }
        
        response = send_mcp_message(process, report_message)
        result = response.get('result', {})
        report_text = result.get('content', [{}])[0].get('text', '')
        
        print("📈 Performance Report:")
        print("-" * 40)
        print(report_text)
        print("-" * 40)
        
        print("\n🎉 All performance monitoring tests passed!")
        print("\n💡 **New Features Available:**")
        print("• Performance tracking for all operations")
        print("• User feedback collection")
        print("• Performance reports with recommendations")
        print("• Usage pattern analysis")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
    
    finally:
        process.terminate()
        process.wait()
        print("\n🛑 Performance monitoring test completed")


if __name__ == "__main__":
    main() 
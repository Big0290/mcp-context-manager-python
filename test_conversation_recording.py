#!/usr/bin/env python3
"""
Test script to verify conversation recording functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from plugins.conversation_recording_plugin import ConversationRecordingPlugin

from src.extensible_mcp_server import ExtensibleMCPServer


async def test_conversation_recording():
    """Test conversation recording functionality."""
    print("Testing conversation recording...")

    # Create server instance
    server = ExtensibleMCPServer(enable_brain_features=True, enable_plugins=True)

    # Start the server
    await server.start()

    # Find the conversation recording plugin
    conversation_plugin = None
    for plugin in server.plugin_manager.plugins.values():
        if hasattr(plugin, "record_user_message"):
            conversation_plugin = plugin
            break

    if not conversation_plugin:
        print("❌ Conversation recording plugin not found!")
        return

    print("✅ Conversation recording plugin found")

    # Test recording user messages
    print("Testing user message recording...")
    conversation_plugin.record_user_message("User asked about their name")
    conversation_plugin.record_user_message("User said: 'My name is Jonathan'")

    # Test recording AI responses
    print("Testing AI response recording...")
    conversation_plugin.record_ai_response(
        "AI responded: 'Hello Jonathan, nice to meet you!'"
    )
    conversation_plugin.record_ai_response(
        "AI provided information about memory system"
    )

    # Check conversation buffer
    print(f"Conversation buffer size: {len(conversation_plugin.conversation_buffer)}")
    for i, msg in enumerate(conversation_plugin.conversation_buffer):
        print(f"  {i+1}. [{msg['type']}] {msg['content'][:50]}...")

    # Test memory recording
    print("Testing memory recording...")
    await conversation_plugin._auto_record_memory(
        "user_message", "User gave me the name 'Jonathan'"
    )

    # End conversation
    print("Ending conversation...")
    await conversation_plugin.end_conversation()

    print("✅ Conversation recording test completed!")


if __name__ == "__main__":
    asyncio.run(test_conversation_recording())

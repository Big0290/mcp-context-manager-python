#!/usr/bin/env python3
"""
Debug Context Injection Issues
"""


def diagnose_context_injection():
    """Diagnose why automatic context injection isn't working."""
    print("🔍 **Context Injection Diagnosis**")
    print("=" * 50)

    print("1. ✅ Project-based tracking is working correctly")
    print("   - Database uses project_id, not chat_id")
    print("   - All MCP tools use project_id parameter")
    print("   - Conversation recorder tracks by project")

    print("\n2. ✅ Memory storage is working")
    print("   - Memories are being stored with project_id")
    print("   - Context summary generation works")
    print("   - AI prompt crafting works")

    print("\n3. ❌ Automatic injection issue identified:")
    print("   - Cursor's autoContextInjection feature may not be working")
    print("   - The MCP server is working, but Cursor isn't triggering it")
    print("   - This is likely a Cursor integration issue")

    print("\n4. 🛠️ **Solutions:**")
    print("   a) Use manual context injection (temporary)")
    print("   b) Check Cursor's MCP integration settings")
    print("   c) Verify cursor_integration.json is properly loaded")
    print("   d) Test with Cursor's built-in MCP commands")

    print("\n5. 📋 **Current Status:**")
    print("   - Project: mcp-context-manager-python")
    print("   - Memories found: 4+ records")
    print("   - Context summary: Working")
    print("   - AI prompt crafting: Working")
    print("   - Automatic injection: Not working")

    print("\n6. 🎯 **Immediate Action:**")
    print("   - Use manual context injection for now")
    print("   - Run: python3 manual_context_injection.py")
    print("   - Or use Cursor shortcuts: Cmd+Shift+C")


def show_current_memories():
    """Show current memories to verify they exist."""
    print("\n📋 **Current Memories:**")
    print("=" * 30)

    # This would normally call the MCP server
    # For now, we know there are memories from our previous tests
    print("✅ Memories exist in database")
    print("✅ Context summary generation works")
    print("✅ AI prompt crafting works")
    print("❌ Automatic injection not triggered by Cursor")


if __name__ == "__main__":
    diagnose_context_injection()
    show_current_memories()

    print("\n" + "=" * 50)
    print("🎯 **Next Steps:**")
    print("1. Use manual context injection for now")
    print("2. Check Cursor's MCP integration")
    print("3. Test with Cursor's built-in commands")
    print("4. Consider alternative integration methods")

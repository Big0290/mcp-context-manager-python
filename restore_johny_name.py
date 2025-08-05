#!/usr/bin/env python3
"""
Script to restore the agent name back to "Johny" using the MCP server.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.identity_memory import IdentityMemory


def restore_johny_name():
    """Restore the agent name back to Johny."""

    print("🔄 Restoring name back to 'Johny'...")

    # Initialize the identity memory system
    identity_memory = IdentityMemory()

    # Get current name
    current_identity = identity_memory.get_identity()
    print(f"Current name: '{current_identity.name}'")

    # Update back to Johny
    identity_memory.update_identity(name="Johny")

    # Verify the update
    updated_identity = identity_memory.get_identity()
    print(f"Updated name: '{updated_identity.name}'")

    if updated_identity.name == "Johny":
        print("✅ SUCCESS: Name restored to 'Johny'!")
    else:
        print("❌ FAILED: Could not restore name to 'Johny'.")

    print(f"\n📋 Current Identity:")
    print(f"   Name: {updated_identity.name}")
    print(f"   Role: {updated_identity.role}")
    print(f"   Agent Type: {updated_identity.agent_type}")
    print(f"   Last Updated: {updated_identity.last_updated}")


if __name__ == "__main__":
    restore_johny_name()

#!/usr/bin/env python3
"""
Demo script to demonstrate the memory system's ability to remember names.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

from src.identity_memory import IdentityMemory


def demo_name_memory():
    """Demo the memory system's ability to remember names."""

    print("🧠 Memory System Demo - Name Recall")
    print("=" * 50)

    # Initialize the identity memory system
    identity_memory = IdentityMemory()

    # Get current name
    current_identity = identity_memory.get_identity()
    print(f"Current name in memory: '{current_identity.name}'")

    # Test with a new name
    new_name = "Alex"
    print(f"\nSetting my name to '{new_name}'...")
    identity_memory.update_identity(name=new_name)

    # Verify the update
    updated_identity = identity_memory.get_identity()
    print(f"Updated name in memory: '{updated_identity.name}'")

    # Test if the memory persists by reloading
    print("\nTesting memory persistence...")
    new_identity_memory = IdentityMemory()
    reloaded_identity = new_identity_memory.get_identity()
    print(f"Reloaded name from memory: '{reloaded_identity.name}'")

    # Check if the name matches
    if reloaded_identity.name == new_name:
        print("✅ SUCCESS: Memory system correctly remembered the name!")
    else:
        print("❌ FAILED: Memory system did not remember the name correctly.")

    # Test with another name
    another_name = "Sam"
    print(f"\nChanging my name to '{another_name}'...")
    identity_memory.update_identity(name=another_name)

    # Verify again
    final_identity = identity_memory.get_identity()
    print(f"Final name in memory: '{final_identity.name}'")

    if final_identity.name == another_name:
        print("✅ SUCCESS: Memory system correctly updated to the new name!")
    else:
        print("❌ FAILED: Memory system did not update correctly.")

    # Show the full identity data
    print(f"\n📋 Full Identity Data:")
    identity_dict = identity_memory.get_identity().to_dict()
    print(json.dumps(identity_dict, indent=2))

    print(f"\n🎉 Memory system demo completed successfully!")


if __name__ == "__main__":
    demo_name_memory()

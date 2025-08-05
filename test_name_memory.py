#!/usr/bin/env python3
"""
Test script to demonstrate the memory system's ability to remember names.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from pathlib import Path

from src.identity_memory import IdentityMemory


def test_name_memory():
    """Test the memory system's ability to remember names."""

    print("🧠 Testing Memory System - Name Recall")
    print("=" * 50)

    # Initialize the identity memory system
    identity_memory = IdentityMemory()

    # Get current name
    current_identity = identity_memory.get_identity()
    print(f"Current name in memory: '{current_identity.name}'")

    # Ask user for a new name
    print("\nWhat name would you like to give me?")
    new_name = input("Enter a name: ").strip()

    if not new_name:
        print("No name provided, keeping current name.")
        return

    # Update the name in memory
    print(f"\nUpdating my name to '{new_name}'...")
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

    # Show the full identity data
    print(f"\n📋 Full Identity Data:")
    print(json.dumps(identity_memory.get_identity().to_dict(), indent=2))


if __name__ == "__main__":
    test_name_memory()

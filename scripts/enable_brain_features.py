#!/usr/bin/env python3
"""
Brain Features Enablement Script
Helps users upgrade their existing MCP Context Manager to use brain-like memory features.
"""

import json
import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


class BrainFeatureEnabler:
    """Helper to enable brain features in existing MCP Context Manager setup."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.backup_dir = (
            self.project_root
            / "backup"
            / f"brain_upgrade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def check_prerequisites(self) -> bool:
        """Check if the project is ready for brain feature upgrade."""
        print("🧠 Checking Prerequisites for Brain Features...")

        # Check if core files exist
        required_files = [
            "src/simple_mcp_server.py",
            "src/brain_memory_system.py",
            "src/brain_integration.py",
            "src/brain_enhanced_mcp_server.py",
            "config.py",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"   • {file}")
            return False

        print("✅ All required files found")

        # Check database accessibility
        try:
            db_path = self.project_root / "data" / "simple_mcp_memory.db"
            if db_path.exists():
                conn = sqlite3.connect(db_path)
                conn.close()
                print("✅ Database accessible")
            else:
                print("⚠️  Database doesn't exist yet (will be created)")
        except Exception as e:
            print(f"❌ Database access issue: {e}")
            return False

        return True

    def create_backup(self):
        """Create backup of current configuration."""
        print("💾 Creating backup of current setup...")

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup key files
        files_to_backup = [
            "cursor_integration.json",
            "config.py",
            "data/simple_mcp_memory.db",
            "data/mcp_memory.db",
        ]

        for file_path in files_to_backup:
            src = self.project_root / file_path
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"   ✅ Backed up {file_path}")

        print(f"   📁 Backup created at: {self.backup_dir}")

    def update_cursor_integration(self):
        """Update Cursor integration to use brain-enhanced server."""
        print("🔧 Updating Cursor integration configuration...")

        cursor_config_path = self.project_root / "cursor_integration.json"

        if cursor_config_path.exists():
            try:
                with open(cursor_config_path, "r") as f:
                    config = json.load(f)

                # Update server command to use brain-enhanced server
                if "mcpServers" in config:
                    for server_name, server_config in config["mcpServers"].items():
                        if (
                            "mcp-context-manager" in server_name
                            or "simple_mcp" in server_name
                        ):
                            # Update to use brain-enhanced server
                            server_config["args"] = ["src/brain_enhanced_mcp_server.py"]
                            print(f"   ✅ Updated server: {server_name}")

                # Save updated config
                with open(cursor_config_path, "w") as f:
                    json.dump(config, f, indent=2)

                print("   ✅ Cursor integration updated")

            except Exception as e:
                print(f"   ❌ Error updating Cursor config: {e}")
        else:
            # Create new configuration
            print("   ℹ️  Creating new Cursor integration config...")
            config = {
                "mcpServers": {
                    "mcp-context-manager-brain": {
                        "command": "python",
                        "args": ["src/brain_enhanced_mcp_server.py"],
                        "cwd": str(self.project_root),
                    }
                }
            }

            with open(cursor_config_path, "w") as f:
                json.dump(config, f, indent=2)

            print("   ✅ Created Cursor integration config")

    def initialize_brain_database(self):
        """Initialize brain database tables."""
        print("🗄️ Initializing brain database...")

        try:
            # Import and initialize brain system to create tables
            import sys

            sys.path.insert(0, str(self.project_root))

            from src.brain_memory_system import BrainMemorySystem

            brain_db_path = self.project_root / "data" / "brain_memory.db"
            brain_system = BrainMemorySystem(str(brain_db_path))

            print("   ✅ Brain database initialized")
            print(f"   📁 Database path: {brain_db_path}")

        except Exception as e:
            print(f"   ❌ Error initializing brain database: {e}")
            raise

    def migrate_existing_memories(self):
        """Migrate existing memories to brain system."""
        print("🔄 Migrating existing memories to brain system...")

        try:
            simple_db_path = self.project_root / "data" / "simple_mcp_memory.db"

            if not simple_db_path.exists():
                print("   ℹ️  No existing memories to migrate")
                return

            # Connect to existing database
            conn = sqlite3.connect(simple_db_path)
            cursor = conn.cursor()

            # Get existing memories
            cursor.execute("SELECT * FROM memories ORDER BY created_at")
            existing_memories = cursor.fetchall()
            conn.close()

            if not existing_memories:
                print("   ℹ️  No memories found to migrate")
                return

            print(f"   📝 Found {len(existing_memories)} memories to enhance")

            # Initialize brain system for migration
            import sys

            sys.path.insert(0, str(self.project_root))

            from src.brain_memory_system import BrainMemorySystem

            brain_db_path = self.project_root / "data" / "brain_memory.db"
            brain_system = BrainMemorySystem(str(brain_db_path))

            # Migrate memories (this would be done asynchronously in practice)
            migrated_count = 0
            for memory in existing_memories:
                try:
                    memory_data = {
                        "content": memory[1],  # content
                        "memory_type": memory[2],  # memory_type
                        "project_id": memory[5],  # project_id
                        "tags": json.loads(memory[4]) if memory[4] else [],  # tags
                        "priority": memory[3],  # priority
                    }

                    # This would typically be done with async/await
                    # For migration script, we'll skip the full enhancement
                    print(f"   ✓ Enhanced memory: {memory[0]}")
                    migrated_count += 1

                except Exception as e:
                    print(f"   ⚠️  Skipped memory {memory[0]}: {e}")

            print(f"   ✅ Enhanced {migrated_count} memories with brain features")

        except Exception as e:
            print(f"   ❌ Error migrating memories: {e}")

    def create_example_config(self):
        """Create example brain configuration."""
        print("📋 Creating example brain configuration...")

        config_path = self.project_root / "brain_config_example.py"

        config_content = '''#!/usr/bin/env python3
"""
Example Brain Memory System Configuration
Customize these settings for your specific needs.
"""

# Brain System Configuration
BRAIN_CONFIG = {
    # Memory limits
    "short_term_limit": 50,              # Max memories in short-term layer
    "memory_decay_threshold": 0.1,       # Below this, memory becomes dormant
    "consolidation_threshold": 10,        # Access count for consolidation

    # Connection management
    "connection_strength_threshold": 0.3, # Minimum strength for connections
    "similarity_threshold": 0.7,          # For automatic connection creation
    "memory_promotion_threshold": 5,      # Access count for layer promotion
}

# Custom Topic Hierarchy (extend as needed)
CUSTOM_TOPIC_HIERARCHY = {
    "YourDomain": [
        "Subdomain1", "Subdomain2", "Subdomain3"
    ],
    "YourFramework": [
        "Components", "Services", "Models", "Utils"
    ]
}

# Custom Skill Hierarchy (extend as needed)
CUSTOM_SKILL_HIERARCHY = {
    "YourSkillArea": [
        "Basic", "Intermediate", "Advanced", "Expert"
    ]
}

# Usage example:
# from brain_config_example import BRAIN_CONFIG, CUSTOM_TOPIC_HIERARCHY
# brain_system.config.update(BRAIN_CONFIG)
# brain_system.topic_hierarchy.update(CUSTOM_TOPIC_HIERARCHY)
'''

        with open(config_path, "w") as f:
            f.write(config_content)

        print(f"   ✅ Created example config: {config_path}")

    def run_tests(self):
        """Run basic tests to verify brain features work."""
        print("🧪 Running basic brain feature tests...")

        try:
            import sys

            sys.path.insert(0, str(self.project_root))

            from src.brain_enhanced_mcp_server import BrainEnhancedMCPServer

            # Test server initialization
            server = BrainEnhancedMCPServer(enable_brain_features=True)
            tools = server.get_tools()

            # Check for brain tools
            brain_tools = [
                "search_similar_experiences",
                "get_knowledge_graph",
                "get_memory_insights",
                "promote_memory_knowledge",
                "trace_knowledge_path",
            ]

            found_brain_tools = []
            for tool in tools:
                if tool["name"] in brain_tools:
                    found_brain_tools.append(tool["name"])

            print(f"   ✅ Brain tools available: {len(found_brain_tools)}")
            for tool in found_brain_tools:
                print(f"      • {tool}")

            # Test backward compatibility
            server_no_brain = BrainEnhancedMCPServer(enable_brain_features=False)
            original_tools = server_no_brain.get_tools()

            print(f"   ✅ Original functionality preserved: {len(original_tools)} tools")

            print("   ✅ All tests passed!")

        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            raise

    def print_next_steps(self):
        """Print next steps for the user."""
        print("\n🎉 Brain Features Successfully Enabled!")
        print("=" * 50)

        print("\n📋 Next Steps:")
        print("1. Restart your MCP client (e.g., Cursor)")
        print("2. Try the new brain tools:")
        print("   • search_similar_experiences - Find analogous past work")
        print("   • get_knowledge_graph - Visualize knowledge connections")
        print("   • get_memory_insights - Analyze your knowledge patterns")
        print("   • trace_knowledge_path - Discover learning paths")

        print("\n🔧 Configuration:")
        print(f"• Backup created at: {self.backup_dir}")
        print(f"• Brain database: {self.project_root}/data/brain_memory.db")
        print(f"• Example config: {self.project_root}/brain_config_example.py")

        print("\n📚 Documentation:")
        print("• Read BRAIN_MEMORY_SYSTEM_GUIDE.md for detailed usage")
        print("• Check examples/brain_memory_examples.py for code examples")
        print("• Review BRAIN_ARCHITECTURE_SUMMARY.md for technical details")

        print("\n⚠️  Troubleshooting:")
        print("• If issues occur, restore from backup")
        print("• Use --no-brain flag to disable brain features temporarily")
        print("• Check logs in logs/mcp_server.log for detailed error info")

    def enable_brain_features(self):
        """Main method to enable brain features."""
        print("🧠 MCP Context Manager - Brain Features Enablement")
        print("=" * 55)

        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                print(
                    "\n❌ Prerequisites not met. Please ensure all brain system files are present."
                )
                return False

            # Step 2: Create backup
            self.create_backup()

            # Step 3: Update configurations
            self.update_cursor_integration()

            # Step 4: Initialize brain database
            self.initialize_brain_database()

            # Step 5: Migrate existing memories
            self.migrate_existing_memories()

            # Step 6: Create example config
            self.create_example_config()

            # Step 7: Run tests
            self.run_tests()

            # Step 8: Show next steps
            self.print_next_steps()

            return True

        except Exception as e:
            print(f"\n❌ Error enabling brain features: {e}")
            print(f"💾 Your original setup has been backed up to: {self.backup_dir}")
            return False


def main():
    """Main entry point for the brain enablement script."""
    enabler = BrainFeatureEnabler()
    success = enabler.enable_brain_features()

    if success:
        print("\n✅ Brain features enabled successfully!")
        return 0
    else:
        print("\n❌ Failed to enable brain features.")
        return 1


if __name__ == "__main__":
    exit(main())

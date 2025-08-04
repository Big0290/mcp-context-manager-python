#!/usr/bin/env python3
"""
Migration script to transfer existing memories to the brain extension system.
"""

import json
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config


def migrate_memories():
    """Migrate memories from old system to brain extension."""
    print("🧠 Starting brain extension migration...")

    # Source database (where memories currently are)
    source_db = Config.SIMPLE_DB_PATH
    target_db = Config.SIMPLE_DB_PATH  # Same database, but with new structure

    if not source_db.exists():
        print(f"❌ Source database not found: {source_db}")
        return False

    try:
        # Connect to source database
        source_conn = sqlite3.connect(source_db)
        source_cursor = source_conn.cursor()

        # Check if memories table exists and has data
        source_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='memories'"
        )
        if not source_cursor.fetchone():
            print("❌ No memories table found in source database")
            return False

        # Get memory count
        source_cursor.execute("SELECT COUNT(*) FROM memories")
        memory_count = source_cursor.fetchone()[0]
        print(f"📊 Found {memory_count} memories to migrate")

        if memory_count == 0:
            print("✅ No memories to migrate")
            return True

        # Get all memories
        source_cursor.execute(
            """
            SELECT content, memory_type, priority, tags, project_id, created_at
            FROM memories
            ORDER BY created_at
        """
        )
        memories = source_cursor.fetchall()

        # Connect to target database (same file, but ensure new structure)
        target_conn = sqlite3.connect(target_db)
        target_cursor = target_conn.cursor()

        # Ensure target tables exist
        target_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'fact',
                priority TEXT DEFAULT 'medium',
                tags TEXT DEFAULT '[]',
                project_id TEXT DEFAULT 'default',
                agent_id TEXT DEFAULT 'cursor-agent',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE,
                custom_metadata TEXT DEFAULT '{}'
            )
        """
        )

        target_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_message TEXT,
                ai_response TEXT,
                context_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        target_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS brain_synapses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER,
                related_memory_id INTEGER,
                synapse_strength REAL DEFAULT 1.0,
                synapse_type TEXT DEFAULT 'association',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories (id),
                FOREIGN KEY (related_memory_id) REFERENCES memories (id)
            )
        """
        )

        # Check if target already has memories
        target_cursor.execute("SELECT COUNT(*) FROM memories")
        existing_count = target_cursor.fetchone()[0]

        if existing_count > 0:
            print(f"⚠️  Target database already has {existing_count} memories")
            response = input("Do you want to continue? (y/N): ")
            if response.lower() != "y":
                print("Migration cancelled")
                return False

        # Migrate memories
        migrated_count = 0
        for memory in memories:
            content, memory_type, priority, tags, project_id, created_at = memory

            # Ensure tags is valid JSON
            if tags and not tags.startswith("["):
                tags = "[]"

            # Insert into target database with default agent_id
            target_cursor.execute(
                """
                INSERT INTO memories (content, memory_type, priority, tags, project_id, agent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    content,
                    memory_type,
                    priority,
                    tags,
                    project_id,
                    "cursor-agent",
                    created_at,
                ),
            )

            migrated_count += 1
            if migrated_count % 10 == 0:
                print(f"📦 Migrated {migrated_count}/{memory_count} memories...")

        target_conn.commit()
        print(f"✅ Successfully migrated {migrated_count} memories to brain extension")

        # Create some brain synapses for related memories
        print("🔗 Creating brain synapses for related memories...")
        create_brain_synapses(target_cursor)
        target_conn.commit()

        # Close connections
        source_conn.close()
        target_conn.close()

        print("🎉 Brain extension migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def create_brain_synapses(cursor):
    """Create brain synapses between related memories."""
    # Get all memories
    cursor.execute("SELECT id, content, tags FROM memories WHERE is_deleted = FALSE")
    memories = cursor.fetchall()

    synapse_count = 0
    for i, (memory_id, content, tags) in enumerate(memories):
        # Find related memories based on tags
        if tags and tags != "[]":
            try:
                tags_list = json.loads(tags)
                for tag in tags_list:
                    # Find other memories with similar tags
                    cursor.execute(
                        """
                        SELECT id FROM memories
                        WHERE id != ? AND tags LIKE ? AND is_deleted = FALSE
                        LIMIT 3
                    """,
                        (memory_id, f"%{tag}%"),
                    )

                    related_memories = cursor.fetchall()
                    for (related_memory_id,) in related_memories:
                        # Check if synapse already exists
                        cursor.execute(
                            """
                            SELECT id FROM brain_synapses
                            WHERE memory_id = ? AND related_memory_id = ?
                        """,
                            (memory_id, related_memory_id),
                        )

                        if not cursor.fetchone():
                            cursor.execute(
                                """
                                INSERT INTO brain_synapses (memory_id, related_memory_id, synapse_strength, synapse_type)
                                VALUES (?, ?, ?, ?)
                            """,
                                (memory_id, related_memory_id, 0.8, "tag_association"),
                            )
                            synapse_count += 1
            except json.JSONDecodeError:
                continue

    print(f"🔗 Created {synapse_count} brain synapses")


def test_brain_extension():
    """Test the brain extension functionality."""
    print("🧪 Testing brain extension...")

    db_path = Config.SIMPLE_DB_PATH

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test memory retrieval
        cursor.execute("SELECT COUNT(*) FROM memories WHERE is_deleted = FALSE")
        memory_count = cursor.fetchone()[0]
        print(f"📊 Total memories: {memory_count}")

        # Test recent memories
        cursor.execute(
            """
            SELECT content, memory_type, priority, tags
            FROM memories
            WHERE is_deleted = FALSE
            ORDER BY created_at DESC
            LIMIT 3
        """
        )
        recent_memories = cursor.fetchall()

        print("📝 Recent memories:")
        for memory in recent_memories:
            content, memory_type, priority, tags = memory
            print(f"  • [{priority.upper()}] {content[:50]}...")
            print(f"    Type: {memory_type}, Tags: {tags}")

        # Test brain synapses
        cursor.execute("SELECT COUNT(*) FROM brain_synapses")
        synapse_count = cursor.fetchone()[0]
        print(f"🔗 Brain synapses: {synapse_count}")

        conn.close()
        print("✅ Brain extension test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Brain extension test failed: {e}")
        return False


def main():
    """Main migration function."""
    print("🧠 Brain Extension Migration Tool")
    print("=" * 40)

    # Check if migration is needed
    db_path = Config.SIMPLE_DB_PATH
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    # Run migration
    if migrate_memories():
        print("\n🧪 Testing brain extension...")
        test_brain_extension()

        print("\n🎉 Migration Summary:")
        print("✅ Memories migrated to brain extension")
        print("✅ Brain synapses created")
        print("✅ Database structure updated")
        print("\n🚀 Your brain extension is ready!")
        print("Use Cmd+Shift+C to get context summary")
        print("Use Cmd+Shift+P to craft AI prompts")
        print("Use Cmd+Shift+M to search memories")
        print("Use Cmd+Shift+A to add memories")
        print("Use Cmd+Shift+S to see brain stats")
    else:
        print("❌ Migration failed")


if __name__ == "__main__":
    main()

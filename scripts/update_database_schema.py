#!/usr/bin/env python3
"""
Update database schema to support brain extension features.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config


def update_schema():
    """Update database schema to support brain extension."""
    print("🔧 Updating database schema...")
    
    db_path = Config.SIMPLE_DB_PATH
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(memories)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns: {columns}")
        
        # Add missing columns if they don't exist
        if 'agent_id' not in columns:
            print("➕ Adding agent_id column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN agent_id TEXT DEFAULT 'cursor-agent'")
        
        if 'updated_at' not in columns:
            print("➕ Adding updated_at column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN updated_at TEXT")
            # Update existing rows with current timestamp
            cursor.execute("UPDATE memories SET updated_at = created_at WHERE updated_at IS NULL")
        
        if 'is_deleted' not in columns:
            print("➕ Adding is_deleted column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN is_deleted INTEGER DEFAULT 0")
        
        if 'custom_metadata' not in columns:
            print("➕ Adding custom_metadata column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN custom_metadata TEXT DEFAULT '{}'")
        
        # Create conversations table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
        if not cursor.fetchone():
            print("➕ Creating conversations table...")
            cursor.execute('''
                CREATE TABLE conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    user_message TEXT,
                    ai_response TEXT,
                    context_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Create brain_synapses table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='brain_synapses'")
        if not cursor.fetchone():
            print("➕ Creating brain_synapses table...")
            cursor.execute('''
                CREATE TABLE brain_synapses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER,
                    related_memory_id INTEGER,
                    synapse_strength REAL DEFAULT 1.0,
                    synapse_type TEXT DEFAULT 'association',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory_id) REFERENCES memories (id),
                    FOREIGN KEY (related_memory_id) REFERENCES memories (id)
                )
            ''')
        
        conn.commit()
        
        # Verify updated schema
        cursor.execute("PRAGMA table_info(memories)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns: {updated_columns}")
        
        # Check table counts
        cursor.execute("SELECT COUNT(*) FROM memories")
        memory_count = cursor.fetchone()[0]
        print(f"📊 Total memories: {memory_count}")
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        print(f"💬 Total conversations: {conversation_count}")
        
        cursor.execute("SELECT COUNT(*) FROM brain_synapses")
        synapse_count = cursor.fetchone()[0]
        print(f"🔗 Total brain synapses: {synapse_count}")
        
        conn.close()
        print("✅ Database schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        return False


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
        cursor.execute("""
            SELECT content, memory_type, priority, tags 
            FROM memories 
            WHERE is_deleted = FALSE 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
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
    """Main function."""
    print("🔧 Database Schema Update Tool")
    print("=" * 40)
    
    # Update schema
    if update_schema():
        print("\n🧪 Testing brain extension...")
        test_brain_extension()
        
        print("\n🎉 Schema Update Summary:")
        print("✅ Database schema updated")
        print("✅ Brain extension tables created")
        print("✅ All columns added successfully")
        print("\n🚀 Your brain extension is ready!")
    else:
        print("❌ Schema update failed")


if __name__ == "__main__":
    main() 
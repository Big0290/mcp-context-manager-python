#!/usr/bin/env python3
"""
Memory Migration Script for MCP Context Manager

This script migrates memories from old project IDs to the new project ID
after a project has been renamed. It handles both simple and full database types.
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config


class MemoryMigrator:
    """Handles migration of memories between project IDs."""

    def __init__(self, new_project_id: str, backup_dir: Optional[str] = None):
        self.new_project_id = new_project_id
        self.backup_dir = (
            backup_dir or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.data_dir = Config.DATA_DIR
        self.migration_log = []

    def discover_old_project_ids(self) -> List[str]:
        """Discover all project IDs in existing databases."""
        old_project_ids = set()

        # Check simple database
        simple_db_path = Config.SIMPLE_DB_PATH
        if simple_db_path.exists():
            try:
                with sqlite3.connect(simple_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()

                    if any("memories" in table[0].lower() for table in tables):
                        cursor.execute(
                            "SELECT DISTINCT project_id FROM memories WHERE project_id != ?",
                            (self.new_project_id,),
                        )
                        old_project_ids.update(row[0] for row in cursor.fetchall())

            except Exception as e:
                self.migration_log.append(f"Error reading simple database: {e}")

        # Check full database
        full_db_path = Config.FULL_DB_PATH
        if full_db_path.exists():
            try:
                with sqlite3.connect(full_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()

                    if any("memories" in table[0].lower() for table in tables):
                        cursor.execute(
                            "SELECT DISTINCT project_id FROM memories WHERE project_id != ?",
                            (self.new_project_id,),
                        )
                        old_project_ids.update(row[0] for row in cursor.fetchall())

            except Exception as e:
                self.migration_log.append(f"Error reading full database: {e}")

        return list(old_project_ids)

    def backup_databases(self) -> bool:
        """Create backup of existing databases."""
        try:
            backup_path = Path(self.backup_dir)
            backup_path.mkdir(exist_ok=True)

            # Backup simple database
            simple_db_path = Config.SIMPLE_DB_PATH
            if simple_db_path.exists():
                backup_file = (
                    backup_path
                    / f"simple_mcp_memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )
                shutil.copy2(simple_db_path, backup_file)
                self.migration_log.append(
                    f"Backed up simple database to: {backup_file}"
                )

            # Backup full database
            full_db_path = Config.FULL_DB_PATH
            if full_db_path.exists():
                backup_file = (
                    backup_path
                    / f"mcp_memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )
                shutil.copy2(full_db_path, backup_file)
                self.migration_log.append(f"Backed up full database to: {backup_file}")

            return True

        except Exception as e:
            self.migration_log.append(f"Error creating backup: {e}")
            return False

    def migrate_simple_database(self, old_project_ids: List[str]) -> Dict[str, int]:
        """Migrate memories in simple database."""
        migration_stats = {}
        simple_db_path = Config.SIMPLE_DB_PATH

        if not simple_db_path.exists():
            self.migration_log.append("Simple database not found")
            return migration_stats

        try:
            with sqlite3.connect(simple_db_path) as conn:
                cursor = conn.cursor()

                for old_project_id in old_project_ids:
                    # Get memories for this project ID (simple schema)
                    cursor.execute(
                        """
                        SELECT id, content, memory_type, priority, tags, project_id, created_at
                        FROM memories
                        WHERE project_id = ?
                    """,
                        (old_project_id,),
                    )

                    memories = cursor.fetchall()
                    migrated_count = 0

                    for memory in memories:
                        try:
                            # Insert with new project ID (simple schema)
                            cursor.execute(
                                """
                                INSERT INTO memories (
                                    content, memory_type, priority, tags, project_id, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    memory[1],
                                    memory[2],
                                    memory[3],
                                    memory[4],
                                    self.new_project_id,
                                    memory[6],
                                ),
                            )
                            migrated_count += 1

                        except sqlite3.IntegrityError:
                            # Memory already exists with new project ID, skip
                            continue

                    migration_stats[old_project_id] = migrated_count
                    self.migration_log.append(
                        f"Migrated {migrated_count} memories from '{old_project_id}' to '{self.new_project_id}'"
                    )

                conn.commit()

        except Exception as e:
            self.migration_log.append(f"Error migrating simple database: {e}")

        return migration_stats

    def migrate_full_database(self, old_project_ids: List[str]) -> Dict[str, int]:
        """Migrate memories in full database."""
        migration_stats = {}
        full_db_path = Config.FULL_DB_PATH

        if not full_db_path.exists():
            self.migration_log.append("Full database not found")
            return migration_stats

        try:
            with sqlite3.connect(full_db_path) as conn:
                cursor = conn.cursor()

                for old_project_id in old_project_ids:
                    # Get memories for this project ID
                    cursor.execute(
                        """
                        SELECT id, agent_id, content, memory_type, priority, tags,
                               custom_metadata, embedding, similarity_score, is_short_term,
                               is_deleted, created_at, updated_at
                        FROM memories
                        WHERE project_id = ?
                    """,
                        (old_project_id,),
                    )

                    memories = cursor.fetchall()
                    migrated_count = 0

                    for memory in memories:
                        try:
                            # Insert with new project ID
                            cursor.execute(
                                """
                                INSERT INTO memories (
                                    id, agent_id, project_id, content, memory_type, priority,
                                    tags, custom_metadata, embedding, similarity_score,
                                    is_short_term, is_deleted, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    memory[0],
                                    memory[1],
                                    self.new_project_id,
                                    memory[2],
                                    memory[3],
                                    memory[4],
                                    memory[5],
                                    memory[6],
                                    memory[7],
                                    memory[8],
                                    memory[9],
                                    memory[10],
                                    memory[11],
                                    memory[12],
                                ),
                            )
                            migrated_count += 1

                        except sqlite3.IntegrityError:
                            # Memory already exists with new project ID, skip
                            continue

                    migration_stats[old_project_id] = migrated_count
                    self.migration_log.append(
                        f"Migrated {migrated_count} memories from '{old_project_id}' to '{self.new_project_id}'"
                    )

                conn.commit()

        except Exception as e:
            self.migration_log.append(f"Error migrating full database: {e}")

        return migration_stats

    def validate_migration(self) -> bool:
        """Validate that migration was successful."""
        try:
            # Check simple database
            simple_db_path = Config.SIMPLE_DB_PATH
            if simple_db_path.exists():
                with sqlite3.connect(simple_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM memories WHERE project_id = ?",
                        (self.new_project_id,),
                    )
                    simple_count = cursor.fetchone()[0]
                    self.migration_log.append(
                        f"Simple database: {simple_count} memories for new project ID"
                    )

            # Check full database
            full_db_path = Config.FULL_DB_PATH
            if full_db_path.exists():
                with sqlite3.connect(full_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM memories WHERE project_id = ?",
                        (self.new_project_id,),
                    )
                    full_count = cursor.fetchone()[0]
                    self.migration_log.append(
                        f"Full database: {full_count} memories for new project ID"
                    )

            return True

        except Exception as e:
            self.migration_log.append(f"Error validating migration: {e}")
            return False

    def run_migration(self, dry_run: bool = False) -> bool:
        """Run the complete migration process."""
        print(f"🔍 Starting memory migration to project ID: {self.new_project_id}")

        # Discover old project IDs
        old_project_ids = self.discover_old_project_ids()
        if not old_project_ids:
            print("✅ No old project IDs found to migrate")
            return True

        print(
            f"📋 Found {len(old_project_ids)} old project IDs: {', '.join(old_project_ids)}"
        )

        if dry_run:
            print("🔍 DRY RUN - No changes will be made")
            return True

        # Create backup
        print("💾 Creating database backup...")
        if not self.backup_databases():
            print("❌ Failed to create backup. Aborting migration.")
            return False

        # Migrate simple database
        print("🔄 Migrating simple database...")
        simple_stats = self.migrate_simple_database(old_project_ids)

        # Migrate full database
        print("🔄 Migrating full database...")
        full_stats = self.migrate_full_database(old_project_ids)

        # Validate migration
        print("✅ Validating migration...")
        if not self.validate_migration():
            print("❌ Migration validation failed")
            return False

        # Print summary
        print("\n📊 Migration Summary:")
        print(f"New Project ID: {self.new_project_id}")
        print(f"Old Project IDs: {', '.join(old_project_ids)}")

        total_migrated = sum(simple_stats.values()) + sum(full_stats.values())
        print(f"Total memories migrated: {total_migrated}")

        if simple_stats:
            print("Simple database migrations:")
            for project_id, count in simple_stats.items():
                print(f"  - {project_id}: {count} memories")

        if full_stats:
            print("Full database migrations:")
            for project_id, count in full_stats.items():
                print(f"  - {project_id}: {count} memories")

        print(f"\n📝 Migration log saved to: {self.backup_dir}/migration_log.txt")

        # Save migration log
        log_file = Path(self.backup_dir) / "migration_log.txt"
        with open(log_file, "w") as f:
            f.write(f"Memory Migration Log - {datetime.now()}\n")
            f.write(f"New Project ID: {self.new_project_id}\n")
            f.write(f"Old Project IDs: {', '.join(old_project_ids)}\n\n")
            for log_entry in self.migration_log:
                f.write(f"{log_entry}\n")

        return True


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description="Migrate memories between project IDs")
    parser.add_argument(
        "--new-project-id",
        default="mcp-context-manager-python",
        help="New project ID to migrate memories to",
    )
    parser.add_argument("--backup-dir", help="Directory for database backups")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only discover old project IDs without migrating",
    )

    args = parser.parse_args()

    # Ensure data directory exists
    Config.ensure_directories()

    migrator = MemoryMigrator(args.new_project_id, args.backup_dir)

    if args.discover_only:
        old_project_ids = migrator.discover_old_project_ids()
        if old_project_ids:
            print(f"Found {len(old_project_ids)} old project IDs:")
            for project_id in old_project_ids:
                print(f"  - {project_id}")
        else:
            print("No old project IDs found")
        return

    success = migrator.run_migration(dry_run=args.dry_run)

    if success:
        print("\n✅ Migration completed successfully!")
        if not args.dry_run:
            print(
                "🔄 You may need to restart your MCP server for changes to take effect"
            )
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

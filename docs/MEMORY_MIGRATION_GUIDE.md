# Memory Migration Guide

This guide explains how to use the memory migration script to move memories from old project IDs to the new project ID after a project has been renamed.

## Overview

When you rename a project, the project ID changes, which can cause the automatic context injection to stop working because memories are stored under the old project ID. The migration script helps you move these memories to the new project ID.

## Quick Start

### 1. Discover Old Project IDs

First, let's see what old project IDs exist in your databases:

```bash
python scripts/migrate_project_memories.py --discover-only
```

This will show you all the old project IDs that have memories stored in them.

### 2. Dry Run Migration

Before making any changes, run a dry run to see what would be migrated:

```bash
python scripts/migrate_project_memories.py --dry-run
```

This will show you exactly what memories would be migrated without making any changes.

### 3. Run the Migration

Once you're satisfied with the dry run results, run the actual migration:

```bash
python scripts/migrate_project_memories.py
```

## Command Line Options

| Option             | Description                                        | Default                      |
| ------------------ | -------------------------------------------------- | ---------------------------- |
| `--new-project-id` | New project ID to migrate memories to              | `mcp-context-manager-python` |
| `--backup-dir`     | Directory for database backups                     | `backup_YYYYMMDD_HHMMSS`     |
| `--dry-run`        | Show what would be migrated without making changes | `False`                      |
| `--discover-only`  | Only discover old project IDs without migrating    | `False`                      |

## Examples

### Basic Migration

```bash
# Migrate to default project ID
python scripts/migrate_project_memories.py
```

### Custom Project ID

```bash
# Migrate to a specific project ID
python scripts/migrate_project_memories.py --new-project-id "my-new-project"
```

### Custom Backup Directory

```bash
# Use a specific backup directory
python scripts/migrate_project_memories.py --backup-dir "my_backups"
```

### Discover Only

```bash
# Just see what old project IDs exist
python scripts/migrate_project_memories.py --discover-only
```

### Dry Run

```bash
# See what would be migrated without making changes
python scripts/migrate_project_memories.py --dry-run
```

## What the Script Does

1. **Discovers Old Project IDs**: Searches both simple and full databases for memories stored under different project IDs
2. **Creates Backups**: Automatically backs up your databases before making any changes
3. **Migrates Memories**: Copies memories from old project IDs to the new project ID
4. **Validates Migration**: Checks that the migration was successful
5. **Generates Logs**: Creates detailed logs of the migration process

## Safety Features

- **Automatic Backups**: Databases are backed up before any changes
- **Dry Run Mode**: Test the migration without making changes
- **Duplicate Prevention**: Won't create duplicate memories if they already exist
- **Detailed Logging**: Full migration log is saved for reference
- **Error Handling**: Graceful error handling with rollback information

## After Migration

1. **Restart MCP Server**: You may need to restart your MCP server for changes to take effect
2. **Test Context Injection**: Try triggering context injection to verify it's working
3. **Check Logs**: Review the migration log in the backup directory if needed

## Troubleshooting

### No Old Project IDs Found

If the script doesn't find any old project IDs, it might mean:

- The project was never renamed
- Memories were already migrated
- The databases are empty

### Migration Fails

If migration fails:

1. Check the error messages in the console
2. Review the migration log in the backup directory
3. Restore from backup if needed
4. Check database permissions

### Context Injection Still Not Working

After migration:

1. Restart your MCP server
2. Check that the project ID in `cursor_integration.json` matches the new project ID
3. Verify that memories exist for the new project ID
4. Test manual context injection first

## Backup and Restore

### Backup Location

Backups are stored in a timestamped directory (e.g., `backup_20241201_143022/`)

### Restore from Backup

If you need to restore from backup:

```bash
# Stop the MCP server first
cp backup_YYYYMMDD_HHMMSS/simple_mcp_memory_backup_*.db data/simple_mcp_memory.db
cp backup_YYYYMMDD_HHMMSS/mcp_memory_backup_*.db data/mcp_memory.db
```

## Database Types

The script handles two types of databases:

1. **Simple Database** (`simple_mcp_memory.db`): Used by the simple MCP server
2. **Full Database** (`mcp_memory.db`): Used by the full MCP server

Both databases are backed up and migrated independently.

## Migration Log

The migration log contains:

- Timestamp of migration
- Old and new project IDs
- Number of memories migrated per project ID
- Any errors or warnings
- Validation results

The log is saved as `migration_log.txt` in the backup directory.

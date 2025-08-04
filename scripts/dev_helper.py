#!/usr/bin/env python3
"""
Developer Helper Script
Provides quick access to common development tasks in the organized project structure.
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def run_command(cmd, description):
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False


def main():
    print_header("MCP Context Manager Python - Developer Helper")

    print("\n📁 Project Structure Overview:")
    print("├── src/           - Main source code")
    print("├── mcp_memory_server/ - Memory server implementation")
    print("├── tests/         - Test suite")
    print("├── examples/      - Usage examples")
    print("├── debug/         - Debugging tools")
    print("├── scripts/       - Utility scripts")
    print("├── docs/          - Documentation")
    print("├── data/          - Database files")
    print("└── logs/          - Application logs")

    print("\n🚀 Quick Actions:")
    print("1. Setup development environment")
    print("2. Run tests")
    print("3. Start server")
    print("4. Run examples")
    print("5. Debug context injection")
    print("6. View project structure")
    print("7. Exit")

    while True:
        try:
            choice = input("\nSelect an action (1-7): ").strip()

            if choice == "1":
                print_header("Setting up development environment")
                run_command("python scripts/setup_dev.py", "Running development setup")

            elif choice == "2":
                print_header("Running tests")
                run_command("python -m pytest tests/ -v", "Running test suite")

            elif choice == "3":
                print_header("Starting server")
                print("Choose server type:")
                print("1. Simple MCP Server")
                print("2. Full MCP Server")
                server_choice = input("Select (1-2): ").strip()

                if server_choice == "1":
                    run_command(
                        "python src/simple_mcp_server.py", "Starting simple MCP server"
                    )
                elif server_choice == "2":
                    run_command("python src/mcp_server.py", "Starting full MCP server")
                else:
                    print("Invalid choice")

            elif choice == "4":
                print_header("Running examples")
                print("Available examples:")
                examples = [
                    "examples/example_usage.py",
                    "examples/context_injection_example.py",
                    "examples/ai_prompt_crafting_example.py",
                    "examples/intelligent_context_injection_example.py",
                ]

                for i, example in enumerate(examples, 1):
                    print(f"{i}. {example}")

                example_choice = input("Select example (1-4): ").strip()
                try:
                    example_idx = int(example_choice) - 1
                    if 0 <= example_idx < len(examples):
                        run_command(
                            f"python {examples[example_idx]}",
                            f"Running {examples[example_idx]}",
                        )
                    else:
                        print("Invalid choice")
                except ValueError:
                    print("Invalid choice")

            elif choice == "5":
                print_header("Debugging context injection")
                run_command(
                    "python debug/debug_context_injection.py",
                    "Running context injection debug",
                )

            elif choice == "6":
                print_header("Project Structure")
                run_command(
                    "find . -type f -name '*.py' | head -20", "Showing Python files"
                )

            elif choice == "7":
                print("\n👋 Goodbye!")
                break

            else:
                print("Invalid choice. Please select 1-7.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

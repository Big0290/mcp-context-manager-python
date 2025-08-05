#!/usr/bin/env python3
"""
Brain Enhancement Demo for MCP Server
Demonstrates all brain-like enhancement features working together.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brain_enhancement_integration import BrainEnhancementIntegration
from src.brain_memory_system import BrainMemorySystem


async def demo_brain_enhancements():
    """Demonstrate all brain-like enhancement features."""

    print("🧠 Brain Enhancement Demo for MCP Server")
    print("=" * 50)

    # Initialize brain enhancement integration
    brain_integration = BrainEnhancementIntegration(enable_all_features=True)

    # Demo 1: Identity and Emotional State
    print("\n1️⃣ Identity and Emotional State")
    print("-" * 30)

    identity_summary = brain_integration.get_identity_summary()
    print(f"Agent Name: {identity_summary['name']}")
    print(f"Role: {identity_summary['role']}")
    print(f"Emotional Summary: {identity_summary['emotional_summary']}")

    # Update emotional state
    brain_integration.update_emotional_state(
        joy=0.8, curiosity=0.9, confidence=0.7, energy_level=0.9
    )

    print("✅ Updated emotional state with joy, curiosity, and confidence")

    # Demo 2: Session Management
    print("\n2️⃣ Session Management")
    print("-" * 30)

    session_id = brain_integration.create_session(
        user_id="demo_user", project_id="brain_demo_project"
    )
    print(f"Created session: {session_id}")

    session_data = brain_integration.get_session_data(session_id)
    print(f"Session data: {json.dumps(session_data, indent=2)}")

    # Demo 3: Experience Logging
    print("\n3️⃣ Experience Logging")
    print("-" * 30)

    # Log some experiences
    experience_id1 = brain_integration.experience_logger.log_successful_task(
        task_description="Successfully implemented brain enhancement features",
        task_type="development",
        solution_source="new_creation",
        project_id="brain_demo_project",
        session_id=session_id,
        skills_used=["brain_enhancement", "memory_system", "emotional_learning"],
        patterns_recognized=["brain_like_architecture"],
    )

    experience_id2 = brain_integration.experience_logger.log_learning_experience(
        task_description="Learned about emotional tagging in memory systems",
        knowledge_gained=["emotional_learning", "memory_prioritization"],
        project_id="brain_demo_project",
        session_id=session_id,
    )

    print(f"Logged successful task: {experience_id1}")
    print(f"Logged learning experience: {experience_id2}")

    # Demo 4: Memory Search with Brain
    print("\n4️⃣ Brain-Enhanced Memory Search")
    print("-" * 30)

    search_results = await brain_integration.search_memories_with_brain(
        query="brain enhancement features",
        project_id="brain_demo_project",
        search_tags=["brain", "enhancement", "memory"],
        max_results=5,
    )

    print(f"Found {search_results['results_count']} relevant memories")
    for i, result in enumerate(search_results["results"][:3]):
        print(
            f"  {i+1}. {result['content'][:50]}... (relevance: {result['relevance_score']:.2f})"
        )

    # Demo 5: Emotional Learning
    print("\n5️⃣ Emotional Learning")
    print("-" * 30)

    # Add emotional tags to memories
    await brain_integration.add_emotional_tag(
        memory_id="demo_memory_1",
        emotion_type="joy",
        intensity=0.8,
        context="successful_brain_enhancement_implementation",
    )

    await brain_integration.add_emotional_tag(
        memory_id="demo_memory_2",
        emotion_type="curiosity",
        intensity=0.7,
        context="learning_about_emotional_learning",
    )

    # Get joyful memories
    joyful_memories = brain_integration.get_joyful_memories(limit=5)
    print(f"Found {len(joyful_memories)} joyful memories")

    # Demo 6: Cognitive Loop Processing
    print("\n6️⃣ Cognitive Loop Processing")
    print("-" * 30)

    # Process some tasks through the cognitive loop
    tasks = [
        {
            "description": "Debug a Python memory leak issue",
            "type": "debugging",
            "priority": 0.8,
        },
        {
            "description": "Learn about new brain-like AI architectures",
            "type": "learning",
            "priority": 0.6,
        },
        {
            "description": "Create a new brain enhancement feature",
            "type": "creation",
            "priority": 0.9,
        },
    ]

    for task in tasks:
        result = await brain_integration.process_task_with_brain(
            task_description=task["description"],
            task_type=task["type"],
            priority=task["priority"],
            project_id="brain_demo_project",
            session_id=session_id,
        )

        print(f"Task: {task['description']}")
        print(f"  Decision: {result['decision']['type'].value}")
        print(f"  Confidence: {result['decision']['confidence']:.2f}")
        print(f"  Reasoning: {result['decision']['reasoning']}")
        print(f"  Processing time: {result['processing_time']:.3f}s")
        print()

    # Demo 7: Get Summaries and Statistics
    print("\n7️⃣ Brain Enhancement Summaries")
    print("-" * 30)

    # Get emotional learning summary
    emotional_summary = brain_integration.get_emotional_learning_summary()
    print("Emotional Learning Summary:")
    print(emotional_summary)

    # Get cognitive summary
    cognitive_summary = brain_integration.get_cognitive_summary()
    print("\nCognitive Loop Summary:")
    print(cognitive_summary)

    # Get experience summary
    experience_summary = brain_integration.get_experience_summary("brain_demo_project")
    print(f"\nExperience Statistics:")
    print(
        f"  Total experiences: {experience_summary['experience_statistics'].get('total_experiences', 0)}"
    )
    print(
        f"  Success rate: {experience_summary['experience_statistics'].get('success_rate', 0):.1%}"
    )

    # Demo 8: Brain Enhancement Status
    print("\n8️⃣ Complete Brain Enhancement Status")
    print("-" * 30)

    status = brain_integration.get_brain_enhancement_status()
    print("Brain Enhancement Modules:")
    for module, enabled in status["modules"].items():
        status_icon = "✅" if enabled else "❌"
        print(f"  {status_icon} {module}")

    if status["enabled"]:
        print(f"\nIdentity: {status['identity']['name']}")
        print(f"Current emotional state: {status['identity']['emotional_summary']}")

        if "cognitive" in status:
            print(
                f"Cognitive tasks processed: {status['cognitive'].get('total_tasks_processed', 0)}"
            )
            print(
                f"Most common decision: {status['cognitive'].get('most_common_decision', 'N/A')}"
            )

    # Demo 9: Brain Maintenance
    print("\n9️⃣ Brain Enhancement Maintenance")
    print("-" * 30)

    await brain_integration.run_brain_maintenance()
    print("✅ Brain enhancement maintenance completed")

    print("\n🎉 Brain Enhancement Demo Completed!")
    print("The MCP server now has brain-like capabilities including:")
    print("  • Identity and emotional state management")
    print("  • Session-aware personal data")
    print("  • Experience logging with emotional tagging")
    print("  • Memory cross-referencing and similarity search")
    print("  • Emotional learning and recall prioritization")
    print("  • Human-like decision making and task processing")


async def demo_brain_tools():
    """Demonstrate brain enhancement tools."""

    print("\n🔧 Brain Enhancement Tools Demo")
    print("=" * 40)

    brain_integration = BrainEnhancementIntegration(enable_all_features=True)

    # Get available tools
    tools = brain_integration.get_brain_enhancement_tools()
    print(f"Available brain tools: {len(tools)}")

    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")

    # Demo tool execution
    print("\nExecuting brain tools:")

    # Get brain status
    status_result = await brain_integration.execute_brain_tool("get_brain_status", {})
    print(f"Brain status: {status_result['enabled']}")

    # Process a task
    task_result = await brain_integration.execute_brain_tool(
        "process_task_with_brain",
        {
            "task_description": "Demonstrate brain enhancement tools",
            "task_type": "demo",
            "priority": 0.7,
        },
    )
    print(f"Task processed: {task_result.get('task_id', 'N/A')}")

    # Get identity summary
    identity_result = await brain_integration.execute_brain_tool(
        "get_identity_summary", {}
    )
    print(f"Agent name: {identity_result.get('name', 'N/A')}")

    print("\n✅ Brain tools demo completed!")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demos
    asyncio.run(demo_brain_enhancements())
    asyncio.run(demo_brain_tools())

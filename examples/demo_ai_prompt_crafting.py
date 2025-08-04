#!/usr/bin/env python3
"""
AI Prompt Crafting Demonstration

This script demonstrates how the AI Prompt Crafter uses context summaries
to generate intelligent, contextual prompts for AI interactions.
"""

import asyncio

from src.ai_prompt_crafter import AIPromptCrafter, PromptContext, PromptType


async def demonstrate_ai_prompt_crafting():
    """Demonstrate AI prompt crafting with different scenarios."""
    print("🎯 **AI Prompt Crafting Demonstration**")
    print("=" * 60)

    # Initialize the AI Prompt Crafter
    crafter = AIPromptCrafter()

    # Get current context summary
    print("📋 **Current Context Summary:**")
    context_summary = """📋 **Context Summary for Project: mcp-context-manager-python**
Found 4 relevant memories:

**Threads:**
• [LOW] [USER_MESSAGE] User requested context summary
  Tags: mcp
• [LOW] [USER_MESSAGE] User called tool: start_conversation_recording
• [LOW] [AI_RESPONSE] AI provided response: ✅ Automatic conversation recording started for project: mcp-context-manager-python
User message recording: Enabled
AI response recording: Enabled
  Tags: python

**Facts:**
• [LOW] [AI_RESPONSE] AI provided response: No previous context found for this project. Starting fresh conversation.
  Tags: mcp"""

    print(context_summary)
    print("\n" + "=" * 60)

    # Test scenarios
    scenarios = [
        {
            "name": "Task-Focused Implementation",
            "user_message": "I need to implement a new feature for the MCP memory server",
            "prompt_type": PromptType.TASK_FOCUSED,
            "focus_areas": ["python", "mcp", "memory", "implementation"],
        },
        {
            "name": "Problem-Solving Debugging",
            "user_message": "I'm getting an error when trying to connect to the database",
            "prompt_type": PromptType.PROBLEM_SOLVING,
            "focus_areas": ["database", "error", "debugging", "python"],
        },
        {
            "name": "Educational Explanation",
            "user_message": "Can you explain how the MCP memory system works?",
            "prompt_type": PromptType.EXPLANATION,
            "focus_areas": ["mcp", "memory", "context", "explanation"],
        },
        {
            "name": "Code Review Assessment",
            "user_message": "Please review this code for best practices",
            "prompt_type": PromptType.CODE_REVIEW,
            "focus_areas": ["python", "code-quality", "best-practices"],
        },
        {
            "name": "Continuation of Previous Work",
            "user_message": "Based on our previous work, what should we focus on next?",
            "prompt_type": PromptType.CONTINUATION,
            "focus_areas": ["mcp", "python", "development"],
        },
        {
            "name": "Auto-Detected Problem Solving",
            "user_message": "How do I fix this bug in my React component?",
            "prompt_type": PromptType.GENERAL,  # Will be auto-detected
            "focus_areas": ["react", "javascript", "debugging"],
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎭 **Scenario {i}: {scenario['name']}**")
        print("-" * 50)

        # Create prompt context
        context = PromptContext(
            project_id="mcp-context-manager-python",
            focus_areas=scenario["focus_areas"],
            prompt_type=scenario["prompt_type"],
        )

        # Craft the AI prompt
        crafted_prompt = await crafter.craft_ai_prompt(
            context, scenario["user_message"]
        )

        print("🎯 **Crafted AI Prompt:**")
        print(crafted_prompt)
        print("\n" + "=" * 60)

    # Demonstrate intelligent analysis
    print("\n🧠 **Intelligent Context Analysis**")
    print("-" * 40)

    # Show how the system analyzes context
    analysis = crafter._analyze_context(
        context_summary, "Help me implement a new feature"
    )
    print("📊 **Context Analysis Results:**")
    print(f"• Has Tasks: {analysis['has_tasks']}")
    print(f"• Has Problems: {analysis['has_problems']}")
    print(f"• Has Code: {analysis['has_code']}")
    print(f"• Has Questions: {analysis['has_questions']}")
    print(f"• Priority Levels: {analysis['priority_levels']}")
    print(f"• Technologies: {analysis['technologies']}")
    print(f"• User Intent: {analysis['user_intent']}")
    print(f"• Key Topics: {analysis['key_topics']}")

    print("\n🎉 **Demonstration Complete!**")
    print("\n**Key Features Demonstrated:**")
    print("✅ Context-aware prompt generation")
    print("✅ Multiple prompt types for different scenarios")
    print("✅ Intelligent auto-detection of prompt type")
    print("✅ Focus area filtering")
    print("✅ User message incorporation")
    print("✅ Context analysis and understanding")


def show_prompt_types():
    """Show available prompt types and their characteristics."""
    print("\n🎭 **Available Prompt Types**")
    print("=" * 40)

    prompt_types = [
        {
            "type": PromptType.CONTINUATION,
            "description": "For ongoing conversations and follow-ups",
            "best_for": "Continuing previous work, maintaining context",
        },
        {
            "type": PromptType.TASK_FOCUSED,
            "description": "For implementation and development work",
            "best_for": "Coding, building features, step-by-step guidance",
        },
        {
            "type": PromptType.PROBLEM_SOLVING,
            "description": "For debugging and issue resolution",
            "best_for": "Error fixing, troubleshooting, systematic debugging",
        },
        {
            "type": PromptType.EXPLANATION,
            "description": "For educational and explanatory content",
            "best_for": "Explaining concepts, teaching, documentation",
        },
        {
            "type": PromptType.CODE_REVIEW,
            "description": "For code quality assessment",
            "best_for": "Code review, best practices, optimization",
        },
        {
            "type": PromptType.DEBUGGING,
            "description": "For systematic debugging assistance",
            "best_for": "Step-by-step debugging, error analysis",
        },
        {
            "type": PromptType.GENERAL,
            "description": "For general assistance (auto-detected)",
            "best_for": "General help, auto-detection of intent",
        },
    ]

    for prompt_type in prompt_types:
        print(f"\n📝 **{prompt_type['type'].value.replace('_', ' ').title()}**")
        print(f"Description: {prompt_type['description']}")
        print(f"Best For: {prompt_type['best_for']}")


def main():
    """Main demonstration function."""
    print("🎯 **AI Prompt Crafting with Context Summary**")
    print("=" * 60)

    # Show available prompt types
    show_prompt_types()

    # Run the main demonstration
    asyncio.run(demonstrate_ai_prompt_crafting())


if __name__ == "__main__":
    main()

"""
AI Prompt Crafter Module

This module provides intelligent AI prompt generation using context summaries
from the MCP Memory Server. It analyzes conversation history and crafts
contextual prompts for better AI interactions.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from dataclasses import dataclass
from enum import Enum


class PromptType(Enum):
    """Types of AI prompts that can be crafted."""
    CONTINUATION = "continuation"
    TASK_FOCUSED = "task_focused"
    PROBLEM_SOLVING = "problem_solving"
    EXPLANATION = "explanation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    GENERAL = "general"


@dataclass
class PromptContext:
    """Context information for prompt crafting."""
    project_id: str
    user_intent: Optional[str] = None
    focus_areas: List[str] = None
    max_memories: int = 10
    include_recent: bool = True
    prompt_type: PromptType = PromptType.GENERAL


class AIPromptCrafter:
    """
    Intelligent AI prompt crafter that uses context summaries to generate
    contextual and effective prompts for AI interactions.
    """
    
    def __init__(self, mcp_server=None):
        self.mcp_server = mcp_server
        self.logger = logging.getLogger(__name__)
        
        # Prompt templates for different scenarios
        self.prompt_templates = {
            PromptType.CONTINUATION: self._create_continuation_prompt,
            PromptType.TASK_FOCUSED: self._create_task_focused_prompt,
            PromptType.PROBLEM_SOLVING: self._create_problem_solving_prompt,
            PromptType.EXPLANATION: self._create_explanation_prompt,
            PromptType.CODE_REVIEW: self._create_code_review_prompt,
            PromptType.DEBUGGING: self._create_debugging_prompt,
            PromptType.GENERAL: self._create_general_prompt
        }
    
    async def craft_ai_prompt(self, context: PromptContext, user_message: str = None) -> str:
        """
        Craft an intelligent AI prompt using context summary and user input.
        
        Args:
            context: PromptContext object with project and intent information
            user_message: Optional user message to incorporate into prompt
            
        Returns:
            Crafted AI prompt string
        """
        try:
            # Get context summary from MCP server
            context_summary = await self._get_context_summary(context)
            
            # Analyze context and user intent
            analysis = self._analyze_context(context_summary, user_message)
            
            # Determine prompt type based on analysis
            prompt_type = self._determine_prompt_type(analysis, context.prompt_type)
            
            # Craft the prompt using appropriate template
            crafted_prompt = self.prompt_templates[prompt_type](
                context_summary, analysis, user_message, context
            )
            
            self.logger.info(f"Crafted {prompt_type.value} prompt for project: {context.project_id}")
            return crafted_prompt
            
        except Exception as e:
            self.logger.error(f"Error crafting AI prompt: {e}")
            return self._create_fallback_prompt(context, user_message)
    
    async def _get_context_summary(self, context: PromptContext) -> str:
        """Get context summary from MCP server."""
        if not self.mcp_server:
            return "No MCP server available for context retrieval."
        
        try:
            result = await self.mcp_server._get_context_summary({
                "project_id": context.project_id,
                "max_memories": context.max_memories,
                "include_recent": context.include_recent,
                "focus_areas": context.focus_areas or []
            })
            
            if result.get("isError", False):
                return "Error retrieving context summary."
            
            content = result.get("content", [{}])[0].get("text", "")
            return content if content else "No context available."
            
        except Exception as e:
            self.logger.error(f"Error getting context summary: {e}")
            return "Unable to retrieve context summary."
    
    def _analyze_context(self, context_summary: str, user_message: str = None) -> Dict[str, Any]:
        """Analyze context summary and user message to extract key information."""
        analysis = {
            "has_tasks": False,
            "has_problems": False,
            "has_code": False,
            "has_questions": False,
            "priority_levels": [],
            "technologies": [],
            "user_intent": "general",
            "key_topics": []
        }
        
        # Analyze context summary
        if context_summary:
            analysis["has_tasks"] = "task" in context_summary.lower()
            analysis["has_problems"] = any(word in context_summary.lower() 
                                         for word in ["error", "bug", "issue", "problem", "fix"])
            analysis["has_code"] = any(word in context_summary.lower() 
                                     for word in ["code", "implementation", "function", "class"])
            analysis["has_questions"] = "?" in context_summary
            
            # Extract priority levels
            priority_pattern = r'\[(HIGH|MEDIUM|LOW)\]'
            analysis["priority_levels"] = re.findall(priority_pattern, context_summary)
            
            # Extract technologies
            tech_keywords = ["python", "javascript", "react", "mcp", "sql", "api", "docker"]
            analysis["technologies"] = [tech for tech in tech_keywords 
                                      if tech in context_summary.lower()]
            
            # Extract key topics
            analysis["key_topics"] = self._extract_key_topics(context_summary)
        
        # Analyze user message
        if user_message:
            analysis["user_intent"] = self._determine_user_intent(user_message)
            
            # Update analysis based on user message
            if any(word in user_message.lower() for word in ["explain", "how", "what", "why"]):
                analysis["has_questions"] = True
            if any(word in user_message.lower() for word in ["fix", "error", "bug", "problem"]):
                analysis["has_problems"] = True
            if any(word in user_message.lower() for word in ["implement", "create", "build", "code"]):
                analysis["has_tasks"] = True
        
        return analysis
    
    def _extract_key_topics(self, context_summary: str) -> List[str]:
        """Extract key topics from context summary."""
        topics = []
        
        # Look for common topic indicators
        topic_patterns = [
            r'Tags: ([^,\n]+)',
            r'\*\*([^*]+)\*\*:',
            r'🎯 Key Priorities:',
            r'📋 Context Summary'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, context_summary)
            topics.extend(matches)
        
        return list(set(topics))  # Remove duplicates
    
    def _determine_user_intent(self, user_message: str) -> str:
        """Determine user intent from message."""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["explain", "how", "what", "why"]):
            return "explanation"
        elif any(word in message_lower for word in ["fix", "error", "bug", "problem"]):
            return "problem_solving"
        elif any(word in message_lower for word in ["implement", "create", "build", "code"]):
            return "task"
        elif any(word in message_lower for word in ["review", "check", "examine"]):
            return "review"
        elif any(word in message_lower for word in ["debug", "trace", "log"]):
            return "debugging"
        else:
            return "general"
    
    def _determine_prompt_type(self, analysis: Dict[str, Any], 
                              requested_type: PromptType) -> PromptType:
        """Determine the best prompt type based on analysis."""
        if requested_type != PromptType.GENERAL:
            return requested_type
        
        # Auto-determine based on analysis
        if analysis["has_problems"]:
            return PromptType.PROBLEM_SOLVING
        elif analysis["has_tasks"]:
            return PromptType.TASK_FOCUSED
        elif analysis["has_questions"]:
            return PromptType.EXPLANATION
        elif analysis["has_code"]:
            return PromptType.CODE_REVIEW
        else:
            return PromptType.CONTINUATION
    
    def _create_continuation_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                                   user_message: str, context: PromptContext) -> str:
        """Create a continuation prompt for ongoing conversations."""
        prompt = f"""🤖 **AI Assistant with Context Awareness**

📋 **Previous Conversation Context:**
{context_summary}

🎯 **Current Focus:**
- Project: {context.project_id}
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}
- Priority Level: {analysis['priority_levels'][0] if analysis['priority_levels'] else 'Medium'}

💬 **Your Message:** {user_message if user_message else 'Continue helping with the project'}

**Instructions:** Based on the conversation history and current context, provide a helpful and contextual response. Consider the previous work, priorities, and ongoing tasks when formulating your response.

**Response Guidelines:**
- Acknowledge the context and previous work
- Provide specific, actionable advice
- Reference relevant previous discussions
- Maintain continuity with ongoing tasks
- Be concise but comprehensive

Please continue helping with the project:"""
        
        return prompt
    
    def _create_task_focused_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                                   user_message: str, context: PromptContext) -> str:
        """Create a task-focused prompt for implementation work."""
        prompt = f"""🚀 **Task-Focused AI Assistant**

📋 **Project Context:**
{context_summary}

🎯 **Task Analysis:**
- Project: {context.project_id}
- Task Type: Implementation/Development
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}
- Priority: {analysis['priority_levels'][0] if analysis['priority_levels'] else 'Medium'}

💬 **User Request:** {user_message if user_message else 'Help with implementation'}

**Instructions:** Focus on practical implementation guidance, code examples, and step-by-step solutions. Consider the existing codebase and previous implementations.

**Response Guidelines:**
- Provide specific code examples when relevant
- Include step-by-step implementation steps
- Consider best practices and patterns
- Reference existing code structure
- Address potential challenges and solutions

Ready to help with implementation:"""
        
        return prompt
    
    def _create_problem_solving_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                                     user_message: str, context: PromptContext) -> str:
        """Create a problem-solving focused prompt."""
        prompt = f"""🔧 **Problem-Solving AI Assistant**

📋 **Context & Issues:**
{context_summary}

🎯 **Problem Analysis:**
- Project: {context.project_id}
- Issue Type: Technical Problem/Error
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}
- Priority: {analysis['priority_levels'][0] if analysis['priority_levels'] else 'High'}

💬 **Problem Description:** {user_message if user_message else 'Help solve technical issue'}

**Instructions:** Focus on debugging, error resolution, and technical problem-solving. Provide systematic approaches to identify and fix issues.

**Response Guidelines:**
- Analyze the problem systematically
- Provide debugging steps
- Suggest multiple solution approaches
- Include error prevention strategies
- Reference relevant documentation or resources

Ready to help solve the problem:"""
        
        return prompt
    
    def _create_explanation_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                                  user_message: str, context: PromptContext) -> str:
        """Create an explanation-focused prompt."""
        prompt = f"""📚 **Educational AI Assistant**

📋 **Context for Explanation:**
{context_summary}

🎯 **Explanation Focus:**
- Project: {context.project_id}
- Topics: {', '.join(analysis['key_topics']) if analysis['key_topics'] else 'Various'}
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}

💬 **Question/Topic:** {user_message if user_message else 'Explain relevant concepts'}

**Instructions:** Provide clear, educational explanations with examples and context. Make complex topics accessible and practical.

**Response Guidelines:**
- Start with clear, simple explanations
- Provide practical examples
- Connect to the project context
- Include relevant code examples
- Suggest learning resources

Ready to explain:"""
        
        return prompt
    
    def _create_code_review_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                                  user_message: str, context: PromptContext) -> str:
        """Create a code review focused prompt."""
        prompt = f"""🔍 **Code Review AI Assistant**

📋 **Project Context:**
{context_summary}

🎯 **Review Focus:**
- Project: {context.project_id}
- Code Type: Implementation/Refactoring
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}

💬 **Review Request:** {user_message if user_message else 'Review code or implementation'}

**Instructions:** Provide comprehensive code review with focus on quality, best practices, and improvements.

**Response Guidelines:**
- Review code structure and organization
- Identify potential issues or improvements
- Suggest optimizations and best practices
- Consider security and performance
- Provide specific recommendations

Ready to review code:"""
        
        return prompt
    
    def _create_debugging_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                                user_message: str, context: PromptContext) -> str:
        """Create a debugging focused prompt."""
        prompt = f"""🐛 **Debugging AI Assistant**

📋 **Debugging Context:**
{context_summary}

🎯 **Debug Focus:**
- Project: {context.project_id}
- Issue Type: Bug/Error/Debugging
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}

💬 **Debug Request:** {user_message if user_message else 'Help debug an issue'}

**Instructions:** Provide systematic debugging assistance with step-by-step troubleshooting and error resolution.

**Response Guidelines:**
- Systematic debugging approach
- Step-by-step troubleshooting
- Error analysis and interpretation
- Testing and verification steps
- Prevention strategies

Ready to help debug:"""
        
        return prompt
    
    def _create_general_prompt(self, context_summary: str, analysis: Dict[str, Any], 
                              user_message: str, context: PromptContext) -> str:
        """Create a general-purpose prompt."""
        prompt = f"""🤖 **AI Assistant with Context**

📋 **Conversation Context:**
{context_summary}

🎯 **General Information:**
- Project: {context.project_id}
- Technologies: {', '.join(analysis['technologies']) if analysis['technologies'] else 'Various'}
- Topics: {', '.join(analysis['key_topics']) if analysis['key_topics'] else 'General'}

💬 **User Message:** {user_message if user_message else 'General assistance needed'}

**Instructions:** Provide helpful, contextual assistance based on the conversation history and project context.

**Response Guidelines:**
- Be helpful and informative
- Consider the project context
- Provide relevant suggestions
- Maintain conversation continuity
- Be concise but comprehensive

Ready to help:"""
        
        return prompt
    
    def _create_fallback_prompt(self, context: PromptContext, user_message: str) -> str:
        """Create a fallback prompt when context retrieval fails."""
        prompt = f"""🤖 **AI Assistant**

📋 **Project:** {context.project_id}

💬 **User Message:** {user_message if user_message else 'General assistance needed'}

**Instructions:** Provide helpful assistance for the project. Since context retrieval is unavailable, ask clarifying questions if needed.

**Response Guidelines:**
- Be helpful and informative
- Ask clarifying questions if needed
- Provide general guidance
- Suggest next steps

Ready to help:"""
        
        return prompt


# Utility functions for easy integration
async def craft_prompt_for_project(project_id: str, user_message: str = None, 
                                 prompt_type: PromptType = PromptType.GENERAL,
                                 mcp_server=None) -> str:
    """
    Convenience function to craft a prompt for a specific project.
    
    Args:
        project_id: Project identifier
        user_message: Optional user message
        prompt_type: Type of prompt to craft
        mcp_server: MCP server instance
        
    Returns:
        Crafted AI prompt string
    """
    crafter = AIPromptCrafter(mcp_server)
    context = PromptContext(
        project_id=project_id,
        prompt_type=prompt_type
    )
    
    return await crafter.craft_ai_prompt(context, user_message)


async def craft_intelligent_prompt(project_id: str, user_message: str, 
                                 focus_areas: List[str] = None,
                                 mcp_server=None) -> str:
    """
    Craft an intelligent prompt that auto-detects the best approach.
    
    Args:
        project_id: Project identifier
        user_message: User message to analyze
        focus_areas: Specific areas to focus on
        mcp_server: MCP server instance
        
    Returns:
        Crafted AI prompt string
    """
    crafter = AIPromptCrafter(mcp_server)
    context = PromptContext(
        project_id=project_id,
        focus_areas=focus_areas,
        prompt_type=PromptType.GENERAL  # Will be auto-detected
    )
    
    return await crafter.craft_ai_prompt(context, user_message) 
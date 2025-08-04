# AI Prompt Crafting Guide

## Overview

The AI Prompt Crafter is an intelligent system that uses context summaries from the MCP Memory Server to generate contextual, effective prompts for AI interactions. This feature enhances AI responses by providing rich context and tailored prompt structures for different scenarios.

## 🎯 **What is AI Prompt Crafting?**

AI Prompt Crafting analyzes conversation history and user intent to generate intelligent prompts that:

- **Provide Context**: Include relevant conversation history and project context
- **Match Intent**: Adapt prompt structure based on user's intent (task, problem-solving, explanation, etc.)
- **Focus Areas**: Filter and emphasize specific areas of interest
- **Auto-Detect**: Automatically determine the best prompt type based on content analysis
- **Enhance Responses**: Generate more relevant and contextual AI responses

## 🛠️ **How It Works**

### **1. Context Analysis**

The system analyzes the context summary to understand:

- **Project History**: Previous conversations and work
- **User Intent**: What the user is trying to accomplish
- **Technologies**: Programming languages and tools mentioned
- **Priority Levels**: High, medium, or low priority items
- **Key Topics**: Main themes and subjects

### **2. Intent Detection**

Based on user messages, the system detects:

- **Task-Focused**: Implementation, coding, building features
- **Problem-Solving**: Debugging, error fixing, troubleshooting
- **Explanation**: Educational content, how-to guides
- **Code Review**: Quality assessment, best practices
- **Debugging**: Systematic error resolution
- **Continuation**: Ongoing conversations and follow-ups

### **3. Prompt Generation**

Creates structured prompts with:

- **Context Summary**: Relevant conversation history
- **Focus Areas**: Specific technologies or topics
- **User Message**: The current request
- **Response Guidelines**: Instructions for the AI
- **Project Information**: Current project context

## 📋 **Available Prompt Types**

### **1. Continuation (`continuation`)**

**Best For**: Ongoing conversations and follow-ups

```python
prompt_type = PromptType.CONTINUATION
```

**Characteristics**:

- Maintains conversation continuity
- References previous work
- Provides contextual responses
- Acknowledges ongoing tasks

### **2. Task-Focused (`task_focused`)**

**Best For**: Implementation and development work

```python
prompt_type = PromptType.TASK_FOCUSED
```

**Characteristics**:

- Step-by-step implementation guidance
- Code examples and patterns
- Best practices and solutions
- Practical development advice

### **3. Problem-Solving (`problem_solving`)**

**Best For**: Debugging and issue resolution

```python
prompt_type = PromptType.PROBLEM_SOLVING
```

**Characteristics**:

- Systematic debugging approach
- Error analysis and interpretation
- Multiple solution strategies
- Prevention and best practices

### **4. Explanation (`explanation`)**

**Best For**: Educational and explanatory content

```python
prompt_type = PromptType.EXPLANATION
```

**Characteristics**:

- Clear, simple explanations
- Practical examples
- Learning resources
- Contextual connections

### **5. Code Review (`code_review`)**

**Best For**: Code quality assessment

```python
prompt_type = PromptType.CODE_REVIEW
```

**Characteristics**:

- Code structure analysis
- Best practices review
- Optimization suggestions
- Security considerations

### **6. Debugging (`debugging`)**

**Best For**: Systematic debugging assistance

```python
prompt_type = PromptType.DEBUGGING
```

**Characteristics**:

- Step-by-step troubleshooting
- Error analysis
- Testing and verification
- Prevention strategies

### **7. General (`general`)**

**Best For**: Auto-detection of intent

```python
prompt_type = PromptType.GENERAL
```

**Characteristics**:

- Automatic intent detection
- Flexible response structure
- Context-aware assistance
- General help and guidance

## 🚀 **Usage Examples**

### **Basic Usage**

```python
from src.ai_prompt_crafter import AIPromptCrafter, PromptContext, PromptType

# Initialize the crafter
crafter = AIPromptCrafter()

# Create context
context = PromptContext(
    project_id="my-project",
    prompt_type=PromptType.TASK_FOCUSED,
    focus_areas=["python", "api", "implementation"]
)

# Craft a prompt
crafted_prompt = await crafter.craft_ai_prompt(
    context,
    "Help me implement a new API endpoint"
)
```

### **MCP Server Integration**

```python
# Using the MCP tool
response = await mcp_client.call_tool("craft_ai_prompt", {
    "project_id": "mcp-context-manager-python",
    "user_message": "I need to implement user authentication",
    "prompt_type": "task_focused",
    "focus_areas": ["python", "authentication", "security"]
})
```

### **Auto-Detection Example**

```python
# Let the system auto-detect the best prompt type
context = PromptContext(
    project_id="my-project",
    prompt_type=PromptType.GENERAL  # Will be auto-detected
)

# The system will analyze the user message and choose the best type
crafted_prompt = await crafter.craft_ai_prompt(
    context,
    "I'm getting a database connection error"  # Will auto-detect as problem_solving
)
```

## 🧠 **Intelligent Features**

### **1. Context Analysis**

The system automatically analyzes context summaries to extract:

- **Priority Levels**: `[HIGH]`, `[MEDIUM]`, `[LOW]`
- **Technologies**: Python, JavaScript, React, MCP, SQL, etc.
- **Key Topics**: Tags and main discussion points
- **User Intent**: Task, problem-solving, explanation, etc.

### **2. Intent Detection**

Based on user message keywords:

- **Task Keywords**: "implement", "create", "build", "code"
- **Problem Keywords**: "fix", "error", "bug", "problem"
- **Explanation Keywords**: "explain", "how", "what", "why"
- **Review Keywords**: "review", "check", "examine"
- **Debug Keywords**: "debug", "trace", "log"

### **3. Focus Area Filtering**

Filter context by specific areas:

```python
focus_areas = ["python", "mcp", "memory", "context"]
```

### **4. Response Guidelines**

Each prompt type includes specific guidelines:

- **Continuation**: Acknowledge context, provide actionable advice
- **Task-Focused**: Code examples, step-by-step guidance
- **Problem-Solving**: Systematic analysis, multiple solutions
- **Explanation**: Clear explanations, practical examples
- **Code Review**: Quality assessment, best practices
- **Debugging**: Step-by-step troubleshooting

## 📊 **Performance Monitoring**

The system tracks performance metrics:

- **Context Length**: Size of context summary used
- **Processing Time**: Time to craft the prompt
- **Success Rate**: Successful prompt generation
- **User Feedback**: Ratings and comments

## 🔧 **Configuration Options**

### **Prompt Context Parameters**

```python
@dataclass
class PromptContext:
    project_id: str                    # Project identifier
    user_intent: Optional[str] = None  # User's intent
    focus_areas: List[str] = None      # Areas to focus on
    max_memories: int = 10            # Max memories to include
    include_recent: bool = True        # Include recent memories
    prompt_type: PromptType = PromptType.GENERAL  # Prompt type
```

### **Analysis Results**

```python
analysis = {
    "has_tasks": bool,           # Contains task-related content
    "has_problems": bool,        # Contains problem-related content
    "has_code": bool,           # Contains code-related content
    "has_questions": bool,      # Contains questions
    "priority_levels": List[str], # Extracted priority levels
    "technologies": List[str],   # Detected technologies
    "user_intent": str,         # Detected user intent
    "key_topics": List[str]     # Key topics extracted
}
```

## 🎯 **Best Practices**

### **1. Choose Appropriate Prompt Types**

- Use `task_focused` for implementation work
- Use `problem_solving` for debugging and errors
- Use `explanation` for educational content
- Use `continuation` for ongoing conversations
- Use `general` for auto-detection

### **2. Specify Focus Areas**

```python
focus_areas = ["python", "api", "authentication"]  # Be specific
```

### **3. Provide Clear User Messages**

```python
user_message = "I need to implement OAuth2 authentication for my API"
# Instead of: "Help me with auth"
```

### **4. Use Context Appropriately**

- Include relevant project context
- Filter by focus areas when needed
- Consider priority levels
- Reference previous work

### **5. Monitor Performance**

- Track prompt effectiveness
- Collect user feedback
- Monitor processing times
- Analyze success rates

## 🚀 **Integration Examples**

### **Cursor/IDE Integration**

```python
# Automatic context injection for new chat sessions
def inject_context_for_new_session(project_id: str):
    context_summary = get_context_summary(project_id)
    crafted_prompt = craft_ai_prompt(
        project_id=project_id,
        user_message="Continue helping with the project",
        prompt_type="continuation"
    )
    return crafted_prompt
```

### **Chatbot Integration**

```python
# Dynamic prompt crafting for chatbot responses
async def handle_user_message(user_message: str, project_id: str):
    # Auto-detect intent and craft appropriate prompt
    crafted_prompt = await craft_intelligent_prompt(
        project_id=project_id,
        user_message=user_message,
        focus_areas=["python", "development"]
    )
    return crafted_prompt
```

### **Documentation Generation**

```python
# Generate contextual documentation prompts
async def create_documentation_prompt(project_id: str, topic: str):
    crafted_prompt = await craft_ai_prompt(
        context=PromptContext(
            project_id=project_id,
            prompt_type=PromptType.EXPLANATION,
            focus_areas=["documentation", topic]
        ),
        user_message=f"Create comprehensive documentation for {topic}"
    )
    return crafted_prompt
```

## 🎉 **Benefits**

### **For Developers**

- ✅ **Contextual Responses**: AI understands project history
- ✅ **Focused Assistance**: Tailored to specific needs
- ✅ **Continuity**: Seamless conversation flow
- ✅ **Efficiency**: No need to re-explain context

### **For Projects**

- ✅ **Consistent Context**: Maintains project awareness
- ✅ **Better Quality**: More relevant and accurate responses
- ✅ **Time Savings**: Reduced context re-explanation
- ✅ **Improved UX**: Better user experience

### **For Teams**

- ✅ **Shared Context**: Team members benefit from collective knowledge
- ✅ **Knowledge Retention**: Important information is preserved
- ✅ **Collaboration**: Better collaboration through context awareness
- ✅ **Onboarding**: New team members get project context

## 🔮 **Future Enhancements**

### **Planned Features**

- **Multi-Modal Prompts**: Support for images, code, and documents
- **Learning Algorithms**: Improve prompt effectiveness over time
- **Custom Templates**: User-defined prompt templates
- **Advanced Analytics**: Detailed performance insights
- **Integration APIs**: Easy integration with other tools

### **Advanced Capabilities**

- **Semantic Analysis**: Deep understanding of context meaning
- **Intent Prediction**: Predict user needs before they ask
- **Dynamic Adaptation**: Real-time prompt optimization
- **Cross-Project Context**: Share context across related projects

---

This AI Prompt Crafting system transforms how we interact with AI by providing rich, contextual, and intelligent prompts that lead to better, more relevant responses! 🚀

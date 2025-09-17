from typing import Dict, Any, Callable

from AgentCrew.modules.agents import AgentManager
from .base_service import BaseMemoryService


def get_memory_forget_tool_definition(provider="claude") -> Dict[str, Any]:
    """Optimized memory forgetting tool definition."""

    tool_description = """Removes memories related to specific topics or IDs from storage.

Use for clearing outdated information, removing sensitive data, resolving conflicting memories, or correcting errors.

Be specific with topics to avoid over-deletion. Use IDs for precise removal when available."""

    tool_arguments = {
        "topic": {
            "type": "string",
            "description": "Keywords describing what to forget. Use specific terms like 'project alpha 2024 credentials' or 'outdated api documentation v1'. Avoid broad terms like 'user' or 'project'.",
        },
        "ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional list of specific memory IDs for precise removal. Takes precedence over topic when provided.",
        },
    }

    tool_required = ["topic"]

    if provider == "claude":
        return {
            "name": "forget_memory_topic",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq"
        return {
            "type": "function",
            "function": {
                "name": "forget_memory_topic",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_memory_forget_tool_handler(memory_service: BaseMemoryService) -> Callable:
    """Optimized memory forgetting handler with concise feedback."""

    def handle_memory_forget(**params) -> str:
        topic = params.get("topic", "").strip()
        ids = params.get("ids", [])

        # Use provided agent_name or fallback to current agent
        current_agent = AgentManager.get_instance().get_current_agent()
        agent_name = current_agent.name if current_agent else "None"

        # ID-based removal (preferred)
        if ids:
            try:
                result = memory_service.forget_ids(ids, agent_name)
                return (
                    f"✅ Removed {len(ids)} memories: {result.get('message', 'Success')}"
                    if result.get("success")
                    else f"⚠️ Removal incomplete: {result.get('message', 'Unknown error')}"
                )
            except Exception as e:
                return f"❌ ID removal failed: {str(e)}"

        # Topic-based removal
        if not topic:
            return "❌ Topic or IDs required for memory removal."

        # Prevent overly broad deletion
        risky_terms = ["all", "everything", "user", "conversation", "memory"]
        if topic.lower() in risky_terms:
            return f"⚠️ '{topic}' too broad. Use specific terms to avoid over-deletion."

        try:
            result = memory_service.forget_topic(topic, agent_name)
            return (
                f"✅ Removed memories for '{topic}': {result.get('message', 'Success')}"
                if result.get("success")
                else f"⚠️ Removal incomplete: {result.get('message', 'Not found')}"
            )
        except Exception as e:
            return f"❌ Topic removal failed: {str(e)}"

    return handle_memory_forget


def get_memory_retrieve_tool_definition(provider="claude") -> Dict[str, Any]:
    """Optimized memory retrieval tool definition."""

    tool_description = """Retrieves relevant information from conversation history using semantic search.

Use for gathering context, accessing user preferences, finding similar problems, and maintaining conversation continuity. 

Search with specific, descriptive keywords for better results."""

    tool_arguments = {
        "phrases": {
            "type": "string",
            "description": "Search a phrases for finding relevant memories. Use specific semantic phrases like 'project alpha database issues' or 'user preferences communication style' rather than single words.",
        },
        "limit": {
            "type": "integer",
            "default": 5,
            "description": "Maximum results (1-15). Use 1-3 for quick facts, 4-7 for standard context, 8-15 for comprehensive background.",
        },
    }

    tool_required = ["phrases"]

    if provider == "claude":
        return {
            "name": "retrieve_memory",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq"
        return {
            "type": "function",
            "function": {
                "name": "retrieve_memory",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def memory_instruction_prompt():
    """Concise memory system instructions for system prompt."""
    return """<Memory_System>
  <Purpose>
    Maintain conversation continuity and context through intelligent storage and retrieval of relevant information.
  </Purpose>
  <Usage_Guidelines>
    <Retrieval_Triggers>
      • Start of new conversations - gather relevant context
      • Topic changes - search for background information  
      • Complex queries - collect comprehensive context
      • User references to past interactions
    </Retrieval_Triggers>
    <Search_Strategy>
      • Use specific, descriptive phrases
      • Combine related concepts with spaces
      • Include temporal indicators when relevant
      • Balance specificity with breadth based on need
    </Search_Strategy>
    <Memory_Management>
      • Remove outdated/conflicting information when corrected
      • Clear sensitive data when requested
      • Use precise topic phrases to avoid over-deletion
      • Prefer ID-based removal for surgical precision
    </Memory_Management>
  </Usage_Guidelines>
</Memory_System>"""


def get_memory_retrieve_tool_handler(memory_service: BaseMemoryService) -> Callable:
    """Optimized memory retrieval handler with concise feedback."""

    def handle_memory_retrieve(**params) -> str:
        phrases = params.get("phrases", "").strip()
        limit = max(1, min(params.get("limit", 5), 50))

        if not phrases:
            return "❌ Phrases required for memory search."

        if len(phrases) < 3:
            return f"⚠️ Search term '{phrases}' too short. Use more semantica and descriptive phrases."

        # Use provided agent_name or fallback to current agent
        current_agent = AgentManager.get_instance().get_current_agent()
        agent_name = current_agent.name if current_agent else ""

        try:
            result = memory_service.retrieve_memory(phrases, limit, agent_name)

            if not result or result.strip() == "":
                return f"📝 No memories found for '{phrases}'. Try broader phrases or related terms."

            # Count memories for user feedback
            return f"📚 Found relevant memories:\n\n{result}"

        except Exception as e:
            return f"❌ Memory search failed: {str(e)}"

    return handle_memory_retrieve


def get_adapt_tool_definition(provider="claude") -> Dict[str, Any]:
    """Optimized adaptive behavior tool definition."""

    tool_description = """Stores behavioral patterns to personalize future interactions based on user preferences and successful approaches.

Use when you identify effective communication styles, task approaches, or user preferences that should be consistently applied.

All behaviors must follow 'when..., [action]...' format for automatic activation."""

    tool_arguments = {
        "id": {
            "type": "string",
            "description": "Unique identifier using format 'category_context' (e.g., 'communication_style_technical', 'task_execution_code_review'). Use existing ID to update behavior.",
        },
        "behavior": {
            "type": "string",
            "description": "Behavior pattern in 'when [condition], [action] [objective]' format. Example: 'when user asks about debugging, provide step-by-step troubleshooting with code examples'.",
        },
    }

    tool_required = ["id", "behavior"]

    if provider == "claude":
        return {
            "name": "adapt",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq"
        return {
            "type": "function",
            "function": {
                "name": "adapt",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_adapt_tool_handler(persistence_service: Any) -> Callable:
    """Optimized adaptive behavior handler with concise feedback."""

    def handle_adapt(**params) -> str:
        behavior_id = params.get("id", "").strip()
        behavior = params.get("behavior", "").strip()

        if not behavior_id:
            return "❌ Behavior ID required (e.g., 'communication_style_technical')."

        if not behavior:
            return "❌ Behavior description required in 'when...do...' format."

        # Validate format
        behavior_lower = behavior.lower()
        if not behavior_lower.startswith("when "):
            return "❌ Use format: 'when [condition], [action]'"

        current_agent = AgentManager.get_instance().get_current_agent()
        agent_name = current_agent.name if current_agent else "default"

        try:
            success = persistence_service.store_adaptive_behavior(
                agent_name, behavior_id, behavior
            )
            return (
                f"✅ Stored behavior '{behavior_id}': {behavior}"
                if success
                else "⚠️ Storage completed but may need verification."
            )
        except ValueError as e:
            return f"❌ Invalid format: {str(e)}"
        except Exception as e:
            return f"❌ Storage failed: {str(e)}"

    return handle_adapt


def adaptive_instruction_prompt():
    """Concise adaptive behavior instructions for system prompt."""
    return """<Adaptive_Behaviors>
  <Purpose>
    Learn and apply personalized interaction patterns to improve user experience over time.
  </Purpose>
  <Learning_Triggers>
    - User expresses preferences for communication style
    - Positive feedback on specific approaches
    - Repeated requests indicating preferred workflows
    - Successful problem-solving patterns
    - Specific "when...do..." instructions from the user
  </Learning_Triggers>
  <Behavior_Format>
    All behaviors must follow: "when [specific condition] do [specific action]"
    
    Examples:
    - "when user asks about code, do provide complete examples with explanations"
    - "when user mentions deadlines, do prioritize speed over detailed explanations"
    - "when user corrects information, do acknowledge and thank them for the correction"
  </Behavior_Format>
  <ID_Conventions>
    Use structured IDs: category_context
    • communication_style_[aspect]
    • task_execution_[domain] 
    • personalization_[area]
  </ID_Conventions>
</Adaptive_Behaviors>"""


def register(
    service_instance=None,
    persistence_service=None,
    agent=None,
):
    """Register optimized memory tools with comprehensive capabilities."""
    from AgentCrew.modules.tools.registration import register_tool

    # Register core memory management tools
    register_tool(
        get_memory_retrieve_tool_definition,
        get_memory_retrieve_tool_handler,
        service_instance,
        agent,
    )
    register_tool(
        get_memory_forget_tool_definition,
        get_memory_forget_tool_handler,
        service_instance,
        agent,
    )

    # Register adaptive behavior tool if persistence service is available
    if persistence_service is not None:
        register_tool(
            get_adapt_tool_definition,
            get_adapt_tool_handler,
            persistence_service,
            agent,
        )

import asyncio
from typing import Dict, Any, Callable

from AgentCrew.modules.agents import AgentManager
from .base_service import BaseMemoryService


def get_memory_forget_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for forgetting memories based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Removes memories related to a specific topic from the conversation history. This is useful for clearing sensitive information, irrelevant details, or outdated information that might conflict with the current task. Use this sparingly and only when absolutely necessary to avoid losing valuable context. Provide a clear justification for why the topic is being removed."
    tool_arguments = {
        "topic": {
            "type": "string",
            "description": "Keywords describing the topic to be forgotten. Be precise and comprehensive to ensure all relevant memories are removed. Include any IDs or specific identifiers related to the topic.",
        },
        "ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional list of specific memory IDs to forget. If provided, only these memories will be removed. Use this to target specific entries without affecting the entire topic.",
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
    """
    Get the handler function for the memory forget tool.

    Args:
        memory_service: The memory service instance

    Returns:
        Function that handles memory forgetting requests
    """

    def handle_memory_forget(**params) -> str:
        topic = params.get("topic")
        ids = params.get("ids", [])
        current_agent = AgentManager.get_instance().get_current_agent()

        if len(ids) > 0:
            try:
                result = memory_service.forget_ids(ids, current_agent.name)
                if result["success"]:
                    return result["message"]
                else:
                    return "Unable to forget memories"
            except Exception as e:
                return f"Error forgetting memories: {str(e)}"

        if not topic:
            return "Error: Topic is required for forgetting memories."

        try:
            result = memory_service.forget_topic(topic, current_agent.name)
            if result["success"]:
                return result["message"]
            else:
                return f"Unable to forget memories: {result['message']}"
        except Exception as e:
            return f"Error forgetting memories: {str(e)}"

    return handle_memory_forget


def get_memory_retrieve_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for retrieving memories based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Retrieves relevant information from past conversations and stored knowledge, based on semantic keywords. ALWAYS use this tool as a primary method for finding relevant information and context. Use specific semantic keywords for best results."
    tool_arguments = {
        "keywords": {
            "type": "string",
            "description": "Semantic Keywords used to search for relevant information in memory. Use specific and descriptive terms to narrow the search and retrieve the most useful results. Consider synonyms and related terms to broaden the search.",
        },
        "limit": {
            "type": "integer",
            "default": 5,
            "description": "Maximum number of memory items to retrieve. Defaults to 5 if not specified. Use this to control the amount of information returned, especially when dealing with large datasets.",
        },
    }
    tool_required = ["keywords"]
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
    return """<Memory_System>
  <Purpose>
    Enrichment the input context with relevant past interactions and knowledge.
    Allow agent control over memory retrieval and forgetting.
  </Purpose>
  <Trigger_Conditions>
    <retrieve_memory>At beginning of conversations or when user changes the discussion subject</retrieve_memory>
    <forget_memory_topic>When user deny about a fact that you provided, use `ids` when possible</forget_memory_topic>
  </Trigger_Conditions>

</Memory_System>"""


def get_memory_retrieve_tool_handler(memory_service: BaseMemoryService) -> Callable:
    """
    Get the handler function for the memory retrieve tool.

    Args:
        memory_service: The memory service instance

    Returns:
        Function that handles memory retrieval requests
    """

    def handle_memory_retrieve(**params) -> str:
        keywords = params.get("keywords")
        limit = params.get("limit", 5)

        current_agent = AgentManager.get_instance().get_current_agent()

        if not keywords:
            return "Error: Keywords are required for memory retrieval."

        try:
            result = asyncio.run(
                memory_service.retrieve_memory(keywords, limit, current_agent.name)
            )
            return result
        except Exception as e:
            return f"Error retrieving memories: {str(e)}"

    return handle_memory_retrieve


def get_adapt_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for adaptive behavior management based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Store new or update existing adaptive behaviors that help improve user experience. Use this when you identify patterns in user interactions or need to remember specific ways to handle certain situations. Behaviors must follow 'when...do...' format."
    tool_arguments = {
        "id": {
            "type": "string",
            "description": "Unique identifier for this adaptive behavior. Use descriptive names like 'tech_documentation_search' or 'code_review_style'. Can be new or existing to update.",
        },
        "behavior": {
            "type": "string",
            "description": "The adaptive behavior description in 'when...do...' format. Example: 'when user mentions new technology, search for its latest documentation and provide comprehensive examples'",
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
    """
    Get the handler function for the adaptive behavior tool.

    Args:
        persistence_service: The context persistence service instance

    Returns:
        Function that handles adaptive behavior storage requests
    """

    def handle_adapt(**params) -> str:
        behavior_id = params.get("id")
        behavior = params.get("behavior")
        current_agent = AgentManager.get_instance().get_current_agent()

        if not behavior_id:
            return "Error: Behavior ID is required."

        if not behavior:
            return "Error: Behavior description is required."

        try:
            success = persistence_service.store_adaptive_behavior(
                current_agent.name, behavior_id, behavior
            )
            if success:
                return f"Successfully updated behavior '{behavior_id}': {behavior}"
            else:
                return f"Failed to update adaptive behavior '{behavior_id}'"
        except ValueError as e:
            return f"Invalid behavior format: {str(e)}"
        except Exception as e:
            return f"Error updating adaptive behavior: {str(e)}"

    return handle_adapt


def adaptive_instruction_prompt():
    return """<Adapting_Behaviors>
  <Purpose>
    Store behavioral patterns that improve user experience using the 'adapt' tool.
  </Purpose>

  <Trigger_Conditions>
    <User_Preferences>Recurring requests or communication styles</User_Preferences>
    <Task_Patterns>Specific ways users like information presented</Task_Patterns>
    <Context_Triggers>Situations requiring special handling</Context_Triggers>
  </Trigger_Conditions>

  <Behavior_Format>
    <Structure>Always use "when...do..." format</Structure>
    <Examples>
      • "when user asks about code, provide complete examples with explanations"
      • "when user mentions deadlines, prioritize speed over detailed explanations"
      • "when user shares personal info, acknowledge and reference it in future interactions"
    </Examples>
  </Behavior_Format>

  <Implementation_Guidelines>
    • Use descriptive IDs (e.g., "code_explanation_style", "deadline_response")
    • Be specific about triggers and actions
    • Update existing behaviors when behaviors change
    • Focus on actionable, consistent improvements
  </Implementation_Guidelines>
</Adapting_Behaviors>"""


def register(
    service_instance=None,
    persistence_service=None,
    agent=None,
):
    """
    Register this tool with the central registry or directly with an agent

    Args:
        service_instance: The memory service instance
        agent: Agent instance to register with directly (optional)
        persistence_service: The context persistence service instance (optional)
    """
    from AgentCrew.modules.tools.registration import register_tool

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

    # Register adapt tool if persistence service is provided
    if persistence_service is not None:
        register_tool(
            get_adapt_tool_definition,
            get_adapt_tool_handler,
            persistence_service,
            agent,
        )

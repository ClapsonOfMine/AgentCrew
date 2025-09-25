from typing import Dict, Any, Callable
import asyncio

from AgentCrew.modules.agents import AgentManager

# from AgentCrew.modules.llm.message import MessageTransformer
from AgentCrew.modules.agents.base import MessageType


def get_delegate_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the definition for the delegate tool.

    Args:
        provider: The LLM provider (claude, openai, groq)

    Returns:
        The tool definition
    """
    tool_description = "Delegates a specific task to a specialized agent while keeping the current agent active. The target agent will process the task with full conversation context and then be deactivated, returning control to the current agent. This is a fire-and-forget action that doesn't modify the current agent's message history."

    tool_arguments = {
        "from_agent": {
            "type": "string",
            "description": "The name of agent who calls the delegate tool (You).",
        },
        "target_agent": {
            "type": "string",
            "description": "The name of the specialized agent to delegate the task to. Refer to the official <Available_Agents_List> tags for available specialist agents and their capabilities.",
        },
        "task_description": {
            "type": "string",
            "description": "A precise, actionable description of the task for the target agent. Start with action verbs (Create, Analyze, Design, Implement, etc.) and clearly state what the target agent needs to achieve. Include specific deliverables, success criteria, and constraints.",
        },
    }

    tool_required = ["from_agent", "target_agent", "task_description"]

    if provider == "claude":
        return {
            "name": "delegate",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:
        return {
            "type": "function",
            "function": {
                "name": "delegate",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_delegate_tool_handler(agent_manager: AgentManager) -> Callable:
    """
    Get the handler function for the delegate tool.

    Args:
        agent_manager: The agent manager instance

    Returns:
        The handler function
    """

    def handler(**params) -> str:
        """
        Handle a delegation request.

        Args:
            target_agent: The name of the agent to delegate to
            task_description: The task description for the target agent

        Returns:
            A string containing the response from the delegated agent
        """
        from_agent_name = params.get("from_agent")
        target_agent_name = params.get("target_agent")
        task_description = params.get("task_description")

        if not from_agent_name:
            raise ValueError("Error: No source agent specified for delegation")

        if not target_agent_name:
            raise ValueError("Error: No target agent specified")

        if not task_description:
            raise ValueError("Error: No task description specified for delegation")

        # Check if target agent exists
        if target_agent_name not in agent_manager.agents:
            available_agents = ", ".join(agent_manager.agents.keys())
            raise ValueError(
                f"Error: Agent '{target_agent_name}' not found. Available agents: {available_agents}"
            )

        if from_agent_name not in agent_manager.agents:
            available_agents = ", ".join(agent_manager.agents.keys())
            raise ValueError(
                f"Error: Agent '{from_agent_name}' not found. Available agents: {available_agents}"
            )

        # Check if trying to delegate to self
        if (
            agent_manager.current_agent
            and target_agent_name == agent_manager.current_agent.name
        ):
            raise ValueError("Error: Cannot delegate to the same agent")

        # Store the current agent and its state
        original_agent = agent_manager.get_agent(from_agent_name)

        try:
            # Get the target agent
            target_agent = agent_manager.get_agent(target_agent_name)
            if not target_agent:
                raise ValueError(
                    f"Error: Could not retrieve agent '{target_agent_name}'"
                )

            # Prepare context from current conversation
            context_messages = []
            if original_agent and original_agent.std_history:
                # Get conversation context to share with the delegated agent
                for msg in original_agent.std_history:
                    if "content" in msg and msg.get("role") != "tool":
                        content = ""
                        processing_content = msg["content"]

                        if isinstance(processing_content, str):
                            content = msg.get("content", "")
                        elif (
                            isinstance(processing_content, list)
                            and len(processing_content) > 0
                        ):
                            if processing_content[0].get("type") == "text":
                                content = processing_content[0]["text"]

                        if content.strip():
                            role = (
                                "User"
                                if msg.get("role", "user") == "user"
                                else original_agent.name
                            )
                            context_messages.append(f"**{role}**: {content}")

            # Temporarily activate the target agent
            original_target_active = target_agent.is_active
            if not original_target_active:
                target_agent.activate()

            # Prepare the delegation message with context
            delegation_message = f"<delegate_tool>## Delegated Task from {from_agent_name}:\n{task_description}\n\n"

            if context_messages:
                delegation_message += f"## Conversation Context:\n{'\\n'.join(context_messages)}\n\n"  # Last 10 messages for context

            delegation_message += "## Instructions:\nComplete the above task using the provided context. Provide a complete response as if responding directly to the user.</delegate_tool>"

            # Create the user message for the target agent
            user_message = {"role": "user", "content": delegation_message}

            # Convert message to target agent's format and set as target agent's history
            delegate_history = [user_message]
            # MessageTransformer.convert_messages(
            #     [user_message], target_agent.get_provider()
            # )

            try:

                async def _process_delegation():
                    """Process delegation similar to _process_agent_task - runs until no tool uses"""

                    current_response = ""
                    tool_uses = []
                    input_tokens = 0
                    output_tokens = 0
                    thinking_content = ""

                    def process_result(_tool_uses, _input_tokens, _output_tokens):
                        nonlocal tool_uses, input_tokens, output_tokens
                        tool_uses = _tool_uses
                        input_tokens += _input_tokens
                        output_tokens += _output_tokens

                    if not target_agent:
                        return current_response
                    async for (
                        response_message,
                        chunk_text,
                        thinking_chunk,
                    ) in target_agent.process_messages(
                        delegate_history, callback=process_result
                    ):
                        if response_message:
                            current_response = response_message

                        if thinking_chunk:
                            think_text_chunk, _ = thinking_chunk
                            if think_text_chunk:
                                thinking_content += think_text_chunk

                    if tool_uses and len(tool_uses) > 0:
                        filtered_tool_uses = [
                            t
                            for t in tool_uses
                            if t["name"] not in ["transfer", "delegate"]
                        ]

                        if not filtered_tool_uses:
                            return current_response

                        # Add thinking content as a separate message if available
                        thinking_data = (
                            (thinking_content, None) if thinking_content else None
                        )
                        if thinking_data:
                            thinking_message = target_agent.format_message(
                                MessageType.Thinking, {"thinking": thinking_data}
                            )
                            if thinking_message:
                                delegate_history.append(thinking_message)

                        # Format assistant message with the response and tool uses
                        assistant_message = target_agent.format_message(
                            MessageType.Assistant,
                            {
                                "message": current_response,
                                "tool_uses": filtered_tool_uses,
                            },
                        )
                        if assistant_message:
                            delegate_history.append(assistant_message)

                        # Process each tool use
                        for tool_use in filtered_tool_uses:
                            try:
                                tool_result = await target_agent.execute_tool_call(
                                    tool_use["name"],
                                    tool_use["input"],
                                )

                                tool_result_message = target_agent.format_message(
                                    MessageType.ToolResult,
                                    {
                                        "tool_use": tool_use,
                                        "tool_result": tool_result,
                                    },
                                )
                                if tool_result_message:
                                    delegate_history.append(tool_result_message)

                            except Exception as e:
                                error_message = target_agent.format_message(
                                    MessageType.ToolResult,
                                    {
                                        "tool_use": tool_use,
                                        "tool_result": str(e),
                                        "is_error": True,
                                    },
                                )
                                if error_message:
                                    delegate_history.append(error_message)

                        # Continue the loop to process more messages
                        return await _process_delegation()

                    return current_response

                response = asyncio.run(_process_delegation())

            except Exception as e:
                raise ValueError(
                    f"Error processing delegation with target agent '{target_agent_name}': {str(e)}"
                )

            # Deactivate the target agent if it wasn't originally active
            if not original_target_active:
                target_agent.deactivate()
                if agent_manager.current_agent:
                    agent_manager.current_agent.activate()

            # Format the response
            formatted_response = (
                f"## Delegation Result from {target_agent_name}:\n\n{response}"
            )

            return formatted_response

        except Exception as e:
            # Ensure target agent is deactivated in case of error
            raise ValueError(f"Error during delegation: {str(e)}")

    return handler


def delegate_tool_prompt(agent_manager: AgentManager) -> str:
    return agent_manager.get_delegate_system_prompt()


def register(agent_manager, agent=None):
    """
    Register the delegate tool with all agents or a specific agent.

    Args:
        agent_manager: The agent manager instance
        agent: Specific agent to register with (optional)
    """
    from AgentCrew.modules.tools.registration import register_tool

    register_tool(
        get_delegate_tool_definition, get_delegate_tool_handler, agent_manager, agent
    )

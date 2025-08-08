from typing import Dict, List, Any

from AgentCrew.modules.llm.base import BaseLLMService


class ConversationConsolidator:
    """
    A class for consolidating conversation messages to reduce token usage while preserving key information.
    Handles summarizing older messages and inserting consolidated message markers.
    """

    def __init__(self, llm_service: BaseLLMService):
        """
        Initialize the ConversationConsolidator.

        Args:
            message_handler: The MessageHandler instance to access messages and LLM services.
        """
        self.llm = llm_service

    async def consolidate(
        self, messages: List[Dict[str, Any]], preserve_count: int
    ) -> Dict[str, Any]:
        """
        Consolidate conversation messages, preserving the specified number of recent messages.

        Args:
            preserve_count: Number of most recent messages to preserve intact

        Returns:
            A dictionary with information about the consolidation (messages consolidated, tokens saved, etc.)
        """
        if preserve_count < 1:
            raise ValueError("preserve_count must be a positive integer")

        # Get current messages
        all_messages = messages

        # Nothing to consolidate if we don't have enough messages
        if len(all_messages) <= preserve_count:
            return {
                "success": False,
                "reason": "Not enough messages to consolidate",
                "total_messages": len(all_messages),
                "preserve_count": preserve_count,
            }

        # Find the last consolidated message if one exists
        last_consolidated_idx = -1
        for i, msg in reversed(list(enumerate(all_messages))):
            if msg.get("role") == "consolidated":
                last_consolidated_idx = i
                break

        # if first message preserved is a tool message, we need to find the assistant message that called it
        if all_messages[-preserve_count].get("role", "") == "tool":
            for i, msg in reversed(list(enumerate(all_messages[:-preserve_count]))):
                if msg.get("role") == "assistant":
                    preserve_count += len(all_messages[:-preserve_count]) - i
                    break

        # Split messages into those to consolidate and those to preserve
        if last_consolidated_idx >= 0:
            # Already have consolidated messages, so consolidate from the last one to (total - preserve_count)
            to_consolidate = (
                all_messages[last_consolidated_idx + 1 : -preserve_count]
                if preserve_count > 0
                else all_messages[last_consolidated_idx + 1 :]
            )
            to_preserve = all_messages[-preserve_count:] if preserve_count > 0 else []

            # Remove the old consolidated message since we'll create a new one
        else:
            # First time consolidating - consolidate all but the last preserve_count messages
            to_consolidate = (
                all_messages[:-preserve_count] if preserve_count > 0 else all_messages
            )
            to_preserve = all_messages[-preserve_count:] if preserve_count > 0 else []

            # Start with an empty list as we haven't consolidated before

        # Don't proceed if nothing to consolidate
        if not to_consolidate:
            return {
                "success": False,
                "reason": "No messages to consolidate after preserving recent messages",
                "total_messages": len(all_messages),
                "preserve_count": preserve_count,
            }

        # Calculate token counts before consolidation
        original_tokens = self.estimate_token_count(to_consolidate)

        # Generate a summary of the messages to consolidate
        summary = await self.generate_summary(to_consolidate)

        # Create a consolidated message
        consolidated_msg = {
            "role": "consolidated",
            "content": [{"type": "text", "text": summary}],
            "metadata": {
                "messages_consolidated": len(to_consolidate),
                "original_token_count": original_tokens,
                "consolidated_token_count": self.estimate_token_count(
                    [{"content": summary}]
                ),
            },
        }

        # Calculate token savings
        consolidated_tokens = self.estimate_token_count([consolidated_msg])

        # Update the streamline messages
        messages.insert(-preserve_count, consolidated_msg)

        # Return information about the consolidation
        result = {
            "success": True,
            "messages_consolidated": len(to_consolidate),
            "messages_preserved": len(to_preserve),
            "original_token_count": original_tokens,
            "consolidated_token_count": consolidated_tokens,
            "summary": summary,
        }

        return result

    async def generate_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the given messages using the current agent's LLM.

        Args:
            messages: The messages to summarize

        Returns:
            A string summary of the messages
        """
        # Get the current agent

        # Format the messages for summary generation
        formatted_conversation = self.format_conversation_for_summary(messages)

        # Create a prompt for summarizing
        summary_prompt = self.create_summary_prompt(formatted_conversation)

        # Process the summary request
        summary = await self.llm.process_message(summary_prompt)

        return summary

    def format_conversation_for_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format conversation messages for summarization.

        Args:
            messages: The messages to format

        Returns:
            Formatted conversation as a string
        """
        formatted_parts = []

        for msg in messages:
            role = msg.get("role", "")
            agent_name = msg.get("agent", "unknown")

            if role == "user":
                prefix = "USER: "
            elif role == "assistant":
                prefix = f"{agent_name.upper()}: "
            elif role == "tool":
                prefix = f"TOOL ({msg.get('name', 'unknown')}): "
            elif role == "consolidated":
                # If we're summarizing a section that already has a consolidated message,
                # include it directly to preserve that context
                prefix = "PREVIOUS SUMMARY: "
            else:
                # Skip other types of messages
                continue

            content = msg.get("content", "")

            # Handle different content formats
            if isinstance(content, str):
                text_content = content
            elif isinstance(content, list):
                # Extract text from content parts
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                        elif part.get("type") == "image_url":
                            text_parts.append("[IMAGE]")
                text_content = " ".join(text_parts)
            else:
                text_content = str(content)

            formatted_parts.append(f"{prefix}{text_content}")

        return "\n\n".join(formatted_parts)

    def create_summary_prompt(self, conversation: str) -> str:
        """
        Create a prompt for the LLM to generate a conversation summary.

        Args:
            conversation: The formatted conversation text

        Returns:
            A prompt string
        """
        return (
            """You are an expert conversation summarizer tasked with creating a concise but comprehensive summary of a conversation between a user and AI assistants.

IMPORTANT GUIDELINES:
1. Preserve critical information in these categories:
   - Key questions and their complete answers
   - Important decisions and conclusions
   - Technical details, facts, code snippets, and data
   - Project and key files location and project structure
   - Problems identified and their solutions
   - Commitments or agreements made
   
2. Structure your summary effectively:
   - Begin with a clear overview statement: "This conversation covers [main topics]"
   - Organize by main topics rather than chronologically when appropriate
   - Use bullet points or paragraphs as needed for clarity
   - Format code snippets with markdown code blocks (```language\ncode\n```)
   
3. Focus on content quality:
   - Be factual and objective - avoid adding information not in the original
   - Include specific details that would be needed to continue the conversation
   - Preserve the tone and style of technical information
   - Maintain technical accuracy and precision
   
4. Optimize for efficiency:
   - Aim for 15-20% of the original length
   - Eliminate redundancies and tangential discussions
   - Focus on substance over conversational patterns
   - Be comprehensive yet concise

The conversation to summarize is delimited between triple quotes:
"""
            + f'"""\n{conversation}\n"""'
        )

    def estimate_token_count(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate the token count for the given messages.

        Args:
            messages: The messages to count tokens for

        Returns:
            An estimated token count
        """
        # Simple approximation - 1 token ~= 4 characters
        total_chars = 0

        for msg in messages:
            content = msg.get("content", "")

            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        total_chars += len(part.get("text", ""))

        return total_chars // 4  # Rough approximation

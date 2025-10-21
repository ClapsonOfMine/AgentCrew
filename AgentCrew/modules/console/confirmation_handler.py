"""
Confirmation handlers for console UI.
Handles tool confirmation requests and MCP prompt confirmations.
"""

from rich.console import Console
from rich.text import Text
import time

from .constants import (
    RICH_STYLE_BLUE,
    RICH_STYLE_YELLOW,
    RICH_STYLE_GREEN,
    RICH_STYLE_RED,
    RICH_STYLE_GRAY,
)


class ConfirmationHandler:
    """Handles confirmation dialogs for tools and MCP prompts."""

    def __init__(self, console: Console, input_handler):
        """Initialize the confirmation handler."""
        self.console = console
        self.input_handler = input_handler

    def display_tool_confirmation_request(self, tool_info, message_handler):
        """Display tool confirmation request and get user response."""
        tool_use = tool_info.copy()
        confirmation_id = tool_use.pop("confirmation_id")

        # Special handling for 'ask' tool
        if tool_use["name"] == "ask":
            self._handle_ask_tool(tool_use, confirmation_id, message_handler)
            return

        self.console.print(
            Text(
                "\n🔧 Tool execution requires your permission:", style=RICH_STYLE_YELLOW
            )
        )
        tool_name = Text("Tool: ", style=RICH_STYLE_YELLOW)
        tool_name.append(tool_use["name"])
        self.console.print(tool_name)

        # Display tool parameters
        if isinstance(tool_use["input"], dict):
            self.console.print(Text("Parameters:", style=RICH_STYLE_YELLOW))
            for key, value in tool_use["input"].items():
                param_text = Text(f"  - {key}: ", style=RICH_STYLE_YELLOW)
                param_text.append(str(value))
                self.console.print(param_text)
        else:
            input_text = Text("Input: ", style=RICH_STYLE_YELLOW)
            input_text.append(str(tool_use["input"]))
            self.console.print(input_text)

        # Get user response
        self.input_handler._stop_input_thread()
        while True:
            # Use Rich to print the prompt but still need to use input() for user interaction
            self.console.print(
                Text(
                    "\nAllow this tool to run? [y]es/[n]o/[a]ll in this session/[f]orever (this and future sessions): ",
                    style=RICH_STYLE_BLUE,
                ),
                end="",
            )
            try:
                response = input().lower()
            except KeyboardInterrupt:
                response = "no"

            if response in ["y", "yes"]:
                message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "approve"}
                )
                break
            elif response in ["n", "no"]:
                self.console.print(
                    Text(
                        "\nPlease tell me why you are denying this tool:",
                        style=RICH_STYLE_BLUE,
                    ),
                    end="",
                )
                response = input()
                message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "deny", "reason": response}
                )
                break
            elif response in ["a", "all"]:
                message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "approve_all"}
                )
                approved_text = Text(
                    f"✓ Approved all future calls to '{tool_use['name']}' for this session.",
                    style=RICH_STYLE_GREEN,
                )
                self.console.print(approved_text)
                break
            elif response in ["f", "forever"]:
                from AgentCrew.modules.config import ConfigManagement

                config_manager = ConfigManagement()
                config_manager.write_auto_approval_tools(tool_use["name"], add=True)

                message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "approve_all"}
                )
                saved_text = Text(
                    f"✓ Tool '{tool_use['name']}' will be auto-approved forever.",
                    style=RICH_STYLE_YELLOW,
                )
                self.console.print(saved_text)
                break
            else:
                self.console.print(
                    Text("Please enter 'y', 'n', 'a', or 'f'.", style=RICH_STYLE_YELLOW)
                )
        self.input_handler._start_input_thread()
        time.sleep(0.2)  # Small delay to between tool calls

    def _handle_ask_tool(self, tool_use, confirmation_id, message_handler):
        """Handle the ask tool - display question and guided answers."""
        question = tool_use["input"].get("question", "")
        guided_answers = tool_use["input"].get("guided_answers", [])
        if isinstance(guided_answers, str):
            guided_answers = guided_answers.strip("\n ").splitlines()

        # Display the question
        self.console.print(
            Text("\n❓ Agent is asking for clarification:", style=RICH_STYLE_BLUE)
        )
        self.console.print(Text(f"\n{question}", style=RICH_STYLE_YELLOW))

        # Display guided answers with numbers
        self.console.print(Text("\nSuggested answers:", style=RICH_STYLE_BLUE))
        for idx, answer in enumerate(guided_answers, 1):
            answer_text = Text(f"  {idx}. ", style=RICH_STYLE_GREEN)
            answer_text.append(answer)
            self.console.print(answer_text)

        # Get user response
        self.input_handler._stop_input_thread()
        while True:
            self.console.print(
                Text(
                    "\nYour response (number(s) separated by comma, or custom text): ",
                    style=RICH_STYLE_BLUE,
                ),
                end="",
            )
            try:
                response = input().strip()
            except KeyboardInterrupt:
                message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "answer", "answer": "Cancelled by user"}
                )
                break

            if not response:
                self.console.print(
                    Text("Please provide a response.", style=RICH_STYLE_RED)
                )
                continue

            # Try to parse as number(s)
            selected_answers = []
            is_numeric_selection = True

            # Check if response contains commas (multiple selections)
            if "," in response:
                try:
                    indices = [int(x.strip()) for x in response.split(",")]
                    for idx in indices:
                        if 1 <= idx <= len(guided_answers):
                            selected_answers.append(guided_answers[idx - 1])
                        else:
                            is_numeric_selection = False
                            break
                except ValueError:
                    is_numeric_selection = False
            else:
                # Single selection
                try:
                    idx = int(response)
                    if 1 <= idx <= len(guided_answers):
                        selected_answers.append(guided_answers[idx - 1])
                    else:
                        is_numeric_selection = False
                except ValueError:
                    is_numeric_selection = False

            # Determine final answer
            if is_numeric_selection and selected_answers:
                final_answer = ", ".join(selected_answers)
                self.console.print(
                    Text(f"✓ Selected: {final_answer}", style=RICH_STYLE_GREEN)
                )
            else:
                # Treat as custom response
                final_answer = response
                self.console.print(
                    Text(f"✓ Custom answer: {final_answer}", style=RICH_STYLE_GREEN)
                )

            message_handler.resolve_tool_confirmation(
                confirmation_id, {"action": "answer", "answer": final_answer}
            )
            break

        self.input_handler._start_input_thread()

    def display_mcp_prompt_confirmation(self, prompt_data, input_queue):
        """Display MCP prompt confirmation request and get user response."""
        self.console.print(
            Text("\n🤖 MCP Tool wants to execute a prompt:", style=RICH_STYLE_YELLOW)
        )

        # Display the prompt content
        if isinstance(prompt_data, dict):
            if "name" in prompt_data:
                prompt_name = Text("Prompt: ", style=RICH_STYLE_YELLOW)
                prompt_name.append(prompt_data["name"])
                self.console.print(prompt_name)

            if "content" in prompt_data:
                self.console.print(Text("Content:", style=RICH_STYLE_YELLOW))
                # Display content with proper formatting
                content = str(prompt_data["content"])
                if len(content) > 1000:
                    self.console.print(f"  {content[:1000]}...")
                    self.console.print(
                        Text(
                            f"  (Content truncated, total length: {len(content)} characters)",
                            style=RICH_STYLE_GRAY,
                        )
                    )
                else:
                    self.console.print(f"  {content}")

        # Get user response
        self.input_handler._stop_input_thread()
        while True:
            self.console.print(
                Text(
                    "\nAllow this prompt to be executed? [y]es/[n]o: ",
                    style=RICH_STYLE_YELLOW,
                ),
                end="",
            )
            response = input().lower()

            if response in ["y", "yes"]:
                # User approved, put the prompt data in the input queue
                self.console.print(
                    Text(
                        "✓ MCP prompt approved and queued for execution.",
                        style=RICH_STYLE_GREEN,
                    )
                )
                input_queue.put(prompt_data["content"])
                break
            elif response in ["n", "no"]:
                # User denied, don't queue the prompt
                self.console.print(
                    Text("❌ MCP prompt execution denied.", style=RICH_STYLE_RED)
                )
                break
            else:
                self.console.print(
                    Text(
                        "Please enter 'y' for yes or 'n' for no.",
                        style=RICH_STYLE_YELLOW,
                    )
                )

        self.input_handler._start_input_thread()

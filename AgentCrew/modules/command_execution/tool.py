"""
Command Execution Tools

Tool definitions and handlers for secure shell command execution.
"""

from typing import Dict, Any, Callable
from .service import CommandExecutionService


def get_run_command_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for running shell commands.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    import sys

    is_windows = sys.platform == "win32"

    # Platform-specific descriptions and examples
    if is_windows:
        platform_info = (
            "\n\n**WINDOWS DETECTED**: Commands execute via PowerShell with UTF-8 encoding. "
            "Use PowerShell syntax and cmdlets. "
            "\n• List files: 'dir' or 'Get-ChildItem'"
            "\n• View file: 'type file.txt' or 'Get-Content file.txt'"
            "\n• Current directory: 'pwd' or 'Get-Location'"
            "\n• Find files: 'Get-ChildItem -Recurse -Filter \"*.py\"'"
            "\n• Process list: 'Get-Process'"
            "\n• Environment: 'echo $env:PATH'"
        )
        command_examples = (
            "Windows examples: 'dir /s', 'type README.md', 'python script.py', "
            "'git status', 'curl https://api.example.com', 'Get-Process python'"
        )
        whitelist_commands = (
            "dir, type, echo, where, python, python3, pip, node, npm, git, docker, curl, "
            "Get-Process, Get-Content, Get-ChildItem, Get-Location, pwd, mkdir"
        )
    else:
        platform_info = (
            "\n\n**LINUX/MAC DETECTED**: Commands execute via bash shell. "
            "Use standard Unix commands and bash syntax. "
            "\n• List files: 'ls -la'"
            "\n• View file: 'cat file.txt' or 'head -n 20 file.txt'"
            "\n• Current directory: 'pwd'"
            "\n• Find files: 'find . -name \"*.py\"'"
            "\n• Process list: 'ps aux' or 'top -bn1'"
            "\n• Environment: 'echo $PATH'"
        )
        command_examples = (
            "Unix examples: 'ls -la', 'cat README.md', 'python script.py', "
            "'git status', 'curl https://api.example.com', 'ps aux | grep python'"
        )
        whitelist_commands = (
            "ls, cat, echo, grep, find, pwd, cd, mkdir, wc, head, tail, sort, uniq, "
            "python, python3, pip, node, npm, git, docker, curl, wget, ps, top"
        )

    tool_description = (
        f"Execute shell commands with automatic platform detection. {platform_info}"
        "\n\nCommands are validated against security policies and execute with resource limits. "
        "If the command doesn't complete within the timeout, you'll receive a command_id to check status later. "
        "\n\n**Security**: Only whitelisted commands are allowed. "
        "Dangerous commands (rm -rf, sudo, chmod 777, del /F /S /Q, format, diskpart) are blocked. "
        "\n\n**Resource Limits**: Max 3 concurrent commands, 10 commands per minute, "
        "1 minute max execution time, 1MB max output size."
    )

    tool_arguments = {
        "command": {
            "type": "string",
            "description": (
                f"Shell command to execute. Must be from whitelist: {whitelist_commands}. "
                f"\n\n{command_examples}"
            ),
        },
        "timeout": {
            "type": "integer",
            "description": (
                "Timeout in seconds to wait for command completion (default: 5). "
                "If command is still running after timeout, returns status='running' with command_id "
                "for status checking. Max: 60 seconds."
            ),
            "default": 5,
        },
        "working_dir": {
            "type": "string",
            "default": "./",
            "description": (
                "Working directory for command execution. Default is current directory ('./'). "
            ),
        },
        "env_vars": {
            "type": "object",
            "description": (
                "Additional environment variables as key-value pairs (optional). "
                "Cannot override protected variables (PATH, HOME, USER). "
                "Example: {'DEBUG': 'true', 'API_KEY': 'xxx'}"
            ),
        },
    }

    tool_required = ["command"]

    if provider == "claude":
        return {
            "name": "run_command",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or others
        return {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_check_command_status_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for checking command status.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    import sys

    is_windows = sys.platform == "win32"

    platform_examples = (
        "\n\n**Usage Pattern**:"
        "\n1. Run long command: run_command(command='python train.py', timeout=5)"
        "\n2. Get command_id from response if status='running'"
        "\n3. Check periodically: check_command_status(command_id='cmd_xxx')"
        "\n4. Repeat until status='completed' or 'timeout'"
    )

    if is_windows:
        use_case = (
            "\n\n**Windows Examples**:"
            "\n• Monitor build: 'python -m build' or 'npm run build'"
            "\n• Watch install: 'pip install -r requirements.txt'"
            "\n• Track test: 'python -m pytest tests/'"
        )
    else:
        use_case = (
            "\n\n**Unix Examples**:"
            "\n• Monitor build: 'make build' or 'npm run build'"
            "\n• Watch install: 'pip install -r requirements.txt'"
            "\n• Track test: 'pytest tests/' or './run_tests.sh'"
        )

    tool_description = (
        f"Check the status and output of a running command. Use this to monitor long-running commands "
        f"that didn't complete within the initial timeout. Returns current output, status (running/completed), "
        f"and elapsed time. If command completed, includes exit code. {platform_examples}{use_case}"
        "\n\nAutomatically consumes and returns accumulated output from the command."
    )

    tool_arguments = {
        "command_id": {
            "type": "string",
            "description": (
                "Unique identifier for the command, returned by run_command when status='running'. "
                "Format: 'cmd_xxxxxxxxxxxx'. Example: 'cmd_a1b2c3d4e5f6'"
            ),
        },
    }

    tool_required = ["command_id"]

    if provider == "claude":
        return {
            "name": "check_command_status",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or others
        return {
            "type": "function",
            "function": {
                "name": "check_command_status",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_list_running_commands_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for listing running commands.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    import sys

    is_windows = sys.platform == "win32"

    usage_info = (
        "\n\n**Usage Pattern**:"
        "\n1. Check what commands are currently running: list_running_commands()"
        "\n2. Review command IDs, states, and elapsed times"
        "\n3. Use terminate_command(command_id='cmd_xxx') to stop a specific command"
        "\n4. Use check_command_status(command_id='cmd_xxx') to get detailed output"
    )

    if is_windows:
        examples = (
            "\n\n**Windows Use Cases**:"
            "\n• Monitor long-running builds or installations"
            "\n• Check status of background Python scripts"
            "\n• Identify stuck or hanging processes"
            "\n• Review active command pipeline"
        )
    else:
        examples = (
            "\n\n**Unix Use Cases**:"
            "\n• Monitor long-running builds or installations"
            "\n• Check status of background processes"
            "\n• Identify stuck or hanging commands"
            "\n• Review active command pipeline"
        )

    tool_description = (
        f"List all currently running commands with their details. "
        f"Returns command IDs, original commands, current states, elapsed times, and working directories. "
        f"Use this to monitor active commands, identify long-running processes, or find command IDs "
        f"for status checking or termination.{usage_info}{examples}"
        "\n\n**Returns**: List of all active commands with metadata including command_id, command text, "
        "state (running/completing/waiting_input), elapsed time, working directory, and platform."
    )

    tool_arguments = {}

    tool_required = []

    if provider == "claude":
        return {
            "name": "list_running_commands",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or others
        return {
            "type": "function",
            "function": {
                "name": "list_running_commands",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_terminate_command_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for terminating running commands.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    import sys

    is_windows = sys.platform == "win32"

    workflow = (
        "\n\n**Workflow**:"
        "\n1. Use list_running_commands() to see active commands"
        "\n2. Identify the command_id of the process to terminate"
        "\n3. Call terminate_command(command_id='cmd_xxx')"
        "\n4. Command and all child processes will be terminated"
    )

    if is_windows:
        termination_info = (
            "\n\n**Windows Termination**: Uses TERMINATE then KILL with grace period. "
            "Attempts graceful shutdown first, then forces termination if needed."
        )
    else:
        termination_info = (
            "\n\n**Unix Termination**: Sends SIGTERM to process group, then SIGKILL if needed. "
            "Terminates the entire process group including child processes."
        )

    tool_description = (
        f"Terminate a running command by its command ID. "
        f"This forcefully stops command execution and cleans up all associated resources. "
        f"Use this for stuck commands, hanging processes, or when cancellation is needed.{workflow}{termination_info}"
        "\n\n**Safety**: Only terminates commands managed by this service. "
        "Cannot affect external system processes. Command output up to termination point may be lost."
    )

    tool_arguments = {
        "command_id": {
            "type": "string",
            "description": (
                "Unique identifier for the command to terminate. "
                "Format: 'cmd_xxxxxxxxxxxx'. Example: 'cmd_a1b2c3d4e5f6'. "
                "Use list_running_commands() to find command IDs."
            ),
        },
    }

    tool_required = ["command_id"]

    if provider == "claude":
        return {
            "name": "terminate_command",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or others
        return {
            "type": "function",
            "function": {
                "name": "terminate_command",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_send_command_input_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for sending input to running commands.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    import sys

    is_windows = sys.platform == "win32"

    workflow = (
        "\n\n**Workflow**:"
        "\n1. run_command returns status='running' (command waiting for input)"
        "\n2. send_command_input to provide the input"
        "\n3. check_command_status to see the result"
    )

    if is_windows:
        examples = (
            "\n\n**Windows Examples**:"
            "\n• Python script: python script.py → prompts 'Enter name:' → send 'Alice'"
            "\n• Confirmation: del file.txt → prompts '(Y/N)' → send 'Y'"
            "\n• Interactive CLI: python -m pip install → prompts 'Proceed?' → send 'y'"
            "\n• Password input: psexec → prompts 'Password:' → send 'secret123'"
        )
    else:
        examples = (
            "\n\n**Unix Examples**:"
            "\n• Python script: python script.py → prompts 'Enter name:' → send 'Alice'"
            "\n• Confirmation: rm file.txt → prompts '(y/n)' → send 'y'"
            "\n• Interactive CLI: sudo apt install → prompts '[Y/n]' → send 'Y'"
            "\n• SSH/GPG: ssh-keygen → prompts 'Passphrase:' → send 'secret123'"
        )

    tool_description = (
        f"Send input to a running interactive command's stdin. Use this for commands that require user input "
        f"(e.g., Python scripts with input(), interactive CLIs, prompts, confirmations). "
        f"The input is automatically terminated with a newline character. {workflow}{examples}"
        "\n\n**Security**: Input is sanitized - max 1024 characters, no control characters except newline/tab/CR."
    )

    tool_arguments = {
        "command_id": {
            "type": "string",
            "description": (
                "Unique identifier for the running command. "
                "Format: 'cmd_xxxxxxxxxxxx'. Example: 'cmd_a1b2c3d4e5f6'"
            ),
        },
        "input_text": {
            "type": "string",
            "description": (
                "Text to send to command's stdin. Will be automatically terminated with newline. "
                "Max 1024 characters. Examples: 'Alice' (name), 'yes' (confirmation), 'password123' (password), "
                "'1' (menu selection), 'q' (quit command)"
            ),
        },
    }

    tool_required = ["command_id", "input_text"]

    if provider == "claude":
        return {
            "name": "send_command_input",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or others
        return {
            "type": "function",
            "function": {
                "name": "send_command_input",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_run_command_tool_handler(command_service: CommandExecutionService) -> Callable:
    """
    Get the handler function for the run_command tool.

    Args:
        command_service: The command execution service instance

    Returns:
        Function that handles command execution requests
    """

    def handle_run_command(**params) -> str | Dict[str, Any]:
        """
        Handle command execution request.

        Returns:
            Result dict or formatted string with command output
        """
        command = params.get("command")
        timeout = params.get("timeout", 5)
        working_dir = params.get("working_dir", "./")
        env_vars = params.get("env_vars")

        if not command:
            raise ValueError("Missing required parameter: command")

        if timeout < 1 or timeout > 60:
            raise ValueError("Timeout must be between 1 and 60 seconds")

        result = command_service.execute_command(
            command=command,
            timeout=timeout,
            working_dir=working_dir,
            env_vars=env_vars,
        )

        if result["status"] == "completed":
            response = "Command completed successfully.\n"
            response += f"Exit Code: {result['exit_code']}\n"
            response += f"Duration: {result['duration_seconds']}s\n\n"

            if result["output"]:
                response += f"Output:\n{result['output']}"

            if result.get("error"):
                response += f"\n\nStderr:\n{result['error']}"

            return response

        elif result["status"] == "running":
            response = f"Command is still running after {result['timeout_seconds']}s.\n"
            response += f"Command ID: {result['command_id']}\n\n"
            response += "Use check_command_status(command_id='{cmd_id}') to monitor progress.\n".format(
                cmd_id=result["command_id"]
            )
            response += "Use send_command_input(command_id='{cmd_id}', input_text='...') ".format(
                cmd_id=result["command_id"]
            )
            response += "if command is waiting for input."

            return response

        else:  # error
            return f"Command execution failed: {result.get('error', 'Unknown error')}"

    return handle_run_command


def get_check_command_status_tool_handler(
    command_service: CommandExecutionService,
) -> Callable:
    """
    Get the handler function for the check_command_status tool.

    Args:
        command_service: The command execution service instance

    Returns:
        Function that handles status check requests
    """

    def handle_check_command_status(**params) -> str | Dict[str, Any]:
        """
        Handle command status check request.

        Returns:
            Formatted string with command status and output
        """
        command_id = params.get("command_id")

        if not command_id:
            raise ValueError("Missing required parameter: command_id")

        result = command_service.get_command_status(
            command_id=command_id, consume_output=True
        )

        if result["status"] == "completed":
            response = "Command completed.\n"
            response += f"Exit Code: {result['exit_code']}\n"
            response += f"Duration: {result['duration_seconds']}s\n\n"

            if result["output"]:
                response += f"Output:\n{result['output']}"

            if result.get("error"):
                response += f"\n\nStderr:\n{result['error']}"

            return response

        elif result["status"] == "running":
            response = "Command is still running.\n"
            response += f"Elapsed: {result['elapsed_seconds']}s\n"
            response += f"State: {result.get('state', 'running')}\n\n"

            if result.get("output"):
                response += f"Output so far:\n{result['output']}\n\n"

            if result.get("error"):
                response += f"Stderr so far:\n{result['error']}\n\n"

            response += "Check again later to monitor progress."

            return response

        elif result["status"] == "timeout":
            response = "Command exceeded maximum lifetime and was terminated.\n"
            response += f"Elapsed: {result['elapsed_seconds']}s\n\n"

            if result.get("output"):
                response += f"Output before timeout:\n{result['output']}"

            if result.get("error"):
                response += f"\n\nStderr:\n{result['error']}"

            return response

        else:
            return (
                f"Error checking command status: {result.get('error', 'Unknown error')}"
            )

    return handle_check_command_status


def get_list_running_commands_tool_handler(
    command_service: CommandExecutionService,
) -> Callable:
    """
    Get the handler function for the list_running_commands tool.

    Args:
        command_service: The command execution service instance

    Returns:
        Function that handles list running commands requests
    """

    def handle_list_running_commands(**params) -> str | Dict[str, Any]:
        """
        Handle list running commands request.

        Returns:
            Formatted string with all running commands
        """
        result = command_service.list_running_commands()

        if result["status"] == "error":
            return f"Error listing commands: {result.get('error', 'Unknown error')}"

        count = result["count"]
        commands = result["commands"]

        if count == 0:
            return "No commands are currently running."

        response = f"Currently running commands: {count}\n\n"

        for idx, cmd_info in enumerate(commands, 1):
            response += f"{idx}. Command ID: {cmd_info['command_id']}\n"
            response += f"   Command: {cmd_info['command']}\n"
            response += f"   State: {cmd_info['state']}\n"
            response += f"   Elapsed: {cmd_info['elapsed_seconds']}s\n"
            response += f"   Working Dir: {cmd_info['working_dir']}\n"

            if "exit_code" in cmd_info:
                response += f"   Exit Code: {cmd_info['exit_code']}\n"

            response += "\n"

        response += (
            "Use check_command_status(command_id='cmd_xxx') for detailed output.\n"
        )
        response += "Use terminate_command(command_id='cmd_xxx') to stop a command."

        return response

    return handle_list_running_commands


def get_terminate_command_tool_handler(
    command_service: CommandExecutionService,
) -> Callable:
    """
    Get the handler function for the terminate_command tool.

    Args:
        command_service: The command execution service instance

    Returns:
        Function that handles command termination requests
    """

    def handle_terminate_command(**params) -> str | Dict[str, Any]:
        """
        Handle command termination request.

        Returns:
            Success message or error
        """
        command_id = params.get("command_id")

        if not command_id:
            raise ValueError("Missing required parameter: command_id")

        result = command_service.terminate_command(command_id=command_id)

        if result["status"] == "success":
            return (
                f"Command {command_id} has been terminated successfully.\n"
                "All associated processes and resources have been cleaned up."
            )
        else:
            return (
                f"Failed to terminate command: {result.get('error', 'Unknown error')}"
            )

    return handle_terminate_command


def get_send_command_input_tool_handler(
    command_service: CommandExecutionService,
) -> Callable:
    """
    Get the handler function for the send_command_input tool.

    Args:
        command_service: The command execution service instance

    Returns:
        Function that handles input send requests
    """

    def handle_send_command_input(**params) -> str | Dict[str, Any]:
        """
        Handle send input request.

        Returns:
            Success message or error
        """
        command_id = params.get("command_id")
        input_text = params.get("input_text")

        if not command_id:
            raise ValueError("Missing required parameter: command_id")

        if not input_text:
            raise ValueError("Missing required parameter: input_text")
        result = command_service.send_input(
            command_id=command_id, input_text=input_text
        )

        if result["status"] == "success":
            return (
                f"Input sent successfully to command {command_id}.\n"
                "Use check_command_status to see the result."
            )
        else:
            return f"Failed to send input: {result.get('error', 'Unknown error')}"

    return handle_send_command_input


def register(service_instance=None, agent=None):
    """
    Register command execution tools with the central registry or directly with an agent.

    Args:
        service_instance: The command execution service instance
        agent: Agent instance to register with directly (optional)
    """
    from AgentCrew.modules.tools.registration import register_tool

    if service_instance is None:
        service_instance = CommandExecutionService.get_instance()

    register_tool(
        get_run_command_tool_definition,
        get_run_command_tool_handler,
        service_instance,
        agent,
    )

    register_tool(
        get_check_command_status_tool_definition,
        get_check_command_status_tool_handler,
        service_instance,
        agent,
    )

    register_tool(
        get_send_command_input_tool_definition,
        get_send_command_input_tool_handler,
        service_instance,
        agent,
    )

    register_tool(
        get_list_running_commands_tool_definition,
        get_list_running_commands_tool_handler,
        service_instance,
        agent,
    )

    register_tool(
        get_terminate_command_tool_definition,
        get_terminate_command_tool_handler,
        service_instance,
        agent,
    )

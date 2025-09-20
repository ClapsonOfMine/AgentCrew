"""
Browser automation tool definitions and handlers.

Provides five tools for browser automation:
- browser_navigate: Navigate to URLs
- browser_click: Click elements using XPath selectors
- browser_scroll: Scroll page content in specified directions
- browser_get_content: Extract page content, clickable elements, and input elements as markdown
- browser_input: Input data into form fields using XPath selectors
"""

from typing import Dict, Any, Callable
from .service import BrowserAutomationService


def get_browser_navigate_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for browser navigation based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Navigate to a specific URL in the controlled browser. Use this to visit web pages, follow links, or load specific websites. The browser will load the page and wait for content to be ready. Always check the result to confirm successful navigation before proceeding with other browser actions."
    tool_arguments = {
        "url": {
            "type": "string",
            "description": "The URL to navigate to. Must be a valid HTTP or HTTPS URL (e.g., 'https://example.com'). Ensure the URL is properly formatted and accessible.",
        }
    }
    tool_required = ["url"]

    if provider == "claude":
        return {
            "name": "browser_navigate",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or other OpenAI-compatible
        return {
            "type": "function",
            "function": {
                "name": "browser_navigate",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_browser_click_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for browser element clicking based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Click on a specific element in the browser using an XPath selector. Use this to interact with buttons, links, form inputs, and other clickable elements. The element must be visible and enabled. Use browser_get_content first to identify available clickable elements and their XPath selectors."
    tool_arguments = {
        "xpath": {
            "type": "string",
            "description": "The XPath selector for the element to click. Must be a valid XPath expression that uniquely identifies the target element (e.g., '//button[@id=\"submit\"]' or '/html/body/div[1]/button[2]'). Use the XPath values from browser_get_content output.",
        }
    }
    tool_required = ["xpath"]

    if provider == "claude":
        return {
            "name": "browser_click",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or other OpenAI-compatible
        return {
            "type": "function",
            "function": {
                "name": "browser_click",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_browser_scroll_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for browser scrolling based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Scroll the page content in a specified direction. Use this to reveal more content, navigate to different sections of a page, or bring specific elements into view. Each scroll unit moves approximately 300 pixels. Useful when content extends beyond the current viewport."
    tool_arguments = {
        "direction": {
            "type": "string",
            "enum": ["up", "down", "left", "right"],
            "description": "The direction to scroll the page. 'up' and 'down' are most commonly used for vertical scrolling, while 'left' and 'right' are for horizontal scrolling.",
        },
        "amount": {
            "type": "integer",
            "description": "Number of scroll units to move (default: 3). Each unit is approximately 300 pixels. Use smaller values (1-2) for precise scrolling, larger values (4-6) for quick navigation.",
            "default": 3,
            "minimum": 1,
            "maximum": 10,
        },
    }
    tool_required = ["direction"]

    if provider == "claude":
        return {
            "name": "browser_scroll",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or other OpenAI-compatible
        return {
            "type": "function",
            "function": {
                "name": "browser_scroll",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_browser_get_content_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for browser content extraction based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Extract the current page content and identify all clickable and input elements. Returns the page content converted to markdown format along with tables of clickable elements and input elements with their XPath selectors. Use this to understand what's currently visible on the page and to identify elements you can interact with using browser_click or browser_input."
    tool_arguments = {}
    tool_required = []

    if provider == "claude":
        return {
            "name": "browser_get_content",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or other OpenAI-compatible
        return {
            "type": "function",
            "function": {
                "name": "browser_get_content",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_browser_navigate_tool_handler(
    browser_service: BrowserAutomationService,
) -> Callable:
    """
    Get the handler function for the browser navigate tool.

    Args:
        browser_service: The browser automation service instance

    Returns:
        Function that handles browser navigation requests
    """

    def handle_browser_navigate(**params) -> str:
        url = params.get("url")

        if not url:
            return "Error: No URL provided for navigation."

        result = browser_service.navigate(url)

        if result.get("success", True):
            return f"✅ {result.get('message', 'Success')}. Use `browser_get_content` to read the url content.\nCurrent URL: {result.get('current_url', 'Unknown')}"
        else:
            return f"❌ Navigation failed: {result['error']}"

    return handle_browser_navigate


def get_browser_click_tool_handler(
    browser_service: BrowserAutomationService,
) -> Callable:
    """
    Get the handler function for the browser click tool.

    Args:
        browser_service: The browser automation service instance

    Returns:
        Function that handles browser click requests
    """

    def handle_browser_click(**params) -> str:
        xpath = params.get("xpath")

        if not xpath:
            return "Error: No XPath provided for element clicking."

        result = browser_service.click_element(xpath)
        print(result)

        if result.get("success", True):
            return f"✅ {result.get('message', 'Success')}. Use `browser_get_content` to get the updated content.\nXPath: {xpath}"
        else:
            return f"❌ Click failed: {result['error']}\nXPath: {xpath}"

    return handle_browser_click


def get_browser_scroll_tool_handler(
    browser_service: BrowserAutomationService,
) -> Callable:
    """
    Get the handler function for the browser scroll tool.

    Args:
        browser_service: The browser automation service instance

    Returns:
        Function that handles browser scroll requests
    """

    def handle_browser_scroll(**params) -> str:
        direction = params.get("direction")
        amount = params.get("amount", 3)

        if not direction:
            return "Error: No scroll direction provided."

        if direction not in ["up", "down", "left", "right"]:
            return (
                "Error: Invalid scroll direction. Use 'up', 'down', 'left', or 'right'."
            )

        result = browser_service.scroll_page(direction, amount)

        if result.get("success", True):
            return f"✅ {result.get('message', 'Success')}. Use `browser_get_content` to get the updated content."
        else:
            return f"❌ Scroll failed: {result['error']}"

    return handle_browser_scroll


def get_browser_input_tool_definition(provider="claude") -> Dict[str, Any]:
    """
    Get the tool definition for browser input based on provider.

    Args:
        provider: The LLM provider ("claude" or "groq")

    Returns:
        Dict containing the tool definition
    """
    tool_description = "Input data into a form field or input element using an XPath selector. Use this to fill out forms, enter text into search boxes, select options from dropdowns, or input data into any editable field. The element must be visible and enabled. Use browser_get_content first to identify available input elements and their XPath selectors."
    tool_arguments = {
        "xpath": {
            "type": "string",
            "description": "The XPath selector for the input element to fill. Must be a valid XPath expression that uniquely identifies the target input field (e.g., '//input[@id=\"username\"]' or '/html/body/form/input[1]'). Use the XPath values from browser_get_content output.",
        },
        "value": {
            "type": "string",
            "description": "The value to input into the field. For text inputs, this will be the text to enter. For select elements, this should be either the option value or option text. For checkboxes, use 'true' or 'false'.",
        },
    }
    tool_required = ["xpath", "value"]

    if provider == "claude":
        return {
            "name": "browser_input",
            "description": tool_description,
            "input_schema": {
                "type": "object",
                "properties": tool_arguments,
                "required": tool_required,
            },
        }
    else:  # provider == "groq" or other OpenAI-compatible
        return {
            "type": "function",
            "function": {
                "name": "browser_input",
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": tool_arguments,
                    "required": tool_required,
                },
            },
        }


def get_browser_get_content_tool_handler(
    browser_service: BrowserAutomationService,
) -> Callable:
    """
    Get the handler function for the browser content extraction tool.

    Args:
        browser_service: The browser automation service instance

    Returns:
        Function that handles browser content extraction requests
    """

    def handle_browser_get_content(**params) -> str:
        result = browser_service.get_page_content()

        if result["success"]:
            content_info = "📄 Page content extracted successfully\n"
            content_info += f"URL: {result.get('url', 'Unknown')}\n"
            content_info += (
                f"Content length: {result.get('content_length', 0)} characters\n"
            )

            status_messages = []
            if result.get("has_clickable_elements"):
                status_messages.append("✅ Clickable elements found")
            else:
                status_messages.append("ℹ️ No clickable elements found")

            if result.get("has_input_elements"):
                status_messages.append("✅ Input elements found")
            else:
                status_messages.append("ℹ️ No input elements found")

            content_info += " | ".join(status_messages) + "\n\n"

            return content_info + "---\n\n" + result["content"]
        else:
            return f"❌ Content extraction failed: {result['error']}"

    return handle_browser_get_content


def get_browser_input_tool_handler(
    browser_service: BrowserAutomationService,
) -> Callable:
    """
    Get the handler function for the browser input tool.

    Args:
        browser_service: The browser automation service instance

    Returns:
        Function that handles browser input requests
    """

    def handle_browser_input(**params) -> str:
        xpath = params.get("xpath")
        value = params.get("value")

        if not xpath:
            return "Error: No XPath provided for input element."

        if value is None:
            return "Error: No value provided for input."

        result = browser_service.input_data(xpath, str(value))

        if result.get("success", True):
            return (
                f"✅ {result.get('message', 'Success')}\nXPath: {xpath}\nValue: {value}"
            )
        else:
            return f"❌ Input failed: {result['error']}\nXPath: {xpath}\nValue: {value}"

    return handle_browser_input


def register(service_instance=None, agent=None):
    """
    Register browser automation tools with the central registry or directly with an agent.

    Args:
        service_instance: The browser automation service instance
        agent: Agent instance to register with directly (optional)
    """
    from AgentCrew.modules.tools.registration import register_tool

    # Register all five browser automation tools
    register_tool(
        get_browser_navigate_tool_definition,
        get_browser_navigate_tool_handler,
        service_instance,
        agent,
    )
    register_tool(
        get_browser_click_tool_definition,
        get_browser_click_tool_handler,
        service_instance,
        agent,
    )
    register_tool(
        get_browser_scroll_tool_definition,
        get_browser_scroll_tool_handler,
        service_instance,
        agent,
    )
    register_tool(
        get_browser_get_content_tool_definition,
        get_browser_get_content_tool_handler,
        service_instance,
        agent,
    )
    register_tool(
        get_browser_input_tool_definition,
        get_browser_input_tool_handler,
        service_instance,
        agent,
    )

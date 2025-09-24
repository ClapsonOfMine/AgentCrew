"""
JavaScript file loader and template processor for browser automation.

This module provides utilities to load JavaScript files and inject variables
for use with Chrome DevTools Protocol.
"""

from pathlib import Path
from typing import Dict


class JavaScriptLoader:
    """Loads and processes JavaScript files for browser automation."""

    def __init__(self):
        """Initialize the JavaScript loader with the js directory path."""
        self.js_dir = Path(__file__).parent / "js"
        self._js_cache: Dict[str, str] = {}

    def load_js_file(self, filename: str) -> str:
        """
        Load a JavaScript file from the js directory.

        Args:
            filename: Name of the JavaScript file (with or without .js extension)

        Returns:
            JavaScript code as string

        Raises:
            FileNotFoundError: If the JavaScript file doesn't exist
        """
        # Ensure .js extension
        if not filename.endswith(".js"):
            filename += ".js"

        # Check cache first
        if filename in self._js_cache:
            return self._js_cache[filename]

        file_path = self.js_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"JavaScript file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            js_code = f.read()

        # Cache the loaded code
        self._js_cache[filename] = js_code
        return js_code

    def get_extract_clickable_elements_js(self) -> str:
        """Get JavaScript code for extracting clickable elements."""
        return self.load_js_file("extract_clickable_elements.js")

    def get_extract_input_elements_js(self) -> str:
        """Get JavaScript code for extracting input elements."""
        return self.load_js_file("extract_input_elements.js")

    def get_extract_scrollable_elements_js(self) -> str:
        """Get JavaScript code for extracting scrollable elements."""
        return self.load_js_file("extract_scrollable_elements.js")

    def get_extract_elements_by_text_js(self, text: str) -> str:
        """
        Get JavaScript code for extracting elements by text.

        Args:
            text: Text to search for in elements

        Returns:
            JavaScript code with text parameter injected
        """
        # Load the base function
        js_code = self.load_js_file("extract_elements_by_text.js")

        # Escape the text for JavaScript
        escaped_text = text.replace("'", "\\'").replace("\\", "\\\\")

        # Wrap with IIFE and inject the text parameter
        wrapper = f"""
        (() => {{
            const text = `{escaped_text}`;
            return extractElementsByText(text);
        }})();
        """

        return js_code + "\n" + wrapper

    def get_click_element_js(self, xpath: str) -> str:
        """
        Get JavaScript code for clicking an element.

        Args:
            xpath: XPath selector for the element to click

        Returns:
            JavaScript code with xpath parameter injected
        """
        js_code = self.load_js_file("click_element.js")

        # Escape the xpath for JavaScript
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")

        # Wrap with IIFE and inject the xpath parameter
        wrapper = f"""
        (() => {{
            const xpath = `{escaped_xpath}`;
            return clickElement(xpath);
        }})();
        """

        return js_code + "\n" + wrapper

    def get_scroll_page_js(
        self, direction: str, distance: int, xpath: str = "", element_uuid: str = ""
    ) -> str:
        """
        Get JavaScript code for scrolling the page or element.

        Args:
            direction: Direction to scroll ('up', 'down', 'left', 'right')
            distance: Distance to scroll in pixels
            xpath: Optional XPath of specific element to scroll
            element_uuid: Optional UUID of the element for identification

        Returns:
            JavaScript code with parameters injected
        """
        js_code = self.load_js_file("scroll_page.js")

        # Escape parameters for JavaScript
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")
        escaped_uuid = element_uuid.replace("`", "\\`").replace("\\", "\\\\")

        # Wrap with IIFE and inject parameters
        wrapper = f"""
        (() => {{
            const direction = '{direction}';
            const distance = {distance};
            const xpath = `{escaped_xpath}`;
            const elementUuid = `{escaped_uuid}`;
            return scrollPage(direction, distance, xpath, elementUuid);
        }})();
        """

        return js_code + "\n" + wrapper

    def get_focus_and_clear_element_js(self, xpath: str) -> str:
        """
        Get JavaScript code for focusing and clearing an element.

        Args:
            xpath: XPath selector for the element

        Returns:
            JavaScript code with xpath parameter injected
        """
        js_code = self.load_js_file("focus_and_clear_element.js")

        # Escape the xpath for JavaScript
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")

        # Wrap with IIFE and inject the xpath parameter
        wrapper = f"""
        (() => {{
            const xpath = `{escaped_xpath}`;
            return focusAndClearElement(xpath);
        }})();
        """

        return js_code + "\n" + wrapper

    def get_trigger_input_events_js(self, xpath: str, value: str) -> str:
        """
        Get JavaScript code for triggering input events.

        Args:
            xpath: XPath selector for the element

        Returns:
            JavaScript code with xpath parameter injected
        """
        js_code = self.load_js_file("trigger_input_events.js")

        # Escape the xpath for JavaScript
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")

        # Wrap with IIFE and inject the xpath parameter
        wrapper = f"""
        (() => {{
            const xpath = `{escaped_xpath}`;
            const value = `{value}`;
            return triggerInputEvents(xpath, value);
        }})();
        """

        return js_code + "\n" + wrapper

    def clear_cache(self):
        """Clear the JavaScript file cache."""
        self._js_cache.clear()


# Global instance for convenience
js_loader = JavaScriptLoader()

# Key code mapping for common keys
key_codes = {
    # Arrow Keys
    "up": 38,
    "down": 40,
    "left": 37,
    "right": 39,
    # Navigation Keys
    "home": 36,
    "end": 35,
    "pageup": 33,
    "pagedown": 34,
    # Control Keys
    "enter": 13,
    "escape": 27,
    "tab": 9,
    "backspace": 8,
    "delete": 46,
    "space": 32,
    # Function Keys
    "f1": 112,
    "f2": 113,
    "f3": 114,
    "f4": 115,
    "f5": 116,
    "f6": 117,
    "f7": 118,
    "f8": 119,
    "f9": 120,
    "f10": 121,
    "f11": 122,
    "f12": 123,
    # Numpad
    "numpad0": 96,
    "numpad1": 97,
    "numpad2": 98,
    "numpad3": 99,
    "numpad4": 100,
    "numpad5": 101,
    "numpad6": 102,
    "numpad7": 103,
    "numpad8": 104,
    "numpad9": 105,
    # Media Keys
    "volumeup": 175,
    "volume_up": 175,
    "volumedown": 174,
    "volume_down": 174,
    "volumemute": 173,
    "volume_mute": 173,
    # Lock Keys
    "capslock": 20,
    "numlock": 144,
    "scrolllock": 145,
    # Modifier Keys (for key events, not just modifiers)
    "shift": 16,
    "ctrl": 17,
    "control": 17,
    "alt": 18,
    "meta": 91,
    "cmd": 91,
    "command": 91,
    "windows": 91,
}

"""
JavaScript file loader and template processor for browser automation.

This module provides utilities to load JavaScript files and inject variables
for use with Chrome DevTools Protocol.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import time
from loguru import logger


class JavaScriptExecutor:
    """Handles JavaScript code execution and result parsing for browser automation."""

    @staticmethod
    def execute_and_parse_result(chrome_interface: Any, js_code: str) -> Dict[str, Any]:
        """
        Execute JavaScript code and parse the result.

        Args:
            chrome_interface: Chrome DevTools Protocol interface
            js_code: JavaScript code to execute

        Returns:
            Parsed result dictionary
        """
        try:
            result = (None, [])
            retried = 0
            while result[0] is None and retried < 10:
                result = chrome_interface.Runtime.evaluate(
                    expression=js_code,
                    returnByValue=True,
                    awaitPromise=True,
                    timeout=60000,
                )
                retried += 1
                time.sleep(0.4)

            if isinstance(result, tuple) and len(result) >= 2:
                if isinstance(result[1], dict):
                    return (
                        result[1].get("result", {}).get("result", {}).get("value", {})
                    )
                elif isinstance(result[1], list) and len(result[1]) > 0:
                    return (
                        result[1][0]
                        .get("result", {})
                        .get("result", {})
                        .get("value", {})
                    )
                else:
                    return {
                        "success": False,
                        "error": "Invalid response format from JavaScript execution",
                    }
            else:
                return {
                    "success": False,
                    "error": "No response from JavaScript execution",
                }

        except Exception as e:
            logger.error(f"JavaScript execution error: {e}")
            return {"success": False, "error": f"JavaScript execution error: {str(e)}"}

    @staticmethod
    def get_current_url(chrome_interface: Any) -> str:
        """
        Get the current page URL.

        Args:
            chrome_interface: Chrome DevTools Protocol interface

        Returns:
            Current URL or "Unknown" if retrieval fails
        """
        try:
            runtime_result = chrome_interface.Runtime.evaluate(
                expression="window.location.href"
            )

            if isinstance(runtime_result, tuple) and len(runtime_result) >= 2:
                if isinstance(runtime_result[1], dict):
                    current_url = (
                        runtime_result[1]
                        .get("result", {})
                        .get("result", {})
                        .get("value", "Unknown")
                    )
                elif isinstance(runtime_result[1], list) and len(runtime_result[1]) > 0:
                    current_url = (
                        runtime_result[1][0]
                        .get("result", {})
                        .get("result", {})
                        .get("value", "Unknown")
                    )
                else:
                    current_url = "Unknown"
            else:
                current_url = "Unknown"

            return current_url

        except Exception as e:
            logger.warning(f"Could not get current URL: {e}")
            return "Unknown"

    @staticmethod
    def focus_and_clear_element(chrome_interface: Any, xpath: str) -> Dict[str, Any]:
        """
        Focus an element and clear its content.

        Args:
            chrome_interface: Chrome DevTools Protocol interface
            xpath: XPath selector for the element

        Returns:
            Result dictionary with success status
        """
        js_code = js_loader.get_focus_and_clear_element_js(xpath)
        return JavaScriptExecutor.execute_and_parse_result(chrome_interface, js_code)

    @staticmethod
    def draw_element_boxes(
        chrome_interface: Any, uuid_xpath_dict: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Draw colored rectangle boxes with UUID labels over elements.

        Args:
            uuid_xpath_dict: Dictionary mapping UUIDs to XPath selectors

        Returns:
            Dict containing the result of the drawing operation
        """
        try:
            js_code = js_loader.get_draw_element_boxes_js(uuid_xpath_dict)
            eval_result = JavaScriptExecutor.execute_and_parse_result(
                chrome_interface, js_code
            )

            if not eval_result:
                return {
                    "success": False,
                    "error": "No result from drawing element boxes",
                }

            return eval_result

        except Exception as e:
            logger.error(f"Draw element boxes error: {e}")
            return {"success": False, "error": f"Draw element boxes error: {str(e)}"}

    @staticmethod
    def remove_element_boxes(chrome_interface: Any) -> Dict[str, Any]:
        """
        Remove the overlay container with element boxes.

        Returns:
            Dict containing the result of the removal operation
        """
        try:
            js_code = js_loader.get_remove_element_boxes_js()
            eval_result = JavaScriptExecutor.execute_and_parse_result(
                chrome_interface, js_code
            )

            if not eval_result:
                return {
                    "success": False,
                    "error": "No result from removing element boxes",
                }

            return eval_result

        except Exception as e:
            logger.error(f"Remove element boxes error: {e}")
            return {"success": False, "error": f"Remove element boxes error: {str(e)}"}

    @staticmethod
    def trigger_input_events(
        chrome_interface: Any, xpath: str, value: str
    ) -> Dict[str, Any]:
        """
        Trigger input and change events on an element.

        Args:
            chrome_interface: Chrome DevTools Protocol interface
            xpath: XPath selector for the element
            value: Value to set

        Returns:
            Result dictionary with success status
        """
        js_code = js_loader.get_trigger_input_events_js(xpath, value)
        return JavaScriptExecutor.execute_and_parse_result(chrome_interface, js_code)

    @staticmethod
    def simulate_typing(chrome_interface: Any, text: str) -> Dict[str, Any]:
        """
        Simulate keyboard typing character by character.

        Args:
            chrome_interface: Chrome DevTools Protocol interface
            text: Text to type

        Returns:
            Result dictionary with success status and characters typed
        """
        try:
            for char in text:
                time.sleep(0.05)

                if char == "\n":
                    chrome_interface.Input.dispatchKeyEvent(
                        **{
                            "type": "rawKeyDown",
                            "windowsVirtualKeyCode": 13,
                            "unmodifiedText": "\r",
                            "text": "\r",
                        }
                    )
                    chrome_interface.Input.dispatchKeyEvent(
                        **{
                            "type": "char",
                            "windowsVirtualKeyCode": 13,
                            "unmodifiedText": "\r",
                            "text": "\r",
                        }
                    )
                    chrome_interface.Input.dispatchKeyEvent(
                        **{
                            "type": "keyUp",
                            "windowsVirtualKeyCode": 13,
                            "unmodifiedText": "\r",
                            "text": "\r",
                        }
                    )
                elif char == "\t":
                    chrome_interface.Input.dispatchKeyEvent(type="char", text="\t")
                else:
                    chrome_interface.Input.dispatchKeyEvent(type="char", text=char)

            return {
                "success": True,
                "message": f"Successfully typed {len(text)} characters",
                "characters_typed": len(text),
            }

        except Exception as e:
            logger.error(f"Error during typing simulation: {e}")
            return {"success": False, "error": f"Typing simulation failed: {str(e)}"}

    @staticmethod
    def dispatch_key_event(
        chrome_interface: Any, key: str, modifiers: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Dispatch key events using CDP.

        Args:
            chrome_interface: Chrome DevTools Protocol interface
            key: Key to dispatch (e.g., 'Enter', 'Up', 'Down')
            modifiers: Optional list of modifiers ('ctrl', 'alt', 'shift')

        Returns:
            Result dictionary with success status
        """
        if modifiers is None:
            modifiers = []

        try:
            key_name = key.lower().strip()
            key_code = key_codes.get(key_name)

            if key_code is None:
                return {
                    "success": False,
                    "error": f"Unknown key '{key}'. Supported keys: {', '.join(sorted(key_codes.keys()))}",
                    "key": key,
                    "modifiers": modifiers,
                }

            modifier_flags = 0
            if modifiers:
                modifier_names = [m.strip().lower() for m in modifiers]
                for mod in modifier_names:
                    if mod in ["alt"]:
                        modifier_flags |= 1
                    elif mod in ["ctrl", "control"]:
                        modifier_flags |= 2
                    elif mod in ["meta", "cmd", "command"]:
                        modifier_flags |= 4
                    elif mod in ["shift"]:
                        modifier_flags |= 8

            chrome_interface.Input.dispatchKeyEvent(
                type="rawKeyDown",
                windowsVirtualKeyCode=key_code,
                modifiers=modifier_flags,
            )

            printable_keys = {"space", "spacebar", "enter", "return", "tab"}
            if key_name in printable_keys:
                if key_name in ["space", "spacebar"]:
                    char_text = " "
                elif key_name in ["enter", "return"]:
                    char_text = "\r"
                elif key_name == "tab":
                    char_text = "\t"
                else:
                    char_text = ""

                if char_text:
                    chrome_interface.Input.dispatchKeyEvent(
                        type="char",
                        windowsVirtualKeyCode=key_code,
                        text=char_text,
                        unmodifiedText=char_text,
                        modifiers=modifier_flags,
                    )

            chrome_interface.Input.dispatchKeyEvent(
                type="keyUp", windowsVirtualKeyCode=key_code, modifiers=modifier_flags
            )

            time.sleep(0.1)

            return {
                "success": True,
                "message": f"Successfully dispatched key '{key}' with modifiers '{modifiers}'",
                "key": key,
                "key_code": key_code,
                "modifiers": modifiers,
                "modifier_flags": modifier_flags,
            }

        except Exception as e:
            logger.error(f"Key dispatch error: {e}")
            return {
                "success": False,
                "error": f"Key dispatch error: {str(e)}",
                "key": key,
                "modifiers": modifiers,
            }

    @staticmethod
    def filter_hidden_elements(chrome_interface: Any) -> Dict[str, Any]:
        """
        Filter hidden elements from HTML using computed styles.
        Does not modify the actual page, returns filtered HTML string.

        Args:
            chrome_interface: Chrome DevTools Protocol interface

        Returns:
            Result dictionary with filtered HTML string
        """
        js_code = js_loader.get_filter_hidden_elements_js()
        return JavaScriptExecutor.execute_and_parse_result(chrome_interface, js_code)


class JavaScriptLoader:
    """Loads and processes JavaScript files for browser automation."""

    def __init__(self):
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
        if not filename.endswith(".js"):
            filename += ".js"

        if filename in self._js_cache:
            return self._js_cache[filename]

        file_path = self.js_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"JavaScript file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            js_code = f.read()

        self._js_cache[filename] = js_code
        return js_code

    def get_extract_clickable_elements_js(self) -> str:
        return self.load_js_file("extract_clickable_elements.js")

    def get_extract_input_elements_js(self) -> str:
        return self.load_js_file("extract_input_elements.js")

    def get_extract_scrollable_elements_js(self) -> str:
        return self.load_js_file("extract_scrollable_elements.js")

    def get_extract_elements_by_text_js(self, text: str) -> str:
        js_code = self.load_js_file("extract_elements_by_text.js")
        escaped_text = text.replace("'", "\\'").replace("\\", "\\\\")
        wrapper = f"""
        (() => {{
            const text = `{escaped_text}`;
            return extractElementsByText(text);
        }})();
        """
        return js_code + "\n" + wrapper

    def get_click_element_js(self, xpath: str) -> str:
        js_code = self.load_js_file("click_element.js")
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")
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
        js_code = self.load_js_file("scroll_page.js")
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")
        escaped_uuid = element_uuid.replace("`", "\\`").replace("\\", "\\\\")
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
        js_code = self.load_js_file("focus_and_clear_element.js")
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")
        wrapper = f"""
        (() => {{
            const xpath = `{escaped_xpath}`;
            return focusAndClearElement(xpath);
        }})();
        """
        return js_code + "\n" + wrapper

    def get_trigger_input_events_js(self, xpath: str, value: str) -> str:
        js_code = self.load_js_file("trigger_input_events.js")
        escaped_xpath = xpath.replace("`", "\\`").replace("\\", "\\\\")
        wrapper = f"""
        (() => {{
            const xpath = `{escaped_xpath}`;
            const value = `{value}`;
            return triggerInputEvents(xpath, value);
        }})();
        """
        return js_code + "\n" + wrapper

    def get_draw_element_boxes_js(self, uuid_xpath_dict: Dict[str, str]) -> str:
        import json

        js_code = self.load_js_file("draw_element_boxes.js")
        json_str = json.dumps(uuid_xpath_dict)
        wrapper = f"""
        (() => {{
            const uuidXpathMap = {json_str};
            return drawElementBoxes(uuidXpathMap);
        }})();
        """
        return js_code + "\n" + wrapper

    def get_remove_element_boxes_js(self) -> str:
        js_code = self.load_js_file("remove_element_boxes.js")
        wrapper = """
        (() => {
            return removeElementBoxes();
        })();
        """
        return js_code + "\n" + wrapper

    def get_filter_hidden_elements_js(self) -> str:
        js_code = self.load_js_file("filter_hidden_elements.js")
        wrapper = """
        (() => {
            return filterHiddenElements();
        })();
        """
        return js_code + "\n" + wrapper

    def clear_cache(self):
        self._js_cache.clear()


js_loader = JavaScriptLoader()

key_codes = {
    "up": 38,
    "down": 40,
    "left": 37,
    "right": 39,
    "home": 36,
    "end": 35,
    "pageup": 33,
    "pagedown": 34,
    "enter": 13,
    "escape": 27,
    "tab": 9,
    "backspace": 8,
    "delete": 46,
    "space": 32,
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
    "volumeup": 175,
    "volume_up": 175,
    "volumedown": 174,
    "volume_down": 174,
    "volumemute": 173,
    "volume_mute": 173,
    "capslock": 20,
    "numlock": 144,
    "scrolllock": 145,
    "shift": 16,
    "ctrl": 17,
    "control": 17,
    "alt": 18,
    "meta": 91,
    "cmd": 91,
    "command": 91,
    "windows": 91,
}

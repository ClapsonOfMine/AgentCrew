"""
Browser automation service for controlling Chrome browser.

This service provides functionality to navigate web pages, click elements,
scroll content, and extract page information using Chrome DevTools Protocol.
"""

import time
import logging
from typing import Dict, Any, Optional
from trafilatura import extract

from .chrome_manager import ChromeManager
from .element_extractor import (
    extract_clickable_elements,
    extract_input_elements,
    extract_elements_by_text,
    extract_scrollable_elements,
)
from .js_loader import js_loader

import PyChromeDevTools

logger = logging.getLogger(__name__)


class BrowserAutomationService:
    """Service for browser automation using Chrome DevTools Protocol."""

    def __init__(self, debug_port: int = 9222):
        """
        Initialize browser automation service.

        Args:
            debug_port: Port for Chrome DevTools Protocol
        """

        self.debug_port = debug_port
        self.chrome_manager = ChromeManager(debug_port=debug_port)
        self.chrome_interface: Optional[Any] = None
        self._is_initialized = False
        # UUID to XPath mapping for element identification
        self.uuid_to_xpath_mapping: Dict[str, str] = {}

    def _ensure_chrome_running(self, profile: str = "Default"):
        """Ensure Chrome browser is running and connected."""
        if not self._is_initialized:
            self._initialize_chrome(profile)

    def _initialize_chrome(self, profile: str = "Default"):
        """Initialize Chrome browser and DevTools connection."""
        try:
            if not self.chrome_manager.is_chrome_running():
                self.chrome_manager.start_chrome_thread(profile)

                if not self.chrome_manager.is_chrome_running():
                    raise RuntimeError("Failed to start Chrome browser")

            time.sleep(2)

            self.chrome_interface = PyChromeDevTools.ChromeInterface(
                host="localhost", port=self.debug_port, suppress_origin=True
            )

            self.chrome_interface.Network.enable()
            self.chrome_interface.Page.enable()
            self.chrome_interface.Runtime.enable()
            self.chrome_interface.DOM.enable()

            self._is_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize Chrome: {e}")
            self._is_initialized = False
            raise

    def navigate(self, url: str, profile: str = "Default") -> Dict[str, Any]:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to
            profile: Chrome user profile directory name (default: "Default")

        Returns:
            Dict containing navigation result
        """
        try:
            self._ensure_chrome_running(profile)
            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            result = self.chrome_interface.Page.navigate(url=url)

            # Check if navigation was successful
            if isinstance(result, tuple) and len(result) >= 2:
                if isinstance(result[0], dict):
                    error_text = result[0].get("result", {}).get("errorText")
                    if error_text:
                        self.chrome_manager.cleanup()
                        self._is_initialized = False
                        return {
                            "success": False,
                            "error": f"Navigation failed: {error_text}.Please try again",
                            "url": url,
                            "profile": profile,
                        }

            time.sleep(2)
            current_url = self._get_current_url()

            return {
                "success": True,
                "message": f"Successfully navigated to {url}",
                "current_url": current_url,
                "url": url,
                "profile": profile,
            }

        except Exception as e:
            logger.error(f"Navigation error: {e}")
            self.chrome_manager.cleanup()
            self._is_initialized = False
            return {
                "success": False,
                "error": f"Navigation error: {str(e)}. Reset the chrome, Please try to navigate again",
                "url": url,
                "profile": profile,
            }

    def click_element(self, element_uuid: str) -> Dict[str, Any]:
        """
        Click an element using UUID.

        Args:
            element_uuid: UUID of the element to click (from browser_get_content)

        Returns:
            Dict containing click result
        """
        # Resolve UUID to XPath
        xpath = self.uuid_to_xpath_mapping.get(element_uuid)
        if not xpath:
            return {
                "success": False,
                "error": f"Element UUID '{element_uuid}' not found. Please use browser_get_content to get current element UUIDs.",
                "uuid": element_uuid,
            }
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            # Load JavaScript code from external file
            js_code = js_loader.get_click_element_js(xpath)

            result = self.chrome_interface.Runtime.evaluate(
                expression=js_code, returnByValue=True
            )

            if isinstance(result, tuple) and len(result) >= 2:
                if isinstance(result[1], dict):
                    click_result = (
                        result[1].get("result", {}).get("result", {}).get("value", {})
                    )
                    click_result["success"] = True
                elif isinstance(result[1], list) and len(result[1]) > 0:
                    click_result = (
                        result[1][0]
                        .get("result", {})
                        .get("result", {})
                        .get("value", {})
                    )
                    click_result["success"] = True
                else:
                    click_result = {
                        "success": False,
                        "error": "Invalid response format",
                    }
            else:
                click_result = {"success": False, "error": "No response from browser"}

            time.sleep(2)

            return {"uuid": element_uuid, "xpath": xpath, **click_result}

        except Exception as e:
            logger.error(f"Click error: {e}")
            return {
                "success": False,
                "error": f"Click error: {str(e)}",
                "uuid": element_uuid,
                "xpath": xpath,
            }

    def scroll_page(
        self, direction: str, amount: int = 3, element_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scroll the page or a specific element in specified direction.

        Args:
            direction: Direction to scroll ('up', 'down', 'left', 'right')
            amount: Number of scroll units (default: 3)
            element_uuid: Optional UUID of element to scroll (defaults to document)

        Returns:
            Dict containing scroll result
        """
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            scroll_distance = amount * 300

            # Resolve UUID to XPath if provided
            xpath = None
            if element_uuid:
                xpath = self.uuid_to_xpath_mapping.get(element_uuid)
                if not xpath:
                    return {
                        "success": False,
                        "error": f"Element UUID '{element_uuid}' not found. Please use browser_get_content to get current element UUIDs.",
                        "uuid": element_uuid,
                        "direction": direction,
                        "amount": amount,
                    }

            # Load JavaScript code from external file
            js_code = js_loader.get_scroll_page_js(
                direction, scroll_distance, xpath or "", element_uuid or ""
            )

            result = self.chrome_interface.Runtime.evaluate(
                expression=js_code, returnByValue=True
            )

            if isinstance(result, tuple) and len(result) >= 2:
                if isinstance(result[1], dict):
                    scroll_result = (
                        result[1].get("result", {}).get("result", {}).get("value", {})
                    )
                elif isinstance(result[1], list) and len(result[1]) > 0:
                    scroll_result = (
                        result[1][0]
                        .get("result", {})
                        .get("result", {})
                        .get("value", {})
                    )
                else:
                    scroll_result = {
                        "success": False,
                        "error": "Invalid response format",
                    }
            else:
                scroll_result = {"success": False, "error": "No response from browser"}

            time.sleep(1.5)

            result_data = {"direction": direction, "amount": amount, **scroll_result}
            if element_uuid:
                result_data["uuid"] = element_uuid
                result_data["xpath"] = xpath
            return result_data

        except Exception as e:
            logger.error(f"Scroll error: {e}")
            error_data = {
                "success": False,
                "error": f"Scroll error: {str(e)}",
                "direction": direction,
                "amount": amount,
            }
            return error_data

    def get_page_content(self) -> Dict[str, Any]:
        """
        Extract page content and clickable elements as markdown.

        Returns:
            Dict containing page content and clickable elements
        """
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            time.sleep(1)
            # Get page document
            _, dom_data = self.chrome_interface.DOM.getDocument(depth=1)

            # Find HTML node
            html_node = None
            for node in dom_data[0]["result"]["root"]["children"]:
                if node.get("nodeName") == "HTML":
                    html_node = node
                    break

            if not html_node:
                return {"success": False, "error": "Could not find HTML node in page"}

            # Get outer HTML
            html_content, _ = self.chrome_interface.DOM.getOuterHTML(
                nodeId=html_node["nodeId"]
            )
            raw_html = html_content.get("result", {}).get("outerHTML", "")

            if not raw_html:
                return {"success": False, "error": "Could not extract HTML content"}

            # Convert HTML to markdown
            # raw_markdown_content = convert_to_markdown(raw_html, strip_newlines=True)
            raw_markdown_content = extract(
                raw_html,
                include_comments=False,
                output_format="markdown",
                include_links=True,
                include_formatting=True,
                include_images=True,
            )
            if not raw_markdown_content:
                return {"success": False, "error": "Could not convert HTML to markdown"}

            # Clean the markdown content
            # cleaned_markdown_content = clean_markdown_images(raw_markdown_content)

            # Remove consecutive duplicate lines
            # deduplicated_content = remove_duplicate_lines(cleaned_markdown_content)

            self.uuid_to_xpath_mapping.clear()

            clickable_elements_md = extract_clickable_elements(
                self.chrome_interface, self.uuid_to_xpath_mapping
            )

            input_elements_md = extract_input_elements(
                self.chrome_interface, self.uuid_to_xpath_mapping
            )

            scrollable_elements_md = extract_scrollable_elements(
                self.chrome_interface, self.uuid_to_xpath_mapping
            )

            final_content = (
                raw_markdown_content
                + clickable_elements_md
                + input_elements_md
                + scrollable_elements_md
            )

            current_url = self._get_current_url()

            return {
                "success": True,
                "content": final_content,
                "url": current_url,
            }

        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return {"success": False, "error": f"Content extraction error: {str(e)}"}

    def _get_current_url(self) -> str:
        """Get the current page URL."""
        try:
            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")
            runtime_result = self.chrome_interface.Runtime.evaluate(
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

    def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.chrome_manager:
                self.chrome_manager.cleanup()
            self._is_initialized = False
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def input_data(self, element_uuid: str, value: str) -> Dict[str, Any]:
        """
        Input data into a form field using UUID by simulating keyboard typing.

        Args:
            element_uuid: UUID of the input element (from browser_get_content)
            value: Value to input into the field

        Returns:
            Dict containing input result
        """
        # Resolve UUID to XPath
        xpath = self.uuid_to_xpath_mapping.get(element_uuid)
        if not xpath:
            return {
                "success": False,
                "error": f"Element UUID '{element_uuid}' not found. Please use browser_get_content to get current element UUIDs.",
                "uuid": element_uuid,
                "input_value": value,
            }
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            # Focus the element and clear any existing content
            focus_result = self._focus_and_clear_element(xpath)
            if not focus_result.get("success", False):
                return focus_result

            can_simulate_typing = focus_result.get("canSimulateTyping", False)
            # Simulate typing each character
            if can_simulate_typing:
                typing_result = self._simulate_typing(value)
                if not typing_result.get("success", False):
                    return {
                        **typing_result,
                        "uuid": element_uuid,
                        "xpath": xpath,
                        "input_value": value,
                    }

            self._trigger_input_events(xpath, value)
            time.sleep(1.5)

            return {
                "success": True,
                "message": f"Successfully typed '{value}' using keyboard simulation",
                "uuid": element_uuid,
                "xpath": xpath,
                "input_value": value,
                "typing_method": "keyboard_simulation",
            }

        except Exception as e:
            logger.error(f"Keyboard input simulation error: {e}")
            return {
                "success": False,
                "error": f"Keyboard input simulation error: {str(e)}",
                "uuid": element_uuid,
                "xpath": xpath,
                "input_value": value,
                "typing_method": "keyboard_simulation",
            }

    def _focus_and_clear_element(self, xpath: str) -> Dict[str, Any]:
        """
        Focus the target element and clear any existing content.

        Args:
            xpath: XPath selector for the element

        Returns:
            Dict containing focus result
        """
        # Load JavaScript code from external file
        js_code = js_loader.get_focus_and_clear_element_js(xpath)

        if self.chrome_interface is None:
            raise RuntimeError("Chrome interface is not initialized")

        result = self.chrome_interface.Runtime.evaluate(
            expression=js_code, returnByValue=True
        )

        if isinstance(result, tuple) and len(result) >= 2:
            if isinstance(result[1], dict):
                focus_result = (
                    result[1].get("result", {}).get("result", {}).get("value", {})
                )
            elif isinstance(result[1], list) and len(result[1]) > 0:
                focus_result = (
                    result[1][0].get("result", {}).get("result", {}).get("value", {})
                )
            else:
                focus_result = {
                    "success": False,
                    "error": "Invalid response format from focus operation",
                }
        else:
            focus_result = {
                "success": False,
                "error": "No response from focus operation",
            }

        return focus_result

    def _simulate_typing(self, text: str) -> Dict[str, Any]:
        """Simulate keyboard typing character by character."""
        if self.chrome_interface is None:
            raise RuntimeError("Chrome interface is not initialized")

        try:
            for char in text:
                time.sleep(0.05)

                if char == "\n":
                    self.chrome_interface.Input.dispatchKeyEvent(type="char", text="\r")
                elif char == "\t":
                    self.chrome_interface.Input.dispatchKeyEvent(type="char", text="\t")
                else:
                    self.chrome_interface.Input.dispatchKeyEvent(type="char", text=char)

            return {
                "success": True,
                "message": f"Successfully typed {len(text)} characters",
                "characters_typed": len(text),
            }

        except Exception as e:
            logger.error(f"Error during typing simulation: {e}")
            return {"success": False, "error": f"Typing simulation failed: {str(e)}"}

    def _trigger_input_events(self, xpath: str, value: str) -> Dict[str, Any]:
        """Trigger input and change events to notify the page of input changes."""
        # Load JavaScript code from external file
        js_code = js_loader.get_trigger_input_events_js(xpath, value)

        if self.chrome_interface is None:
            raise RuntimeError("Chrome interface is not initialized")

        result = self.chrome_interface.Runtime.evaluate(
            expression=js_code, returnByValue=True
        )

        if isinstance(result, tuple) and len(result) >= 2:
            if isinstance(result[1], dict):
                event_result = (
                    result[1].get("result", {}).get("result", {}).get("value", {})
                )
            elif isinstance(result[1], list) and len(result[1]) > 0:
                event_result = (
                    result[1][0].get("result", {}).get("result", {}).get("value", {})
                )
            else:
                event_result = {
                    "success": False,
                    "error": "Invalid response format from event triggering",
                }
        else:
            event_result = {
                "success": False,
                "error": "No response from event triggering",
            }

        return event_result

    def get_elements_by_text(self, text: str) -> Dict[str, Any]:
        """Find elements containing specified text using XPath."""
        try:
            self._ensure_chrome_running()
            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            initial_mapping_count = len(self.uuid_to_xpath_mapping)
            elements_md = extract_elements_by_text(
                self.chrome_interface, self.uuid_to_xpath_mapping, text
            )
            new_mapping_count = len(self.uuid_to_xpath_mapping) - initial_mapping_count

            return {
                "success": True,
                "content": elements_md,
                "text": text,
                "elements_found": new_mapping_count,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Get elements by text error: {str(e)}",
                "text": text,
            }

    def capture_screenshot(
        self,
        format: str = "png",
        quality: Optional[int] = None,
        clip: Optional[Dict[str, Any]] = None,
        from_surface: bool = True,
        capture_beyond_viewport: bool = False,
    ) -> Dict[str, Any]:
        """
        Capture a screenshot of the current page.

        Args:
            format: Image format ("png", "jpeg", or "webp"). Defaults to "png"
            quality: Compression quality from 0-100 (jpeg only). Optional
            clip: Optional region to capture. Dict with x, y, width, height keys
            from_surface: Capture from surface rather than view. Defaults to True
            capture_beyond_viewport: Capture beyond viewport. Defaults to False

        Returns:
            Dict containing the screenshot as base64 image data in the specified format
        """
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            # Prepare parameters for screenshot capture
            screenshot_params = {
                "format": format,
                "fromSurface": from_surface,
                "captureBeyondViewport": capture_beyond_viewport,
            }

            # Add quality parameter only for jpeg format
            if format == "jpeg" and quality is not None:
                screenshot_params["quality"] = quality

            # Add clip parameter if provided
            if clip is not None:
                screenshot_params["clip"] = clip

            # Capture the screenshot
            result = self.chrome_interface.Page.captureScreenshot(**screenshot_params)

            if isinstance(result, tuple) and len(result) >= 2:
                if isinstance(result[1], dict):
                    screenshot_data = result[1].get("result", {}).get("data", "")
                elif isinstance(result[1], list) and len(result[1]) > 0:
                    screenshot_data = result[1][0].get("result", {}).get("data", "")
                else:
                    return {
                        "success": False,
                        "error": "Invalid response format from screenshot capture",
                    }
            else:
                return {
                    "success": False,
                    "error": "No response from screenshot capture",
                }

            if not screenshot_data:
                return {"success": False, "error": "No screenshot data received"}

            # Determine MIME type based on format
            mime_type_map = {
                "png": "image/png",
                "jpeg": "image/jpeg",
                "webp": "image/webp",
            }
            mime_type = mime_type_map.get(format, "image/png")

            # Get current URL for context
            current_url = self._get_current_url()

            return {
                "success": True,
                "message": f"Successfully captured screenshot in {format} format",
                "screenshot": {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{screenshot_data}"},
                },
                "format": format,
                "url": current_url,
            }

        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            return {"success": False, "error": f"Screenshot capture error: {str(e)}"}

    def __del__(self):
        """Cleanup when service is destroyed."""
        self.cleanup()

"""
Browser automation service for controlling Chrome browser.

This service provides functionality to navigate web pages, click elements,
scroll content, and extract page information using Chrome DevTools Protocol.
"""

import time
import logging
from typing import Dict, Any, Optional
from html_to_markdown import convert_to_markdown

from .chrome_manager import ChromeManager
from .element_extractor import (
    clean_markdown_images,
    remove_duplicate_lines,
    extract_clickable_elements,
    extract_input_elements,
)

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

    def _ensure_chrome_running(self):
        """Ensure Chrome browser is running and connected."""
        if not self._is_initialized:
            self._initialize_chrome()

    def _initialize_chrome(self):
        """Initialize Chrome browser and DevTools connection."""
        try:
            if not self.chrome_manager.is_chrome_running():
                self.chrome_manager.start_chrome_thread()

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

    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to

        Returns:
            Dict containing navigation result
        """
        try:
            self._ensure_chrome_running()
            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            result = self.chrome_interface.Page.navigate(url=url)

            # Check if navigation was successful
            if isinstance(result, tuple) and len(result) >= 2:
                if isinstance(result[0], dict):
                    error_text = result[0].get("result", {}).get("errorText")
                    if error_text:
                        return {
                            "success": False,
                            "error": f"Navigation failed: {error_text}",
                            "url": url,
                        }

            time.sleep(2)
            current_url = self._get_current_url()

            return {
                "success": True,
                "message": f"Successfully navigated to {url}",
                "current_url": current_url,
                "url": url,
            }

        except Exception as e:
            logger.error(f"Navigation error: {e}")
            self.chrome_manager.cleanup()
            self._is_initialized = False
            return {
                "success": False,
                "error": f"Navigation error: {str(e)}. Please try again",
                "url": url,
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


            # JavaScript to find and click element by XPath using realistic mouse events
            js_code = f"""
            (() => {{
                const xpath = `{xpath}`;
                const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                const element = result.singleNodeValue;
                
                if (!element) {{
                    return {{success: false, error: "Element not found"}};
                }}
                
                // Check if element is visible and enabled
                const style = window.getComputedStyle(element);
                if (style.display === 'none' || style.visibility === 'hidden') {{
                    return {{success: false, error: "Element is not visible"}};
                }}
                
                if (element.disabled) {{
                    return {{success: false, error: "Element is disabled"}};
                }}
                
                // Scroll element into view
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                
                // Get element's bounding rect for realistic mouse coordinates
                const rect = element.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                
                // Create realistic mouse event options
                const mouseEventOptions = {{
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: centerX,
                    clientY: centerY,
                    screenX: centerX + window.screenX,
                    screenY: centerY + window.screenY,
                    button: 0, // Left mouse button
                    buttons: 1, // Left mouse button pressed
                    ctrlKey: false,
                    shiftKey: false,
                    altKey: false,
                    metaKey: false
                }};
                
                try {{
                    // Simulate the full sequence of mouse events like a real user click
                    // 1. Mouse down event
                    const mouseDownEvent = new MouseEvent('mousedown', mouseEventOptions);
                    element.dispatchEvent(mouseDownEvent);
                    
                    // 2. Focus the element (realistic behavior)
                    if (element.focus) {{
                        element.focus();
                    }}
                    
                    // 3. Mouse up event
                    const mouseUpEvent = new MouseEvent('mouseup', mouseEventOptions);
                    element.dispatchEvent(mouseUpEvent);
                    
                    // 4. Click event (this is the main event that triggers handlers)
                    const clickEvent = new MouseEvent('click', mouseEventOptions);
                    element.dispatchEvent(clickEvent);
                    
                    return {{success: true, message: "Element clicked successfully"}};
                }} catch (eventError) {{
                    // Fallback to simple click if mouse events fail
                    try {{
                        element.click();
                        return {{success: true, message: "Element clicked successfully"}};
                    }} catch (fallbackError) {{
                        return {{success: false, error: "Failed to click element: " + eventError.message + " (fallback also failed: " + fallbackError.message + ")"}};
                    }}
                }}
            }})();
            """

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

    def scroll_page(self, direction: str, amount: int = 3) -> Dict[str, Any]:
        """
        Scroll the page in specified direction.

        Args:
            direction: Direction to scroll ('up', 'down', 'left', 'right')
            amount: Number of scroll units (default: 3)

        Returns:
            Dict containing scroll result
        """
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            scroll_distance = amount * 300

            # JavaScript to scroll the page
            js_code = f"""
            (() => {{
                const direction = '{direction}';
                const distance = {scroll_distance};
                
                let scrollX = 0;
                let scrollY = 0;
                
                switch(direction.toLowerCase()) {{
                    case 'up':
                        scrollY = -distance;
                        break;
                    case 'down':
                        scrollY = distance;
                        break;
                    case 'left':
                        scrollX = -distance;
                        break;
                    case 'right':
                        scrollX = distance;
                        break;
                    default:
                        return {{success: false, error: "Invalid direction. Use 'up', 'down', 'left', or 'right'"}};
                }}
                
                // Get current scroll position
                const currentX = window.pageXOffset || document.documentElement.scrollLeft;
                const currentY = window.pageYOffset || document.documentElement.scrollTop;
                
                // Scroll the page
                window.scrollBy(scrollX, scrollY);
                
                // Get new scroll position
                const newX = window.pageXOffset || document.documentElement.scrollLeft;
                const newY = window.pageYOffset || document.documentElement.scrollTop;
                
                return {{
                    success: true,
                    message: "Scrolled " + direction + " by " + Math.abs(scrollX || scrollY) + "px",
                    previous_position: {{x: currentX, y: currentY}},
                    new_position: {{x: newX, y: newY}}
                }};
            }})();
            """

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

            return {"direction": direction, "amount": amount, **scroll_result}

        except Exception as e:
            logger.error(f"Scroll error: {e}")
            return {
                "success": False,
                "error": f"Scroll error: {str(e)}",
                "direction": direction,
                "amount": amount,
            }

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
            raw_html = html_content["result"].get("outerHTML", "")

            if not raw_html:
                return {"success": False, "error": "Could not extract HTML content"}

            # Convert HTML to markdown
            raw_markdown_content = convert_to_markdown(raw_html)

            # Clean the markdown content
            cleaned_markdown_content = clean_markdown_images(raw_markdown_content)

            # Remove consecutive duplicate lines
            deduplicated_content = remove_duplicate_lines(cleaned_markdown_content)

            self.uuid_to_xpath_mapping.clear()

            clickable_elements_md = extract_clickable_elements(
                self.chrome_interface, self.uuid_to_xpath_mapping
            )

            input_elements_md = extract_input_elements(
                self.chrome_interface, self.uuid_to_xpath_mapping
            )

            final_content = (
                deduplicated_content + clickable_elements_md + input_elements_md
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

            # Simulate typing each character
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
        js_code = f"""
        (() => {{
            const xpath = `{xpath}`;
            const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            const element = result.singleNodeValue;
            
            if (!element) {{
                return {{success: false, error: "Element not found"}};
            }}
            
            // Check if element is visible and enabled
            const style = window.getComputedStyle(element);
            if (style.display === 'none' || style.visibility === 'hidden') {{
                return {{success: false, error: "Element is not visible"}};
            }}
            
            if (element.disabled) {{
                return {{success: false, error: "Element is disabled"}};
            }}
            
            // Check if element is a valid input type
            const tagName = element.tagName.toLowerCase();
            if (!['input', 'textarea'].includes(tagName) && !element.hasAttribute('contenteditable')) {{
                return {{success: false, error: "Element is not a text input field"}};
            }}
            
            // Scroll element into view and focus
            element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            element.focus();
            
            // Clear existing content - select all and then we'll type over it
            if (tagName === 'input' || tagName === 'textarea') {{
                element.select();
            }} else if (element.hasAttribute('contenteditable')) {{
                // For contenteditable, select all text
                const range = document.createRange();
                range.selectNodeContents(element);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            }}
            
            return {{success: true, message: "Element focused and selected for typing"}};
        }})();
        """

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
        js_code = f"""
        (() => {{
            const xpath = `{xpath}`;
            const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            const element = result.singleNodeValue;
            
            if (!element) {{
                return {{success: false, error: "Element not found for event triggering"}};
            }}
            
            try {{
                // Trigger input event
                element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                // Trigger change event
                element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                // For some forms, also trigger keyup event
                element.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true }}));
                
                return {{success: true, message: "Input events triggered successfully"}};
            }} catch (eventError) {{
                return {{success: false, error: "Failed to trigger events: " + eventError.message}};
            }}
        }})();
        """

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

    def __del__(self):
        """Cleanup when service is destroyed."""
        self.cleanup()

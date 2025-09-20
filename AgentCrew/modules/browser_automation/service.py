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
from .element_extractor import clean_markdown_images, extract_clickable_elements

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

    def _ensure_chrome_running(self):
        """Ensure Chrome browser is running and connected."""
        if not self._is_initialized:
            self._initialize_chrome()

    def _initialize_chrome(self):
        """Initialize Chrome browser and DevTools connection."""
        try:
            # Start Chrome if not running
            if not self.chrome_manager.is_chrome_running():
                logger.info("Starting Chrome browser...")
                self.chrome_manager.start_chrome_thread()

                if not self.chrome_manager.is_chrome_running():
                    raise RuntimeError("Failed to start Chrome browser")

            # Wait for Chrome DevTools to be available
            logger.info("Connecting to Chrome DevTools...")
            time.sleep(2)

            # Connect to Chrome DevTools
            self.chrome_interface = PyChromeDevTools.ChromeInterface(
                host="localhost", port=self.debug_port, suppress_origin=True
            )

            # Enable necessary domains
            self.chrome_interface.Network.enable()
            self.chrome_interface.Page.enable()
            self.chrome_interface.Runtime.enable()
            self.chrome_interface.DOM.enable()

            self._is_initialized = True
            logger.info("Chrome DevTools connection established")

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

            logger.info(f"Navigating to: {url}")
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

            # Wait for content to load
            time.sleep(2)

            # Get current URL to verify navigation
            current_url = self._get_current_url()

            return {
                "success": True,
                "message": f"Successfully navigated to {url}",
                "current_url": current_url,
                "url": url,
            }

        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return {
                "success": False,
                "error": f"Navigation error: {str(e)}",
                "url": url,
            }

    def click_element(self, xpath: str) -> Dict[str, Any]:
        """
        Click an element using XPath selector.

        Args:
            xpath: XPath selector for the element to click

        Returns:
            Dict containing click result
        """
        try:
            self._ensure_chrome_running()

            if self.chrome_interface is None:
                raise RuntimeError("Chrome interface is not initialized")

            logger.info(f"Clicking element with XPath: {xpath}")

            # JavaScript to find and click element by XPath
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
                
                // Click the element
                element.click();
                
                return {{success: true, message: "Element clicked successfully"}};
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
                elif isinstance(result[1], list) and len(result[1]) > 0:
                    click_result = (
                        result[1][0]
                        .get("result", {})
                        .get("result", {})
                        .get("value", {})
                    )
                else:
                    click_result = {
                        "success": False,
                        "error": "Invalid response format",
                    }
            else:
                click_result = {"success": False, "error": "No response from browser"}

            # Wait a moment for any page changes
            time.sleep(1)

            return {"xpath": xpath, **click_result}

        except Exception as e:
            logger.error(f"Click error: {e}")
            return {"success": False, "error": f"Click error: {str(e)}", "xpath": xpath}

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

            logger.info(f"Scrolling {direction} by {amount} units")

            # Calculate scroll distance (300px per unit)
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

            # Wait a moment for scroll to complete
            time.sleep(0.5)

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

            logger.info("Extracting page content...")

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

            # Extract clickable elements
            clickable_elements_md = extract_clickable_elements(self.chrome_interface)

            # Combine content
            final_content = cleaned_markdown_content + clickable_elements_md

            # Get current URL
            current_url = self._get_current_url()

            return {
                "success": True,
                "content": final_content,
                "url": current_url,
                "content_length": len(final_content),
                "has_clickable_elements": "## Clickable Elements"
                in clickable_elements_md,
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
            logger.info("Browser automation service cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def __del__(self):
        """Cleanup when service is destroyed."""
        self.cleanup()


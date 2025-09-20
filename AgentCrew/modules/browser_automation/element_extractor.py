"""
Web element extraction utilities for browser automation.

Provides functionality to extract clickable elements and page content
for browser automation operations.
"""

import re
import logging

logger = logging.getLogger(__name__)


def clean_markdown_images(markdown_content: str) -> str:
    """
    Clean markdown output by:
    1. Replace data: format image URLs with REDACTED
    2. Handle both single and double quotes in image tags
    3. Reduce length of image links (truncate long URLs)
    4. Replace HTML img tags with alt text, or remove if no alt attribute

    Args:
        markdown_content: The markdown content to clean

    Returns:
        Cleaned markdown content
    """
    # Pattern for markdown images: ![alt](url)
    markdown_img_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

    def replace_markdown_img(match):
        alt_text = match.group(1)
        url = match.group(2)

        # Replace data: URLs with REDACTED
        if url.startswith("data:"):
            return f"![{alt_text}](REDACTED)"

        # Truncate long URLs (keep first 50 chars + "...")
        if len(url) > 50:
            url = url[:50] + "..."

        return f"![{alt_text}]({url})"

    # Replace markdown images
    cleaned_content = re.sub(
        markdown_img_pattern, replace_markdown_img, markdown_content
    )

    # Pattern for HTML img tags with flexible quote handling
    # This handles both single and double quotes around attributes
    html_img_pattern = r"<img\s+([^>]*?)/?>"

    def replace_html_img(match):
        attributes = match.group(1)

        # Extract alt attribute (handle both quote types)
        alt_match = re.search(r'alt\s*=\s*(["\'])([^"\']*?)\1', attributes)
        alt = alt_match.group(2) if alt_match else ""

        # Replace img tag with alt text if available, otherwise remove it
        if alt:
            return f"{alt}#img "
        else:
            return ""

    # Replace HTML img tags
    cleaned_content = re.sub(html_img_pattern, replace_html_img, cleaned_content)

    return cleaned_content


def extract_clickable_elements(chrome_interface) -> str:
    """
    Extract all clickable elements from the current webpage in a concise format.

    For each clickable element, extracts:
    - XPath: Unique path to locate the element
    - Text/Alt: Display text or alt text from images

    Deduplication:
    - Elements with href: Deduplicated by href value
    - Elements without href: Deduplicated by tagName + text combination

    Args:
        chrome_interface: ChromeInterface object with enabled DOM

    Returns:
        Concise markdown table with XPath and text/alt for each unique element
    """
    try:
        # JavaScript to find all clickable elements
        js_code = """
        (() => {
            const clickableElements = [];
            const seenHrefs = new Set();
            const seenElements = new Set();
            
            // Function to generate XPath for an element
            function getXPath(element) {
                if (element.id) {
                    return `//*[@id="${element.id}"]`;
                }
                
                const parts = [];
                while (element && element.nodeType === Node.ELEMENT_NODE) {
                    let index = 0;
                    let sibling = element.previousSibling;
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === element.nodeName) {
                            index++;
                        }
                        sibling = sibling.previousSibling;
                    }
                    
                    const tagName = element.nodeName.toLowerCase();
                    const pathIndex = index > 0 ? `[${index + 1}]` : '';
                    parts.unshift(tagName + pathIndex);
                    element = element.parentNode;
                }
                
                return parts.length ? '/' + parts.join('/') : '';
            }
            
            // Define selectors for clickable elements
            const selectors = [
                'a[href]',           // Links
                'button',            // Buttons
                'input[type="button"]',
                'input[type="submit"]',
                'input[type="reset"]',
                '[onclick]',         // Elements with onclick handlers
                '[role="button"]',   // ARIA buttons
                '[tabindex]',        // Focusable elements
                'area[href]',        // Image map areas
                'select',            // Select dropdowns
                'details summary'    // Collapsible details
            ];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    // Skip if element is hidden or disabled
                    const style = window.getComputedStyle(element);
                    if (style.display === 'none' || style.visibility === 'hidden' || element.disabled) {
                        return;
                    }
                    
                    // Get href for deduplication
                    const href = element.href || element.getAttribute('href') || '';
                    
                    // Generate XPath
                    const xpath = getXPath(element);
                    
                    // Get display text
                    let displayText = '';
                    
                    // Check if element contains images and extract alt text
                    const images = element.querySelectorAll('img');
                    if (images.length > 0) {
                        const altTexts = [];
                        images.forEach(img => {
                            const alt = img.getAttribute('alt');
                            if (alt) {
                                altTexts.push(alt);
                            }
                        });
                        if (altTexts.length > 0) {
                            displayText = altTexts.join(', ');
                        }
                    }
                    
                    // If no alt text from images, get text content
                    if (!displayText) {
                        displayText = element.textContent || element.innerText || '';
                        displayText = displayText.trim().replace(/\\s+/g, ' ');
                        
                        // Try aria-label or title if no text content
                        if (!displayText) {
                            displayText = element.getAttribute('aria-label') || element.title || '';
                        }
                        
                        // Limit text length
                        if (displayText.length > 50) {
                            displayText = displayText.substring(0, 50) + '...';
                        }
                    }
                    
                    // Only add if we have some meaningful content
                    if (displayText || xpath) {
                        // Deduplication logic
                        if (href) {
                            // For elements with href, deduplicate by href
                            if (!seenHrefs.has(href)) {
                                seenHrefs.add(href);
                                clickableElements.push({
                                    xpath: xpath,
                                    text: displayText
                                });
                            }
                        } else {
                            // For elements without href, deduplicate by tagName + text combination
                            const elementKey = element.tagName.toLowerCase() + '|' + displayText;
                            if (!seenElements.has(elementKey)) {
                                seenElements.add(elementKey);
                                clickableElements.push({
                                    xpath: xpath,
                                    text: displayText
                                });
                            }
                        }
                    }
                });
            });
            
            return clickableElements;
        })();
        """

        # Execute JavaScript to get clickable elements
        result = chrome_interface.Runtime.evaluate(
            expression=js_code, returnByValue=True
        )
        logger.debug(f"Clickable elements extraction result: {result}")

        if isinstance(result, tuple) and len(result) >= 2:
            if isinstance(result[1], dict):
                elements_data = (
                    result[1].get("result", {}).get("result", {}).get("value", [])
                )
            elif isinstance(result[1], list) and len(result[1]) > 0:
                elements_data = (
                    result[1][0].get("result", {}).get("result", {}).get("value", [])
                )
            else:
                elements_data = []
        else:
            elements_data = []

        if not elements_data:
            return "\n\n## Clickable Elements\n\nNo clickable elements found on this page.\n"

        # Format clickable elements into concise markdown
        markdown_output = []
        markdown_output.append("\n\n## Clickable Elements\n")
        markdown_output.append("| XPath | Text/Alt |\n")
        markdown_output.append("|-------|----------|\n")

        for element in elements_data:
            xpath = element.get("xpath", "")
            text = element.get("text", "").strip()

            # Escape pipe characters in text for markdown table
            if not text:
                continue  # Skip empty text entries

            text = text.replace("|", "\\|")

            # Escape pipe characters in xpath for markdown table
            xpath = xpath.replace("|", "\\|")

            markdown_output.append(f"| `{xpath}` | {text} |\n")

        # Add summary
        total_elements = len(elements_data)
        markdown_output.append(f"\n**Total:** {total_elements} clickable elements\n")

        return "".join(markdown_output)

    except Exception as e:
        logger.error(f"Error extracting clickable elements: {e}")
        return f"\n\n## Clickable Elements\n\nError extracting clickable elements: {str(e)}\n"


def extract_input_elements(chrome_interface) -> str:
    """
    Extract all input elements from the current webpage in a concise format.

    For each input element, extracts:
    - XPath: Unique path to locate the element
    - Type: Input type (text, email, password, etc.)
    - Placeholder/Label: Placeholder text or associated label
    - Required: Whether the field is required

    Args:
        chrome_interface: ChromeInterface object with enabled DOM

    Returns:
        Concise markdown table with XPath, type, and description for each input element
    """
    try:
        # JavaScript to find all input elements
        js_code = """
        (() => {
            const inputElements = [];
            const seenElements = new Set();
            
            // Function to generate XPath for an element
            function getXPath(element) {
                if (element.id) {
                    return `//*[@id="${element.id}"]`;
                }
                
                const parts = [];
                while (element && element.nodeType === Node.ELEMENT_NODE) {
                    let index = 0;
                    let sibling = element.previousSibling;
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === element.nodeName) {
                            index++;
                        }
                        sibling = sibling.previousSibling;
                    }
                    
                    const tagName = element.nodeName.toLowerCase();
                    const pathIndex = index > 0 ? `[${index + 1}]` : '';
                    parts.unshift(tagName + pathIndex);
                    element = element.parentNode;
                }
                
                return parts.length ? '/' + parts.join('/') : '';
            }
            
            // Function to find associated label text
            function getLabelText(element) {
                // Check for direct label association
                if (element.id) {
                    const label = document.querySelector(`label[for="${element.id}"]`);
                    if (label) {
                        return label.textContent.trim();
                    }
                }
                
                // Check if element is inside a label
                const parentLabel = element.closest('label');
                if (parentLabel) {
                    return parentLabel.textContent.trim();
                }
                
                // Check for aria-label
                if (element.getAttribute('aria-label')) {
                    return element.getAttribute('aria-label');
                }
                
                // Check for preceding label or text
                let sibling = element.previousElementSibling;
                while (sibling) {
                    if (sibling.tagName === 'LABEL') {
                        return sibling.textContent.trim();
                    }
                    if (sibling.textContent && sibling.textContent.trim()) {
                        const text = sibling.textContent.trim();
                        if (text.length < 100) { // Reasonable label length
                            return text;
                        }
                    }
                    sibling = sibling.previousElementSibling;
                }
                
                return '';
            }
            
            // Define selectors for input elements
            const selectors = [
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'input[type="number"]',
                'input[type="tel"]',
                'input[type="url"]',
                'input[type="search"]',
                'input[type="date"]',
                'input[type="datetime-local"]',
                'input[type="time"]',
                'input[type="month"]',
                'input[type="week"]',
                'input[type="color"]',
                'input[type="range"]',
                'input[type="file"]',
                'input:not([type])', // Default input type is text
                'textarea',
                'select',
                '[contenteditable="true"]'
            ];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    // Skip if element is hidden or disabled
                    const style = window.getComputedStyle(element);
                    if (style.display === 'none' || style.visibility === 'hidden') {
                        return;
                    }
                    
                    // Generate XPath
                    const xpath = getXPath(element);
                    
                    // Get element type
                    let elementType = element.tagName.toLowerCase();
                    if (elementType === 'input') {
                        elementType = element.type || 'text';
                    } else if (elementType === 'select') {
                        elementType = 'select';
                    } else if (elementType === 'textarea') {
                        elementType = 'textarea';
                    } else if (element.hasAttribute('contenteditable')) {
                        elementType = 'contenteditable';
                    }
                    
                    // Get description (placeholder, label, or name)
                    let description = '';
                    
                    // Try placeholder first
                    if (element.placeholder) {
                        description = element.placeholder;
                    } else {
                        // Try to find associated label
                        const labelText = getLabelText(element);
                        if (labelText) {
                            description = labelText;
                        } else if (element.name) {
                            // Fall back to name attribute
                            description = element.name;
                        } else if (element.title) {
                            // Fall back to title attribute
                            description = element.title;
                        }
                    }
                    
                    // Clean up description
                    description = description.replace(/\\s+/g, ' ').trim();
                    if (description.length > 50) {
                        description = description.substring(0, 50) + '...';
                    }
                    
                    // Check if required
                    const isRequired = element.required || element.hasAttribute('required');
                    
                    // Check if disabled
                    const isDisabled = element.disabled || element.hasAttribute('disabled');
                    
                    // Create unique key for deduplication
                    const elementKey = xpath + '|' + elementType;
                    
                    // Only add if not seen before and has meaningful content
                    if (!seenElements.has(elementKey) && xpath) {
                        seenElements.add(elementKey);
                        inputElements.push({
                            xpath: xpath,
                            type: elementType,
                            description: description || '_no description_',
                            required: isRequired,
                            disabled: isDisabled
                        });
                    }
                });
            });
            
            return inputElements;
        })();
        """

        # Execute JavaScript to get input elements
        result = chrome_interface.Runtime.evaluate(
            expression=js_code, returnByValue=True
        )
        logger.debug(f"Input elements extraction result: {result}")

        if isinstance(result, tuple) and len(result) >= 2:
            if isinstance(result[1], dict):
                elements_data = (
                    result[1].get("result", {}).get("result", {}).get("value", [])
                )
            elif isinstance(result[1], list) and len(result[1]) > 0:
                elements_data = (
                    result[1][0].get("result", {}).get("result", {}).get("value", [])
                )
            else:
                elements_data = []
        else:
            elements_data = []

        if not elements_data:
            return "\n\n## Input Elements\n\nNo input elements found on this page.\n"

        # Format input elements into concise markdown
        markdown_output = []
        markdown_output.append("\n\n## Input Elements\n")
        markdown_output.append("| XPath | Type | Description | Required | Disabled |\n")
        markdown_output.append("|-------|------|-------------|----------|----------|\n")

        for element in elements_data:
            xpath = element.get("xpath", "")
            element_type = element.get("type", "")
            description = element.get("description", "").strip()
            required = "✓" if element.get("required", False) else ""
            disabled = "✓" if element.get("disabled", False) else ""

            # Escape pipe characters for markdown table
            if description:
                description = description.replace("|", "\\|")
            else:
                description = "_no description_"

            xpath = xpath.replace("|", "\\|")
            element_type = element_type.replace("|", "\\|")

            markdown_output.append(
                f"| `{xpath}` | {element_type} | {description} | {required} | {disabled} |\n"
            )

        # Add summary
        total_elements = len(elements_data)
        markdown_output.append(f"\n**Total:** {total_elements} input elements\n")

        return "".join(markdown_output)

    except Exception as e:
        logger.error(f"Error extracting input elements: {e}")
        return f"\n\n## Input Elements\n\nError extracting input elements: {str(e)}\n"


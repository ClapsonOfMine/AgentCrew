"""
Web element extraction utilities for browser automation.

Provides functionality to extract clickable elements and page content
for browser automation operations.
"""

import re
import logging
import uuid
from typing import Dict

logger = logging.getLogger(__name__)


def remove_duplicate_lines(content: str) -> str:
    """
    Remove consecutive duplicate lines from content while preserving structure.

    This function:
    1. Splits content into lines
    2. Removes consecutive duplicate lines (keeps first occurrence)
    3. Preserves empty lines and markdown structure
    4. Handles whitespace variations by stripping for comparison

    Args:
        content: The content to deduplicate

    Returns:
        Content with consecutive duplicate lines removed
    """
    if not content:
        return content

    lines = content.split("\n")
    if len(lines) <= 1:
        return content

    deduplicated_lines = []
    previous_line_stripped = None

    for line in lines:
        # Strip whitespace for comparison but keep original for output
        current_line_stripped = line.strip()
        if not current_line_stripped:
            continue  # Skip adding multiple empty lines

        # Always keep empty lines and lines that differ from previous
        if not current_line_stripped or current_line_stripped != previous_line_stripped:
            deduplicated_lines.append(line)
            previous_line_stripped = current_line_stripped
        # Skip lines that are exact duplicates of the previous line

    return "\n".join(deduplicated_lines)


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
            return f"An Image Of {alt} "
        else:
            return ""

    # Replace HTML img tags
    cleaned_content = re.sub(html_img_pattern, replace_html_img, cleaned_content)

    return cleaned_content


def extract_clickable_elements(chrome_interface, uuid_mapping: Dict[str, str]) -> str:
    """
    Extract all clickable elements from the current webpage in a concise format.

    For each clickable element, extracts:
    - UUID: Short unique identifier for the element
    - Text/Alt: Display text or alt text from images

    Deduplication:
    - Elements with href: Deduplicated by href value
    - Elements without href: Deduplicated by tagName + text combination

    Args:
        chrome_interface: ChromeInterface object with enabled DOM
        uuid_mapping: Dictionary to store UUID to XPath mappings

    Returns:
        Concise markdown table with UUID and text/alt for each unique element
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
                if (element.id !== '') {
                    return `//*[@id="${element.id}"]`;
                }
                if (element === document.body) {
                    return '//' + element.tagName.toLowerCase();
                }

                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                        ix++;
                }
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

        # Format clickable elements into concise markdown with UUID mapping
        markdown_output = []
        markdown_output.append(
            "\n\n## Clickable Elements\nUse browser_click with UUID to click elements.\n"
        )
        markdown_output.append("| UUID | Text/Alt |\n")
        markdown_output.append("|------|----------|\n")

        for element in elements_data:
            xpath = element.get("xpath", "")
            text = element.get("text", "").strip()

            # Skip empty text entries
            if not text:
                continue

            # Generate UUID and store mapping
            element_uuid = str(uuid.uuid4())[:8]  # Use first 8 characters for brevity
            uuid_mapping[element_uuid] = xpath

            # Escape pipe characters in text for markdown table
            text = text.replace("|", "\\|")

            markdown_output.append(f"| `{element_uuid}` | {text} |\n")

        return "".join(markdown_output)

    except Exception as e:
        logger.error(f"Error extracting clickable elements: {e}")
        return f"\n\n## Clickable Elements\n\nError extracting clickable elements: {str(e)}\n"


def extract_input_elements(chrome_interface, uuid_mapping: Dict[str, str]) -> str:
    """
    Extract all input elements from the current webpage in a concise format.

    For each input element, extracts:
    - UUID: Short unique identifier for the element
    - Type: Input type (text, email, password, etc.)
    - Placeholder/Label: Placeholder text or associated label
    - Required: Whether the field is required

    Args:
        chrome_interface: ChromeInterface object with enabled DOM
        uuid_mapping: Dictionary to store UUID to XPath mappings

    Returns:
        Concise markdown table with UUID, type, and description for each input element
    """
    try:
        # JavaScript to find all input elements
        js_code = """
        (() => {
            const inputElements = [];
            const seenElements = new Set();
            
            // Function to generate XPath for an element
            function getXPath(element) {
                if (element.id !== '') {
                    return `//*[@id="${element.id}"]`;
                }
                if (element === document.body) {
                    return '//' + element.tagName.toLowerCase();
                }

                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                        ix++;
                }
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

        # Format input elements into concise markdown with UUID mapping
        markdown_output = []
        markdown_output.append(
            "\n\n## Input Elements\nUse browser_input with UUID and value to fill inputs.\n"
        )
        markdown_output.append("| UUID | Type | Description | Required | Disabled |\n")
        markdown_output.append("|------|------|-------------|----------|----------|\n")

        for element in elements_data:
            xpath = element.get("xpath", "")
            element_type = element.get("type", "")
            description = element.get("description", "").strip()
            required = "✓" if element.get("required", False) else ""
            disabled = "✓" if element.get("disabled", False) else ""

            # Generate UUID and store mapping
            element_uuid = str(uuid.uuid4())[:8]  # Use first 8 characters for brevity
            uuid_mapping[element_uuid] = xpath

            # Escape pipe characters for markdown table
            if description:
                description = description.replace("|", "\\|")
            else:
                description = "_no description_"

            element_type = element_type.replace("|", "\\|")

            markdown_output.append(
                f"| `{element_uuid}` | {element_type} | {description} | {required} | {disabled} |\n"
            )

        return "".join(markdown_output)

    except Exception as e:
        logger.error(f"Error extracting input elements: {e}")
        return f"\n\n## Input Elements\n\nError extracting input elements: {str(e)}\n"

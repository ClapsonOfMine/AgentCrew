/**
 * Extract all clickable elements from the current webpage.
 * 
 * Returns an array of objects with xpath and text properties for each unique clickable element.
 * Deduplicates elements by href (for links) or by tagName + text combination.
 */
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
/**
 * Extract all scrollable elements from the current webpage.
 * 
 * Returns an array of objects with xpath, tagName, description, scrollDirections, and other scroll properties.
 * Uses comprehensive visibility checking including parent element chain.
 */
(() => {
    const scrollableElements = [];
    const seenElements = new Set();
    
    // Utility function to check if element is truly visible (including parent chain)
    function isElementVisible(element) {
        if (!element || !element.nodeType === 1) {
            return false;
        }
        
        // Walk up the parent chain checking visibility
        let currentElement = element;
        
        while (currentElement && currentElement !== document.body && currentElement !== document.documentElement) {
            const style = window.getComputedStyle(currentElement);
            
            // Check if current element is hidden
            if (style.display === 'none' || style.visibility === 'hidden') {
                return false;
            }
            
            // Move to parent element
            currentElement = currentElement.parentElement;
        }
        
        return true;
    }
    
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
    
    // Get all elements on the page
    const allElements = document.querySelectorAll('*');
    
    allElements.forEach(element => {
        try {
            // Skip if element is hidden (checks entire parent chain)
            if (!isElementVisible(element)) {
                return;
            }
            
            const style = window.getComputedStyle(element);
            
            // Check if element has scrollable overflow
            const overflow = style.overflow;
            const overflowX = style.overflowX;
            const overflowY = style.overflowY;
            
            // Check if any overflow property indicates scrollability
            const hasScrollableOverflow = ['auto', 'scroll'].includes(overflow) || 
                                        ['auto', 'scroll'].includes(overflowX) || 
                                        ['auto', 'scroll'].includes(overflowY);
            
            // Also check if content actually overflows (even with overflow: hidden)
            const hasVerticalScroll = element.scrollHeight > element.clientHeight;
            const hasHorizontalScroll = element.scrollWidth > element.clientWidth;
            
            // Element is scrollable if it has scrollable overflow AND actual overflow
            const isScrollable = hasScrollableOverflow && (hasVerticalScroll || hasHorizontalScroll);
            
            if (!isScrollable) {
                return;
            }
            
            // Generate XPath
            const xpath = getXPath(element);
            if (!xpath) {
                return;
            }
            
            // Avoid duplicates
            if (seenElements.has(xpath)) {
                return;
            }
            seenElements.add(xpath);
            
            // Get element description
            let description = '';
            
            // Try to get meaningful text content (limited)
            const textContent = element.textContent || element.innerText || '';
            const cleanText = textContent.trim().replace(/\\s+/g, ' ');
            
            if (cleanText && cleanText.length > 0) {
                // Limit text length for description
                if (cleanText.length > 60) {
                    description = cleanText.substring(0, 60) + '...';
                } else {
                    description = cleanText;
                }
            }
            
            // If no meaningful text, use class or id
            if (!description || description.length < 3) {
                if (element.className) {
                    description = `class: ${element.className}`;
                } else if (element.id) {
                    description = `id: ${element.id}`;
                } else {
                    description = `${element.tagName.toLowerCase()} element`;
                }
            }
            
            // Determine scroll directions
            const scrollDirections = [];
            if (hasVerticalScroll) {
                scrollDirections.push('vertical');
            }
            if (hasHorizontalScroll) {
                scrollDirections.push('horizontal');
            }
            
            scrollableElements.push({
                xpath: xpath,
                tagName: element.tagName.toLowerCase(),
                description: description,
                scrollDirections: scrollDirections.join(', '),
                scrollHeight: element.scrollHeight,
                clientHeight: element.clientHeight,
                scrollWidth: element.scrollWidth,
                clientWidth: element.clientWidth,
                overflow: overflow,
                overflowX: overflowX,
                overflowY: overflowY
            });
            
        } catch (elementError) {
            // Skip problematic elements
            console.warn('Error processing element for scrollability:', elementError);
        }
    });
    
    return scrollableElements;
})();
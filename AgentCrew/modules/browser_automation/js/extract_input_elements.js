/**
 * Extract all input elements from the current webpage.
 * 
 * Returns an array of objects with xpath, type, description, required, and disabled properties.
 * Uses comprehensive visibility checking including parent element chain.
 */
(() => {
    const inputElements = [];
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
            // Skip if element is hidden (checks entire parent chain)
            if (!isElementVisible(element)) {
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
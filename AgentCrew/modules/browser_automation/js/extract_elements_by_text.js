/**
 * Extract elements containing specified text using XPath.
 * 
 * @param {string} text - The text to search for
 * @returns {Array} Array of elements containing the text
 */
function extractElementsByText(text) {
    const elementsFound = [];
    
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
    
    try {
        const xpath = `//div[contains(., '${text}')]`;
        const result = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
        
        let element = result.iterateNext();
        const seenElements = new Set();
        
        while (element) {
            const style = window.getComputedStyle(element);
            if (style.display !== 'none' && style.visibility !== 'hidden') {
                const elementXPath = getXPath(element);
                
                if (!seenElements.has(elementXPath)) {
                    seenElements.add(elementXPath);
                    
                    let elementText = element.textContent || element.innerText || '';
                    elementText = elementText.trim().replace(/\\s+/g, ' ');
                    if (elementText.length > 100) {
                        elementText = elementText.substring(0, 100) + '...';
                    }
                    
                    elementsFound.push({
                        xpath: elementXPath,
                        text: elementText,
                        tagName: element.tagName.toLowerCase(),
                        className: element.className || '',
                        id: element.id || ''
                    });
                }
            }
            
            element = result.iterateNext();
        }
        
        return elementsFound;
    } catch (error) {
        return [];
    }
}

// Export the function - when used in browser automation, wrap with IIFE and pass text
// (() => {
//     const text = '{TEXT_PLACEHOLDER}';
//     return extractElementsByText(text);
// })();
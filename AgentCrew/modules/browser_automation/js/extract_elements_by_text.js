/**
 * Extract elements containing specified text using XPath.
 * Uses comprehensive visibility checking including parent element chain.
 *
 * @param {string} text - The text to search for
 * @returns {Array} Array of elements containing the text
 */
function extractElementsByText(text) {
  const elementsFound = [];

  // Utility function to check if element is truly visible (including parent chain)
  function isElementVisible(element) {
    if (!element || !element.nodeType === 1) {
      return false;
    }

    if (!element.checkVisibility()) {
      return false;
    }

    return true;
  }

  function getXPath(element) {
    if (element.id !== "") {
      return `//*[@id="${element.id}"]`;
    }
    if (element === document.body) {
      return "//" + element.tagName.toLowerCase();
    }

    var ix = 0;
    var siblings = element.parentNode.childNodes;
    for (var i = 0; i < siblings.length; i++) {
      var sibling = siblings[i];
      if (sibling === element)
        return (
          getXPath(element.parentNode) +
          "/" +
          element.tagName.toLowerCase() +
          "[" +
          (ix + 1) +
          "]"
        );
      if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
    }
  }

  function getDirectTextContent(element) {
    let directText = "";
    for (const node of element.childNodes) {
      if (node.nodeType === Node.TEXT_NODE) {
        directText += node.textContent;
      }
    }
    return directText.trim();
  }

  try {
    const xpath = `//*[contains(., '${text}')]`;
    const result = document.evaluate(
      xpath,
      document,
      null,
      XPathResult.ANY_TYPE,
      null,
    );

    let element = result.iterateNext();
    const seenElements = new Set();
    const searchTextLower = text.toLowerCase();

    while (element) {
      if (isElementVisible(element)) {
        const directText = getDirectTextContent(element);
        const ariaLabel = element.getAttribute("aria-label") || "";

        if (
          directText.toLowerCase().includes(searchTextLower) ||
          ariaLabel.toLowerCase().includes(searchTextLower)
        ) {
          const elementXPath = getXPath(element);

          if (!seenElements.has(elementXPath)) {
            seenElements.add(elementXPath);

            let displayText = ariaLabel || directText || "";
            displayText = displayText.trim().replace(/\s+/g, " ");
            if (displayText.length > 100) {
              displayText = displayText.substring(0, 100) + "...";
            }

            elementsFound.push({
              xpath: elementXPath,
              text: displayText,
              tagName: element.tagName.toLowerCase(),
              className: element.className || "",
              id: element.id || "",
            });
          }
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

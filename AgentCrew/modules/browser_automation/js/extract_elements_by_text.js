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

    // Walk up the parent chain checking visibility
    let currentElement = element;

    if (currentElement.clientWidth <= 1 && currentElement.clientHeight <= 1) {
      return false;
    }

    while (
      currentElement &&
      currentElement !== document.body &&
      currentElement !== document.documentElement
    ) {
      const style = window.getComputedStyle(currentElement);

      // Check if current element is hidden
      if (style.display === "none" || style.visibility === "hidden") {
        return false;
      }

      // Move to parent element
      currentElement = currentElement.parentElement;
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

  try {
    const xpath = `//div[contains(., '${text}')]`;
    const result = document.evaluate(
      xpath,
      document,
      null,
      XPathResult.ANY_TYPE,
      null,
    );

    let element = result.iterateNext();
    const seenElements = new Set();

    while (element) {
      // Check if element is truly visible (including parent chain)
      if (isElementVisible(element)) {
        const elementXPath = getXPath(element);

        if (!seenElements.has(elementXPath)) {
          seenElements.add(elementXPath);

          let elementText =
            element.getAttribute("aria-label") ||
            element.textContent ||
            element.innerText ||
            "";
          elementText = elementText.trim().replace(/\\s+/g, " ");
          if (elementText.length > 100) {
            elementText = elementText.substring(0, 100) + "...";
          }

          elementsFound.push({
            xpath: elementXPath,
            text: elementText,
            tagName: element.tagName.toLowerCase(),
            className: element.className || "",
            id: element.id || "",
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


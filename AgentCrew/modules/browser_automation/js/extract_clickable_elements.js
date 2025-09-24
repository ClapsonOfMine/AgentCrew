/**
 * Extract all clickable elements from the current webpage.
 *
 * Returns an array of objects with xpath and text properties for each unique clickable element.
 * Deduplicates elements by href (for links) or by tagName + text combination.
 * Uses comprehensive visibility checking including parent element chain.
 */
(() => {
  const clickableElements = [];
  const seenHrefs = new Set();
  const seenElements = new Set();

  // Utility function to check if element is truly visible (including parent chain)
  function isElementVisible(element) {
    if (!element || !element.nodeType === 1) {
      return false;
    }

    // Check if the element is disabled (for form elements)
    if (element.disabled) {
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

  // Function to generate XPath for an element
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

  // Define selectors for clickable elements
  const selectors = [
    "a[href]", // Links
    "button", // Buttons
    'input[type="button"]',
    'input[type="submit"]',
    'input[type="reset"]',
    "[onclick]", // Elements with onclick handlers
    '[role="button"]', // ARIA buttons
    "[tabindex]", // Focusable elements
    "area[href]", // Image map areas
    '[role="combobox"][aria-haspopup=true]', // Select dropdowns
    "label[for]",
    "details summary", // Collapsible details
  ];

  selectors.forEach((selector) => {
    const elements = document.querySelectorAll(selector);
    elements.forEach((element) => {
      // Skip if element is hidden (checks entire parent chain)
      if (!isElementVisible(element)) {
        return;
      }

      // Get href for deduplication
      const href = element.href || element.getAttribute("href") || "";

      // Generate XPath
      const xpath = getXPath(element);

      // Get display text
      let displayText = element.getAttribute("aria-label");

      // Check if element contains images and extract alt text
      const images = element.querySelectorAll("img");
      if (images.length > 0) {
        const altTexts = [];
        images.forEach((img) => {
          const alt = img.getAttribute("alt");
          const label = img.getAttribute("aria-label");
          if (alt) {
            altTexts.push(alt);
          } else if (label) {
            altTexts.push(label);
          }
        });
        if (altTexts.length > 0 && !displayText) {
          displayText = altTexts.join(", ");
        }
      }

      // If no alt text from images, get text content
      if (!displayText) {
        displayText = element.textContent || element.innerText || "";
        displayText = displayText.trim().replace(/\\s+/g, " ");

        // Try aria-label or title if no text content
        if (!displayText) {
          displayText = element.title || "";
        }

        // Limit text length
        if (displayText.length > 50) {
          displayText = displayText.substring(0, 50) + "...";
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
              text: displayText,
            });
          }
        } else {
          // For elements without href, deduplicate by tagName + text combination
          const elementKey = element.tagName.toLowerCase() + "|" + displayText;
          if (!seenElements.has(elementKey)) {
            seenElements.add(elementKey);
            clickableElements.push({
              xpath: xpath,
              text: displayText,
            });
          }
        }
      }
    });
  });

  return clickableElements;
})();

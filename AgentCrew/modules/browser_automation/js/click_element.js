/**
 * Click an element using XPath selector.
 *
 * @param {string} xpath - The XPath selector for the element to click
 * @returns {Object} Result object with success status and message
 */
function clickElement(xpath) {
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null,
  );
  const element = result.singleNodeValue;

  if (!element) {
    return { success: false, error: "Element not found" };
  }

  // Check if element is visible and enabled
  const style = window.getComputedStyle(element);
  if (style.display === "none" || style.visibility === "hidden") {
    return { success: false, error: "Element is not visible" };
  }

  if (element.disabled) {
    return { success: false, error: "Element is disabled" };
  }

  // Scroll element into view
  element.scrollIntoView({ behavior: "smooth", block: "center" });

  // Get element's bounding rect for mouse coordinates
  const rect = element.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;

  const mouseEventOptions = {
    view: window,
    bubbles: true,
    cancelable: true,
    clientX: centerX,
    clientY: centerY,
    screenX: centerX + window.screenX,
    screenY: centerY + window.screenY,
    button: 0, // Left mouse button
    buttons: 1, // Left mouse button pressed
    ctrlKey: false,
    shiftKey: false,
    altKey: false,
    metaKey: false,
  };

  try {
    const mouseDownEvent = new MouseEvent("mousedown", mouseEventOptions);
    element.dispatchEvent(mouseDownEvent);

    if (element.focus) {
      element.focus();
    }

    const mouseUpEvent = new MouseEvent("mouseup", mouseEventOptions);
    element.dispatchEvent(mouseUpEvent);

    const clickEvent = new MouseEvent("click", mouseEventOptions);
    element.dispatchEvent(clickEvent);

    element.click();

    return { success: true, message: "Element clicked successfully" };
  } catch (eventError) {
    // Fallback to simple click if mouse events fail
    try {
      element.click();
      return { success: true, message: "Element clicked successfully" };
    } catch (fallbackError) {
      return {
        success: false,
        error:
          "Failed to click element: " +
          eventError.message +
          " (fallback also failed: " +
          fallbackError.message +
          ")",
      };
    }
  }
}

// Export the function - when used in browser automation, wrap with IIFE and pass xpath
// (() => {
//     const xpath = '{XPATH_PLACEHOLDER}';
//     return clickElement(xpath);
// })();

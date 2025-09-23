/**
 * Trigger input and change events to notify the page of input changes.
 *
 * @param {string} xpath - XPath selector for the element
 * @returns {Object} Result object with success status and message
 */
function triggerInputEvents(xpath, value) {
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null,
  );
  const element = result.singleNodeValue;

  if (!element) {
    return { success: false, error: "Element not found for event triggering" };
  }

  try {
    // Trigger input event
    element.dispatchEvent(new Event("input", { bubbles: true }));

    element.value = value;
    // Trigger change event
    element.dispatchEvent(new Event("change", { bubbles: true }));

    if (element.tagName.toLowerCase() !== "select") {
      // For some forms, also trigger keyup event
      element.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));
    }

    return { success: true, message: "Input events triggered successfully" };
  } catch (eventError) {
    return {
      success: false,
      error: "Failed to trigger events: " + eventError.message,
    };
  }
}

// Export the function - when used in browser automation, wrap with IIFE and pass xpath
// (() => {
//     const xpath = '{XPATH_PLACEHOLDER}';
//     return triggerInputEvents(xpath);
// })();

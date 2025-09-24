/**
 * Scroll the page or a specific element in specified direction.
 *
 * @param {string} direction - Direction to scroll ('up', 'down', 'left', 'right')
 * @param {number} distance - Distance to scroll in pixels
 * @param {string} xpath - Optional XPath of specific element to scroll
 * @param {string} elementUuid - Optional UUID of the element for identification
 * @returns {Object} Result object with success status, message, and scroll info
 */
function scrollPage(direction, distance, xpath = "", elementUuid = "") {
  let scrollX = 0;
  let scrollY = 0;

  switch (direction.toLowerCase()) {
    case "up":
      scrollY = -distance;
      break;
    case "down":
      scrollY = distance;
      break;
    case "left":
      scrollX = -distance;
      break;
    case "right":
      scrollX = distance;
      break;
    default:
      return {
        success: false,
        error: "Invalid direction. Use 'up', 'down', 'left', or 'right'",
      };
  }

  // Determine scroll target (specific element or document)
  let scrollTarget = document.documentElement || document.body;
  let targetDescription = "the whole document";

  if (xpath && elementUuid) {
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

    // Check if element is scrollable
    const style = window.getComputedStyle(element);
    const hasScrollableOverflow =
      ["auto", "scroll"].includes(style.overflow) ||
      ["auto", "scroll"].includes(style.overflowY) ||
      ["auto", "scroll"].includes(style.overflowX);

    if (
      hasScrollableOverflow ||
      element.scrollHeight > element.clientHeight ||
      element.scrollWidth > element.clientWidth
    ) {
      scrollTarget = element;
      targetDescription = "element " + elementUuid;
    }
  }

  // Get current scroll position
  const currentX =
    scrollTarget === document.documentElement
      ? window.pageXOffset || document.documentElement.scrollLeft
      : scrollTarget.scrollLeft;
  const currentY =
    scrollTarget === document.documentElement
      ? window.pageYOffset || document.documentElement.scrollTop
      : scrollTarget.scrollTop;

  // Create wheel event for smooth scrolling
  const wheelEventOptions = {
    view: window,
    bubbles: true,
    cancelable: true,
    deltaX: scrollX,
    deltaY: scrollY,
    deltaMode: WheelEvent.DOM_DELTA_PIXEL,
  };

  try {
    // Dispatch wheel event to mimic true user scroll
    const wheelEvent = new WheelEvent("wheel", wheelEventOptions);

    if (scrollTarget === document.documentElement) {
      document.dispatchEvent(wheelEvent);
      // Also perform actual scroll for fallback
      window.scrollBy(scrollX, scrollY);
    } else {
      scrollTarget.dispatchEvent(wheelEvent);
      // Perform actual scroll on the element
      scrollTarget.scrollBy(scrollX, scrollY);
    }
  } catch (eventError) {
    // Fallback to direct scrolling if wheel event fails
    if (scrollTarget === document.documentElement) {
      window.scrollBy(scrollX, scrollY);
    } else {
      scrollTarget.scrollBy(scrollX, scrollY);
    }
  }

  // Get new scroll position
  const newX =
    scrollTarget === document.documentElement
      ? window.pageXOffset || document.documentElement.scrollLeft
      : scrollTarget.scrollLeft;
  const newY =
    scrollTarget === document.documentElement
      ? window.pageYOffset || document.documentElement.scrollTop
      : scrollTarget.scrollTop;

  return {
    success: true,
    message:
      "Scrolled " +
      targetDescription +
      " " +
      direction +
      " by " +
      Math.abs(scrollX || scrollY) +
      "px using dispatchEvent",
    previous_position: { x: currentX, y: currentY },
    new_position: { x: newX, y: newY },
    target: targetDescription,
    scroll_method: "wheel_event_with_fallback",
  };
}

// Export the function - when used in browser automation, wrap with IIFE and pass parameters
// (() => {
//     const direction = '{DIRECTION_PLACEHOLDER}';
//     const distance = {DISTANCE_PLACEHOLDER};
//     const xpath = '{XPATH_PLACEHOLDER}';
//     const elementUuid = '{ELEMENT_UUID_PLACEHOLDER}';
//     return scrollPage(direction, distance, xpath, elementUuid);
// })();


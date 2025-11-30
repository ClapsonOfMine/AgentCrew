function filterHiddenElements() {
  try {
    function isElementVisible(element) {
      if (!element || element.nodeType !== 1) {
        return false;
      }

      if (element.disabled) {
        return false;
      }

      if (!element.checkVisibility()) {
        return false;
      }

      return true;
    }

    function getXPath(element) {
      if (!element || element.nodeType !== 1) {
        return null;
      }

      if (element === document.documentElement) {
        return "/html[1]";
      }

      const parts = [];
      let current = element;

      while (current && current.nodeType === 1) {
        if (current === document.documentElement) {
          parts.unshift("/html[1]");
          break;
        }

        let index = 1;
        let sibling = current.previousElementSibling;
        while (sibling) {
          if (sibling.tagName === current.tagName) {
            index++;
          }
          sibling = sibling.previousElementSibling;
        }

        const tagName = current.tagName.toLowerCase();
        parts.unshift(`${tagName}[${index}]`);
        current = current.parentElement;
      }

      return parts.join("/");
    }

    function traverseAndMarkHidden(element, hiddenXPaths) {
      if (!element || element.nodeType !== 1) {
        return;
      }

      const tagName = element.tagName.toLowerCase();
      if (
        tagName === "script" ||
        tagName === "style" ||
        tagName === "noscript"
      ) {
        const xpath = getXPath(element);
        if (xpath) {
          hiddenXPaths.push(xpath);
        }
        return;
      }

      if (!isElementVisible(element)) {
        const xpath = getXPath(element);
        if (xpath) {
          hiddenXPaths.push(xpath);
        }
        return;
      }

      const children = Array.from(element.children);
      for (const child of children) {
        traverseAndMarkHidden(child, hiddenXPaths);
      }
    }

    const documentClone = document.documentElement.cloneNode(true);
    const cloneDoc = document.implementation.createHTMLDocument("");
    cloneDoc.replaceChild(documentClone, cloneDoc.documentElement);

    const hiddenXPaths = [];
    traverseAndMarkHidden(document.documentElement, hiddenXPaths);

    for (const xpath of hiddenXPaths) {
      const result = cloneDoc.evaluate(
        xpath,
        cloneDoc,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null,
      );
      const cloneElement = result.singleNodeValue;
      if (cloneElement) {
        cloneElement.setAttribute("data-hidden", "true");
      }
    }

    const hiddenElements = cloneDoc.querySelectorAll("[data-hidden='true']");
    hiddenElements.forEach((el) => el.remove());

    const filteredHTML = cloneDoc.documentElement.outerHTML;

    return {
      success: true,
      html: filteredHTML,
      message: "Successfully filtered hidden elements using computed styles",
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      stack: error.stack,
    };
  }
}

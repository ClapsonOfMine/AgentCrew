function filterHiddenElements() {
  try {
    function isElementHidden(element) {
      if (element.nodeType !== Node.ELEMENT_NODE) {
        return false;
      }

      const tagName = element.tagName.toLowerCase();
      if (
        tagName === "script" ||
        tagName === "style" ||
        tagName === "noscript"
      ) {
        return true;
      }

      const computedStyle = window.getComputedStyle(element);

      if (
        computedStyle.display === "none" ||
        computedStyle.visibility === "hidden" ||
        computedStyle.opacity === "0"
      ) {
        return true;
      }

      const ariaHidden = element.getAttribute("aria-hidden");
      if (ariaHidden === "true") {
        return true;
      }

      return false;
    }

    function removeHiddenElementsFromNode(node) {
      if (!node || node.nodeType !== Node.ELEMENT_NODE) {
        return;
      }

      const children = Array.from(node.children);

      for (const child of children) {
        const originalElement = document.querySelector(
          `[ag-data-temp-id="${child.getAttribute("ag-data-temp-id")}"]`,
        );

        if (!originalElement) {
          child.remove();
          continue;
        }

        if (isElementHidden(originalElement)) {
          child.remove();
        } else {
          removeHiddenElementsFromNode(child);
        }
      }
    }

    function addTempIds(node, prefix = "") {
      if (!node || node.nodeType !== Node.ELEMENT_NODE) {
        return;
      }

      const children = Array.from(node.children);
      children.forEach((child, index) => {
        const tempId = `${prefix}${index}`;
        child.setAttribute("ag-data-temp-id", tempId);
        addTempIds(child, `${tempId}-`);
      });
    }

    function removeTempIds(node) {
      if (!node || node.nodeType !== Node.ELEMENT_NODE) {
        return;
      }

      node.removeAttribute("ag-data-temp-id");
      Array.from(node.children).forEach((child) => removeTempIds(child));
    }

    addTempIds(document.documentElement);
    const documentClone = document.documentElement.cloneNode(true);

    removeHiddenElementsFromNode(documentClone);

    removeTempIds(document.documentElement);
    removeTempIds(documentClone);

    const filteredHTML = documentClone.outerHTML;

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

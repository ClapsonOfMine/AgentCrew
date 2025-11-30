function scrollToElement(xpath) {
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null,
  );
  const element = result.singleNodeValue;

  if (!element) {
    return { success: false, error: "Element not found with provided xpath" };
  }

  element.scrollIntoView({
    behavior: "instant",
    block: "center",
    inline: "center",
  });

  return {
    success: true,
    message: "Scrolled to element using scrollIntoView()",
  };
}

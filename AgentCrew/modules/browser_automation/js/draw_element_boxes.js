/**
 * Draw colored rectangle boxes with UUID labels over elements
 *
 * @param {Object} uuidXpathMap - Map of UUID to XPath selector
 * @returns {Object} Result object with success status and message
 */
function drawElementBoxes(uuidXpathMap) {
  try {
    const existingContainer = document.getElementById(
      "agentcrew-element-overlay-container",
    );
    if (existingContainer) {
      existingContainer.remove();
    }

    const svgNS = "http://www.w3.org/2000/svg";
    const container = document.createElementNS(svgNS, "svg");
    container.setAttribute("id", "agentcrew-element-overlay-container");
    container.style.position = "fixed";
    container.style.top = "0";
    container.style.left = "0";
    container.style.width = "100%";
    container.style.height = "100%";
    container.style.pointerEvents = "none";
    container.style.zIndex = "2147483647";

    const colors = [
      "#FF6B6B",
      "#4ECDC4",
      "#45B7D1",
      "#FFA07A",
      "#98D8C8",
      "#F7DC6F",
      "#BB8FCE",
      "#85C1E2",
      "#F8B739",
      "#52B788",
    ];

    const labelPadding = 8;
    const fontSize = 14;
    const labelHeight = 24;
    const occupiedSpaces = [];

    function checkOverlap(newLabel, existingLabels) {
      for (const existing of existingLabels) {
        if (
          !(
            newLabel.right < existing.left ||
            newLabel.left > existing.right ||
            newLabel.bottom < existing.top ||
            newLabel.top > existing.bottom
          )
        ) {
          return true;
        }
      }
      return false;
    }

    function findBestLabelPosition(rect, labelWidth, existingLabels) {
      const positions = [
        { x: rect.left, y: rect.top - labelHeight - 4, priority: 1 },
        { x: rect.left, y: rect.bottom + 4, priority: 2 },
        {
          x: rect.right - labelWidth,
          y: rect.top - labelHeight - 4,
          priority: 3,
        },
        { x: rect.right - labelWidth, y: rect.bottom + 4, priority: 4 },
        {
          x: rect.left + rect.width / 2 - labelWidth / 2,
          y: rect.top - labelHeight - 4,
          priority: 5,
        },
        { x: rect.left - labelWidth - 4, y: rect.top, priority: 6 },
        { x: rect.right + 4, y: rect.top, priority: 7 },
        {
          x: rect.left,
          y: rect.top + rect.height / 2 - labelHeight / 2,
          priority: 8,
        },
      ];

      positions.sort((a, b) => a.priority - b.priority);

      for (const pos of positions) {
        const labelBounds = {
          left: pos.x,
          right: pos.x + labelWidth,
          top: pos.y,
          bottom: pos.y + labelHeight,
        };

        if (labelBounds.top >= 0 && labelBounds.left >= 0) {
          if (!checkOverlap(labelBounds, existingLabels)) {
            return { x: pos.x, y: pos.y };
          }
        }
      }

      return { x: rect.left, y: Math.max(0, rect.top - labelHeight - 4) };
    }

    let colorIndex = 0;
    let drawnCount = 0;

    for (const [uuid, xpath] of Object.entries(uuidXpathMap)) {
      try {
        const result = document.evaluate(
          xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null,
        );
        const element = result.singleNodeValue;

        if (!element) {
          continue;
        }

        const rect = element.getBoundingClientRect();

        if (rect.width === 0 || rect.height === 0) {
          continue;
        }

        const color = colors[colorIndex % colors.length];
        colorIndex++;

        const group = document.createElementNS(svgNS, "g");

        const box = document.createElementNS(svgNS, "rect");
        box.setAttribute("x", rect.left);
        box.setAttribute("y", rect.top);
        box.setAttribute("width", rect.width);
        box.setAttribute("height", rect.height);
        box.setAttribute("fill", "none");
        box.setAttribute("stroke", color);
        box.setAttribute("stroke-width", "3");
        box.setAttribute("stroke-dasharray", "5,5");
        box.setAttribute("rx", "4");

        const labelWidth = uuid.length * (fontSize * 0.6) + labelPadding * 2;
        const labelPos = findBestLabelPosition(
          rect,
          labelWidth,
          occupiedSpaces,
        );

        const labelBg = document.createElementNS(svgNS, "rect");
        labelBg.setAttribute("x", labelPos.x);
        labelBg.setAttribute("y", labelPos.y);
        labelBg.setAttribute("width", labelWidth);
        labelBg.setAttribute("height", labelHeight);
        labelBg.setAttribute("fill", color);
        labelBg.setAttribute("rx", "4");

        const label = document.createElementNS(svgNS, "text");
        label.setAttribute("x", labelPos.x + labelPadding);
        label.setAttribute("y", labelPos.y + 17);
        label.setAttribute("fill", "#FFFFFF");
        label.setAttribute("font-family", "monospace");
        label.setAttribute("font-size", fontSize);
        label.setAttribute("font-weight", "bold");
        label.textContent = uuid;

        occupiedSpaces.push({
          left: labelPos.x,
          right: labelPos.x + labelWidth,
          top: labelPos.y,
          bottom: labelPos.y + labelHeight,
        });

        group.appendChild(box);
        group.appendChild(labelBg);
        group.appendChild(label);
        container.appendChild(group);

        drawnCount++;
      } catch (err) {
        console.warn(`Failed to draw box for UUID ${uuid}:`, err);
      }
    }

    document.body.appendChild(container);

    return {
      success: true,
      message: `Successfully drew ${drawnCount} element boxes`,
      count: drawnCount,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

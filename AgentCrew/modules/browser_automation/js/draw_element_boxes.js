/**
 * Draw colored rectangle boxes with UUID labels over elements
 * 
 * @param {Object} uuidXpathMap - Map of UUID to XPath selector
 * @returns {Object} Result object with success status and message
 */
function drawElementBoxes(uuidXpathMap) {
  try {
    const existingContainer = document.getElementById('agentcrew-element-overlay-container');
    if (existingContainer) {
      existingContainer.remove();
    }

    const svgNS = 'http://www.w3.org/2000/svg';
    const container = document.createElementNS(svgNS, 'svg');
    container.setAttribute('id', 'agentcrew-element-overlay-container');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '2147483647';
    
    const colors = [
      '#FF6B6B',
      '#4ECDC4', 
      '#45B7D1',
      '#FFA07A',
      '#98D8C8',
      '#F7DC6F',
      '#BB8FCE',
      '#85C1E2',
      '#F8B739',
      '#52B788'
    ];
    
    let colorIndex = 0;
    let drawnCount = 0;
    
    for (const [uuid, xpath] of Object.entries(uuidXpathMap)) {
      try {
        const result = document.evaluate(
          xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
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
        
        const group = document.createElementNS(svgNS, 'g');
        
        const box = document.createElementNS(svgNS, 'rect');
        box.setAttribute('x', rect.left);
        box.setAttribute('y', rect.top);
        box.setAttribute('width', rect.width);
        box.setAttribute('height', rect.height);
        box.setAttribute('fill', 'none');
        box.setAttribute('stroke', color);
        box.setAttribute('stroke-width', '3');
        box.setAttribute('stroke-dasharray', '5,5');
        box.setAttribute('rx', '4');
        
        const labelBg = document.createElementNS(svgNS, 'rect');
        const labelX = rect.left;
        const labelY = Math.max(0, rect.top - 24);
        const labelPadding = 8;
        const fontSize = 14;
        const labelWidth = uuid.length * (fontSize * 0.6) + labelPadding * 2;
        
        labelBg.setAttribute('x', labelX);
        labelBg.setAttribute('y', labelY);
        labelBg.setAttribute('width', labelWidth);
        labelBg.setAttribute('height', '24');
        labelBg.setAttribute('fill', color);
        labelBg.setAttribute('rx', '4');
        
        const label = document.createElementNS(svgNS, 'text');
        label.setAttribute('x', labelX + labelPadding);
        label.setAttribute('y', labelY + 17);
        label.setAttribute('fill', '#FFFFFF');
        label.setAttribute('font-family', 'monospace');
        label.setAttribute('font-size', fontSize);
        label.setAttribute('font-weight', 'bold');
        label.textContent = uuid;
        
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
      count: drawnCount
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Remove the overlay container with element boxes
 * 
 * @returns {Object} Result object with success status and message
 */
function removeElementBoxes() {
  try {
    const container = document.getElementById('agentcrew-element-overlay-container');
    
    if (!container) {
      return {
        success: true,
        message: 'No overlay container found (already removed or never created)'
      };
    }
    
    container.remove();
    
    return {
      success: true,
      message: 'Successfully removed element boxes overlay'
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// CustomModal Component for displaying notifications and custom content
// Replaces browser alert() with a beautiful, accessible modal dialog
import React, { useEffect } from 'react';

/**
 * CustomModal - A reusable modal component for displaying notifications and custom content
 * @param {string} message - The message to display in the modal
 * @param {function} onClose - Callback function to handle modal closing
 * @param {React.ReactNode} children - Optional custom content to render instead of just message
 * @param {string} title - Optional custom title (defaults to "Notification")
 * @param {boolean} showCloseButton - Whether to show the default close button (defaults to true)
 */
const CustomModal = ({ 
  message, 
  onClose, 
  children, 
  title = "Notification",
  showCloseButton = true 
}) => {
  // Handle escape key press for accessibility
  useEffect(() => {
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    // Add event listener when modal is open
    document.addEventListener('keydown', handleEscapeKey);
    
    // Focus trap - focus on modal when it opens
    const modalElement = document.querySelector('[role="dialog"]');
    if (modalElement) {
      modalElement.focus();
    }

    // Cleanup event listener on unmount
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [onClose]);

  return (
    // Modal overlay - covers entire screen with semi-transparent background
    // Enhanced with proper ARIA attributes for accessibility
    <div 
      className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
      onClick={onClose} // Allow clicking outside to close
    >
      {/* Modal content container with responsive design and click prevention */}
      <div 
        className="bg-white p-4 sm:p-6 rounded-lg shadow-xl max-w-sm sm:max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
      >
        
        {/* Modal title with semantic heading */}
        <h3 
          id="modal-title"
          className="text-lg sm:text-xl font-semibold text-gray-800 mb-3 sm:mb-4"
        >
          {title}
        </h3>
        
        {/* Modal content - either message or custom children */}
        <div id="modal-description" className="mb-4 sm:mb-6">
          {children ? (
            // Render custom content if provided
            <div className="text-sm sm:text-base">
              {children}
            </div>
          ) : (
            // Render message if no custom content
            <p className="text-gray-600 text-sm sm:text-base leading-relaxed break-words whitespace-pre-wrap">
              {message}
            </p>
          )}
        </div>
        
        {/* Close button with enhanced accessibility and responsive design */}
        {showCloseButton && (
          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 focus:ring-offset-2 transition duration-150 ease-in-out text-sm sm:text-base font-medium"
            aria-label="Close notification dialog"
            autoFocus // Automatically focus the close button for keyboard navigation
          >
            Close
          </button>
        )}
      </div>
    </div>
  );
};

export default CustomModal; 
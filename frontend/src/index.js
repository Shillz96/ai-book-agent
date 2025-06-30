// React DOM imports for rendering
import React from 'react';
import ReactDOM from 'react-dom/client';

// Import the main App component
import App from './App';

// Import Tailwind CSS for styling
import './index.css';

// Create root element and render the App
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component with React.StrictMode for development checks
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 
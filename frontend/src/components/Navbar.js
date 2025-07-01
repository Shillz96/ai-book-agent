import React from 'react';
import './Navbar.css';

/**
 * Navbar – lightweight header component that provides a clean brand area
 * and space to extend with future navigation links.  It uses the global
 * CSS variables already defined in `index.css` so we avoid any hard-coded
 * colour values here.
 */
const Navbar = () => {
  return (
    <nav className="navbar-root">
      <span className="navbar-brand">AI Book Agent</span>
      {/* Placeholder for future nav-items – keeps markup minimal for now */}
    </nav>
  );
};

export default Navbar; 
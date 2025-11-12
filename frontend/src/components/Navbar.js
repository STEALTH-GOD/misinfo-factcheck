import React, {useState} from "react";
import "./Navbar.css";

const Navbar = ({currentPage, onNavigate}) => {
  const [isOpen, setIsOpen] = useState(false);

  const isActive = (page) => {
    return currentPage === page;
  };

  const handleNavClick = (page) => {
    onNavigate(page);
    setIsOpen(false); // Close mobile menu after navigation
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-content">
          {/* Logo */}
          <div className="navbar-brand">
            <button
              onClick={() => handleNavClick("home")}
              className="brand-link"
            >
              <div className="brand-icon">
                <span className="brand-letters">MI</span>
              </div>
              <span className="brand-text">MisInfoAI</span>
            </button>
          </div>

          {/* Desktop Navigation */}
          <div className="navbar-menu">
            <button
              onClick={() => handleNavClick("home")}
              className={`nav-link ${
                isActive("home") ? "nav-link-active" : ""
              }`}
            >
              <span>Home</span>
            </button>
            <button
              onClick={() => handleNavClick("detect")}
              className={`nav-link verify-btn ${
                isActive("detect") ? "nav-link-active" : ""
              }`}
            >
              <span>Verify</span>
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="navbar-mobile-toggle">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="mobile-toggle-btn"
              aria-label="Toggle navigation menu"
            >
              <div className={`hamburger ${isOpen ? "hamburger-open" : ""}`}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className={`mobile-menu ${isOpen ? "mobile-menu-open" : ""}`}>
          <div className="mobile-menu-content">
            <button
              onClick={() => handleNavClick("home")}
              className={`mobile-nav-link ${
                isActive("home") ? "mobile-nav-link-active" : ""
              }`}
            >
              <span>Home</span>
            </button>
            <button
              onClick={() => handleNavClick("detect")}
              className={`mobile-nav-link ${
                isActive("detect") ? "mobile-nav-link-active" : ""
              }`}
            >
              <span>Verify</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

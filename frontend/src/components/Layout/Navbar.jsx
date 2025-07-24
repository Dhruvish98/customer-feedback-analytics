// frontend/src/components/Layout/Navbar.jsx - Enhanced version
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  const isActive = (path) => location.pathname.startsWith(path);
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">📊</span>
          <span className="brand-text">ReviewAnalytics Pro</span>
        </Link>
        
        {user && (
          <div className="navbar-menu">
            <Link 
              to="/dashboard" 
              className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
            >
              <span className="nav-icon">🏠</span>
              Dashboard
            </Link>
            
            <Link 
              to="/monitor" 
              className={`nav-link ${isActive('/monitor') ? 'active' : ''}`}
            >
              <span className="nav-icon">📡</span>
              Live Monitor
            </Link>
            
            <div className="nav-dropdown">
              <button 
                className={`nav-link dropdown-toggle ${isActive('/analytics') ? 'active' : ''}`}
                onClick={() => setDropdownOpen(!dropdownOpen)}
              >
                <span className="nav-icon">📈</span>
                Analytics
              </button>
              {dropdownOpen && (
                <div className="dropdown-menu">
                  <Link to="/analytics/aspects/PROD00001" className="dropdown-item">
                    Aspect Analysis
                  </Link>
                  <Link to="/analytics/competitors/PROD00001" className="dropdown-item">
                    Competitor Intel
                  </Link>
                  <Link to="/analytics/predictions/PROD00001" className="dropdown-item">
                    Predictions
                  </Link>
                </div>
              )}
            </div>
            
            <Link 
              to="/submit-review" 
              className={`nav-link ${isActive('/submit-review') ? 'active' : ''}`}
            >
              <span className="nav-icon">✍️</span>
              Submit Review
            </Link>
            
            {/* Add Review History Link */}
            <Link to="/review-history" className="nav-link">
              <span className="nav-icon">📜</span>
              My Reviews
            </Link>

            {user.role === 'admin' && (
              <Link 
                to="/admin" 
                className={`nav-link admin ${isActive('/admin') ? 'active' : ''}`}
              >
                <span className="nav-icon">⚙️</span>
                Admin
              </Link>
            )}
          </div>
        )}
        
        <div className="navbar-right">
          {user ? (
            <div className="user-menu">
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                <span className="user-role">{user.role}</span>
              </div>
              <button onClick={handleLogout} className="logout-btn">
                <span className="logout-icon">🚪</span>
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="btn btn-primary">Sign Up</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
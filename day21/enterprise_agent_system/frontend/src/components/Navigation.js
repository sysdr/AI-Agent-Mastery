import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-logo">
          🤖 Enterprise Agent System
        </div>
        <ul className="nav-links">
          <li>
            <Link 
              to="/" 
              className={location.pathname === '/' ? 'active' : ''}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link 
              to="/security" 
              className={location.pathname === '/security' ? 'active' : ''}
            >
              Security
            </Link>
          </li>
          <li>
            <Link 
              to="/compliance" 
              className={location.pathname === '/compliance' ? 'active' : ''}
            >
              Compliance
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;

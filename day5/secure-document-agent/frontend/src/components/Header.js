import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, FileText, Upload, Activity } from 'lucide-react';

const Header = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          <Shield size={24} />
          SecureDoc Agent
        </Link>
        
        <nav className="nav">
          <Link 
            to="/" 
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            <FileText size={18} />
            Dashboard
          </Link>
          <Link 
            to="/upload" 
            className={`nav-link ${isActive('/upload') ? 'active' : ''}`}
          >
            <Upload size={18} />
            Upload
          </Link>
          <Link 
            to="/audit" 
            className={`nav-link ${isActive('/audit') ? 'active' : ''}`}
          >
            <Activity size={18} />
            Audit Logs
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;

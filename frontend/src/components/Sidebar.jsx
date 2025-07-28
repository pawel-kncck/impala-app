import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <h3 className="sidebar-title">User Profile</h3>
        {/* User details will go here */}
      </div>
      <div className="sidebar-section">
        <h3 className="sidebar-title">Projects</h3>
        {/* Project list will go here */}
      </div>
      <div className="sidebar-section">
        <h3 className="sidebar-title">Settings</h3>
        <Link to="/settings">Go to Settings</Link>
        {/* Settings links will go here */}
      </div>
    </div>
  );
}

export default Sidebar;

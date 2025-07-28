import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

function Sidebar({ user, logout }) {
  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <h3 className="sidebar-title">User Profile</h3>
        {user ? (
          <div>
            <p>Welcome, {user.first_name || user.username}!</p>
            <Link to="/account">Account Settings</Link>
            <br />
            <button onClick={logout}>Logout</button>
          </div>
        ) : (
          <p>
            <Link to="/login">Login</Link>
          </p>
        )}
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

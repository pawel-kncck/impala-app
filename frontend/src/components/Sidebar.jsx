import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Sidebar.css';

function Sidebar({ user, logout }) {
  const [projects, setProjects] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjects = async () => {
      if (user) {
        try {
          const token = localStorage.getItem('token');
          const response = await axios.get('/api/projects', {
            headers: { Authorization: `Bearer ${token}` },
          });
          setProjects(response.data);
        } catch (error) {
          console.error('Failed to fetch projects:', error);
        }
      }
    };

    fetchProjects();
  }, [user]); // Re-run when user object changes

  const handleNewProject = () => {
    navigate('/new-project');
  };

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
        <ul>
          {projects.map((project) => (
            <li key={project.id}>
              <Link to={`/projects/${project.id}`}>{project.name}</Link>
            </li>
          ))}
        </ul>
        <button onClick={handleNewProject}>New Project</button>
      </div>
      <div className="sidebar-section">
        <h3 className="sidebar-title">Settings</h3>
        {/* Settings links will go here */}
      </div>
    </div>
  );
}

export default Sidebar;

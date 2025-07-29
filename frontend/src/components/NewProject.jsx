import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './NewProject.css';

function NewProject() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        '/api/projects',
        { name, description },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      navigate('/'); // Redirect to the homepage to see the new project in the sidebar
    } catch (error) {
      console.error('Failed to create project:', error);
      setError('Failed to create project. Please try again.');
    }
  };

  return (
    <div className="new-project-container">
      <form onSubmit={handleSubmit} className="new-project-form">
        <h2>Create New Project</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project Name"
          required
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Project Description"
        />
        <button type="submit">Create Project</button>
      </form>
    </div>
  );
}

export default NewProject;

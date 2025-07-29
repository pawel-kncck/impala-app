// frontend/src/components/NewCanvas.jsx

import { useState } from 'react';
import axios from 'axios';

function NewCanvas({ projectId, onCanvasCreated }) {
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `/api/projects/${projectId}/canvases`,
        { name },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      onCanvasCreated(); // This will be a function to refresh the canvas list
      setName('');
    } catch (error) {
      console.error('Failed to create canvas:', error);
      setError('Failed to create canvas. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Create New Canvas</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Canvas Name"
        required
      />
      <button type="submit">Create</button>
    </form>
  );
}

export default NewCanvas;

import { useState } from 'react';
import axios from 'axios';

function FileUpload({ projectId, onUpload }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      await axios.post(`/api/projects/${projectId}/upload-csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });
      onUpload(); // Callback to refresh the list of data sources
      setFile(null); // Clear the file input
    } catch (error) {
      console.error('File upload failed:', error);
      setError('File upload failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Upload CSV</h3>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button type="submit">Upload</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
}

export default FileUpload;

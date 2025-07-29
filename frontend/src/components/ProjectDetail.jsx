import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './ProjectDetail.css'; // Import the new CSS file

function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('data'); // 'data' or 'canvases'

  // ... (keep the useEffect for fetching the project)

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        // This is a mock response until the backend is ready
        const mockProject = {
          id: projectId,
          name: `Project ${projectId}`,
          description: 'This is a sample project description.',
        };
        setProject(mockProject);
      } catch (err) {
        setError('Failed to fetch project details.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [projectId]);

  // ... (keep the loading, error, and not found checks)

  if (loading) return <div>Loading project...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!project) return <div>Project not found.</div>;

  return (
    <div>
      <h2>{project.name}</h2>
      <p>{project.description}</p>

      <div className="tabs">
        <div
          className={`tab ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          Data
        </div>
        <div
          className={`tab ${activeTab === 'canvases' ? 'active' : ''}`}
          onClick={() => setActiveTab('canvases')}
        >
          Canvases
        </div>
      </div>

      <div className="tab-content">
        {activeTab === 'data' && (
          <div>
            <h3>Data Sources</h3>
            <p>Placeholder for data upload feature and list of data sources.</p>
          </div>
        )}
        {activeTab === 'canvases' && (
          <div>
            <h3>Canvases</h3>
            <p>Placeholder for the list of canvases.</p>
            <button>New Canvas</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProjectDetail;

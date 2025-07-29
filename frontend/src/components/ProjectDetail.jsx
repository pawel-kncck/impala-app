import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './ProjectDetail.css'; // Import the new CSS file
import FileUpload from './FileUpload'; // Import the FileUpload component

function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('data'); // 'data' or 'canvases'
  const [dataSources, setDataSources] = useState([]); // State for data sources

  const fetchDataSource = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `/api/projects/${projectId}/data-sources`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setDataSources(response.data);
    } catch (err) {
      console.error('Failed to fetch data sources:', err);
    }
  };

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
    fetchDataSource(); // Fetch data sources on mount
  }, [projectId]);

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
            <FileUpload projectId={projectId} onUpload={fetchDataSource} />
            <hr />
            <h3>Data Sources</h3>
            <ul>
              {dataSources.map((ds) => (
                <li key={ds.id}>{ds.file_name}</li>
              ))}
            </ul>
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

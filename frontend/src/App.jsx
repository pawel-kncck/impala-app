import { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Register from './components/Register';
import Login from './components/Login';
import Layout from './components/Layout';
import Account from './components/Account';
import ProjectDetail from './components/ProjectDetail';
import './App.css';

function Home() {
  return (
    <div>
      <h1>Welcome to Impala!</h1>
      <p>Your data journey starts here.</p>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const handleLogin = (token) => {
    localStorage.setItem('token', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    fetchUser();
    navigate('/');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    navigate('/login');
  };

  const fetchUser = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await axios.get('/api/me');
        setUser(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch user on load:', error);
      // If token is invalid, clear it
      localStorage.removeItem('token');
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <div className="container">
      <nav>
        <Link to="/">Home</Link>
        {user ? (
          <>
            | <Link to="/account">Account</Link> |{' '}
            <a href="#" onClick={handleLogout}>
              Logout
            </a>
          </>
        ) : (
          <>
            | <Link to="/register">Register</Link> |{' '}
            <Link to="/login">Login</Link>
          </>
        )}
      </nav>
      <Routes>
        <Route element={<Layout user={user} logout={handleLogout} />}>
          <Route path="/" element={<Home />} />
          <Route path="/account" element={<Account />} />
        </Route>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route element={<Layout user={user} logout={handleLogout} />}>
          <Route path="/" element={<Home />} />
          <Route path="/account" element={<Account />} />
          {/* Add this new route */}
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;

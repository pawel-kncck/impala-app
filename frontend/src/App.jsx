import { useState, useEffect } from 'react';
import {
  Routes,
  Route,
  Link,
  useNavigate,
  useLocation,
} from 'react-router-dom';
import axios from 'axios';
import Register from './components/Register';
import Login from './components/Login';
import Layout from './components/Layout';
import Account from './components/Account';
import ProjectDetail from './components/ProjectDetail';
import NewProject from './components/NewProject'; // Make sure this is imported
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
  const location = useLocation();

  // This effect will run when the user state changes
  useEffect(() => {
    // If we have a user and they are on the login/register page,
    // redirect them to the homepage.
    if (
      user &&
      (location.pathname === '/login' || location.pathname === '/register')
    ) {
      navigate('/');
    }
  }, [user, navigate, location.pathname]);

  const handleLogin = async (token) => {
    localStorage.setItem('token', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    await fetchUser();
    // The useEffect above will now handle the redirect.
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    navigate('/login');
  };

  const fetchUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setUser(null);
      return;
    }
    try {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await axios.get('/api/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user on load:', error);
      localStorage.removeItem('token');
      setUser(null); // Explicitly set user to null on error
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
        {/* Public Routes */}
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route element={<Layout user={user} logout={handleLogout} />}>
          <Route path="/" element={<Home />} />
          <Route path="/account" element={<Account />} />
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
          <Route path="/new-project" element={<NewProject />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;

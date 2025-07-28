import { Routes, Route, Link } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import Layout from './components/Layout'; // Import the new Layout
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
  return (
    <div className="container">
      <nav>
        <Link to="/">Home</Link> | <Link to="/register">Register</Link> |{' '}
        <Link to="/login">Login</Link>
      </nav>
      <Routes>
        {/* Routes that use the sidebar layout */}
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          {/* Add other authenticated routes here later */}
        </Route>

        {/* Routes that do not use the sidebar */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </div>
  );
}

export default App;

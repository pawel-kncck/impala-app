import { Routes, Route, Link } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import './App.css';

function Home() {
  return (
    <div>
      <h1>Hello, Data World!</h1>
      <p>My first app is live!</p>
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
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </div>
  );
}

export default App;

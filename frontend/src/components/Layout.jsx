import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import './Layout.css';

function Layout({ user, logout }) {
  // If the user is not logged in, redirect them to the login page
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar user={user} logout={logout} />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;

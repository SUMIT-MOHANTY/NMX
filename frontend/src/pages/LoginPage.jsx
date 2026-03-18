import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import { isAuthenticated } from '../utils/auth';

const LoginPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard');
    } else {
      setLoading(false);
    }
  }, [navigate]);

  // Handle successful login
  const handleLogin = (userData) => {
    console.log('User logged in:', userData.username);
    navigate('/dashboard');
  };

  if (loading) {
    return <div className="loading">Checking authentication status...</div>;
  }

  return (
    <div>
      <LoginForm onLogin={handleLogin} />
    </div>
  );
};

export default LoginPage;

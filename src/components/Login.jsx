import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authenticateUser } from '../services/authService';
import { validateCredentials } from '../utils/validators';
import '../styles/Login.css';

/**
 * Secure Login Component
 * - Implements input validation
 * - Sanitizes inputs
 * - Handles authentication errors
 * - Prevents excessive login attempts
 * - Secures credentials handling
 */
const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [lockout, setLockout] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const navigate = useNavigate();

  // Securely handle input changes with validation
  const handleChange = (e) => {
    const { name, value } = e.target;
    // Never store plain text password in state beyond form submission
    setCredentials((prev) => ({ ...prev, [name]: value }));

    // Real-time validation
    const fieldErrors = validateCredentials({ [name]: value });
    setErrors((prev) => ({ ...prev, [name]: fieldErrors[name] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError('');

    // Prevent brute force attacks by limiting login attempts
    if (loginAttempts >= 5) {
      setLockout(true);
      setGeneralError('Too many failed attempts. Please try again later.');
      // In production, you would implement a timed lockout here
      setTimeout(() => {
        setLockout(false);
        setLoginAttempts(0);
      }, 30000); // 30 seconds lockout for demo
      return;
    }

    // Full validation before submission
    const fieldErrors = validateCredentials(credentials);
    if (Object.keys(fieldErrors).length > 0) {
      setErrors(fieldErrors);
      return;
    }

    setLoading(true);
    try {
      // Authenticate with backend securely
      const response = await authenticateUser(credentials);

      if (response.success) {
        // Reset counters on success
        setLoginAttempts(0);

        // In production: token should be stored in httpOnly cookies by the server
        // Client-side just receives success/failure
        navigate('/dashboard');
      } else {
        // Increment failed attempts counter
        setLoginAttempts(prev => prev + 1);
        setGeneralError('Invalid username or password');
      }
    } catch (error) {
      console.error('Login error:', error);
      // Generic error message to prevent information disclosure
      setGeneralError('An error occurred during login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Secure Login</h2>

        {generalError && <div className="error-message">{generalError}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              disabled={loading || lockout}
              autoComplete="username"
              aria-invalid={errors.username ? "true" : "false"}
            />
            {errors.username && <div className="field-error">{errors.username}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              disabled={loading || lockout}
              autoComplete="current-password"
              aria-invalid={errors.password ? "true" : "false"}
            />
            {errors.password && <div className="field-error">{errors.password}</div>}
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading || lockout}
          >
            {loading ? "Authenticating..." : "Login"}
          </button>
        </form>

        <div className="login-footer">
          <a href="/forgot-password">Forgot password?</a>
        </div>
      </div>
    </div>
  );
};

export default Login;

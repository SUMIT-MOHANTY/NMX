/**
 * Authentication Service
 * - Securely handles API communication for authentication
 * - Implements CSRF protection
 * - Uses HTTPS
 * - Handles authentication tokens securely
 */
import { sanitizeInput } from '../utils/security';

// Secure authentication function
export const authenticateUser = async (credentials) => {
  try {
    // Sanitize inputs to prevent XSS
    const sanitizedCredentials = {
      username: sanitizeInput(credentials.username),
      password: credentials.password, // Don't sanitize password as it may contain special chars
    };

    // In production, ensure your API is served over HTTPS
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Include CSRF token from cookies if available
        ...(document.cookie.includes('XSRF-TOKEN') && {
          'X-XSRF-TOKEN': document.cookie
            .split('; ')
            .find(row => row.startsWith('XSRF-TOKEN'))
            .split('=')[1]
        })
      },
      credentials: 'include', // Sends cookies with request
      body: JSON.stringify(sanitizedCredentials),
    });

    if (!response.ok) {
      // Handle different HTTP status codes
      if (response.status === 401) {
        return { success: false, message: 'Invalid credentials' };
      } else if (response.status === 429) {
        return { success: false, message: 'Too many login attempts. Try again later.' };
      }
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    // Don't store tokens in localStorage - rely on httpOnly cookies set by server
    return { success: true, user: data.user };
  } catch (error) {
    console.error('Authentication error:', error);
    throw error;
  }
};

// Logout function
export const logout = async () => {
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
      headers: {
        // Include CSRF token
        ...(document.cookie.includes('XSRF-TOKEN') && {
          'X-XSRF-TOKEN': document.cookie
            .split('; ')
            .find(row => row.startsWith('XSRF-TOKEN'))
            .split('=')[1]
        })
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return { success: true };
  } catch (error) {
    console.error('Logout error:', error);
    throw error;
  }
};

// Check authentication status
export const checkAuthStatus = async () => {
  try {
    const response = await fetch('/api/auth/status', {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 401) {
        return { authenticated: false };
      }
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return { authenticated: true, user: data.user };
  } catch (error) {
    console.error('Auth check error:', error);
    return { authenticated: false, error: error.message };
  }
};

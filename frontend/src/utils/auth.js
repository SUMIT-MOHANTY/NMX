/**
 * Authentication utility functions for the application
 */

/**
 * Check if user is authenticated based on token presence
 * @returns {boolean} Whether the user is authenticated
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('token');

  if (!token) {
    return false;
  }

  try {
    // Check token expiration
    // This is a basic check - in production, you might want to decode the JWT
    // and check its expiration date
    return true;
  } catch (error) {
    console.error('Authentication check error:', error);
    return false;
  }
};

/**
 * Get the current authentication token
 * @returns {string|null} The authentication token or null if not found
 */
export const getToken = () => {
  return localStorage.getItem('token');
};

/**
 * Log the user out by removing their token
 */
export const logout = () => {
  localStorage.removeItem('token');
  // You may want to redirect the user or perform additional cleanup here
};

/**
 * Add authentication header to fetch requests
 * @param {Object} headers - The headers object to add the auth header to
 * @returns {Object} Updated headers object with auth token
 */
export const addAuthHeader = (headers = {}) => {
  const token = getToken();
  if (token) {
    return {
      ...headers,
      'Authorization': `Bearer ${token}`
    };
  }
  return headers;
};

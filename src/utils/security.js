/**
 * Security Utilities
 * - Provides security-related helper functions
 * - Sanitizes user inputs to prevent XSS
 */

// Sanitize input to prevent XSS
export const sanitizeInput = (input) => {
  if (!input) return input;

  // Convert to string if not already
  const str = String(input);

  // Replace potentially dangerous characters
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};

// Generate a secure random string (for CSRF tokens, etc)
export const generateRandomToken = (length = 32) => {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
};

// Detect HTTPS
export const isHttps = () => {
  return window.location.protocol === 'https:';
};

// Warning if not using HTTPS in production
export const checkHttps = () => {
  if (process.env.NODE_ENV === 'production' && !isHttps()) {
    console.warn('Warning: This application is not running on HTTPS. Login credentials may be exposed.');
    return false;
  }
  return true;
};

// Detect if DevTools is open (anti-debugging measure for production)
export const detectDevTools = (callback) => {
  if (process.env.NODE_ENV !== 'production') return;

  const devtools = /./;
  devtools.toString = function() {
    callback();
    return '';
  };

  console.log('%c', devtools);
};

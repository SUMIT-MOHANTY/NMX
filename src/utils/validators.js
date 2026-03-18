/**
 * Form Validation Utilities
 * - Securely validates user inputs
 * - Prevents common security issues
 */

// Username validation
const validateUsername = (username) => {
  if (!username) {
    return 'Username is required';
  }

  if (username.length < 3) {
    return 'Username must be at least 3 characters';
  }

  // Prevent potentially dangerous characters in username
  if (!/^[a-zA-Z0-9._-]+$/.test(username)) {
    return 'Username contains invalid characters';
  }

  return null;
};

// Password validation
const validatePassword = (password) => {
  if (!password) {
    return 'Password is required';
  }

  if (password.length < 8) {
    return 'Password must be at least 8 characters';
  }

  // Check for password complexity
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+/.test(password);

  if (!hasLetter || !hasNumber || !hasSpecialChar) {
    return 'Password must include at least one letter, one number, and one special character';
  }

  return null;
};

// Validate credentials
export const validateCredentials = (credentials) => {
  const errors = {};

  if ('username' in credentials) {
    const usernameError = validateUsername(credentials.username);
    if (usernameError) {
      errors.username = usernameError;
    }
  }

  if ('password' in credentials) {
    const passwordError = validatePassword(credentials.password);
    if (passwordError) {
      errors.password = passwordError;
    }
  }

  return errors;
};

// Email validation
export const validateEmail = (email) => {
  if (!email) {
    return 'Email is required';
  }

  // Basic email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Please enter a valid email address';
  }

  return null;
};

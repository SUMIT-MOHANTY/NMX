import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

/**
 * Registration component that handles user registration
 * Uses React Hook Form for form handling and validation
 */
const Register = () => {
  // State for tracking API responses
  const [isLoading, setIsLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState({
    success: false,
    message: '',
    error: false
  });

  // Initialize form with react-hook-form
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm();

  // Get current password value for confirmation validation
  const password = watch('password', '');

  // Form submission handler
  const onSubmit = async (data) => {
    // Set loading state
    setIsLoading(true);
    console.log('Registration form submitted with data:', { ...data, password: '[REDACTED]' });

    // Format payload according to API specification (snake_case)
    const payload = {
      full_name: data.fullName,
      email: data.email,
      mobile: data.mobile,
      password: data.password,
      confirm_password: data.confirmPassword
    };

    try {
      // Call registration API endpoint
      const response = await axios.post('/api/auth/register', payload);

      console.log('Registration successful:', response.data);
      setApiResponse({
        success: true,
        message: 'Registration successful! You can now log in.',
        error: false
      });
    } catch (error) {
      // Handle different error types
      console.error('Registration error:', error);

      let errorMessage = 'Registration failed. Please try again later.';

      if (error.response) {
        // Server responded with an error
        console.error('Error response:', error.response.data);

        // Handle specific HTTP status codes
        if (error.response.status === 409) {
          errorMessage = 'This email is already registered.';
        } else if (error.response.status === 400) {
          errorMessage = error.response.data.detail || 'Invalid input data.';
        }
      } else if (error.request) {
        // Request was made but no response received
        console.error('No response received:', error.request);
        errorMessage = 'No response from server. Please check your internet connection.';
      }

      setApiResponse({
        success: false,
        message: errorMessage,
        error: true
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-container">
      <h1>Create Account</h1>

      {/* Display API response messages */}
      {apiResponse.message && (
        <div className={`alert ${apiResponse.error ? 'alert-error' : 'alert-success'}`}>
          {apiResponse.message}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="register-form">
        {/* Full Name Field */}
        <div className="form-group">
          <label htmlFor="fullName">Full Name</label>
          <input
            id="fullName"
            type="text"
            placeholder="John Doe"
            {...register('fullName', {
              required: 'Full name is required',
              minLength: {
                value: 2,
                message: 'Name must be at least 2 characters'
              }
            })}
          />
          {errors.fullName && <span className="error-message">{errors.fullName.message}</span>}
        </div>

        {/* Email Field */}
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            placeholder="your@email.com"
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
          />
          {errors.email && <span className="error-message">{errors.email.message}</span>}
        </div>

        {/* Mobile Field */}
        <div className="form-group">
          <label htmlFor="mobile">Mobile Number</label>
          <input
            id="mobile"
            type="tel"
            placeholder="1234567890"
            {...register('mobile', {
              required: 'Mobile number is required',
              minLength: {
                value: 10,
                message: 'Mobile number must be at least 10 digits'
              },
              maxLength: {
                value: 15,
                message: 'Mobile number must not exceed 15 digits'
              },
              pattern: {
                value: /^[0-9+\-\s()]*$/,
                message: 'Invalid mobile number format'
              }
            })}
          />
          {errors.mobile && <span className="error-message">{errors.mobile.message}</span>}
        </div>

        {/* Password Field */}
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="********"
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters'
              }
            })}
          />
          {errors.password && <span className="error-message">{errors.password.message}</span>}
        </div>

        {/* Confirm Password Field */}
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            placeholder="********"
            {...register('confirmPassword', {
              required: 'Please confirm your password',
              validate: value => value === password || 'Passwords do not match'
            })}
          />
          {errors.confirmPassword && (
            <span className="error-message">{errors.confirmPassword.message}</span>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="register-button"
          disabled={isLoading}
        >
          {isLoading ? 'Registering...' : 'Register'}
        </button>
      </form>

      {/* Login Link */}
      <p className="login-link">
        Already have an account? <a href="/login">Login</a>
      </p>
    </div>
  );
};

export default Register;

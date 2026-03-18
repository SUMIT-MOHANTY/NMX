import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface RegisterData {
  full_name: string;
  email: string;
  mobile: string;
  password: string;
  confirm_password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface UserResponse {
  id: string;
  full_name: string;
  email: string;
  mobile: string;
  created_at: string;
}

export interface AuthToken {
  token: string;
  user_id: string;
  role: string;
}

/**
 * Register a new user
 * @param data Registration form data
 * @returns User data if registration is successful
 */
export const registerUser = async (data: RegisterData): Promise<UserResponse> => {
  try {
    const response = await axios.post(`${API_URL}/auth/register`, data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 409) {
        throw new Error('Email already registered');
      }
      throw new Error(error.response.data.detail || 'Registration failed');
    }
    throw new Error('Registration failed. Please try again later.');
  }
};

/**
 * Log in a user
 * @param data Login form data
 * @returns Authentication token and user info
 */
export const loginUser = async (data: LoginData): Promise<AuthToken> => {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Login failed');
    }
    throw new Error('Login failed. Please try again later.');
  }
};

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/apiClient';
import { AxiosError } from 'axios';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useApi<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchData = useCallback(async (url: string, options = {}) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiClient.get<T>(url, options);
      setState({
        data: response.data,
        loading: false,
        error: null,
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError;
      setState({
        data: null,
        loading: false,
        error: new Error(
          axiosError.response?.data?.detail ||
          axiosError.message ||
          'An error occurred while fetching data'
        ),
      });
      throw error;
    }
  }, []);

  return {
    ...state,
    fetchData,
  };
}

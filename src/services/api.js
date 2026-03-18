import axios from 'axios';
import { format } from 'date-fns';
import logger from '../utils/logger';

const API_URL = process.env.REACT_APP_API_URL || 'https://api.example.com';

// Create axios instance with defaults
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  config => {
    logger.debug(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    logger.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
apiClient.interceptors.response.use(
  response => {
    logger.debug(`API Response: ${response.status} from ${response.config.url}`);
    return response;
  },
  error => {
    if (error.response) {
      logger.error(`API Error ${error.response.status}: ${error.response.data.message || 'Unknown error'}`);
    } else {
      logger.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// In a real app, these would call actual API endpoints
// For now, we'll mock the responses

export const fetchLocations = async () => {
  try {
    // In a real app: const response = await apiClient.get('/locations');
    // return response.data;

    // Mock data for development
    logger.info('Fetching locations');
    return new Promise(resolve => {
      setTimeout(() => {
        resolve([
          { id: '1', name: 'Downtown Branch' },
          { id: '2', name: 'Uptown Branch' },
          { id: '3', name: 'Suburban Branch' }
        ]);
      }, 500);
    });
  } catch (error) {
    logger.error('Error in fetchLocations:', error);
    throw error;
  }
};

export const fetchSlots = async (locationId, date) => {
  try {
    const formattedDate = format(date, 'yyyy-MM-dd');

    // In a real app:
    // const response = await apiClient.get(`/slots?locationId=${locationId}&date=${formattedDate}`);
    // return response.data;

    // Mock data for development
    logger.info(`Fetching slots for location ${locationId} on ${formattedDate}`);
    return new Promise(resolve => {
      setTimeout(() => {
        const baseDate = new Date(formattedDate);
        baseDate.setHours(9, 0, 0, 0);

        const slots = [];
        for (let i = 0; i < 8; i++) {
          const startTime = new Date(baseDate);
          startTime.setHours(startTime.getHours() + i);

          const endTime = new Date(startTime);
          endTime.setHours(endTime.getHours() + 1);

          slots.push({
            id: `slot-${locationId}-${i}`,
            startTime: startTime.toISOString(),
            endTime: endTime.toISOString(),
            available: Math.random() > 0.3, // 70% chance of being available
            capacity: Math.floor(Math.random() * 10) + 1,
            price: Math.floor(Math.random() * 50) + 20
          });
        }

        resolve(slots);
      }, 800);
    });
  } catch (error) {
    logger.error('Error in fetchSlots:', error);
    throw error;
  }
};

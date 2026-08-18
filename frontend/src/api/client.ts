import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/metrics';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor with graceful fallback
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.warn(`[API Client Error] ${error.config?.url}:`, error.message);
    return Promise.reject(error);
  }
);

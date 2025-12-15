import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Get all available demos
export const getDemos = async () => {
  const response = await api.get('/demos');
  return response.data;
};

// Get specific demo details
export const getDemo = async (demoId) => {
  const response = await api.get(`/demos/${demoId}`);
  return response.data;
};

// Submit a job
export const submitJob = async (demoId, parameters) => {
  const response = await api.post('/jobs', {
    demo_id: demoId,
    parameters: parameters,
  });
  return response.data;
};

// Get job status
export const getJobStatus = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

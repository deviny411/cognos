import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(request => {
  console.log('🌐 Making request:', request.method.toUpperCase(), request.url);
  console.log('🌐 Request data:', request.data);
  return request;
});

// Add response interceptor for debugging
apiClient.interceptors.response.use(
  response => {
    console.log('✅ Response:', response.status, response.data);
    return response;
  },
  error => {
    console.error('❌ Request failed:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export const api = {
  // Tags
  getTags: () => apiClient.get('/tags'),
  getTag: (id) => apiClient.get(`/tags/${id}`),
  createTag: (userId, data) => {
    console.log('📝 createTag called with userId:', userId, 'data:', data);
    return apiClient.post(`/users/${userId}/tags`, data);
  },

  deleteTag: (tagId) => apiClient.delete(`/tags/${tagId}`),  // ADD THIS
  
  // Articles
  getArticlesForTag: (tagId, minScore = null) => {
    const params = minScore ? { min_score: minScore } : {};
    return apiClient.get(`/tags/${tagId}/articles`, { params });
  },
  
  // News fetching
  fetchNewsForTag: (tagId) => apiClient.get(`/tags/${tagId}/fetch-news`),
  
  // Users (for future features)
  getUsers: () => apiClient.get('/users'),
  getUser: (id) => apiClient.get(`/users/${id}`),
  createUser: (data) => apiClient.post('/users', data),
};

export default apiClient;

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Tags
  getTags: () => apiClient.get('/tags'),
  getTag: (id) => apiClient.get(`/tags/${id}`),
  createTag: (data) => apiClient.post('/tags', data),
  
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

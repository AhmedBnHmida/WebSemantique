import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const searchAPI = {
  semanticSearch: (question) => api.post('/search', { question }),

};

export const sponsorsAPI = {
  getAll: () => api.get('/sponsors'),
  getById: (id) => api.get(`/sponsors/${id}`),
  search: (filters) => api.post('/sponsors/search', filters),
};

export const donationsAPI = {
  // params: { type: 'FinancialDonation'|'MaterialDonation'|'ServiceDonation', sort: 'newest'|'oldest', limit: number }
  getAll: (params = {}) => api.get('/donations', { params }),
  getById: (id) => api.get(`/donations/${id}`),
};

export const eventsAPI = {
  getAll: () => api.get('/events'),
  getById: (id) => api.get(`/events/${id}`),
  search: (filters) => api.post('/events/search', filters),
};

export const ontologyAPI = {
  getGraph: () => api.get('/ontology/graph'),
};

export const locationsAPI = {
  getAll: () => api.get('/locations'),
  getById: (id) => api.get(`/locations/${id}`),
  getAvailable: () => api.get('/locations/available'),
  search: (filters) => api.post('/locations/search', filters),
};

export const usersAPI = {
  getAll: () => api.get('/users'),
  getById: (id) => api.get(`/users/${id}`),
  getOrganizers: () => api.get('/users/organizers'),
  getByRole: (role) => api.get(`/users/role/${role}`),
};

export const volunteersAPI = {
  getAll: () => api.get('/volunteers'),
  getById: (id) => api.get(`/volunteers/${id}`),
  search: (filters) => api.post('/volunteers/search', filters),
  getByActivityLevel: (level) => api.get(`/volunteers/by-activity-level/${level}`),
};

export const assignmentsAPI = {
  getAll: () => api.get('/assignments'),
  getById: (id) => api.get(`/assignments/${id}`),
  getByStatus: (status) => api.get(`/assignments/by-status/${status}`),
  getByRating: (minRating) => api.get(`/assignments/by-rating/${minRating}`),
  search: (filters) => api.post('/assignments/search', filters),
  getStatistics: () => api.get('/assignments/statistics'),
};

export const blogsAPI = {
  getAll: () => api.get('/blogs'),
  getById: (id) => api.get(`/blogs/${id}`),
  search: (filters) => api.post('/blogs/search', filters),
};


export default api;
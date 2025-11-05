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
  dbpediaSearch: (text) => api.post('/dbpedia/search', { text }),
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

// New APIs for Education Infin entities

export const personnesAPI = {
  // Récupérer toutes les personnes
  getAll: () => api.get('/personnes'),
  
  // Récupérer une personne spécifique par ID
  getById: (id) => api.get(`/personnes/${id}`),
  
  // Rechercher des personnes avec des filtres
  search: (filters) => api.post('/personnes/search', filters),
  
  // Récupérer tous les étudiants
  getEtudiants: () => api.get('/personnes/etudiants'),
  
  // Récupérer tous les enseignants
  getEnseignants: () => api.get('/personnes/enseignants'),
  
  // Récupérer les cours d'une personne
  getCoursByPersonne: (id) => api.get(`/personnes/${id}/cours`),
  
  // Méthodes utilitaires pour les types spécifiques
  getEtudiantsByNiveau: (niveau) => api.post('/personnes/search', { role: 'Étudiant', niveauEtude: niveau }),
  
  getEnseignantsByGrade: (grade) => api.post('/personnes/search', { role: 'Enseignant', grade: grade }),
  
  // Recherche avancée avec tous les critères possibles
  advancedSearch: (criteria) => api.post('/personnes/search', criteria),
  
  // CRUD operations
  create: (data) => api.post('/personnes', data),
  update: (id, data) => api.put(`/personnes/${id}`, data),
  delete: (id) => api.delete(`/personnes/${id}`),
  
  // Faceted navigation
  getFacets: () => api.get('/personnes/facets'),
  
  // Linked Data integration (DBpedia)
  enrichWithDBpedia: (id, term = null) => {
    const url = `/personnes/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

// NEW: Specialité API endpoints
export const specialitesAPI = {
  // Récupérer toutes les spécialités
  getAll: () => api.get('/specialites'),
  
  // Récupérer une spécialité spécifique par ID
  getById: (id) => api.get(`/specialites/${id}`),
  
  // Rechercher des spécialités avec des filtres
  search: (filters) => api.post('/specialites/search', filters),
  
  // Récupérer les cours d'une spécialité
  getCoursBySpecialite: (id) => api.get(`/specialites/${id}/cours`),
  
  // Récupérer les étudiants d'une spécialité
  getEtudiantsBySpecialite: (id) => api.get(`/specialites/${id}/etudiants`),
  
  // Récupérer les compétences d'une spécialité
  getCompetencesBySpecialite: (id) => api.get(`/specialites/${id}/competences`),
  
  // Récupérer les statistiques des spécialités
  getStats: () => api.get('/specialites/stats'),
  
  // Récupérer les spécialités groupées par université
  getByUniversite: () => api.get('/specialites/par-universite'),
  
  // Méthodes utilitaires pour les recherches courantes
  getByDomaine: (domaine) => api.post('/specialites/search', { domaine }),
  
  getByNiveau: (niveau) => api.post('/specialites/search', { niveau }),
  
  getByUniversiteNom: (universite) => api.post('/specialites/search', { universite }),
  
  // Recherche avancée avec tous les critères
  advancedSearch: (criteria) => api.post('/specialites/search', criteria),
  
  // CRUD operations
  create: (data) => api.post('/specialites', data),
  update: (id, data) => api.put(`/specialites/${id}`, data),
  delete: (id) => api.delete(`/specialites/${id}`),
  
  // Faceted navigation
  getFacets: () => api.get('/specialites/facets'),
  
  // DBpedia enrichment (supports optional term parameter)
  enrichWithDBpedia: (id, term = null) => {
    const url = `/specialites/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

// NEW: Université API endpoints
export const universitesAPI = {
  // Récupérer toutes les universités
  getAll: () => api.get('/universites'),
  
  // Récupérer une université spécifique par ID
  getById: (id) => api.get(`/universites/${id}`),
  
  // Rechercher des universités avec des filtres
  search: (filters) => api.post('/universites/search', filters),
  
  // Récupérer les spécialités d'une université
  getSpecialitesByUniversite: (id) => api.get(`/universites/${id}/specialites`),
  
  // Récupérer les enseignants d'une université
  getEnseignantsByUniversite: (id) => api.get(`/universites/${id}/enseignants`),
  
  // Récupérer les étudiants d'une université
  getEtudiantsByUniversite: (id) => api.get(`/universites/${id}/etudiants`),
  
  // Récupérer les technologies d'une université
  getTechnologiesByUniversite: (id) => api.get(`/universites/${id}/technologies`),
  
  // Récupérer les projets d'une université
  getProjetsByUniversite: (id) => api.get(`/universites/${id}/projets`),
  
  // Récupérer les statistiques des universités
  getStats: () => api.get('/universites/stats'),
  
  // Récupérer le classement des universités
  getRanking: () => api.get('/universites/ranking'),
  
  // Méthodes utilitaires pour les recherches courantes
  getByVille: (ville) => api.post('/universites/search', { ville }),
  
  getByPays: (pays) => api.post('/universites/search', { pays }),
  
  getByType: (type) => api.post('/universites/search', { type }),
  
  getByNom: (nom) => api.post('/universites/search', { nom }),
  
  // Recherche avancée avec tous les critères
  advancedSearch: (criteria) => api.post('/universites/search', criteria),
  
  // CRUD operations
  create: (data) => api.post('/universites', data),
  update: (id, data) => api.put(`/universites/${id}`, data),
  delete: (id) => api.delete(`/universites/${id}`),
  
  // Faceted navigation (stats includes facets)
  getFacets: () => api.get('/universites/stats'),
  
  // Linked Data integration (DBpedia)
  enrichWithDBpedia: (id) => api.get(`/universites/${id}/dbpedia-enrich`)
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

// NEW: Education Statistics API
export const educationStatsAPI = {
  // Récupérer les statistiques générales de l'ontologie
  getOntologyStats: () => api.get('/ontology-stats'),
  
  // Récupérer les statistiques éducatives spécifiques
  getEducationStats: () => api.get('/education-stats'),
  
  // Récupérer les statistiques de test de connexion
  getTestStats: () => api.get('/test')
};

// NEW: Health check API
export const healthAPI = {
  check: () => api.get('/health')
};

// Cours API endpoints
export const coursAPI = {
  getAll: () => api.get('/cours'),
  getById: (id) => api.get(`/cours/${id}`),
  search: (filters) => api.post('/cours/search', filters),
  create: (data) => api.post('/cours', data),
  update: (id, data) => api.put(`/cours/${id}`, data),
  delete: (id) => api.delete(`/cours/${id}`),
  getFacets: () => api.get('/cours/facets'),
  enrichWithDBpedia: (id, term = null) => {
    const url = `/cours/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

// Competences API endpoints
export const competencesAPI = {
  getAll: () => api.get('/competences'),
  getById: (id) => api.get(`/competences/${id}`),
  search: (filters) => api.post('/competences/search', filters),
  create: (data) => api.post('/competences', data),
  update: (id, data) => api.put(`/competences/${id}`, data),
  delete: (id) => api.delete(`/competences/${id}`),
  getFacets: () => api.get('/competences/facets'),
  enrichWithDBpedia: (id, term = null) => {
    const url = `/competences/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

  // Projets Academiques API endpoints
export const projetsAPI = {
  getAll: () => api.get('/projets-academiques'),
  getById: (id) => api.get(`/projets-academiques/${id}`),
  search: (filters) => api.post('/projets-academiques/search', filters),
  create: (data) => api.post('/projets-academiques', data),
  update: (id, data) => api.put(`/projets-academiques/${id}`, data),
  delete: (id) => api.delete(`/projets-academiques/${id}`),
  getFacets: () => api.get('/projets-academiques/facets'),
  
  // Linked Data integration (DBpedia)
  enrichWithDBpedia: (id) => api.get(`/projets-academiques/${id}/dbpedia-enrich`)
};

// Ressources Pedagogiques API endpoints
export const ressourcesAPI = {
  getAll: () => api.get('/ressources-pedagogiques'),
  getById: (id) => api.get(`/ressources-pedagogiques/${id}`),
  search: (filters) => api.post('/ressources-pedagogiques/search', filters),
  create: (data) => api.post('/ressources-pedagogiques', data),
  update: (id, data) => api.put(`/ressources-pedagogiques/${id}`, data),
  delete: (id) => api.delete(`/ressources-pedagogiques/${id}`),
  getFacets: () => api.get('/ressources-pedagogiques/facets'),
  enrichWithDBpedia: (id, term = null) => {
    const url = `/ressources-pedagogiques/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

// Technologies Educatives API endpoints
export const technologiesAPI = {
  getAll: () => api.get('/technologies-educatives'),
  getById: (id) => api.get(`/technologies-educatives/${id}`),
  search: (filters) => api.post('/technologies-educatives/search', filters),
  create: (data) => api.post('/technologies-educatives', data),
  update: (id, data) => api.put(`/technologies-educatives/${id}`, data),
  delete: (id) => api.delete(`/technologies-educatives/${id}`),
  getFacets: () => api.get('/technologies-educatives/facets'),
  enrichWithDBpedia: (id, term = null) => {
    const url = `/technologies-educatives/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

// Evaluations API endpoints
export const evaluationsAPI = {
  getAll: () => api.get('/evaluations'),
  getById: (id) => api.get(`/evaluations/${id}`),
  search: (filters) => api.post('/evaluations/search', filters),
  create: (data) => api.post('/evaluations', data),
  update: (id, data) => api.put(`/evaluations/${id}`, data),
  delete: (id) => api.delete(`/evaluations/${id}`),
  getFacets: () => api.get('/evaluations/facets'),
  enrichWithDBpedia: (id, term = null) => {
    const url = `/evaluations/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

// Orientations Academiques API endpoints
export const orientationsAPI = {
  getAll: () => api.get('/orientations-academiques'),
  getById: (id) => api.get(`/orientations-academiques/${id}`),
  search: (filters) => api.post('/orientations-academiques/search', filters),
  create: (data) => api.post('/orientations-academiques', data),
  update: (id, data) => api.put(`/orientations-academiques/${id}`, data),
  delete: (id) => api.delete(`/orientations-academiques/${id}`),
  getFacets: () => api.get('/orientations-academiques/facets'),
  enrichWithDBpedia: (id, term = null) => {
    const url = `/orientations-academiques/${id}/dbpedia-enrich`;
    const params = term ? { params: { term } } : {};
    return api.get(url, params);
  }
};

export default api;
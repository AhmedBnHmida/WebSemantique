import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { personnesAPI } from '../../../utils/api';
import CRUDModal from '../../../components/CRUDModal';

const Personnes = () => {
  const [personnes, setPersonnes] = useState([]);
  const [filteredPersonnes, setFilteredPersonnes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    role: '',
    universite: '',
    search: ''
  });
  
  // CRUD Modal states
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: null, // 'add', 'edit', 'delete'
    data: {}
  });
  const [submitLoading, setSubmitLoading] = useState(false);
  
  // Details Modal state
  const [selectedPersonne, setSelectedPersonne] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [activeTab, setActiveTab] = useState('info');
  const [dbpediaData, setDbpediaData] = useState(null);
  const [loadingDBpedia, setLoadingDBpedia] = useState(false);

  const [stats, setStats] = useState({
    total: 0,
    etudiants: 0,
    enseignants: 0,
    autres: 0,
    byUniversite: {}
  });

  // Facets state for dynamic filters
  const [facets, setFacets] = useState({
    by_role: [],
    by_universite: [],
    by_specialite: []
  });

  useEffect(() => {
    fetchPersonnes();
    fetchFacets();
  }, []);

  useEffect(() => {
    filterPersonnes();
  }, [personnes, filters]);

  const fetchPersonnes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await personnesAPI.getAll();
      
      if (response.data) {
        const uniquePersonnes = removeDuplicates(response.data, 'personne');
        setPersonnes(uniquePersonnes);
        calculateStats(uniquePersonnes);
      } else {
        setError('Structure de données inattendue');
      }
    } catch (error) {
      console.error('Erreur lors du chargement des personnes:', error);
      setError('Erreur lors du chargement des personnes');
    } finally {
      setLoading(false);
    }
  };

  const fetchFacets = async () => {
    try {
      const response = await personnesAPI.getFacets();
      if (response.data) {
        setFacets(response.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des facettes:', error);
    }
  };

  const calculateStats = (personnesData) => {
    const stats = {
      total: personnesData.length,
      etudiants: 0,
      enseignants: 0,
      autres: 0,
      byUniversite: {}
    };

    personnesData.forEach(personne => {
      const role = personne.role?.toLowerCase() || '';
      const universite = personne.nomUniversite || 'Non affilié';

      if (role.includes('étudiant') || role.includes('etudiant')) {
        stats.etudiants++;
      } else if (role.includes('enseignant') || role.includes('professeur')) {
        stats.enseignants++;
      } else {
        stats.autres++;
      }

      stats.byUniversite[universite] = (stats.byUniversite[universite] || 0) + 1;
    });

    setStats(stats);
  };

  const filterPersonnes = () => {
    let filtered = personnes;

    if (filters.role) {
      filtered = filtered.filter(personne => {
        const role = personne.role?.toLowerCase() || '';
        return role.includes(filters.role.toLowerCase());
      });
    }

    if (filters.universite) {
      filtered = filtered.filter(personne => {
        const universite = personne.nomUniversite?.toLowerCase() || '';
        return universite.includes(filters.universite.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(personne => {
        const nom = personne.nom?.toLowerCase() || '';
        const prenom = personne.prenom?.toLowerCase() || '';
        const email = personne.email?.toLowerCase() || '';
        return nom.includes(filters.search.toLowerCase()) || 
               prenom.includes(filters.search.toLowerCase()) ||
               email.includes(filters.search.toLowerCase());
      });
    }

    setFilteredPersonnes(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      role: '',
      universite: '',
      search: ''
    });
  };

  const removeDuplicates = (array, key) => {
    const seen = new Set();
    return array.filter(item => {
      const value = item[key];
      if (!value || seen.has(value)) {
        return false;
      }
      seen.add(value);
      return true;
    });
  };

  const getRoleBadge = (role) => {
    if (!role) return 'unknown';
    
    const roleLower = role.toLowerCase();
    if (roleLower.includes('étudiant') || roleLower.includes('etudiant')) {
      return 'etudiant';
    } else if (roleLower.includes('enseignant') || roleLower.includes('professeur')) {
      return 'enseignant';
    } else {
      return 'autre';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifié';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR');
    } catch {
      return dateString;
    }
  };

  // CRUD Handlers
  const handleCreate = async (data) => {
    setSubmitLoading(true);
    try {
      await personnesAPI.create(data);
      await fetchPersonnes();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleUpdate = async (data) => {
    setSubmitLoading(true);
    try {
      await personnesAPI.update(data.personne, data);
      await fetchPersonnes();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDelete = async (data) => {
    setSubmitLoading(true);
    try {
      await personnesAPI.delete(data.personne);
      await fetchPersonnes();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleModalSubmit = async (formData) => {
    if (modalState.mode === 'add') {
      await handleCreate(formData);
    } else if (modalState.mode === 'edit') {
      await handleUpdate(formData);
    } else if (modalState.mode === 'delete') {
      await handleDelete(formData);
    }
  };

  const personneFields = [
    { name: 'nom', label: 'Nom', type: 'text', required: true, placeholder: 'Entrez le nom' },
    { name: 'prenom', label: 'Prénom', type: 'text', required: true, placeholder: 'Entrez le prénom' },
    { name: 'email', label: 'Email', type: 'email', placeholder: 'email@example.com' },
    { name: 'telephone', label: 'Téléphone', type: 'tel', placeholder: '+33 6 12 34 56 78' },
    { name: 'dateNaissance', label: 'Date de naissance', type: 'date' },
    { name: 'role', label: 'Rôle', type: 'select', options: [
      { value: 'Etudiant', label: 'Étudiant' },
      { value: 'Enseignant', label: 'Enseignant' },
      { value: 'Professeur', label: 'Professeur' },
      { value: 'Assistant', label: 'Assistant' }
    ] },
    { name: 'numeroMatricule', label: 'Numéro Matricule', type: 'text', placeholder: 'Pour étudiants' },
    { name: 'niveauEtude', label: 'Niveau d\'étude', type: 'text', placeholder: 'L1, L2, M1, etc.' },
    { name: 'moyenneGenerale', label: 'Moyenne Générale', type: 'number', step: '0.01', min: '0', max: '20' },
    { name: 'grade', label: 'Grade', type: 'text', placeholder: 'Pour enseignants' },
    { name: 'anciennete', label: 'Ancienneté', type: 'text', placeholder: 'Pour enseignants' }
  ];

  const showPersonneDetails = async (personne) => {
    try {
      const response = await personnesAPI.getById(personne.personne);
      // Handle both object and array responses
      const details = Array.isArray(response.data) ? response.data[0] : response.data;
      // Merge API response with original personne data to ensure all fields are available
      const mergedData = { ...personne, ...details };
      setSelectedPersonne(mergedData);
      setShowDetailsModal(true);
      setActiveTab('info');
      setDbpediaData(null);
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      setSelectedPersonne(personne);
      setShowDetailsModal(true);
      setActiveTab('info');
      setDbpediaData(null);
    }
  };

  const fetchDBpediaEnrichment = async (personneId, term = null) => {
    try {
      setLoadingDBpedia(true);
      setDbpediaData(null);
      const response = await personnesAPI.enrichWithDBpedia(personneId, term);
      if (response.data) {
        if (response.data.dbpedia_enrichment) {
          setDbpediaData(response.data.dbpedia_enrichment);
          setActiveTab('dbpedia');
        } else if (response.data.error) {
          setDbpediaData({ error: response.data.error });
        }
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données DBpedia:', error);
      setDbpediaData({ error: 'Erreur lors du chargement des données DBpedia' });
    } finally {
      setLoadingDBpedia(false);
    }
  };

  const personneDetailsFields = [
    { name: 'nom', label: 'Nom' },
    { name: 'prenom', label: 'Prénom' },
    { name: 'email', label: 'Email' },
    { name: 'telephone', label: 'Téléphone' },
    { name: 'dateNaissance', label: 'Date de naissance', format: (val) => val ? new Date(val).toLocaleDateString('fr-FR') : null },
    { name: 'role', label: 'Rôle' },
    { name: 'numeroMatricule', label: 'Numéro Matricule' },
    { name: 'niveauEtude', label: 'Niveau d\'étude' },
    { name: 'moyenneGenerale', label: 'Moyenne Générale' },
    { name: 'grade', label: 'Grade' },
    { name: 'anciennete', label: 'Ancienneté' },
    { name: 'nomUniversite', label: 'Université' }
  ];

  if (loading) return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Chargement des personnes...</p>
    </div>
  );

  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h3>Erreur de chargement</h3>
      <p>{error}</p>
      <button className="btn-retry" onClick={fetchPersonnes}>
        Réessayer
      </button>
    </div>
  );

  return (
    <div className="personnes-container">
      {/* Header Section */}
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-title">Gestion des Personnes</h1>
          <p className="page-subtitle">
            Gérez et consultez les informations des étudiants et enseignants
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
            ➕ Ajouter
          </button>
          <button className="btn-refresh" onClick={fetchPersonnes} title="Actualiser">
            🔄
          </button>
        </div>
      </header>

      {/* Statistics Cards */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">👥</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.total}</h3>
              <p className="stat-label">Total Personnes</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon etudiants">🎓</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.etudiants}</h3>
              <p className="stat-label">Étudiants</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon enseignants">👨‍🏫</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.enseignants}</h3>
              <p className="stat-label">Enseignants</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon autres">💼</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.autres}</h3>
              <p className="stat-label">Autres</p>
            </div>
          </div>
        </div>
      </section>

      {/* Filters Section */}
      <section className="filters-section">
        <div className="filters-header">
          <h2>Filtres et Recherche</h2>
          <div className="filters-actions">
            <span className="results-count">
              {filteredPersonnes.length} résultat(s)
            </span>
            <button className="btn-clear-filters" onClick={clearFilters}>
              Effacer tout
            </button>
          </div>
        </div>

        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Rôle</label>
            <select 
              value={filters.role} 
              onChange={(e) => handleFilterChange('role', e.target.value)}
              className="filter-select"
            >
              <option value="">Tous les rôles</option>
              {facets.by_role && facets.by_role.map((facet, index) => (
                <option key={index} value={facet.typePersonneLabel?.toLowerCase() || facet.typePersonne?.split('#').pop()?.toLowerCase() || ''}>
                  {facet.typePersonneLabel || facet.typePersonne?.split('#').pop() || 'Non spécifié'} ({facet.count || 0})
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Université</label>
            <select 
              value={filters.universite} 
              onChange={(e) => handleFilterChange('universite', e.target.value)}
              className="filter-select"
            >
              <option value="">Toutes les universités</option>
              {facets.by_universite && facets.by_universite.map((facet, index) => (
                <option key={index} value={facet.nomUniversite || ''}>
                  {facet.nomUniversite || 'Non spécifié'} ({facet.count || 0})
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group search-group">
            <label className="filter-label">Recherche</label>
            <div className="search-input-container">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Nom, prénom, email..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Persons Grid */}
      <section className="persons-grid-section">
        {filteredPersonnes.length > 0 ? (
          <div className="persons-grid">
            {filteredPersonnes.map((personne, index) => (
              <div key={index} className="person-card">
                <div className="card-header">
                  <div className="person-avatar">
                    {personne.prenom?.[0]}{personne.nom?.[0]}
                  </div>
                  <div className="person-info">
                    <h3 className="person-name">
                      {personne.prenom} {personne.nom}
                    </h3>
                    <span className={`role-badge ${getRoleBadge(personne.role)}`}>
                      {personne.role || 'Non spécifié'}
                    </span>
                  </div>
                </div>

                <div className="card-content">
                  <div className="info-grid">
                    {personne.email && (
                      <div className="info-item">
                        <span className="info-icon">✉️</span>
                        <span className="info-text">{personne.email}</span>
                      </div>
                    )}
                    
                    {personne.telephone && (
                      <div className="info-item">
                        <span className="info-icon">📞</span>
                        <span className="info-text">{personne.telephone}</span>
                      </div>
                    )}
                    
                    {personne.nomUniversite && (
                      <div className="info-item">
                        <span className="info-icon">🏫</span>
                        <span className="info-text">{personne.nomUniversite}</span>
                      </div>
                    )}
                    
                    {personne.dateNaissance && (
                      <div className="info-item">
                        <span className="info-icon">🎂</span>
                        <span className="info-text">{formatDate(personne.dateNaissance)}</span>
                      </div>
                    )}
                  </div>

                  {/* Student specific info */}
                  {(personne.niveauEtude || personne.moyenneGenerale) && (
                    <div className="special-info student-info">
                      <h4>Informations étudiant</h4>
                      <div className="special-details">
                        {personne.niveauEtude && (
                          <span className="detail-tag">Niveau: {personne.niveauEtude}</span>
                        )}
                        {personne.moyenneGenerale && (
                          <span className="detail-tag">Moyenne: {personne.moyenneGenerale}/20</span>
                        )}
                        {personne.numeroMatricule && (
                          <span className="detail-tag">Matricule: {personne.numeroMatricule}</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Teacher specific info */}
                  {(personne.grade || personne.anciennete) && (
                    <div className="special-info teacher-info">
                      <h4>Informations enseignant</h4>
                      <div className="special-details">
                        {personne.grade && (
                          <span className="detail-tag">Grade: {personne.grade}</span>
                        )}
                        {personne.anciennete && (
                          <span className="detail-tag">Expérience: {personne.anciennete} ans</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="card-actions">
                  <button className="btn-secondary">
                    📚 Voir les cours
                  </button>
                  <button className="btn-primary" onClick={() => showPersonneDetails(personne)}>
                    👁️ Détails
                  </button>
                  <button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: personne })}>
                    ✏️
                  </button>
                  <button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: personne })}>
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">👥</div>
            <h3>Aucune personne trouvée</h3>
            <p>Aucun résultat ne correspond à vos critères de recherche</p>
            <button className="btn-clear-filters" onClick={clearFilters}>
              Effacer les filtres
            </button>
          </div>
        )}
      </section>

      <style jsx>{`
        .personnes-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
          background: #f8fafc;
          min-height: 100vh;
        }

        /* Header Styles */
        .page-header {
          display: flex;
          justify-content: between;
          align-items: start;
          margin-bottom: 32px;
        }

        .header-content {
          flex: 1;
        }

        .page-title {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin: 0 0 8px 0;
        }

        .page-subtitle {
          font-size: 1rem;
          color: #64748b;
          margin: 0;
        }

        .btn-refresh {
          background: #f1f5f9;
          border: none;
          border-radius: 8px;
          padding: 8px;
          cursor: pointer;
          font-size: 1.2rem;
          transition: background 0.2s;
        }

        .btn-refresh:hover {
          background: #e2e8f0;
        }

        /* Statistics Styles */
        .stats-section {
          margin-bottom: 32px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .stat-card {
          background: white;
          padding: 24px;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          align-items: center;
          gap: 16px;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .stat-icon {
          font-size: 2rem;
          padding: 12px;
          border-radius: 8px;
        }

        .stat-icon.total { background: #dbeafe; }
        .stat-icon.etudiants { background: #dcfce7; }
        .stat-icon.enseignants { background: #fef3c7; }
        .stat-icon.autres { background: #f3e8ff; }

        .stat-number {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1e293b;
          margin: 0;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #64748b;
          margin: 0;
        }

        /* Filters Styles */
        .filters-section {
          background: white;
          padding: 24px;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin-bottom: 32px;
        }

        .filters-header {
          display: flex;
          justify-content: between;
          align-items: center;
          margin-bottom: 20px;
        }

        .filters-header h2 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin: 0;
        }

        .filters-actions {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .results-count {
          font-size: 0.875rem;
          color: #64748b;
        }

        .btn-clear-filters {
          background: #f1f5f9;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          color: #64748b;
          cursor: pointer;
          font-size: 0.875rem;
          transition: background 0.2s;
        }

        .btn-clear-filters:hover {
          background: #e2e8f0;
        }

        .filters-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .filter-label {
          font-size: 0.875rem;
          font-weight: 500;
          color: #374151;
        }

        .filter-select, .search-input {
          padding: 10px 12px;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 0.875rem;
          transition: border-color 0.2s;
        }

        .filter-select:focus, .search-input:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .search-group {
          grid-column: 1 / -1;
        }

        .search-input-container {
          position: relative;
          display: flex;
          align-items: center;
        }

        .search-icon {
          position: absolute;
          left: 12px;
          color: #9ca3af;
        }

        .search-input {
          padding-left: 40px;
          width: 100%;
        }

        /* Persons Grid Styles */
        .persons-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 24px;
        }

        .person-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .person-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .card-header {
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .person-avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 1rem;
        }

        .person-info {
          flex: 1;
        }

        .person-name {
          margin: 0 0 4px 0;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .role-badge {
          padding: 4px 8px;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .role-badge.etudiant { background: #10b981; }
        .role-badge.enseignant { background: #f59e0b; }
        .role-badge.autre { background: #8b5cf6; }
        .role-badge.unknown { background: #6b7280; }

        .card-content {
          padding: 20px;
        }

        .info-grid {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 16px;
        }

        .info-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .info-icon {
          font-size: 0.875rem;
        }

        .info-text {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .special-info {
          padding: 12px;
          border-radius: 8px;
          margin-bottom: 12px;
        }

        .special-info.student-info {
          background: #f0f9ff;
          border-left: 4px solid #0ea5e9;
        }

        .special-info.teacher-info {
          background: #fffbeb;
          border-left: 4px solid #f59e0b;
        }

        .special-info h4 {
          margin: 0 0 8px 0;
          font-size: 0.875rem;
          font-weight: 600;
          color: #1e293b;
        }

        .special-details {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .detail-tag {
          font-size: 0.75rem;
          color: #64748b;
          background: rgba(255, 255, 255, 0.7);
          padding: 2px 6px;
          border-radius: 4px;
        }

        .card-actions {
          padding: 0 20px 20px;
          display: flex;
          gap: 8px;
        }

        .btn-primary, .btn-secondary {
          flex: 1;
          padding: 10px 16px;
          border: none;
          border-radius: 8px;
          font-size: 0.875rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover {
          background: #2563eb;
        }

        .btn-secondary {
          background: #f1f5f9;
          color: #64748b;
        }

        .btn-secondary:hover {
          background: #e2e8f0;
        }

        /* Empty State */
        .empty-state {
          text-align: center;
          padding: 60px 20px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .empty-icon {
          font-size: 4rem;
          margin-bottom: 16px;
        }

        .empty-state h3 {
          font-size: 1.25rem;
          color: #1e293b;
          margin: 0 0 8px 0;
        }

        .empty-state p {
          color: #64748b;
          margin: 0 0 20px 0;
        }

        /* Loading State */
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 60px 20px;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f1f5f9;
          border-left: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 16px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        /* Error State */
        .error-container {
          text-align: center;
          padding: 60px 20px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .error-icon {
          font-size: 3rem;
          margin-bottom: 16px;
        }

        .error-container h3 {
          font-size: 1.25rem;
          color: #dc2626;
          margin: 0 0 8px 0;
        }

        .error-container p {
          color: #64748b;
          margin: 0 0 20px 0;
        }

        .btn-retry {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 500;
        }

        .btn-retry:hover {
          background: #2563eb;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .personnes-container {
            padding: 16px;
          }

          .page-header {
            flex-direction: column;
            gap: 16px;
          }

          .filters-header {
            flex-direction: column;
            align-items: start;
            gap: 12px;
          }

          .filters-actions {
            width: 100%;
            justify-content: between;
          }

          .persons-grid {
            grid-template-columns: 1fr;
          }

          .card-actions {
            flex-direction: column;
          }
          }

          .btn-add {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
          }

          .btn-add:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          }

          .btn-edit, .btn-delete {
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
          }

          .btn-edit {
            background: #fbbf24;
            color: white;
          }

          .btn-edit:hover {
            background: #f59e0b;
          }

          .btn-delete {
            background: #ef4444;
            color: white;
          }

          .btn-delete:hover {
            background: #dc2626;
          }

          .card-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
          }

          .card-actions .btn-edit,
          .card-actions .btn-delete {
            grid-column: span 1;
          }

          /* Modal Styles */
          .modal-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            background: rgba(0, 0, 0, 0.5) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            z-index: 9999 !important;
            padding: 20px !important;
          }

          .modal-content {
            background: white !important;
            border-radius: 12px !important;
            width: 100% !important;
            max-width: 800px !important;
            max-height: 80vh !important;
            overflow: auto !important;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
            z-index: 10000 !important;
            position: relative !important;
          }

          .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
          }

          .modal-header h2 {
            margin: 0;
            font-size: 1.25rem;
            color: #1e293b;
          }

          .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6b7280;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .modal-close:hover {
            color: #374151;
          }

          .modal-tabs {
            display: flex;
            border-bottom: 1px solid #e5e7eb;
            padding: 0 24px;
          }

          .tab-button {
            background: none;
            border: none;
            padding: 12px 16px;
            cursor: pointer;
            color: #6b7280;
            font-size: 0.875rem;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
          }

          .tab-button:hover {
            color: #374151;
          }

          .tab-button.active {
            color: #3b82f6;
            border-bottom-color: #3b82f6;
          }

          .modal-body {
            padding: 24px;
          }

          .tab-content h3 {
            margin: 0 0 16px 0;
            font-size: 1.125rem;
            color: #1e293b;
          }

          .detail-section {
            margin-bottom: 24px;
          }

          .detail-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
          }

          .detail-item {
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 12px;
            padding: 8px 0;
          }

          .detail-item label {
            font-weight: 500;
            color: #374151;
          }

          .detail-item span {
            color: #6b7280;
          }

          .modal-footer {
            padding: 20px 24px;
            border-top: 1px solid #e5e7eb;
            display: flex;
            justify-content: flex-end;
          }

          .btn-secondary {
            background: #6b7280;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
          }

          .btn-secondary:hover {
            background: #4b5563;
          }

          /* DBpedia Integration Styles */
          .dbpedia-section {
            padding: 16px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
          }

          .dbpedia-item {
            margin-bottom: 16px;
          }

          .dbpedia-item label {
            display: block;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 8px;
          }

          .term-text {
            font-size: 1rem;
            font-weight: 600;
            color: #1e293b;
            margin: 0;
          }

          .dbpedia-info {
            margin-top: 16px;
            padding: 12px;
            background: #eff6ff;
            border-radius: 6px;
            border-left: 3px solid #3b82f6;
          }

          .info-badge {
            font-size: 0.75rem;
            color: #1e40af;
            margin: 0;
            line-height: 1.4;
          }

          .dbpedia-error {
            padding: 16px;
            background: #fef2f2;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
          }

          .dbpedia-error p {
            margin: 0 0 8px 0;
            color: #dc2626;
          }

          .help-text {
            font-size: 0.875rem;
            color: #6b7280;
            margin: 0;
          }

          .no-dbpedia {
            text-align: center;
            padding: 40px 20px;
          }

          .no-dbpedia p {
            color: #64748b;
            margin-bottom: 16px;
          }

          .btn-enrich, .btn-enrich-inline {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: background 0.2s;
          }

          .btn-enrich:hover {
            background: #2563eb;
          }

          .btn-enrich-inline {
            padding: 4px 8px;
            margin-left: 8px;
            font-size: 0.75rem;
          }

          .btn-enrich-inline:hover {
            background: #1d4ed8;
          }

          .loading-state {
            text-align: center;
            padding: 40px 20px;
          }

          .loading-spinner-small {
            width: 24px;
            height: 24px;
            border: 3px solid #f1f5f9;
            border-left: 3px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
          }

          /* DBpedia Results List Styles */
          .dbpedia-results {
            margin-bottom: 24px;
          }

          .dbpedia-results h4 {
            margin: 0 0 16px 0;
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
          }

          .dbpedia-results-list {
            list-style: decimal;
            padding-left: 24px;
            margin: 0;
          }

          .dbpedia-result-item {
            margin-bottom: 16px;
            padding: 12px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            transition: box-shadow 0.2s;
          }

          .dbpedia-result-item:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }

          .dbpedia-result-content {
            display: flex;
            flex-direction: column;
            gap: 8px;
          }

          .dbpedia-result-title {
            font-size: 1rem;
            font-weight: 600;
            color: #1e293b;
            margin: 0;
          }

          .dbpedia-result-uri {
            font-size: 0.875rem;
            color: #3b82f6;
            text-decoration: none;
            word-break: break-all;
            transition: color 0.2s;
          }

          .dbpedia-result-uri:hover {
            color: #1e40af;
            text-decoration: underline;
          }

          .dbpedia-primary {
            margin-bottom: 24px;
            padding: 16px;
            background: #eff6ff;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
          }

          .dbpedia-primary h4 {
            margin: 0 0 12px 0;
            font-size: 1rem;
            font-weight: 600;
            color: #1e293b;
          }

          .dbpedia-uri-link {
            font-size: 0.875rem;
            color: #3b82f6;
            text-decoration: none;
            word-break: break-all;
            transition: color 0.2s;
          }

          .dbpedia-uri-link:hover {
            color: #1e40af;
            text-decoration: underline;
          }
        `}</style>

      {/* CRUD Modals */}
      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode !== 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode={modalState.mode}
        title={modalState.mode === 'add' ? 'Ajouter une personne' : 'Modifier une personne'}
        data={modalState.data}
        onSubmit={handleModalSubmit}
        fields={personneFields}
        loading={submitLoading}
      />

      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode === 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode="delete"
        title="Supprimer une personne"
        data={modalState.data}
        onSubmit={handleModalSubmit}
        loading={submitLoading}
      />

      {/* Details Modal with DBpedia */}
      {showDetailsModal && selectedPersonne && (
        <div 
          className="modal-overlay" 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '20px'
          }}
          onClick={() => {
            setShowDetailsModal(false);
            setSelectedPersonne(null);
            setDbpediaData(null);
            setActiveTab('info');
          }}
        >
          <div 
            className="modal-content" 
            style={{
              background: 'white',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '800px',
              maxHeight: '80vh',
              overflow: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
              zIndex: 10000,
              position: 'relative'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>{`${selectedPersonne.prenom || ''} ${selectedPersonne.nom || ''}`.trim() || 'Détails de la personne'}</h2>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedPersonne(null);
                  setDbpediaData(null);
                  setActiveTab('info');
                }}
              >
                ×
              </button>
            </div>

            <div className="modal-tabs">
              <button 
                className={`tab-button ${activeTab === 'info' ? 'active' : ''}`}
                onClick={() => setActiveTab('info')}
              >
                Informations
              </button>
              {dbpediaData && (
                <button 
                  className={`tab-button ${activeTab === 'dbpedia' ? 'active' : ''}`}
                  onClick={() => setActiveTab('dbpedia')}
                >
                  🌐 DBpedia Info
                </button>
              )}
            </div>

            <div className="modal-body">
              {activeTab === 'info' && selectedPersonne && (
                <div className="tab-content">
                  <div className="detail-section">
                    <h3>Informations générales</h3>
                    <div className="detail-grid">
                      {personneDetailsFields.map((field) => {
                        const value = selectedPersonne[field.name];
                        if (field.hideIfEmpty && !value) return null;
                        
                        return (
                          <div key={field.name} className="detail-item">
                            <label>{field.label}:</label>
                            <span>
                              {field.format ? field.format(value) : (value || 'Non spécifié')}
                              {value && typeof value === 'string' && value.length < 100 && (
                                <button 
                                  className="btn-enrich-inline"
                                  onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    fetchDBpediaEnrichment(selectedPersonne.personne, value);
                                  }}
                                  title={`Enrichir "${value.length > 50 ? value.substring(0, 50) + '...' : value}" avec DBpedia`}
                                >
                                  🌐
                                </button>
                              )}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'dbpedia' && (
                <div className="tab-content">
                  <h3>🌐 Informations DBpedia (Linked Data)</h3>
                  {loadingDBpedia ? (
                    <div className="loading-state">
                      <div className="loading-spinner-small"></div>
                      <p>Chargement des données DBpedia...</p>
                    </div>
                  ) : dbpediaData ? (
                    <div className="dbpedia-section">
                      {dbpediaData.error ? (
                        <div className="dbpedia-error">
                          <p>⚠️ {dbpediaData.error}</p>
                          <p className="help-text">Les données DBpedia ne sont pas disponibles pour "{dbpediaData.search_text || dbpediaData.term || 'ce terme'}".</p>
                        </div>
                      ) : (
                        <>
                          {dbpediaData.all_results && dbpediaData.all_results.length > 0 ? (
                            <div className="dbpedia-results">
                              <h4>🔍 Résultats DBpedia ({dbpediaData.all_results.length})</h4>
                              <ol className="dbpedia-results-list">
                                {dbpediaData.all_results.map((result, index) => (
                                  <li key={index} className="dbpedia-result-item">
                                    <div className="dbpedia-result-content">
                                      <strong className="dbpedia-result-title">{result.title}</strong>
                                      <a 
                                        href={result.uri} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="dbpedia-result-uri"
                                      >
                                        {result.uri}
                                      </a>
                                    </div>
                                  </li>
                                ))}
                              </ol>
                            </div>
                          ) : dbpediaData.results && dbpediaData.results.length > 0 ? (
                            <div className="dbpedia-results">
                              <h4>🔍 Résultats DBpedia ({dbpediaData.results.length})</h4>
                              <ol className="dbpedia-results-list">
                                {dbpediaData.results.map((result, index) => (
                                  <li key={index} className="dbpedia-result-item">
                                    <div className="dbpedia-result-content">
                                      <strong className="dbpedia-result-title">{result.title}</strong>
                                      <a 
                                        href={result.uri} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="dbpedia-result-uri"
                                      >
                                        {result.uri}
                                      </a>
                                    </div>
                                  </li>
                                ))}
                              </ol>
                            </div>
                          ) : null}
                          
                          {dbpediaData.title && dbpediaData.uri && (
                            <div className="dbpedia-primary">
                              <h4>📌 Résultat principal</h4>
                              <div className="dbpedia-item">
                                <label>🏷️ Titre:</label>
                                <p className="term-text">{dbpediaData.title}</p>
                              </div>
                              <div className="dbpedia-item">
                                <label>🔗 URI:</label>
                                <a 
                                  href={dbpediaData.uri} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="dbpedia-uri-link"
                                >
                                  {dbpediaData.uri}
                                </a>
                              </div>
                            </div>
                          )}
                          
                          <div className="dbpedia-info">
                            <p className="info-badge">
                              ℹ️ Ces données proviennent de DBpedia (Linked Data), démontrant l'interopérabilité du Web Sémantique.
                            </p>
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="no-dbpedia">
                      <p>Aucune donnée DBpedia disponible. Cliquez sur l'icône 🌐 à côté d'un champ pour enrichir ce terme.</p>
                      <button 
                        className="btn-enrich"
                        onClick={() => selectedPersonne && fetchDBpediaEnrichment(selectedPersonne.personne, `${selectedPersonne.prenom || ''} ${selectedPersonne.nom || ''}`.trim())}
                      >
                        🔄 Charger les données DBpedia pour "{selectedPersonne?.nom || 'cette personne'}"
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedPersonne(null);
                  setDbpediaData(null);
                  setActiveTab('info');
                }}
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Personnes;
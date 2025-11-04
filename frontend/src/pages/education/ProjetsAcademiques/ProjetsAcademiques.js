import React, { useState, useEffect } from 'react';
import { projetsAPI } from '../../../utils/api';
import CRUDModal from '../../../components/CRUDModal';

const ProjetsAcademiques = () => {
  const [projets, setProjets] = useState([]);
  const [filteredProjets, setFilteredProjets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    type: '',
    domaine: '',
    search: ''
  });

  // CRUD Modal states
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: null,
    data: {}
  });
  const [submitLoading, setSubmitLoading] = useState(false);
  
  // Details Modal state
  const [selectedProjet, setSelectedProjet] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [activeTab, setActiveTab] = useState('info');
  const [dbpediaData, setDbpediaData] = useState(null);
  const [loadingDBpedia, setLoadingDBpedia] = useState(false);

  const [stats, setStats] = useState({
    total: 0
  });

  // Facets state for dynamic filters
  const [facets, setFacets] = useState({
    by_type: [],
    by_domaine: [],
    by_universite: []
  });

  useEffect(() => {
    fetchProjets();
    fetchFacets();
  }, []);

  useEffect(() => {
    filterProjets();
  }, [projets, filters]);

  const fetchProjets = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await projetsAPI.getAll();
      if (response.data) {
        const uniqueProjets = removeDuplicates(response.data, 'projet');
        setProjets(uniqueProjets);
        calculateStats(uniqueProjets);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des projets:', error);
      setError('Erreur lors du chargement des projets');
    } finally {
      setLoading(false);
    }
  };

  const fetchFacets = async () => {
    try {
      const response = await projetsAPI.getFacets();
      if (response.data) {
        setFacets(response.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des facettes:', error);
    }
  };

  const calculateStats = (projetsData) => {
    setStats({ total: projetsData.length });
  };

  const filterProjets = () => {
    let filtered = projets;

    if (filters.type) {
      filtered = filtered.filter(projet => {
        const type = projet.typeProjet?.toLowerCase() || '';
        return type.includes(filters.type.toLowerCase());
      });
    }

    if (filters.domaine) {
      filtered = filtered.filter(projet => {
        const domaine = projet.domaineProjet?.toLowerCase() || '';
        return domaine.includes(filters.domaine.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(projet => {
        const titre = projet.titreProjet?.toLowerCase() || '';
        const domaine = projet.domaineProjet?.toLowerCase() || '';
        return titre.includes(filters.search.toLowerCase()) || 
               domaine.includes(filters.search.toLowerCase());
      });
    }

    setFilteredProjets(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      type: '',
      domaine: '',
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

  // CRUD Handlers
  const handleCreate = async (data) => {
    setSubmitLoading(true);
    try {
      await projetsAPI.create(data);
      await fetchProjets();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleUpdate = async (data) => {
    setSubmitLoading(true);
    try {
      await projetsAPI.update(data.projet, data);
      await fetchProjets();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDelete = async (data) => {
    setSubmitLoading(true);
    try {
      await projetsAPI.delete(data.projet);
      await fetchProjets();
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

  const projetFields = [
    { name: 'titreProjet', label: 'Titre du projet', type: 'text', required: true },
    { name: 'domaineProjet', label: 'Domaine', type: 'text' },
    { name: 'typeProjet', label: 'Type', type: 'text', placeholder: 'Recherche, Stage, etc.' },
    { name: 'noteProjet', label: 'Note', type: 'number', step: '0.1', min: '0', max: '20' }
  ];

  const showProjetDetails = async (projet) => {
    try {
      const response = await projetsAPI.getById(projet.projet);
      const details = Array.isArray(response.data) ? response.data[0] : response.data;
      // Merge API response with original projet data to ensure all fields are available
      const mergedData = { ...projet, ...details };
      setSelectedProjet(mergedData);
      setShowDetailsModal(true);
      setActiveTab('info');
      
      // Fetch DBpedia enrichment if university city is available
      if (mergedData.ville || projet.ville) {
        fetchDBpediaEnrichment(projet.projet);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      setSelectedProjet(projet);
      setShowDetailsModal(true);
      setActiveTab('info');
    }
  };

  const fetchDBpediaEnrichment = async (projetId) => {
    try {
      setLoadingDBpedia(true);
      const response = await projetsAPI.enrichWithDBpedia(projetId);
      if (response.data) {
        if (response.data.dbpedia_enrichment) {
          setDbpediaData(response.data.dbpedia_enrichment);
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

  const projetDetailsFields = [
    { name: 'titreProjet', label: 'Titre du projet' },
    { name: 'domaineProjet', label: 'Domaine' },
    { name: 'typeProjet', label: 'Type' },
    { name: 'noteProjet', label: 'Note' }
  ];

  if (loading) return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Chargement des projets...</p>
    </div>
  );

  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h3>Erreur de chargement</h3>
      <p>{error}</p>
      <button className="btn-retry" onClick={fetchProjets}>
        Réessayer
      </button>
    </div>
  );

  return (
    <div className="projets-container">
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-title">Gestion des Projets Académiques</h1>
          <p className="page-subtitle">
            Gérez et consultez les projets académiques
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
            ➕ Ajouter
          </button>
          <button className="btn-refresh" onClick={fetchProjets} title="Actualiser">
            🔄
          </button>
        </div>
      </header>

      {/* Statistics Cards */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">🔬</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.total}</h3>
              <p className="stat-label">Total Projets</p>
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
              {filteredProjets.length} résultat(s)
            </span>
            <button className="btn-clear-filters" onClick={clearFilters}>
              Effacer tout
            </button>
          </div>
        </div>

        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Type</label>
            <select 
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className="filter-select"
            >
              <option value="">Tous les types</option>
              {facets.by_type && facets.by_type.map((facet, index) => (
                <option key={index} value={facet.typeProjet || ''}>
                  {facet.typeProjet || 'Non spécifié'} ({facet.count || 0})
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Domaine</label>
            <select 
              value={filters.domaine || ''} 
              onChange={(e) => handleFilterChange('domaine', e.target.value)}
              className="filter-select"
            >
              <option value="">Tous les domaines</option>
              {facets.by_domaine && facets.by_domaine.map((facet, index) => (
                <option key={index} value={facet.domaineProjet || ''}>
                  {facet.domaineProjet || 'Non spécifié'} ({facet.count || 0})
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
                placeholder="Titre, domaine..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Projets Grid */}
      <section className="projets-grid-section">
        {filteredProjets.length > 0 ? (
          <div className="projets-grid">
            {filteredProjets.map((projet, index) => (
              <div key={index} className="projet-card">
                <div className="card-header">
                  <h3 className="projet-title">{projet.titreProjet || 'Sans titre'}</h3>
                </div>

                <div className="card-content">
                  <div className="info-grid">
                    {projet.domaineProjet && (
                      <div className="info-item">
                        <span className="info-icon">📁</span>
                        <span className="info-text">{projet.domaineProjet}</span>
                      </div>
                    )}
                    {projet.typeProjet && (
                      <div className="info-item">
                        <span className="info-icon">🏷️</span>
                        <span className="info-text">{projet.typeProjet}</span>
                      </div>
                    )}
                    {projet.noteProjet && (
                      <div className="info-item">
                        <span className="info-icon">⭐</span>
                        <span className="info-text">Note: {projet.noteProjet}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="card-actions">
                  <button className="btn-primary" onClick={() => showProjetDetails(projet)}>
                    👁️ Détails
                  </button>
                  <button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: projet })}>
                    ✏️
                  </button>
                  <button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: projet })}>
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🔬</div>
            <h3>Aucun projet trouvé</h3>
            <p>Essayez de modifier vos filtres de recherche</p>
          </div>
        )}
      </section>

      <style>{`
        .projets-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
          background: #f8fafc;
          min-height: 100vh;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
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

        .btn-refresh, .btn-add {
          background: #f1f5f9;
          border: none;
          border-radius: 8px;
          padding: 8px;
          cursor: pointer;
          font-size: 1.2rem;
          transition: background 0.2s;
        }

        .btn-add {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 10px 20px;
          font-size: 0.95rem;
          font-weight: 500;
        }

        .btn-add:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

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
        }

        .stat-icon {
          font-size: 2rem;
          padding: 12px;
          border-radius: 8px;
          background: #dbeafe;
        }

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

        .filters-section {
          background: white;
          padding: 24px;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin-bottom: 32px;
        }

        .filters-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
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
          font-weight: 500;
          color: #374151;
        }

        .filter-input, .search-input {
          padding: 10px;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 0.95rem;
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
        }

        .projets-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }

        .projet-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .projet-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .card-header {
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .projet-title {
          font-size: 1.25rem;
          font-weight: 600;
          margin: 0;
        }

        .card-content {
          padding: 20px;
        }

        .info-grid {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .info-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .info-icon {
          font-size: 1.2rem;
        }

        .card-actions {
          padding: 0 20px 20px;
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 8px;
        }

        .btn-primary, .btn-edit, .btn-delete {
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

        .loading-container, .error-container {
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
          margin: 0;
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
        title={modalState.mode === 'add' ? 'Ajouter un projet' : 'Modifier un projet'}
        data={modalState.data}
        onSubmit={handleModalSubmit}
        fields={projetFields}
        loading={submitLoading}
      />

      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode === 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode="delete"
        title="Supprimer un projet"
        data={modalState.data}
        onSubmit={handleModalSubmit}
        loading={submitLoading}
      />

      {/* Details Modal with DBpedia */}
      {showDetailsModal && selectedProjet && (
        <div className="modal-overlay" onClick={() => {
          setShowDetailsModal(false);
          setSelectedProjet(null);
          setDbpediaData(null);
          setActiveTab('info');
        }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedProjet.titreProjet}</h2>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedProjet(null);
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
              {activeTab === 'info' && selectedProjet && (
                <div className="tab-content">
                  <div className="detail-section">
                    <h3>Informations générales</h3>
                    <div className="detail-grid">
                      {projetDetailsFields.map((field) => {
                        const value = selectedProjet[field.name];
                        if (field.hideIfEmpty && !value) return null;
                        
                        return (
                          <div key={field.name} className="detail-item">
                            <label>{field.label}:</label>
                            <span>
                              {value || 'Non spécifié'}
                              {(selectedProjet.ville || selectedProjet.nomUniversite) && (
                                <button 
                                  className="btn-enrich-inline"
                                  onClick={() => fetchDBpediaEnrichment(selectedProjet.projet)}
                                  title="Enrichir avec DBpedia"
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
                          {/* Display list of DBpedia references */}
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
                          
                          {/* Display primary result (first result) */}
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
                          
                          {/* Legacy fields for backward compatibility */}
                          {dbpediaData.abstract && (
                            <div className="dbpedia-item">
                              <label>📖 Description:</label>
                              <p className="abstract-text">
                                {typeof dbpediaData.abstract === 'string' 
                                  ? dbpediaData.abstract 
                                  : (dbpediaData.abstract.value || dbpediaData.abstract)}
                              </p>
                            </div>
                          )}
                          <div className="dbpedia-grid">
                            {dbpediaData.population && (
                              <div className="dbpedia-stat">
                                <label>👥 Population:</label>
                                <span>
                                  {typeof dbpediaData.population === 'string'
                                    ? parseInt(dbpediaData.population).toLocaleString('fr-FR')
                                    : parseInt(dbpediaData.population.value || dbpediaData.population).toLocaleString('fr-FR')}
                                </span>
                              </div>
                            )}
                            {dbpediaData.country && (
                              <div className="dbpedia-stat">
                                <label>🌍 Pays:</label>
                                <span>
                                  {typeof dbpediaData.country === 'string'
                                    ? dbpediaData.country
                                    : (dbpediaData.country.value || dbpediaData.country)}
                                </span>
                              </div>
                            )}
                            {dbpediaData.latitude && dbpediaData.longitude && (
                              <div className="dbpedia-stat">
                                <label>📍 Coordonnées:</label>
                                <span>
                                  {typeof dbpediaData.latitude === 'string'
                                    ? `${parseFloat(dbpediaData.latitude).toFixed(4)}, ${parseFloat(dbpediaData.longitude).toFixed(4)}`
                                    : `${parseFloat(dbpediaData.latitude.value || dbpediaData.latitude).toFixed(4)}, ${parseFloat(dbpediaData.longitude.value || dbpediaData.longitude).toFixed(4)}`}
                                </span>
                                <a 
                                  href={`https://www.openstreetmap.org/?mlat=${
                                    typeof dbpediaData.latitude === 'string' 
                                      ? dbpediaData.latitude 
                                      : (dbpediaData.latitude.value || dbpediaData.latitude)
                                  }&mlon=${
                                    typeof dbpediaData.longitude === 'string'
                                      ? dbpediaData.longitude
                                      : (dbpediaData.longitude.value || dbpediaData.longitude)
                                  }&zoom=12`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="map-link"
                                >
                                  🗺️ Voir sur la carte
                                </a>
                              </div>
                            )}
                          </div>
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
                      <p>Aucune donnée DBpedia disponible pour ce projet.</p>
                      <button 
                        className="btn-enrich"
                        onClick={() => selectedProjet && fetchDBpediaEnrichment(selectedProjet.projet)}
                      >
                        🔄 Charger les données DBpedia
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
          setSelectedProjet(null);
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

export default ProjetsAcademiques;

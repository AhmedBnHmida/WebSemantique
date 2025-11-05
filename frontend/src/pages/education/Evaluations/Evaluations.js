import React, { useState, useEffect } from 'react';
import { evaluationsAPI } from '../../../utils/api';
import CRUDModal from '../../../components/CRUDModal';

const Evaluations = () => {
  const [evaluations, setEvaluations] = useState([]);
  const [filteredEvaluations, setFilteredEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    type: '',
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
  const [selectedEvaluation, setSelectedEvaluation] = useState(null);
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
    by_cours: [],
    by_competence: []
  });

  useEffect(() => {
    fetchEvaluations();
    fetchFacets();
  }, []);

  useEffect(() => {
    filterEvaluations();
  }, [evaluations, filters]);

  const fetchEvaluations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await evaluationsAPI.getAll();
      if (response.data) {
        const uniqueEvaluations = removeDuplicates(response.data, 'evaluation');
        setEvaluations(uniqueEvaluations);
        calculateStats(uniqueEvaluations);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des évaluations:', error);
      setError('Erreur lors du chargement des évaluations');
    } finally {
      setLoading(false);
    }
  };

  const fetchFacets = async () => {
    try {
      const response = await evaluationsAPI.getFacets();
      if (response.data) {
        setFacets(response.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des facettes:', error);
    }
  };

  const calculateStats = (evaluationsData) => {
    setStats({ total: evaluationsData.length });
  };

  const filterEvaluations = () => {
    let filtered = evaluations;

    if (filters.type) {
      filtered = filtered.filter(evaluation => {
        const type = evaluation.typeEvaluation?.toLowerCase() || '';
        return type.includes(filters.type.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(evaluation => {
        const type = evaluation.typeEvaluation?.toLowerCase() || '';
        return type.includes(filters.search.toLowerCase());
      });
    }

    setFilteredEvaluations(filtered);
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
      await evaluationsAPI.create(data);
      await fetchEvaluations();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleUpdate = async (data) => {
    setSubmitLoading(true);
    try {
      await evaluationsAPI.update(data.evaluation, data);
      await fetchEvaluations();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDelete = async (data) => {
    setSubmitLoading(true);
    try {
      await evaluationsAPI.delete(data.evaluation);
      await fetchEvaluations();
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

  const evaluationFields = [
    { name: 'typeEvaluation', label: 'Type d\'évaluation', type: 'text', required: true, placeholder: 'Contrôle continu, Examen, etc.' },
    { name: 'dateEvaluation', label: 'Date', type: 'date' }
  ];

  const showEvaluationDetails = async (evaluation) => {
    try {
      const response = await evaluationsAPI.getById(evaluation.evaluation);
      const details = Array.isArray(response.data) ? response.data[0] : response.data;
      // Merge API response with original evaluation data to ensure all fields are available
      const mergedData = { ...evaluation, ...details };
      setSelectedEvaluation(mergedData);
      setShowDetailsModal(true);
      setActiveTab('info');
      setDbpediaData(null);
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      setSelectedEvaluation(evaluation);
      setShowDetailsModal(true);
      setActiveTab('info');
      setDbpediaData(null);
    }
  };

  const fetchDBpediaEnrichment = async (evaluationId, term = null) => {
    try {
      setLoadingDBpedia(true);
      setDbpediaData(null);
      const response = await evaluationsAPI.enrichWithDBpedia(evaluationId, term);
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

  const evaluationDetailsFields = [
    { name: 'typeEvaluation', label: 'Type d\'évaluation' },
    { name: 'dateEvaluation', label: 'Date', format: (val) => val ? new Date(val).toLocaleDateString('fr-FR') : null }
  ];

  if (loading) return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Chargement des évaluations...</p>
    </div>
  );

  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h3>Erreur de chargement</h3>
      <p>{error}</p>
      <button className="btn-retry" onClick={fetchEvaluations}>
        Réessayer
      </button>
    </div>
  );

  return (
    <div className="evaluations-container">
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-title">Gestion des Évaluations</h1>
          <p className="page-subtitle">
            Gérez et consultez les évaluations
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
            ➕ Ajouter
          </button>
          <button className="btn-refresh" onClick={fetchEvaluations} title="Actualiser">
            🔄
          </button>
        </div>
      </header>

      {/* Statistics Cards */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">📝</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.total}</h3>
              <p className="stat-label">Total Évaluations</p>
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
              {filteredEvaluations.length} résultat(s)
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
                <option key={index} value={facet.typeEvaluation || ''}>
                  {facet.typeEvaluation || 'Non spécifié'} ({facet.count || 0})
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
                placeholder="Type..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Evaluations Grid */}
      <section className="evaluations-grid-section">
        {filteredEvaluations.length > 0 ? (
          <div className="evaluations-grid">
            {filteredEvaluations.map((evaluation, index) => (
              <div key={index} className="evaluation-card">
                <div className="card-header">
                  <h3 className="evaluation-title">{evaluation.typeEvaluation || 'Sans type'}</h3>
                </div>

                <div className="card-content">
                  <div className="info-grid">
                    {evaluation.dateEvaluation && (
                      <div className="info-item">
                        <span className="info-icon">📅</span>
                        <span className="info-text">{new Date(evaluation.dateEvaluation).toLocaleDateString('fr-FR')}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="card-actions">
                  <button className="btn-primary" onClick={() => showEvaluationDetails(evaluation)}>
                    👁️ Détails
                  </button>
                  <button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: evaluation })}>
                    ✏️
                  </button>
                  <button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: evaluation })}>
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📝</div>
            <h3>Aucune évaluation trouvée</h3>
            <p>Essayez de modifier vos filtres de recherche</p>
          </div>
        )}
      </section>

      <style>{`
        .evaluations-container {
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

        .evaluations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }

        .evaluation-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .evaluation-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .card-header {
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .evaluation-title {
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
        title={modalState.mode === 'add' ? 'Ajouter une évaluation' : 'Modifier une évaluation'}
        data={modalState.data}
        onSubmit={handleModalSubmit}
        fields={evaluationFields}
        loading={submitLoading}
      />

      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode === 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode="delete"
        title="Supprimer une évaluation"
        data={modalState.data}
        onSubmit={handleModalSubmit}
        loading={submitLoading}
      />

      {/* Details Modal with DBpedia */}
      {showDetailsModal && selectedEvaluation && (
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
          setSelectedEvaluation(null);
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
              <h2>{selectedEvaluation.typeEvaluation || 'Détails de l\'évaluation'}</h2>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedEvaluation(null);
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
              {activeTab === 'info' && selectedEvaluation && (
                <div className="tab-content">
                  <div className="detail-section">
                    <h3>Informations générales</h3>
                    <div className="detail-grid">
                      {evaluationDetailsFields.map((field) => {
                        const value = selectedEvaluation[field.name];
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
                                    fetchDBpediaEnrichment(selectedEvaluation.evaluation, value);
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
                        onClick={() => selectedEvaluation && fetchDBpediaEnrichment(selectedEvaluation.evaluation, selectedEvaluation.typeEvaluation)}
                      >
                        🔄 Charger les données DBpedia pour "{selectedEvaluation?.typeEvaluation || 'cette évaluation'}"
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
                  setSelectedEvaluation(null);
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

export default Evaluations;

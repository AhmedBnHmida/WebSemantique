import React, { useState, useEffect } from 'react';
import { evaluationsAPI } from '../../../utils/api';
import CRUDModal from '../../../components/CRUDModal';
import DetailsModal from '../../../components/DetailsModal';

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
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      setSelectedEvaluation(evaluation);
      setShowDetailsModal(true);
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

      {/* Details Modal */}
      <DetailsModal
        isOpen={showDetailsModal}
        onClose={() => {
          setShowDetailsModal(false);
          setSelectedEvaluation(null);
        }}
        title={selectedEvaluation ? selectedEvaluation.typeEvaluation || 'Détails de l\'évaluation' : 'Détails'}
        data={selectedEvaluation}
        fields={evaluationDetailsFields}
      />
    </div>
  );
};

export default Evaluations;

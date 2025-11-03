import React, { useState, useEffect } from 'react';
import { specialitesAPI } from '../../../utils/api';
import CRUDModal from '../../../components/CRUDModal';
import DetailsModal from '../../../components/DetailsModal';

const Specialites = () => {
  const [specialites, setSpecialites] = useState([]);
  const [filteredSpecialites, setFilteredSpecialites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    domaine: '',
    universite: '',
    niveau: '',
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
  const [selectedSpecialite, setSelectedSpecialite] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const [stats, setStats] = useState({
    total: 0,
    parDomaine: {},
    parUniversite: {},
    parNiveau: {}
  });

  // Helper functions
  const getDomaineFromSpecialite = (nomSpecialite) => {
    if (!nomSpecialite) return 'Autre';
    
    const nomLower = nomSpecialite.toLowerCase();
    if (nomLower.includes('informatique') || nomLower.includes('data') || nomLower.includes('ia')) {
      return 'Informatique';
    } else if (nomLower.includes('ingénieur') || nomLower.includes('génie')) {
      return 'Ingénierie';
    } else if (nomLower.includes('science') || nomLower.includes('physique') || nomLower.includes('chimie')) {
      return 'Sciences';
    } else if (nomLower.includes('médecine') || nomLower.includes('santé')) {
      return 'Médecine';
    } else if (nomLower.includes('économie') || nomLower.includes('gestion')) {
      return 'Économie';
    } else if (nomLower.includes('droit') || nomLower.includes('juridique')) {
      return 'Droit';
    } else if (nomLower.includes('lettre') || nomLower.includes('langue') || nomLower.includes('littérature')) {
      return 'Lettres';
    } else {
      return 'Autre';
    }
  };

  const getDomaineIcon = (domaine) => {
    switch(domaine) {
      case 'Informatique': return '💻';
      case 'Ingénierie': return '⚙️';
      case 'Sciences': return '🔬';
      case 'Médecine': return '🏥';
      case 'Économie': return '📈';
      case 'Droit': return '⚖️';
      case 'Lettres': return '📚';
      default: return '🎓';
    }
  };

  const getDomaineBadge = (nomSpecialite) => {
    const domaine = getDomaineFromSpecialite(nomSpecialite);
    
    switch(domaine) {
      case 'Informatique': return 'informatique';
      case 'Ingénierie': return 'ingenierie';
      case 'Sciences': return 'sciences';
      case 'Médecine': return 'medecine';
      case 'Économie': return 'economie';
      case 'Droit': return 'droit';
      case 'Lettres': return 'lettres';
      default: return 'autre';
    }
  };

  const formatDuree = (duree) => {
    if (!duree) return 'Non spécifié';
    return `${duree} an${duree > 1 ? 's' : ''}`;
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

  useEffect(() => {
    fetchSpecialites();
  }, []);

  useEffect(() => {
    filterSpecialites();
  }, [specialites, filters]);

  const fetchSpecialites = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await specialitesAPI.getAll();
      
      if (response.data) {
        const uniqueSpecialites = removeDuplicates(response.data, 'specialite');
        setSpecialites(uniqueSpecialites);
        calculateStats(uniqueSpecialites);
      } else {
        setError('Structure de données inattendue');
      }
    } catch (error) {
      console.error('Erreur lors du chargement des spécialités:', error);
      setError('Erreur lors du chargement des spécialités');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (specialitesData) => {
    const stats = {
      total: specialitesData.length,
      parDomaine: {},
      parUniversite: {},
      parNiveau: {}
    };

    specialitesData.forEach(specialite => {
      const domaine = getDomaineFromSpecialite(specialite.nomSpecialite);
      const universite = specialite.nomUniversite || 'Non affiliée';
      const niveau = specialite.niveauDiplome || 'Non spécifié';

      // Compter par domaine
      stats.parDomaine[domaine] = (stats.parDomaine[domaine] || 0) + 1;

      // Compter par université
      stats.parUniversite[universite] = (stats.parUniversite[universite] || 0) + 1;

      // Compter par niveau
      stats.parNiveau[niveau] = (stats.parNiveau[niveau] || 0) + 1;
    });

    setStats(stats);
  };

  const filterSpecialites = () => {
    let filtered = specialites;

    if (filters.domaine) {
      filtered = filtered.filter(specialite => {
        const domaine = getDomaineFromSpecialite(specialite.nomSpecialite);
        return domaine.toLowerCase().includes(filters.domaine.toLowerCase());
      });
    }

    if (filters.universite) {
      filtered = filtered.filter(specialite => {
        const universite = specialite.nomUniversite?.toLowerCase() || '';
        return universite.includes(filters.universite.toLowerCase());
      });
    }

    if (filters.niveau) {
      filtered = filtered.filter(specialite => {
        const niveau = specialite.niveauDiplome?.toLowerCase() || '';
        return niveau.includes(filters.niveau.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(specialite => {
        const nom = specialite.nomSpecialite?.toLowerCase() || '';
        const description = specialite.description?.toLowerCase() || '';
        const code = specialite.codeSpecialite?.toLowerCase() || '';
        return nom.includes(filters.search.toLowerCase()) || 
               description.includes(filters.search.toLowerCase()) ||
               code.includes(filters.search.toLowerCase());
      });
    }

    setFilteredSpecialites(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      domaine: '',
      universite: '',
      niveau: '',
      search: ''
    });
  };

  // CRUD Handlers
  const handleCreate = async (data) => {
    setSubmitLoading(true);
    try {
      await specialitesAPI.create(data);
      await fetchSpecialites();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleUpdate = async (data) => {
    setSubmitLoading(true);
    try {
      await specialitesAPI.update(data.specialite, data);
      await fetchSpecialites();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDelete = async (data) => {
    setSubmitLoading(true);
    try {
      await specialitesAPI.delete(data.specialite);
      await fetchSpecialites();
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

  const specialiteFields = [
    { name: 'nomSpecialite', label: 'Nom de la spécialité', type: 'text', required: true },
    { name: 'codeSpecialite', label: 'Code spécialité', type: 'text' },
    { name: 'description', label: 'Description', type: 'textarea', rows: 4 },
    { name: 'dureeFormation', label: 'Durée de formation', type: 'text', placeholder: 'Ex: 3 ans' },
    { name: 'niveauDiplome', label: 'Niveau diplôme', type: 'select', options: [
      { value: 'Licence', label: 'Licence' },
      { value: 'Master', label: 'Master' },
      { value: 'Doctorat', label: 'Doctorat' }
    ] },
    { name: 'nombreModules', label: 'Nombre de modules', type: 'number', min: '0' }
  ];

  const showSpecialiteDetails = async (specialite) => {
    try {
      const response = await specialitesAPI.getById(specialite.specialite);
      const details = Array.isArray(response.data) ? response.data[0] : response.data;
      setSelectedSpecialite(details || specialite);
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      setSelectedSpecialite(specialite);
      setShowDetailsModal(true);
    }
  };

  const specialiteDetailsFields = [
    { name: 'nomSpecialite', label: 'Nom de la spécialité' },
    { name: 'codeSpecialite', label: 'Code spécialité' },
    { name: 'description', label: 'Description' },
    { name: 'dureeFormation', label: 'Durée de formation' },
    { name: 'niveauDiplome', label: 'Niveau diplôme' },
    { name: 'nombreModules', label: 'Nombre de modules' },
    { name: 'nomUniversite', label: 'Université' }
  ];

  if (loading) return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Chargement des spécialités...</p>
    </div>
  );

  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h3>Erreur de chargement</h3>
      <p>{error}</p>
      <button className="btn-retry" onClick={fetchSpecialites}>
        Réessayer
      </button>
    </div>
  );

  return (
    <div className="specialites-container">
      {/* Header Section */}
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-title">Gestion des Spécialités</h1>
          <p className="page-subtitle">
            Explorez et gérez les spécialités académiques et leurs programmes
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
            ➕ Ajouter
          </button>
          <button className="btn-refresh" onClick={fetchSpecialites} title="Actualiser">
            🔄
          </button>
        </div>
      </header>

      {/* Statistics Cards */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">🎯</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.total}</h3>
              <p className="stat-label">Total Spécialités</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon informatique">💻</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.parDomaine.Informatique || 0}</h3>
              <p className="stat-label">Informatique</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon ingenierie">⚙️</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.parDomaine.Ingénierie || 0}</h3>
              <p className="stat-label">Ingénierie</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon sciences">🔬</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.parDomaine.Sciences || 0}</h3>
              <p className="stat-label">Sciences</p>
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
              {filteredSpecialites.length} spécialité(s) trouvée(s)
            </span>
            <button className="btn-clear-filters" onClick={clearFilters}>
              Effacer tout
            </button>
          </div>
        </div>

        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Domaine</label>
            <select 
              value={filters.domaine} 
              onChange={(e) => handleFilterChange('domaine', e.target.value)}
              className="filter-select"
            >
              <option value="">Tous les domaines</option>
              <option value="informatique">Informatique</option>
              <option value="ingénierie">Ingénierie</option>
              <option value="sciences">Sciences</option>
              <option value="médecine">Médecine</option>
              <option value="économie">Économie</option>
              <option value="droit">Droit</option>
              <option value="lettres">Lettres</option>
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
              <option value="Hassan II">Université Hassan II</option>
              <option value="Rabat">Université de Rabat</option>
              <option value="Marrakech">Université de Marrakech</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Niveau</label>
            <select 
              value={filters.niveau} 
              onChange={(e) => handleFilterChange('niveau', e.target.value)}
              className="filter-select"
            >
              <option value="">Tous les niveaux</option>
              <option value="licence">Licence</option>
              <option value="master">Master</option>
              <option value="doctorat">Doctorat</option>
              <option value="ingénieur">Ingénieur</option>
            </select>
          </div>

          <div className="filter-group search-group">
            <label className="filter-label">Recherche</label>
            <div className="search-input-container">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Nom, description, code..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Specialties Grid */}
      <section className="specialites-grid-section">
        {filteredSpecialites.length > 0 ? (
          <div className="specialites-grid">
            {filteredSpecialites.map((specialite, index) => (
              <div key={index} className="specialite-card">
                <div className="card-header">
                  <div className="specialite-icon">
                    {getDomaineIcon(getDomaineFromSpecialite(specialite.nomSpecialite))}
                  </div>
                  <div className="specialite-info">
                    <h3 className="specialite-name">
                      {specialite.nomSpecialite}
                    </h3>
                    <span className={`domaine-badge ${getDomaineBadge(specialite.nomSpecialite)}`}>
                      {getDomaineFromSpecialite(specialite.nomSpecialite)}
                    </span>
                  </div>
                </div>

                <div className="card-content">
                  <div className="info-grid">
                    {specialite.codeSpecialite && (
                      <div className="info-item">
                        <span className="info-icon">🏷️</span>
                        <span className="info-text">Code: {specialite.codeSpecialite}</span>
                      </div>
                    )}
                    
                    {specialite.nomUniversite && (
                      <div className="info-item">
                        <span className="info-icon">🏫</span>
                        <span className="info-text">{specialite.nomUniversite}</span>
                      </div>
                    )}
                    
                    {specialite.niveauDiplome && (
                      <div className="info-item">
                        <span className="info-icon">📊</span>
                        <span className="info-text">Niveau: {specialite.niveauDiplome}</span>
                      </div>
                    )}
                    
                    {specialite.dureeFormation && (
                      <div className="info-item">
                        <span className="info-icon">⏱️</span>
                        <span className="info-text">Durée: {formatDuree(specialite.dureeFormation)}</span>
                      </div>
                    )}
                  </div>

                  {specialite.description && (
                    <div className="description-section">
                      <h4>Description</h4>
                      <p className="description-text">{specialite.description}</p>
                    </div>
                  )}

                  {/* Modules information */}
                  {specialite.nombreModules && (
                    <div className="modules-info">
                      <div className="modules-stats">
                        <span className="module-count">
                          {specialite.nombreModules} module(s)
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="card-actions">
                  <button 
                    className="btn-secondary"
                    onClick={() => {
                      console.log('Voir les cours de:', specialite.specialite);
                    }}
                  >
                    📚 Voir les cours
                  </button>
                  <button 
                    className="btn-primary"
                    onClick={() => showSpecialiteDetails(specialite)}
                  >
                    👁️ Détails
                  </button>
                  <button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: specialite })}>
                    ✏️
                  </button>
                  <button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: specialite })}>
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🎓</div>
            <h3>Aucune spécialité trouvée</h3>
            <p>Aucun résultat ne correspond à vos critères de recherche</p>
            <button className="btn-clear-filters" onClick={clearFilters}>
              Effacer les filtres
            </button>
          </div>
        )}
      </section>

      <style jsx>{`
        .specialites-container {
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
        .stat-icon.informatique { background: #dcfce7; }
        .stat-icon.ingenierie { background: #fef3c7; }
        .stat-icon.sciences { background: #f3e8ff; }

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

        /* Specialties Grid Styles */
        .specialites-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
          gap: 24px;
        }

        .specialite-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .specialite-card:hover {
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

        .specialite-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 1.2rem;
        }

        .specialite-info {
          flex: 1;
        }

        .specialite-name {
          margin: 0 0 4px 0;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .domaine-badge {
          padding: 4px 8px;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .domaine-badge.informatique { background: #10b981; }
        .domaine-badge.ingenierie { background: #f59e0b; }
        .domaine-badge.sciences { background: #8b5cf6; }
        .domaine-badge.medecine { background: #ef4444; }
        .domaine-badge.economie { background: #06b6d4; }
        .domaine-badge.droit { background: #84cc16; }
        .domaine-badge.lettres { background: #f97316; }
        .domaine-badge.autre { background: #6b7280; }

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

        .description-section {
          margin-bottom: 16px;
        }

        .description-section h4 {
          margin: 0 0 8px 0;
          font-size: 0.875rem;
          font-weight: 600;
          color: #1e293b;
        }

        .description-text {
          font-size: 0.875rem;
          color: #64748b;
          line-height: 1.4;
        }

        .modules-info {
          padding: 12px;
          background: #f8fafc;
          border-radius: 8px;
          margin-bottom: 12px;
        }

        .modules-stats {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .module-count {
          font-size: 0.875rem;
          color: #64748b;
          font-weight: 500;
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
          .specialites-container {
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

          .specialites-grid {
            grid-template-columns: 1fr;
          }

          .card-actions {
            flex-direction: column;
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
        }
      `}</style>

      {/* CRUD Modals */}
      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode !== 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode={modalState.mode}
        title={modalState.mode === 'add' ? 'Ajouter une spécialité' : 'Modifier une spécialité'}
        data={modalState.data}
        onSubmit={handleModalSubmit}
        fields={specialiteFields}
        loading={submitLoading}
      />

      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode === 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode="delete"
        title="Supprimer une spécialité"
        data={modalState.data}
        onSubmit={handleModalSubmit}
        loading={submitLoading}
      />

      {/* Details Modal */}
      <DetailsModal
        isOpen={showDetailsModal}
        onClose={() => {
          setShowDetailsModal(false);
          setSelectedSpecialite(null);
        }}
        title={selectedSpecialite ? selectedSpecialite.nomSpecialite || 'Détails de la spécialité' : 'Détails'}
        data={selectedSpecialite}
        fields={specialiteDetailsFields}
      />
    </div>
  );
};

export default Specialites;
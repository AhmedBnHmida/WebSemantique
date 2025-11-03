import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { universitesAPI, specialitesAPI } from '../../../utils/api';
import CRUDModal from '../../../components/CRUDModal';

const Universites = () => {
  const [universites, setUniversites] = useState([]);
  const [filteredUniversites, setFilteredUniversites] = useState([]);
  const [specialites, setSpecialites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    type: '',
    ville: '',
    pays: '',
    search: ''
  });

  const [stats, setStats] = useState({
    total: 0,
    publiques: 0,
    privees: 0,
    totalEtudiants: 0,
    totalEnseignants: 0,
    byVille: {}
  });

  const [selectedUniversite, setSelectedUniversite] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [activeTab, setActiveTab] = useState('info');
  
  // CRUD Modal states
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: null,
    data: {}
  });
  const [submitLoading, setSubmitLoading] = useState(false);

  useEffect(() => {
    fetchUniversites();
    fetchSpecialites();
  }, []);

  useEffect(() => {
    filterUniversites();
  }, [universites, filters]);

  const fetchUniversites = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await universitesAPI.getAll();
      
      if (response.data) {
        const uniqueUniversites = removeDuplicates(response.data, 'universite');
        setUniversites(uniqueUniversites);
        calculateStats(uniqueUniversites);
      } else {
        setError('Structure de données inattendue');
      }
    } catch (error) {
      console.error('Erreur lors du chargement des universités:', error);
      setError('Erreur lors du chargement des universités');
    } finally {
      setLoading(false);
    }
  };

  const fetchSpecialites = async () => {
    try {
      const response = await specialitesAPI.getAll();
      if (response.data) {
        setSpecialites(response.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des spécialités:', error);
    }
  };

  const calculateStats = (universitesData) => {
    const stats = {
      total: universitesData.length,
      publiques: 0,
      privees: 0,
      totalEtudiants: 0,
      totalEnseignants: 0,
      byVille: {}
    };

    universitesData.forEach(universite => {
      const type = universite.typeUniversite?.toLowerCase() || '';
      const ville = universite.ville || 'Non spécifié';
      const nbEtudiants = parseInt(universite.nombreEtudiants) || 0;

      if (type.includes('publique')) {
        stats.publiques++;
      } else if (type.includes('privée')) {
        stats.privees++;
      }

      stats.totalEtudiants += nbEtudiants;
      stats.byVille[ville] = (stats.byVille[ville] || 0) + 1;
    });

    setStats(stats);
  };

  const filterUniversites = () => {
    let filtered = universites;

    if (filters.type) {
      filtered = filtered.filter(universite => {
        const type = universite.typeUniversite?.toLowerCase() || '';
        return type.includes(filters.type.toLowerCase());
      });
    }

    if (filters.ville) {
      filtered = filtered.filter(universite => {
        const ville = universite.ville?.toLowerCase() || '';
        return ville.includes(filters.ville.toLowerCase());
      });
    }

    if (filters.pays) {
      filtered = filtered.filter(universite => {
        const pays = universite.pays?.toLowerCase() || '';
        return pays.includes(filters.pays.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(universite => {
        const nom = universite.nomUniversite?.toLowerCase() || '';
        const siteWeb = universite.siteWeb?.toLowerCase() || '';
        return nom.includes(filters.search.toLowerCase()) || 
               siteWeb.includes(filters.search.toLowerCase());
      });
    }

    setFilteredUniversites(filtered);
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
      ville: '',
      pays: '',
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

  const getTypeBadge = (type) => {
    if (!type) return 'unknown';
    
    const typeLower = type.toLowerCase();
    if (typeLower.includes('publique')) {
      return 'publique';
    } else if (typeLower.includes('privée')) {
      return 'privee';
    } else {
      return 'autre';
    }
  };

  const formatNombre = (nombre) => {
    if (!nombre) return '0';
    return parseInt(nombre).toLocaleString('fr-FR');
  };

  // CRUD Handlers
  const handleCreate = async (data) => {
    setSubmitLoading(true);
    try {
      await universitesAPI.create(data);
      await fetchUniversites();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleUpdate = async (data) => {
    setSubmitLoading(true);
    try {
      await universitesAPI.update(data.universite, data);
      await fetchUniversites();
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDelete = async (data) => {
    setSubmitLoading(true);
    try {
      await universitesAPI.delete(data.universite);
      await fetchUniversites();
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

  const universiteFields = [
    { name: 'nomUniversite', label: 'Nom de l\'université', type: 'text', required: true },
    { name: 'type', label: 'Type', type: 'select', options: [
      { value: 'Publique', label: 'Publique' },
      { value: 'Privée', label: 'Privée' }
    ] },
    { name: 'anneeFondation', label: 'Année de fondation', type: 'number', min: '1800', max: '2024' },
    { name: 'ville', label: 'Ville', type: 'text' },
    { name: 'pays', label: 'Pays', type: 'text' },
    { name: 'nombreEtudiants', label: 'Nombre d\'étudiants', type: 'number', min: '0' },
    { name: 'rangNational', label: 'Rang national', type: 'number', min: '1' },
    { name: 'siteWeb', label: 'Site web', type: 'url', placeholder: 'https://...' }
  ];

  const showUniversiteDetails = async (universite) => {
    try {
      // Fetch detailed information for the selected university
      const response = await universitesAPI.getById(universite.universite);
      setSelectedUniversite(response.data);
      setShowDetailsModal(true);
      setActiveTab('info');
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      setSelectedUniversite(universite);
      setShowDetailsModal(true);
      setActiveTab('info');
    }
  };

  const showUniversiteSpecialites = async (universite) => {
    try {
      const response = await universitesAPI.getSpecialitesByUniversite(universite.universite);
      setSelectedUniversite({
        ...universite,
        specialites: response.data
      });
      setShowDetailsModal(true);
      setActiveTab('specialites');
    } catch (error) {
      console.error('Erreur lors du chargement des spécialités:', error);
    }
  };

  const showUniversiteEnseignants = async (universite) => {
    try {
      const response = await universitesAPI.getEnseignantsByUniversite(universite.universite);
      setSelectedUniversite({
        ...universite,
        enseignants: response.data
      });
      setShowDetailsModal(true);
      setActiveTab('enseignants');
    } catch (error) {
      console.error('Erreur lors du chargement des enseignants:', error);
    }
  };

  const showUniversiteEtudiants = async (universite) => {
    try {
      const response = await universitesAPI.getEtudiantsByUniversite(universite.universite);
      setSelectedUniversite({
        ...universite,
        etudiants: response.data
      });
      setShowDetailsModal(true);
      setActiveTab('etudiants');
    } catch (error) {
      console.error('Erreur lors du chargement des étudiants:', error);
    }
  };

  const getVilleOptions = () => {
    const villes = [...new Set(universites.map(u => u.ville).filter(Boolean))];
    return villes.sort();
  };

  const getPaysOptions = () => {
    const pays = [...new Set(universites.map(u => u.pays).filter(Boolean))];
    return pays.sort();
  };

  if (loading) return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Chargement des universités...</p>
    </div>
  );

  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h3>Erreur de chargement</h3>
      <p>{error}</p>
      <button className="btn-retry" onClick={fetchUniversites}>
        Réessayer
      </button>
    </div>
  );

  return (
    <div className="universites-container">
      {/* Header Section */}
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-title">Gestion des Universités</h1>
          <p className="page-subtitle">
            Gérez et consultez les informations des universités et leurs composantes
          </p>
        </div>
        <div className="header-actions" style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
            ➕ Ajouter
          </button>
          <button className="btn-export" title="Exporter les données">
            📊 Exporter
          </button>
          <button className="btn-refresh" onClick={fetchUniversites} title="Actualiser">
            🔄
          </button>
        </div>
      </header>

      {/* Statistics Cards */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">🏛️</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.total}</h3>
              <p className="stat-label">Total Universités</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon publiques">🇫🇷</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.publiques}</h3>
              <p className="stat-label">Universités Publiques</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon privees">🏢</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.privees}</h3>
              <p className="stat-label">Universités Privées</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon etudiants">🎓</div>
            <div className="stat-content">
              <h3 className="stat-number">{formatNombre(stats.totalEtudiants)}</h3>
              <p className="stat-label">Étudiants Total</p>
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
              {filteredUniversites.length} résultat(s) sur {universites.length}
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
              <option value="publique">Publique</option>
              <option value="privée">Privée</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Ville</label>
            <select 
              value={filters.ville} 
              onChange={(e) => handleFilterChange('ville', e.target.value)}
              className="filter-select"
            >
              <option value="">Toutes les villes</option>
              {getVilleOptions().map((ville, index) => (
                <option key={index} value={ville}>
                  {ville}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Pays</label>
            <select 
              value={filters.pays} 
              onChange={(e) => handleFilterChange('pays', e.target.value)}
              className="filter-select"
            >
              <option value="">Tous les pays</option>
              {getPaysOptions().map((pays, index) => (
                <option key={index} value={pays}>
                  {pays}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group search-group">
            <label className="filter-label">Recherche avancée</label>
            <div className="search-input-container">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Nom, site web..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Universities Grid */}
      <section className="universites-grid-section">
        {filteredUniversites.length > 0 ? (
          <div className="universites-grid">
            {filteredUniversites.map((universite, index) => (
              <div key={`${universite.universite}-${index}`} className="universite-card">
                <div className="card-header">
                  <div className="universite-logo">
                    {universite.nomUniversite?.[0]}
                  </div>
                  <div className="universite-info">
                    <h3 className="universite-name">
                      {universite.nomUniversite}
                    </h3>
                    <div className="universite-meta">
                      <span className={`type-badge ${getTypeBadge(universite.typeUniversite)}`}>
                        {universite.typeUniversite || 'Non spécifié'}
                      </span>
                      <span className="rang-badge">
                        Rang: {universite.rangNational || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="card-content">
                  <div className="info-grid">
                    {universite.ville && (
                      <div className="info-item">
                        <span className="info-icon">📍</span>
                        <span className="info-text">
                          {universite.ville}{universite.pays ? `, ${universite.pays}` : ''}
                        </span>
                      </div>
                    )}
                    
                    {universite.siteWeb && (
                      <div className="info-item">
                        <span className="info-icon">🌐</span>
                        <span className="info-text">
                          <a href={universite.siteWeb} target="_blank" rel="noopener noreferrer">
                            {universite.siteWeb.replace('https://', '').replace('http://', '')}
                          </a>
                        </span>
                      </div>
                    )}
                    
                    {universite.anneeFondation && (
                      <div className="info-item">
                        <span className="info-icon">📅</span>
                        <span className="info-text">Fondée en {universite.anneeFondation}</span>
                      </div>
                    )}
                    
                    {universite.nombreEtudiants && (
                      <div className="info-item">
                        <span className="info-icon">👥</span>
                        <span className="info-text">
                          {formatNombre(universite.nombreEtudiants)} étudiants
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Quick Stats */}
                  <div className="quick-stats">
                    <div className="stat-item">
                      <span className="stat-value">{universite.rangNational || 'N/A'}</span>
                      <span className="stat-label">Rang National</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{formatNombre(universite.nombreEtudiants)}</span>
                      <span className="stat-label">Étudiants</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{universite.anneeFondation || 'N/A'}</span>
                      <span className="stat-label">Fondation</span>
                    </div>
                  </div>
                </div>

                <div className="card-actions">
                  <button 
                    className="btn-secondary"
                    onClick={() => showUniversiteSpecialites(universite)}
                  >
                    📚 Spécialités
                  </button>
                  <button 
                    className="btn-secondary"
                    onClick={() => showUniversiteEnseignants(universite)}
                  >
                    👨‍🏫 Enseignants
                  </button>
                  <button 
                    className="btn-primary"
                    onClick={() => showUniversiteDetails(universite)}
                  >
                    👁️ Détails
                  </button>
                  <button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: universite })}>
                    ✏️
                  </button>
                  <button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: universite })}>
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🏛️</div>
            <h3>Aucune université trouvée</h3>
            <p>Aucun résultat ne correspond à vos critères de recherche</p>
            <button className="btn-clear-filters" onClick={clearFilters}>
              Effacer les filtres
            </button>
          </div>
        )}
      </section>

      {/* Details Modal */}
      {showDetailsModal && selectedUniversite && (
        <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedUniversite.nomUniversite}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowDetailsModal(false)}
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
              <button 
                className={`tab-button ${activeTab === 'specialites' ? 'active' : ''}`}
                onClick={() => setActiveTab('specialites')}
              >
                Spécialités
              </button>
              <button 
                className={`tab-button ${activeTab === 'enseignants' ? 'active' : ''}`}
                onClick={() => setActiveTab('enseignants')}
              >
                Enseignants
              </button>
              <button 
                className={`tab-button ${activeTab === 'etudiants' ? 'active' : ''}`}
                onClick={() => setActiveTab('etudiants')}
              >
                Étudiants
              </button>
            </div>

            <div className="modal-body">
              {activeTab === 'info' && (
                <div className="tab-content">
                  <div className="detail-section">
                    <h3>Informations générales</h3>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <label>Type:</label>
                        <span>{selectedUniversite.typeUniversite || 'Non spécifié'}</span>
                      </div>
                      <div className="detail-item">
                        <label>Ville:</label>
                        <span>{selectedUniversite.ville || 'Non spécifié'}</span>
                      </div>
                      <div className="detail-item">
                        <label>Pays:</label>
                        <span>{selectedUniversite.pays || 'Non spécifié'}</span>
                      </div>
                      <div className="detail-item">
                        <label>Année de fondation:</label>
                        <span>{selectedUniversite.anneeFondation || 'Non spécifié'}</span>
                      </div>
                      <div className="detail-item">
                        <label>Nombre d'étudiants:</label>
                        <span>{formatNombre(selectedUniversite.nombreEtudiants)}</span>
                      </div>
                      <div className="detail-item">
                        <label>Rang national:</label>
                        <span>{selectedUniversite.rangNational || 'Non spécifié'}</span>
                      </div>
                      <div className="detail-item">
                        <label>Site web:</label>
                        <span>
                          {selectedUniversite.siteWeb ? (
                            <a href={selectedUniversite.siteWeb} target="_blank" rel="noopener noreferrer">
                              {selectedUniversite.siteWeb}
                            </a>
                          ) : 'Non spécifié'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'specialites' && (
                <div className="tab-content">
                  <h3>Spécialités offertes</h3>
                  {selectedUniversite.specialites && selectedUniversite.specialites.length > 0 ? (
                    <div className="items-list">
                      {selectedUniversite.specialites.map((specialite, index) => (
                        <div key={index} className="list-item">
                          <div className="item-main">
                            <strong>{specialite.nomSpecialite}</strong>
                            {specialite.codeSpecialite && <span> ({specialite.codeSpecialite})</span>}
                          </div>
                          <div className="item-details">
                            {specialite.niveauDiplome && <span className="detail-tag">{specialite.niveauDiplome}</span>}
                            {specialite.dureeFormation && <span className="detail-tag">{specialite.dureeFormation} ans</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-data">Aucune spécialité disponible</p>
                  )}
                </div>
              )}

              {activeTab === 'enseignants' && (
                <div className="tab-content">
                  <h3>Enseignants</h3>
                  {selectedUniversite.enseignants && selectedUniversite.enseignants.length > 0 ? (
                    <div className="items-list">
                      {selectedUniversite.enseignants.map((enseignant, index) => (
                        <div key={index} className="list-item">
                          <div className="item-main">
                            <strong>{enseignant.prenomEnseignant} {enseignant.nomEnseignant}</strong>
                            {enseignant.grade && <span> - {enseignant.grade}</span>}
                          </div>
                          {enseignant.email && (
                            <div className="item-details">
                              <span className="detail-text">{enseignant.email}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-data">Aucun enseignant disponible</p>
                  )}
                </div>
              )}

              {activeTab === 'etudiants' && (
                <div className="tab-content">
                  <h3>Étudiants</h3>
                  {selectedUniversite.etudiants && selectedUniversite.etudiants.length > 0 ? (
                    <div className="items-list">
                      {selectedUniversite.etudiants.map((etudiant, index) => (
                        <div key={index} className="list-item">
                          <div className="item-main">
                            <strong>{etudiant.prenom} {etudiant.nom}</strong>
                            {etudiant.niveauEtude && <span> - {etudiant.niveauEtude}</span>}
                          </div>
                          <div className="item-details">
                            {etudiant.numeroMatricule && <span className="detail-tag">Matricule: {etudiant.numeroMatricule}</span>}
                            {etudiant.moyenneGenerale && <span className="detail-tag">Moyenne: {etudiant.moyenneGenerale}/20</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-data">Aucun étudiant disponible</p>
                  )}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => setShowDetailsModal(false)}
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .universites-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
          background: #f8fafc;
          min-height: 100vh;
        }

        /* Header Styles */
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 32px;
        }

        .header-content {
          flex: 1;
        }

        .header-actions {
          display: flex;
          gap: 12px;
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

        .btn-refresh, .btn-export {
          background: #f1f5f9;
          border: none;
          border-radius: 8px;
          padding: 8px 12px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: background 0.2s;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .btn-refresh:hover, .btn-export:hover {
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
        .stat-icon.publiques { background: #dcfce7; }
        .stat-icon.privees { background: #fef3c7; }
        .stat-icon.etudiants { background: #f3e8ff; }

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
          justify-content: space-between;
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

        /* Universities Grid Styles */
        .universites-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 24px;
        }

        .universite-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .universite-card:hover {
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

        .universite-logo {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 1.2rem;
        }

        .universite-info {
          flex: 1;
        }

        .universite-name {
          margin: 0 0 8px 0;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .universite-meta {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .type-badge, .rang-badge {
          padding: 4px 8px;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
          color: white;
        }

        .type-badge.publique { background: #10b981; }
        .type-badge.privee { background: #f59e0b; }
        .type-badge.autre { background: #6b7280; }
        .type-badge.unknown { background: #9ca3af; }

        .rang-badge {
          background: rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
        }

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

        .info-text a {
          color: #3b82f6;
          text-decoration: none;
        }

        .info-text a:hover {
          text-decoration: underline;
        }

        .quick-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          padding: 16px;
          background: #f8fafc;
          border-radius: 8px;
        }

        .stat-item {
          text-align: center;
        }

        .stat-value {
          display: block;
          font-size: 1.125rem;
          font-weight: 700;
          color: #1e293b;
        }

        .stat-label {
          font-size: 0.75rem;
          color: #64748b;
          margin: 0;
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

        /* Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .modal-content {
          background: white;
          border-radius: 12px;
          width: 100%;
          max-width: 800px;
          max-height: 80vh;
          overflow: auto;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
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

        .detail-item a {
          color: #3b82f6;
          text-decoration: none;
        }

        .detail-item a:hover {
          text-decoration: underline;
        }

        .items-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .list-item {
          padding: 12px;
          background: #f8fafc;
          border-radius: 8px;
          border-left: 3px solid #3b82f6;
        }

        .item-main {
          margin-bottom: 4px;
        }

        .item-details {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .detail-tag {
          font-size: 0.75rem;
          color: #64748b;
          background: rgba(255, 255, 255, 0.7);
          padding: 2px 6px;
          border-radius: 4px;
        }

        .detail-text {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .no-data {
          text-align: center;
          color: #64748b;
          font-style: italic;
          padding: 20px;
        }

        .modal-footer {
          padding: 20px 24px;
          border-top: 1px solid #e5e7eb;
          display: flex;
          justify-content: flex-end;
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
          .universites-container {
            padding: 16px;
          }

          .page-header {
            flex-direction: column;
            gap: 16px;
          }

          .header-actions {
            width: 100%;
            justify-content: flex-end;
          }

          .filters-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .filters-actions {
            width: 100%;
            justify-content: space-between;
          }

          .filters-grid {
            grid-template-columns: 1fr;
          }

          .universites-grid {
            grid-template-columns: 1fr;
          }

          .card-actions {
            flex-direction: column;
          }

          .modal-content {
            margin: 20px;
            width: calc(100% - 40px);
          }

          .detail-item {
            grid-template-columns: 1fr;
            gap: 4px;
          }

          .modal-tabs {
            flex-wrap: wrap;
          }

          .quick-stats {
            grid-template-columns: 1fr;
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
        title={modalState.mode === 'add' ? 'Ajouter une université' : 'Modifier une université'}
        data={modalState.data}
        onSubmit={handleModalSubmit}
        fields={universiteFields}
        loading={submitLoading}
      />

      <CRUDModal
        isOpen={modalState.isOpen && modalState.mode === 'delete'}
        onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
        mode="delete"
        title="Supprimer une université"
        data={modalState.data}
        onSubmit={handleModalSubmit}
        loading={submitLoading}
      />
    </div>
  );
};

export default Universites;
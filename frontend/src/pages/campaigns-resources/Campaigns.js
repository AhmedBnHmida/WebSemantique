import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Campaigns.css';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [filteredCampaigns, setFilteredCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    type: '',
    search: ''
  });

  // Statistiques
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    planned: 0,
    completed: 0,
    byType: {}
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  useEffect(() => {
    filterCampaigns();
  }, [campaigns, filters]);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('http://localhost:5000/api/campaigns');
      
      if (response.data && response.data.results && response.data.results.bindings) {
        const uniqueCampaigns = removeDuplicates(response.data.results.bindings, 'name');
        setCampaigns(uniqueCampaigns);
        calculateStats(uniqueCampaigns);
      } else {
        setError('Structure de données inattendue');
      }
    } catch (error) {
      console.error('Erreur lors du chargement des campagnes:', error);
      setError('Erreur lors du chargement des campagnes');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (campaignsData) => {
    const stats = {
      total: campaignsData.length,
      active: 0,
      planned: 0,
      completed: 0,
      byType: {}
    };

    campaignsData.forEach(campaign => {
      const status = campaign.status?.value?.toLowerCase() || '';
      const type = campaign.type?.value?.split('#')[1] || 'Campaign';

      // Compter par statut
      if (status.includes('active') || status.includes('actif') || status.includes('en cours')) {
        stats.active++;
      } else if (status.includes('planned') || status.includes('planifié')) {
        stats.planned++;
      } else if (status.includes('completed') || status.includes('terminé')) {
        stats.completed++;
      }

      // Compter par type
      stats.byType[type] = (stats.byType[type] || 0) + 1;
    });

    setStats(stats);
  };

  const filterCampaigns = () => {
    let filtered = campaigns;

    if (filters.status) {
      filtered = filtered.filter(campaign => {
        const status = campaign.status?.value?.toLowerCase() || '';
        return status.includes(filters.status.toLowerCase());
      });
    }

    if (filters.type) {
      filtered = filtered.filter(campaign => {
        const type = campaign.type?.value?.split('#')[1] || '';
        return type.toLowerCase().includes(filters.type.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(campaign => {
        const name = campaign.name?.value?.toLowerCase() || '';
        const description = campaign.description?.value?.toLowerCase() || '';
        return name.includes(filters.search.toLowerCase()) || 
               description.includes(filters.search.toLowerCase());
      });
    }

    setFilteredCampaigns(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      status: '',
      type: '',
      search: ''
    });
  };

  const removeDuplicates = (array, key) => {
    const seen = new Set();
    return array.filter(item => {
      const value = item[key]?.value;
      if (!value || seen.has(value)) {
        return false;
      }
      seen.add(value);
      return true;
    });
  };

  if (loading) return <div className="loading">Chargement des campagnes...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="campaigns-page">
      <h1>Campagnes Écologiques</h1>

      {/* Cartes de Statistiques */}
      <div className="stats-cards">
        <div className="stat-card total">
          <h3>Total</h3>
          <div className="stat-number">{stats.total}</div>
          <p>Campagnes</p>
        </div>
        <div className="stat-card active">
          <h3>Actives</h3>
          <div className="stat-number">{stats.active}</div>
          <p>En cours</p>
        </div>
        <div className="stat-card planned">
          <h3>Planifiées</h3>
          <div className="stat-number">{stats.planned}</div>
          <p>À venir</p>
        </div>
        <div className="stat-card completed">
          <h3>Terminées</h3>
          <div className="stat-number">{stats.completed}</div>
          <p>Réalisées</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="filters-section">
        <h3>Filtrer les campagnes</h3>
        <div className="filters">
          <div className="filter-group">
            <label>Statut:</label>
            <select 
              value={filters.status} 
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">Tous les statuts</option>
              <option value="active">Actives</option>
              <option value="planned">Planifiées</option>
              <option value="completed">Terminées</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Type:</label>
            <select 
              value={filters.type} 
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="">Tous les types</option>
              <option value="Cleanup">Nettoyage</option>
              <option value="Awareness">Sensibilisation</option>
              <option value="Funding">Financement</option>
              <option value="Event">Événement</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Recherche:</label>
            <input
              type="text"
              placeholder="Rechercher par nom ou description..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>

          <button className="clear-filters" onClick={clearFilters}>
            Effacer les filtres
          </button>
        </div>

        <div className="results-count">
          {filteredCampaigns.length} campagne(s) trouvée(s)
        </div>
      </div>

      {/* Grille des campagnes */}
      <div className="campaigns-grid">
        {filteredCampaigns.length > 0 ? (
          filteredCampaigns.map((campaign, index) => (
            <div key={index} className="campaign-card">
              <h3>{campaign.name?.value || 'Nom non disponible'}</h3>
              <p>{campaign.description?.value || 'Pas de description'}</p>
              <div className="campaign-details">
                <span className={`status ${campaign.status?.value?.toLowerCase() || 'unknown'}`}>
                  Statut: {campaign.status?.value || 'Inconnu'}
                </span>
                {campaign.type && (
                  <span className="type">
                    Type: {campaign.type.value.split('#')[1]}
                  </span>
                )}
                {campaign.startDate && (
                  <span>Début: {new Date(campaign.startDate.value).toLocaleDateString()}</span>
                )}
                {campaign.endDate && (
                  <span>Fin: {new Date(campaign.endDate.value).toLocaleDateString()}</span>
                )}
                {campaign.goal && (
                  <span>Objectif: {campaign.goal.value}</span>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="no-results">
            <p>Aucune campagne trouvée avec les critères sélectionnés</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Campaigns;
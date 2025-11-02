import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Resources.css';

const Resources = () => {
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    category: '',
    type: '',
    search: ''
  });

  // Statistiques
  const [stats, setStats] = useState({
    total: 0,
    human: 0,
    material: 0,
    equipment: 0,
    financial: 0,
    digital: 0,
    totalCost: 0
  });

  useEffect(() => {
    fetchResources();
  }, []);

  useEffect(() => {
    filterResources();
  }, [resources, filters]);

  const fetchResources = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('http://localhost:5000/api/resources');
      
      if (response.data && response.data.results && response.data.results.bindings) {
        const uniqueResources = removeDuplicates(response.data.results.bindings, 'name');
        setResources(uniqueResources);
        calculateStats(uniqueResources);
      } else {
        setError('Structure de données inattendue');
      }
    } catch (error) {
      console.error('Erreur lors du chargement des ressources:', error);
      setError('Erreur lors du chargement des ressources');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (resourcesData) => {
    const stats = {
      total: resourcesData.length,
      human: 0,
      material: 0,
      equipment: 0,
      financial: 0,
      digital: 0,
      totalCost: 0
    };

    resourcesData.forEach(resource => {
      const type = resource.type?.value?.split('#')[1] || '';
      const quantity = parseFloat(resource.quantity?.value) || 0;
      const unitCost = parseFloat(resource.unitCost?.value) || 0;
      const totalCost = quantity * unitCost;

      // Compter par type
      if (type.includes('Human')) stats.human++;
      else if (type.includes('Material')) stats.material++;
      else if (type.includes('Equipment')) stats.equipment++;
      else if (type.includes('Financial')) stats.financial++;
      else if (type.includes('Digital')) stats.digital++;

      // Calculer le coût total
      stats.totalCost += totalCost;
    });

    setStats(stats);
  };

  const filterResources = () => {
    let filtered = resources;

    if (filters.category) {
      filtered = filtered.filter(resource => {
        const category = resource.category?.value?.toLowerCase() || '';
        return category.includes(filters.category.toLowerCase());
      });
    }

    if (filters.type) {
      filtered = filtered.filter(resource => {
        const type = resource.type?.value?.split('#')[1] || '';
        return type.toLowerCase().includes(filters.type.toLowerCase());
      });
    }

    if (filters.search) {
      filtered = filtered.filter(resource => {
        const name = resource.name?.value?.toLowerCase() || '';
        const description = resource.description?.value?.toLowerCase() || '';
        return name.includes(filters.search.toLowerCase()) || 
               description.includes(filters.search.toLowerCase());
      });
    }

    setFilteredResources(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      category: '',
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

  if (loading) return <div className="loading">Chargement des ressources...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="resources-page">
      <h1>Ressources Écologiques</h1>

      {/* Cartes de Statistiques */}
      <div className="stats-cards">
        <div className="stat-card total">
          <h3>Total</h3>
          <div className="stat-number">{stats.total}</div>
          <p>Ressources</p>
        </div>
        <div className="stat-card human">
          <h3>Humaines</h3>
          <div className="stat-number">{stats.human}</div>
          <p>Volontaires</p>
        </div>
        <div className="stat-card material">
          <h3>Matérielles</h3>
          <div className="stat-number">{stats.material}</div>
          <p>Matériaux</p>
        </div>
        <div className="stat-card equipment">
          <h3>Équipements</h3>
          <div className="stat-number">{stats.equipment}</div>
          <p>Outils</p>
        </div>
        <div className="stat-card financial">
          <h3>Financières</h3>
          <div className="stat-number">{stats.financial}</div>
          <p>Fonds</p>
        </div>
        <div className="stat-card cost">
          <h3>Coût Total</h3>
          <div className="stat-number">{stats.totalCost.toFixed(2)}€</div>
          <p>Valeur estimée</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="filters-section">
        <h3>Filtrer les ressources</h3>
        <div className="filters">
          <div className="filter-group">
            <label>Type:</label>
            <select 
              value={filters.type} 
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="">Tous les types</option>
              <option value="Human">Ressources Humaines</option>
              <option value="Material">Ressources Matérielles</option>
              <option value="Equipment">Équipements</option>
              <option value="Financial">Ressources Financières</option>
              <option value="Digital">Ressources Numériques</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Catégorie:</label>
            <input
              type="text"
              placeholder="Filtrer par catégorie..."
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            />
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
          {filteredResources.length} ressource(s) trouvée(s)
        </div>
      </div>

      {/* Grille des ressources */}
      <div className="resources-grid">
        {filteredResources.length > 0 ? (
          filteredResources.map((resource, index) => (
            <div key={index} className="resource-card">
              <h3>{resource.name?.value || 'Nom non disponible'}</h3>
              <p>{resource.description?.value || 'Pas de description'}</p>
              <div className="resource-details">
                <span className="category">
                  Catégorie: {resource.category?.value || 'Non spécifiée'}
                </span>
                {resource.type && (
                  <span className="type">
                    Type: {resource.type.value.split('#')[1]}
                  </span>
                )}
                {resource.quantity && (
                  <span className="quantity">
                    Quantité: {resource.quantity.value}
                  </span>
                )}
                {resource.unitCost && (
                  <span className="unit-cost">
                    Coût unitaire: {resource.unitCost.value}€
                  </span>
                )}
                {resource.quantity && resource.unitCost && (
                  <span className="total-cost">
                    Coût total: {(parseFloat(resource.quantity.value) * parseFloat(resource.unitCost.value)).toFixed(2)}€
                  </span>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="no-results">
            <p>Aucune ressource trouvée avec les critères sélectionnés</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Resources;
import React, { useState, useEffect } from 'react';
import './OntologyStats.css';

const OntologyStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOntologyStats();
  }, []);

  const fetchOntologyStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/ontology-stats');
      const data = await response.json();
      
      if (data.status === 'success') {
        setStats(data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Erreur lors du chargement des statistiques');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="ontology-stats">
        <div className="stats-loading">Chargement des statistiques...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ontology-stats">
        <div className="stats-error">Erreur: {error}</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const { ontology_info, statistics, instances } = stats;

  return (
    <div className="ontology-stats">
      <div className="stats-header">
        <h3>📊 Statistiques de l'Ontologie</h3>
        {ontology_info.title && (
          <div className="ontology-title">{ontology_info.title}</div>
        )}
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{statistics.total_classes || 0}</div>
          <div className="stat-label">Classes</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{statistics.total_properties || 0}</div>
          <div className="stat-label">Propriétés</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number">{statistics.total_individuals || 0}</div>
          <div className="stat-label">Instances</div>
        </div>
      </div>

      <div className="instances-grid">
        <h4>📈 Instances par Type</h4>
        <div className="instances-stats">
          <div className="instance-item">
            <span className="instance-label">Événements:</span>
            <span className="instance-count">{instances.events || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Locations:</span>
            <span className="instance-count">{instances.locations || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Utilisateurs:</span>
            <span className="instance-count">{instances.users || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Campagnes:</span>
            <span className="instance-count">{instances.campaigns || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Ressources:</span>
            <span className="instance-count">{instances.resources || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Sponsors:</span>
            <span className="instance-count">{instances.sponsors || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Dons:</span>
            <span className="instance-count">{instances.donations || 0}</span>
          </div>
          <div className="instance-item">
            <span className="instance-label">Blogs:</span>
            <span className="instance-count">{instances.blogs || 0}</span>
          </div>
        </div>
      </div>

      {ontology_info.description && (
        <div className="ontology-description">
          <h4>ℹ️ Description</h4>
          <p>{ontology_info.description}</p>
        </div>
      )}

      {ontology_info.version && (
        <div className="ontology-version">
          <span>Version: {ontology_info.version}</span>
        </div>
      )}
    </div>
  );
};

export default OntologyStats;


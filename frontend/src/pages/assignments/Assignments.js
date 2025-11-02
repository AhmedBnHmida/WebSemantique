import React, { useState, useEffect } from 'react';
import { assignmentsAPI } from '../../utils/api';
import './Assignments.css';

const Assignments = () => {
  const [assignments, setAssignments] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    status: '',
    min_rating: '',
    date_from: '',
    date_to: ''
  });

  useEffect(() => {
    fetchAssignments();
    fetchStatistics();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await assignmentsAPI.getAll();
      setAssignments(response.data);
    } catch (error) {
      console.error('Erreur chargement assignements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await assignmentsAPI.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Erreur chargement statistiques:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await assignmentsAPI.search(searchFilters);
      setAssignments(response.data);
    } catch (error) {
      console.error('Erreur recherche assignements:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setSearchFilters({ status: '', min_rating: '', date_from: '', date_to: '' });
    fetchAssignments();
  };

  const getStatusColor = (status) => {
    if (!status) return 'gray';
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes('approuvé')) return 'green';
    if (lowerStatus.includes('non approuvé')) return 'red';
    return 'gray';
  };

  const getRatingStars = (rating) => {
    if (!rating) return '⭐ Non noté';
    const stars = '⭐'.repeat(parseInt(rating));
    return `${stars} (${rating}/5)`;
  };

  const extractUserName = (userUri) => {
    if (!userUri) return 'Non spécifié';
    const parts = userUri.split('#');
    return parts.length > 1 ? parts[1] : userUri.split('/').pop();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifiée';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR');
    } catch {
      return dateString;
    }
  };

  if (loading) return <div className="loading">Chargement des assignements...</div>;

  return (
    <div className="assignments-section">
      <h1>Assignements</h1>
      
      {/* Statistiques */}
      {statistics && Object.keys(statistics).length > 0 && (
        <div className="statistics-panel">
          <h2>Statistiques</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">{statistics.total || 0}</span>
              <span className="stat-label">Total</span>
            </div>
            <div className="stat-item approved">
              <span className="stat-number">{statistics.approved_count || 0}</span>
              <span className="stat-label">Approuvés</span>
            </div>
            <div className="stat-item rejected">
              <span className="stat-number">{statistics.rejected_count || 0}</span>
              <span className="stat-label">Rejetés</span>
            </div>
            <div className="stat-item rating">
              <span className="stat-number">
                {statistics.average_rating ? parseFloat(statistics.average_rating).toFixed(1) : 'N/A'}
              </span>
              <span className="stat-label">Note moyenne</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Formulaire de recherche */}
      <form onSubmit={handleSearch} className="search-filters">
        <div className="filter-group">
          <select
            value={searchFilters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="filter-input"
          >
            <option value="">Tous les statuts</option>
            <option value="approuvé">Approuvé</option>
            <option value="non approuvé">Non approuvé</option>
          </select>
          
          <select
            value={searchFilters.min_rating}
            onChange={(e) => handleFilterChange('min_rating', e.target.value)}
            className="filter-input"
          >
            <option value="">Toutes les notes</option>
            <option value="1">1⭐ et plus</option>
            <option value="2">2⭐ et plus</option>
            <option value="3">3⭐ et plus</option>
            <option value="4">4⭐ et plus</option>
            <option value="5">5⭐ seulement</option>
          </select>
          
          <input
            type="date"
            placeholder="Date de début..."
            value={searchFilters.date_from}
            onChange={(e) => handleFilterChange('date_from', e.target.value)}
            className="filter-input"
          />
          
          <input
            type="date"
            placeholder="Date de fin..."
            value={searchFilters.date_to}
            onChange={(e) => handleFilterChange('date_to', e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-buttons">
          <button type="submit" className="filter-button">Rechercher</button>
          <button type="button" onClick={clearFilters} className="filter-button clear">
            Effacer
          </button>
        </div>
      </form>

      {/* Liste des assignements */}
      <div className="assignments-grid">
        {assignments.length > 0 ? (
          assignments.map((assignment, index) => (
            <div key={index} className="assignment-card">
              <div className="assignment-header">
                <h3>{assignment.label || `Assignement ${index + 1}`}</h3>
                <span 
                  className={`status-badge ${getStatusColor(assignment.status)}`}
                >
                  {assignment.status || 'Non spécifié'}
                </span>
              </div>
              
              <div className="assignment-details">
                <div className="detail-item">
                  <strong>Volontaire:</strong> 
                  <span>{extractUserName(assignment.volunteer)}</span>
                </div>
                
                <div className="detail-item">
                  <strong>Date de début:</strong> 
                  <span>{formatDate(assignment.startDate)}</span>
                </div>
                
                {assignment.rating && (
                  <div className="detail-item rating-item">
                    <strong>Évaluation:</strong> 
                    <span className="rating-display">
                      {getRatingStars(assignment.rating)}
                    </span>
                  </div>
                )}
                
                {assignment.event && (
                  <div className="detail-item">
                    <strong>Événement:</strong> 
                    <span className="event-link">
                      {assignment.event.split('/').pop()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <p>Aucun assignement trouvé</p>
        )}
      </div>
    </div>
  );
};

export default Assignments;


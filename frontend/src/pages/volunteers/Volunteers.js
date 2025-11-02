import React, { useState, useEffect } from 'react';
import { volunteersAPI } from '../../utils/api';
import './Volunteers.css';

const Volunteers = () => {
  const [volunteers, setVolunteers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    skills: '',
    activity_level: '',
    medical_conditions: ''
  });

  useEffect(() => {
    fetchVolunteers();
  }, []);

  const fetchVolunteers = async () => {
    try {
      const response = await volunteersAPI.getAll();
      setVolunteers(response.data);
    } catch (error) {
      console.error('Erreur chargement volontaires:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await volunteersAPI.search(searchFilters);
      setVolunteers(response.data);
    } catch (error) {
      console.error('Erreur recherche volontaires:', error);
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
    setSearchFilters({ skills: '', activity_level: '', medical_conditions: '' });
    fetchVolunteers();
  };

  const getActivityLevelColor = (level) => {
    if (!level) return 'gray';
    const lowerLevel = level.toLowerCase();
    if (lowerLevel.includes('très actif')) return 'green';
    if (lowerLevel.includes('actif')) return 'orange';
    if (lowerLevel.includes('modérément')) return 'blue';
    return 'gray';
  };

  const extractUserName = (userUri) => {
    if (!userUri) return 'Non spécifié';
    const parts = userUri.split('#');
    return parts.length > 1 ? parts[1] : userUri.split('/').pop();
  };

  if (loading) return <div className="loading">Chargement des volontaires...</div>;

  return (
    <div className="volunteers-section">
      <h1>Volontaires</h1>
      
      {/* Formulaire de recherche */}
      <form onSubmit={handleSearch} className="search-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Rechercher par compétences..."
            value={searchFilters.skills}
            onChange={(e) => handleFilterChange('skills', e.target.value)}
            className="filter-input"
          />
          
          <select
            value={searchFilters.activity_level}
            onChange={(e) => handleFilterChange('activity_level', e.target.value)}
            className="filter-input"
          >
            <option value="">Tous les niveaux d'activité</option>
            <option value="très actif">Très actif</option>
            <option value="actif">Actif</option>
            <option value="modérément actif">Modérément actif</option>
          </select>
          
          <input
            type="text"
            placeholder="Conditions médicales..."
            value={searchFilters.medical_conditions}
            onChange={(e) => handleFilterChange('medical_conditions', e.target.value)}
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

      {/* Liste des volontaires */}
      <div className="volunteers-grid">
        {volunteers.length > 0 ? (
          volunteers.map((volunteer, index) => (
            <div key={index} className="volunteer-card">
              <div className="volunteer-header">
                <h3>{volunteer.label || `Volontaire ${index + 1}`}</h3>
                <span 
                  className={`activity-badge ${getActivityLevelColor(volunteer.activityLevel)}`}
                >
                  {volunteer.activityLevel || 'Non spécifié'}
                </span>
              </div>
              
              <div className="volunteer-details">
                <div className="detail-item">
                  <strong>Utilisateur:</strong> 
                  <span>{extractUserName(volunteer.user)}</span>
                </div>
                
                {volunteer.phone && (
                  <div className="detail-item">
                    <strong>Téléphone:</strong> 
                    <span>{volunteer.phone}</span>
                  </div>
                )}
                
                {volunteer.skills && (
                  <div className="detail-item">
                    <strong>Compétences:</strong> 
                    <span className="skills-tag">{volunteer.skills}</span>
                  </div>
                )}
                
                {volunteer.medicalConditions && (
                  <div className="detail-item">
                    <strong>Conditions médicales:</strong> 
                    <span className="medical-info">{volunteer.medicalConditions}</span>
                  </div>
                )}
                
                {volunteer.motivation && (
                  <div className="detail-item motivation">
                    <strong>Motivation:</strong>
                    <p>{volunteer.motivation}</p>
                  </div>
                )}
                
                {volunteer.experience && (
                  <div className="detail-item experience">
                    <strong>Expérience:</strong>
                    <p>{volunteer.experience}</p>
                  </div>
                )}
                
                {volunteer.generalMotivation && (
                  <div className="detail-item general-motivation">
                    <strong>Motivation générale:</strong>
                    <p>{volunteer.generalMotivation}</p>
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <p>Aucun volontaire trouvé</p>
        )}
      </div>
    </div>
  );
};

export default Volunteers;


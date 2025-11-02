import React, { useState, useEffect } from 'react';
import { locationsAPI } from '../../utils/api';
import './event.css'

const Locations = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
      total: 0,
      dispo: 0,
      reserved: 0,
      inrepair: 0
    });



    
 

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await locationsAPI.getAll();
      setLocations(response.data);
      calculateStats(response.data);
    } catch (error) {
      console.error('Erreur chargement locations:', error);
    } finally {
      setLoading(false);
    }
  };

const calculateStats = (locationData) => {
  const total = locationData.length;
  const dispo = locationData.filter(location => 
    location.reserved === 'false' && location.inRepair === 'false'
  ).length;
  const reserved = locationData.filter(location => 
    location.reserved === 'true'
  ).length;
  const inrepair = locationData.filter(location => 
    location.inRepair === 'true'
  ).length;

  setStats({
    total,
    dispo,
    reserved,
    inrepair
  });
};


  if (loading) return <div className="loading">Chargement des locations...</div>;

  return (
    <div className="resources-page">
      <h1>Lieux d'Événements</h1>


<div className="stats-cards">
  <div className="stat-card total">
    <h3>Total lieux</h3>
    <div className="stat-number">{stats.total}</div>
    <p>Tous les lieux</p>
  </div>
  
  <div className="stat-card total">
    <h3>Réservés</h3>
    <div className="stat-number">{stats.reserved}</div>
    <p>Lieux réservés</p>
  </div>
  
  <div className="stat-card total">
    <h3>En Réparation</h3>
    <div className="stat-number">{stats.inrepair}</div>
    <p>Lieux en réparation</p>
  </div>
  
  <div className="stat-card total">
    <h3>Disponibles</h3>
    <div className="stat-number">{stats.dispo}</div>
    <p>Lieux disponibles</p>
  </div>
</div>
            

      {/* Liste des locations */}
      <div className="locations-grid">
        {locations.length > 0 ? (
          locations.map((location, index) => (
            <div key={index} className="location-card">
              <h3>{location.name}</h3>
              <div className="location-details">
                <p><strong>Adresse:</strong> {location.address}</p>
                {location.city && <p><strong>Ville:</strong> {location.city}</p>}
                {location.country && <p><strong>Pays:</strong> {location.country}</p>}
                <p><strong>Capacité:</strong> {location.capacity} personnes</p>
                <p><strong>Prix:</strong> {location.price || '0'} €</p>
                {location.description && (
                  <p className="location-description">{location.description}</p>
                )}
                <div className="location-status">
                  {location.reserved === 'true' && <span className="status reserved">Réservée</span>}
                  {location.inRepair === 'true' && <span className="status repair">En réparation</span>}
                  {(!location.reserved || location.reserved === 'false') && 
                   (!location.inRepair || location.inRepair === 'false') && 
                   <span className="status available">Disponible</span>}
                </div>
              </div>
            </div>
          ))
        ) : (
          <p>Aucune location trouvée</p>
        )}
      </div>
    </div>
  );
};

export default Locations;
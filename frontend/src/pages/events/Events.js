import React, { useState, useEffect } from 'react';
import { eventsAPI, locationsAPI } from '../../utils/api'; 

const Events = () => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [locationsLoading, setLocationsLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    title: '',
    location: '',
    date: ''
  });
  const [stats, setStats] = useState({
    total: 0,
    scheduled: 0,
    planning: 0,
    confirmed: 0
  });

  useEffect(() => {
    fetchEvents();
    fetchLocations();
  }, []);

  useEffect(() => {
    // Filter events whenever searchFilters change
    filterEvents();
  }, [searchFilters, events]);

  const fetchEvents = async () => {
    try {
      const response = await eventsAPI.getAll();
      console.log('API Response:', response);
      console.log('Events data:', response.data);
      setEvents(response.data);
      setFilteredEvents(response.data); // Initialize filtered events
      calculateStats(response.data);
    } catch (error) {
      console.error('Erreur chargement événements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await locationsAPI.getAll();
      console.log('Locations data:', response.data);
      setLocations(response.data);
    } catch (error) {
      console.error('Erreur chargement des lieux:', error);
    } finally {
      setLocationsLoading(false);
    }
  };

  const filterEvents = () => {
    let filtered = events;

    // Filter by title
    if (searchFilters.title) {
      filtered = filtered.filter(event => 
        event.title.toLowerCase().includes(searchFilters.title.toLowerCase())
      );
    }

    // Filter by location
    if (searchFilters.location) {
      filtered = filtered.filter(event => 
        (event.locationName || '').toLowerCase().includes(searchFilters.location.toLowerCase())
      );
    }

    // Filter by date
    if (searchFilters.date) {
      filtered = filtered.filter(event => {
        const eventDate = new Date(event.date).toISOString().split('T')[0];
        const filterDate = searchFilters.date;
        return eventDate === filterDate;
      });
    }

    setFilteredEvents(filtered);
    calculateStats(filtered); // Update stats based on filtered results
  };

  const calculateStats = (eventsData) => {
    const total = eventsData.length;
    const scheduled = eventsData.filter(event => 
      event.status && event.status.toLowerCase().includes('scheduled')
    ).length;
    const planning = eventsData.filter(event => 
      event.status && event.status.toLowerCase().includes('planning')
    ).length;
    const confirmed = eventsData.filter(event => 
      event.status && event.status.toLowerCase().includes('confirmed')
    ).length;

    setStats({
      total,
      scheduled,
      planning,
      confirmed
    });
  };

  const handleFilterChange = (field, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setSearchFilters({ title: '', location: '', date: '' });
  };

  const getImageArray = (imagesString) => {
    console.log('Images string:', imagesString);
    if (!imagesString || imagesString === 'undefined' || imagesString === 'null') return [];
    if (Array.isArray(imagesString)) return imagesString;
    
    const cleaned = imagesString.toString().trim();
    if (!cleaned) return [];
    
    return cleaned.split(',').map(img => {
      const trimmed = img.trim();
      if (trimmed.startsWith('http')) {
        return trimmed;
      }
      return `https://images.unsplash.com/${trimmed}`;
    }).filter(img => img !== '');
  };

  if (loading) return <div className="loading">Chargement des événements...</div>;

  return (
    <div className="resources-page">
      <h1>Événements Écologiques</h1>
      
      {/* Statistics Cards */}
      <div className="stats-cards">
        <div className="stat-card total">
          <h3>Total Événements</h3>
          <div className="stat-number">{stats.total}</div>
          <p>Tous les événements</p>
        </div>
        
        <div className="stat-card total">
          <h3>Programmés</h3>
          <div className="stat-number">{stats.scheduled}</div>
          <p>Événements programmés</p>
        </div>
        
        <div className="stat-card total">
          <h3>En Planification</h3>
          <div className="stat-number">{stats.planning}</div>
          <p>En cours de planification</p>
        </div>
        
        <div className="stat-card total">
          <h3>Confirmés</h3>
          <div className="stat-number">{stats.confirmed}</div>
          <p>Événements confirmés</p>
        </div>
      </div>
      
      {/* Formulaire de recherche avec filtrage automatique */}
      <div className="filters-section" style={{
        display: 'flex',
        gap: '1rem',
        alignItems: 'end',
        flexWrap: 'nowrap'
      }}>
        <div className="filter-group" style={{flex: 1, marginBottom: 0}}>
          <input
            type="text"
            placeholder="Rechercher par titre..."
            value={searchFilters.title}
            onChange={(e) => handleFilterChange('title', e.target.value)}
            style={{width: '100%', height: '40px'}}
          />
        </div>
        <div className="filter-group" style={{flex: 1, marginBottom: 0}}>
          <select
            value={searchFilters.location}
            onChange={(e) => handleFilterChange('location', e.target.value)}
            style={{width: '100%', height: '40px'}}
          >
            <option value="">Tous les lieux</option>
            {locations.map((location, index) => (
              <option key={index} value={location.name || location.locationName}>
                {location.name || location.locationName}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group" style={{flex: 1, marginBottom: 0}}>
          <input
            type="date"
            value={searchFilters.date}
            onChange={(e) => handleFilterChange('date', e.target.value)}
            style={{width: '100%', height: '40px'}}
          />
        </div>

        <div className="filter-buttons" style={{flexShrink: 0, marginBottom: 0}}>
          <button type="button" onClick={clearFilters} className="filter-button clear">
            Effacer
          </button>
        </div>
      </div>

      {/* Nombre de résultats */}
      <div className="results-count" style={{ 
        margin: '1rem 0', 
        fontSize: '1rem', 
        color: '#495057',
        fontWeight: '600'
      }}>
        {filteredEvents.length} événement{filteredEvents.length !== 1 ? 's' : ''} trouvé{filteredEvents.length !== 1 ? 's' : ''}
        {(searchFilters.title || searchFilters.location || searchFilters.date) && (
          <span style={{ fontSize: '0.9rem', color: '#6c757d', marginLeft: '0.5rem' }}>
          </span>
        )}
      </div>

      {/* Liste des événements */}
      <div className="events-grid">
        {filteredEvents.length > 0 ? (
          filteredEvents.map((event, index) => {
            const eventImages = getImageArray(event.images);
            console.log(`Event ${index} images:`, eventImages);
            
            return (
              <div key={index} className="event-card">
                <div className="event-image-container">
                  {eventImages.length > 0 ? (
                    <img 
                      src={eventImages[0]} 
                      alt={event.title}
                      className="event-image"
                      onError={(e) => {
                        console.error(`Image failed to load: ${eventImages[0]}`);
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                  ) : null}
                  <div className="event-image-placeholder" style={{ 
                    display: eventImages.length > 0 ? 'none' : 'block' 
                  }}>
                    📷 Aucune image
                  </div>
                </div>
                
                <h3>{event.title}</h3>
                {event.description && (
                  <p className="event-description">{event.description}</p>
                )}
                <div className="event-details">
                  <p><strong>Date:</strong> {new Date(event.date).toLocaleString('fr-FR')}</p>
                  <p><strong>Lieu:</strong> {event.locationName || 'Non spécifié'}</p>
                  <p><strong>Participants max:</strong> {event.maxParticipants}</p>
                  {event.status && <p><strong>Statut:</strong> {event.status}</p>}
                  {event.duration && <p><strong>Durée:</strong> {event.duration}</p>}
                </div>
              </div>
            );
          })
        ) : (
          <div style={{ 
            gridColumn: '1 / -1', 
            textAlign: 'center', 
            padding: '3rem',
            color: '#6c757d'
          }}>
            {events.length === 0 ? 'Aucun événement disponible' : 'Aucun événement ne correspond aux critères de recherche.'}
          </div>
        )}
      </div>
    </div>
  );
};

export default Events;
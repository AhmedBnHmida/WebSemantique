import React, { useState, useEffect } from 'react';
import './Reservations.css';

const Reservations = () => {
    const [reservations, setReservations] = useState([]);
    const [filteredReservations, setFilteredReservations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [statusFilter, setStatusFilter] = useState('all');
    const [stats, setStats] = useState([]);

    useEffect(() => {
        fetchReservations();
        fetchStats();
    }, []);

    useEffect(() => {
        filterReservations();
    }, [reservations, statusFilter]);

    const fetchReservations = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/reservations');
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des réservations');
            }
            const data = await response.json();
            setReservations(data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/reservations/stats');
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (err) {
            console.error('Erreur lors de la récupération des statistiques:', err);
        }
    };

    const filterReservations = () => {
        if (statusFilter === 'all') {
            setFilteredReservations(reservations);
        } else {
            const filtered = reservations.filter(reservation => 
                reservation.status && reservation.status.toLowerCase() === statusFilter.toLowerCase()
            );
            setFilteredReservations(filtered);
        }
    };

    const getStatusBadgeClass = (status) => {
        switch (status?.toLowerCase()) {
            case 'confirmed':
                return 'status-badge confirmed';
            case 'pending':
                return 'status-badge pending';
            case 'cancelled':
                return 'status-badge cancelled';
            default:
                return 'status-badge unknown';
        }
    };

    const getStatusText = (status) => {
        switch (status?.toLowerCase()) {
            case 'confirmed':
                return 'Confirmée';
            case 'pending':
                return 'En attente';
            case 'cancelled':
                return 'Annulée';
            default:
                return status || 'Inconnu';
        }
    };

    if (loading) {
        return (
            <div className="reservations-container">
                <div className="loading">Chargement des réservations...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="reservations-container">
                <div className="error">Erreur: {error}</div>
                <button onClick={fetchReservations} className="retry-button">
                    Réessayer
                </button>
            </div>
        );
    }

    return (
        <div className="reservations-container">
            <div className="reservations-header">
                <h1>Gestion des Réservations</h1>
                <p>Gérez toutes les réservations d'événements de la plateforme</p>
            </div>

            {/* Statistiques */}
            {stats.length > 0 && (
                <div className="stats-section">
                    <h3>Statistiques des Réservations</h3>
                    <div className="stats-grid">
                        {stats.map((stat, index) => (
                            <div key={index} className="stat-card">
                                <div className="stat-value">{stat.count}</div>
                                <div className="stat-label">
                                    {getStatusText(stat.status)}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Filtres */}
            <div className="filters-section">
                <div className="filter-group">
                    <label htmlFor="status-filter">Filtrer par statut:</label>
                    <select 
                        id="status-filter"
                        value={statusFilter} 
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">Tous les statuts</option>
                        <option value="confirmed">Confirmées</option>
                        <option value="pending">En attente</option>
                        <option value="cancelled">Annulées</option>
                    </select>
                </div>
                <div className="results-count">
                    {filteredReservations.length} réservation(s) trouvée(s)
                </div>
            </div>

            {/* Liste des réservations */}
            <div className="reservations-list">
                {filteredReservations.length === 0 ? (
                    <div className="no-reservations">
                        <p>Aucune réservation trouvée.</p>
                    </div>
                ) : (
                    <div className="reservations-grid">
                        {filteredReservations.map((reservation, index) => (
                            <div key={index} className="reservation-card">
                                <div className="reservation-header">
                                    <h3>{reservation.eventTitle || 'Événement non spécifié'}</h3>
                                    <span className={getStatusBadgeClass(reservation.status)}>
                                        {getStatusText(reservation.status)}
                                    </span>
                                </div>
                                <div className="reservation-details">
                                    <div className="detail-row">
                                        <span className="detail-label">Utilisateur:</span>
                                        <span className="detail-value">
                                            {reservation.userName && reservation.userLastName 
                                                ? `${reservation.userName} ${reservation.userLastName}`
                                                : reservation.userName || 'Non spécifié'
                                            }
                                        </span>
                                    </div>
                                    {reservation.userEmail && (
                                        <div className="detail-row">
                                            <span className="detail-label">Email:</span>
                                            <span className="detail-value">{reservation.userEmail}</span>
                                        </div>
                                    )}
                                    {reservation.seatNumber && (
                                        <div className="detail-row">
                                            <span className="detail-label">Siège:</span>
                                            <span className="detail-value">{reservation.seatNumber}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Reservations;

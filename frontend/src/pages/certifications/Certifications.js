import React, { useState, useEffect } from 'react';
import './Certifications.css';

const Certifications = () => {
    const [certifications, setCertifications] = useState([]);
    const [filteredCertifications, setFilteredCertifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [typeFilter, setTypeFilter] = useState('all');
    const [stats, setStats] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);

    useEffect(() => {
        fetchCertifications();
        fetchStats();
        fetchLeaderboard();
    }, []);

    useEffect(() => {
        filterCertifications();
    }, [certifications, typeFilter]);

    const fetchCertifications = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/certifications');
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des certifications');
            }
            const data = await response.json();
            setCertifications(data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/certifications/stats');
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (err) {
            console.error('Erreur lors de la récupération des statistiques:', err);
        }
    };

    const fetchLeaderboard = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/certifications/leaderboard');
            if (response.ok) {
                const data = await response.json();
                setLeaderboard(data);
            }
        } catch (err) {
            console.error('Erreur lors de la récupération du classement:', err);
        }
    };

    const filterCertifications = () => {
        if (typeFilter === 'all') {
            setFilteredCertifications(certifications);
        } else {
            const filtered = certifications.filter(cert => 
                cert.type && cert.type.toLowerCase().includes(typeFilter.toLowerCase())
            );
            setFilteredCertifications(filtered);
        }
    };

    const getTypeBadgeClass = (type) => {
        switch (type?.toLowerCase()) {
            case 'participation':
                return 'type-badge participation';
            case 'achievement':
                return 'type-badge achievement';
            case 'eco-points':
                return 'type-badge eco-points';
            case 'volunteer-excellence':
                return 'type-badge volunteer';
            case 'leadership':
                return 'type-badge leadership';
            default:
                return 'type-badge default';
        }
    };

    const getTypeText = (type) => {
        switch (type?.toLowerCase()) {
            case 'participation':
                return 'Participation';
            case 'achievement':
                return 'Accomplissement';
            case 'eco-points':
                return 'Points Éco';
            case 'volunteer-excellence':
                return 'Excellence Bénévole';
            case 'leadership':
                return 'Leadership';
            default:
                return type || 'Non spécifié';
        }
    };

    if (loading) {
        return (
            <div className="certifications-container">
                <div className="loading">Chargement des certifications...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="certifications-container">
                <div className="error">Erreur: {error}</div>
                <button onClick={fetchCertifications} className="retry-button">
                    Réessayer
                </button>
            </div>
        );
    }

    return (
        <div className="certifications-container">
            <div className="certifications-header">
                <h1>Gestion des Certifications</h1>
                <p>Gérez toutes les certifications et récompenses de la plateforme</p>
            </div>

            {/* Classement */}
            {leaderboard.length > 0 && (
                <div className="leaderboard-section">
                    <h3>🏆 Classement des Utilisateurs</h3>
                    <div className="leaderboard-list">
                        {leaderboard.slice(0, 5).map((user, index) => (
                            <div key={index} className={`leaderboard-item ${index < 3 ? 'top-three' : ''}`}>
                                <div className="rank">#{index + 1}</div>
                                <div className="user-info">
                                    <div className="user-name">{user.awardedToName}</div>
                                    {user.awardedToEmail && (
                                        <div className="user-email">{user.awardedToEmail}</div>
                                    )}
                                </div>
                                <div className="user-stats">
                                    <div className="total-points">{Math.round(user.avgPoints || 0)} pts moy.</div>
                                    <div className="cert-count">{user.certCount} cert.</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Statistiques */}
            {stats.length > 0 && (
                <div className="stats-section">
                    <h3>📊 Statistiques des Certifications</h3>
                    <div className="stats-grid">
                        {stats.map((stat, index) => (
                            <div key={index} className="stat-card">
                                <div className="stat-header">
                                    <div className="stat-type">{getTypeText(stat.type)}</div>
                                </div>
                                <div className="stat-details">
                                    <div className="stat-row">
                                        <span>Nombre:</span>
                                        <span className="stat-value">{stat.count}</span>
                                    </div>
                                    {stat.totalPoints && (
                                        <div className="stat-row">
                                            <span>Total pts:</span>
                                            <span className="stat-value">{stat.totalPoints}</span>
                                        </div>
                                    )}
                                    {stat.avgPoints && (
                                        <div className="stat-row">
                                            <span>Moyenne:</span>
                                            <span className="stat-value">{Math.round(stat.avgPoints)}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Filtres */}
            <div className="filters-section">
                <div className="filter-group">
                    <label htmlFor="type-filter">Filtrer par type:</label>
                    <select 
                        id="type-filter"
                        value={typeFilter} 
                        onChange={(e) => setTypeFilter(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">Tous les types</option>
                        <option value="participation">Participation</option>
                        <option value="achievement">Accomplissement</option>
                        <option value="eco-points">Points Éco</option>
                        <option value="volunteer">Excellence Bénévole</option>
                        <option value="leadership">Leadership</option>
                    </select>
                </div>
                <div className="results-count">
                    {filteredCertifications.length} certification(s) trouvée(s)
                </div>
            </div>

            {/* Liste des certifications */}
            <div className="certifications-list">
                {filteredCertifications.length === 0 ? (
                    <div className="no-certifications">
                        <p>Aucune certification trouvée.</p>
                    </div>
                ) : (
                    <div className="certifications-grid">
                        {filteredCertifications.map((cert, index) => (
                            <div key={index} className="certification-card">
                                <div className="certification-header">
                                    <div className="cert-code">
                                        {cert.certificateCode || 'Code non spécifié'}
                                    </div>
                                    <span className={getTypeBadgeClass(cert.type)}>
                                        {getTypeText(cert.type)}
                                    </span>
                                </div>
                                <div className="certification-details">
                                    <div className="points-section">
                                        <div className="points-value">
                                            {cert.pointsEarned || 0}
                                        </div>
                                        <div className="points-label">Points</div>
                                    </div>
                                    <div className="issuer-section">
                                        <div className="detail-row">
                                            <span className="detail-label">Émis par:</span>
                                            <span className="detail-value">
                                                {cert.issuerName || 'Non spécifié'}
                                            </span>
                                        </div>
                                        {cert.awardedToEmail && (
                                            <div className="detail-row">
                                                <span className="detail-label">Email:</span>
                                                <span className="detail-value">{cert.awardedToEmail}</span>
                                            </div>
                                        )}
                                        {cert.reservationCode && cert.eventTitle && (
                                            <div className="detail-row reservation-info">
                                                <span className="detail-label">Réservation:</span>
                                                <span className="detail-value">
                                                    {cert.reservationCode} - {cert.eventTitle}
                                                    {cert.reservationStatus && (
                                                        <span className={`status-badge ${cert.reservationStatus.toLowerCase()}`}>
                                                            {cert.reservationStatus}
                                                        </span>
                                                    )}
                                                    {cert.confirmedByName && (
                                                        <span className="confirmed-by">
                                                            Confirmé par: {cert.confirmedByName}
                                                        </span>
                                                    )}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Certifications;

"use client"

import { useState, useEffect } from "react"
import { donationsAPI } from "../../utils/api"
import "./Donations.css"

const Donations = () => {
  const [donations, setDonations] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState("")
  const [sortOrder, setSortOrder] = useState("newest")
  const [limit, setLimit] = useState(200)

  useEffect(() => {
    fetchDonations()
  }, [])

  const fetchDonations = async () => {
    try {
      const params = {}
      if (filterType) params.type = filterType
      if (sortOrder) params.sort = sortOrder
      if (limit) params.limit = limit

      const res = await donationsAPI.getAll(params)
      setDonations(res.data || [])
    } catch (err) {
      console.error("Erreur chargement donations:", err)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    setLoading(true)
    fetchDonations()
  }

  const resetFilters = () => {
    setFilterType("")
    setSortOrder("newest")
    setLimit(200)
    setLoading(true)
    fetchDonations()
  }

  const getDonationTypeBadge = (type) => {
    const typeMap = {
      FinancialDonation: { label: "Financière", color: "badge-financial" },
      MaterialDonation: { label: "Matérielle", color: "badge-material" },
      ServiceDonation: { label: "Service", color: "badge-service" },
    }
    return typeMap[type] || { label: type, color: "badge-default" }
  }

  if (loading) {
    return (
      <div className="donations-page">
        <div className="loading-spinner">Chargement des donations...</div>
      </div>
    )
  }

  return (
    <div className="donations-page">
      <div className="donations-header">
        <h1>Donations</h1>
        <p className="donations-subtitle">Gérez et consultez toutes les donations</p>
      </div>

      <div className="donation-filters-card">
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="type-select">Type</label>
            <select
              id="type-select"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="filter-select"
            >
              <option value="">Toutes</option>
              <option value="FinancialDonation">Financière</option>
              <option value="MaterialDonation">Matérielle</option>
              <option value="ServiceDonation">Service</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-select">Trier par</label>
            <select
              id="sort-select"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              className="filter-select"
            >
              <option value="newest">Les plus récentes</option>
              <option value="oldest">Les plus anciennes</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="limit-input">Limite</label>
            <input
              id="limit-input"
              type="number"
              value={limit}
              min={1}
              max={1000}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="filter-input"
            />
          </div>

          <div className="filter-buttons">
            <button onClick={applyFilters} className="btn-apply">
              Appliquer
            </button>
            <button onClick={resetFilters} className="btn-reset">
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      {donations.length > 0 ? (
        <div className="donations-grid">
          {donations.map((d, idx) => (
            <div key={idx} className="donation-card">
              <div className="card-header">
                <div className="card-title-section">
                  <h3 className="card-title">
                    {d.rdfs_label || d.rdfsLabel || d.label || d.donation || `Donation ${idx + 1}`}
                  </h3>
                  <span className={`donation-badge ${getDonationTypeBadge(d.type).color}`}>
                    {getDonationTypeBadge(d.type).label}
                  </span>
                </div>
                {d.montant || d.amount ? (
                  <div className="card-amount">
                    {d.montant || d.amount} {d.devise || d.currency || ""}
                  </div>
                ) : null}
              </div>

              <div className="card-content">
                {d.donateur || d.donorName ? (
                  <div className="detail-row">
                    <span className="detail-label">Donateur</span>
                    <span className="detail-value">{d.donateur || d.donorName}</span>
                  </div>
                ) : null}

                {d.description || d.itemDescription || d.serviceDescription ? (
                  <div className="detail-row">
                    <span className="detail-label">Détails</span>
                    <span className="detail-value">{d.description || d.itemDescription || d.serviceDescription}</span>
                  </div>
                ) : null}

                {d.valeurEstimee || d.estimatedValue ? (
                  <div className="detail-row">
                    <span className="detail-label">Valeur estimée</span>
                    <span className="detail-value">{d.valeurEstimee || d.estimatedValue}</span>
                  </div>
                ) : null}

                {d.heuresDonnees || d.hoursDonated ? (
                  <div className="detail-row">
                    <span className="detail-label">Heures</span>
                    <span className="detail-value">{d.heuresDonnees || d.hoursDonated}</span>
                  </div>
                ) : null}

                {d.evenement || d.eventTitle ? (
                  <div className="detail-row">
                    <span className="detail-label">Événement</span>
                    <span className="detail-value">{d.evenement || d.eventTitle}</span>
                  </div>
                ) : null}

                {d.date ? (
                  <div className="detail-row">
                    <span className="detail-label">Date</span>
                    <span className="detail-value">{new Date(d.date).toLocaleString("fr-FR")}</span>
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="donations-empty">
          <p>Aucune donation trouvée</p>
        </div>
      )}
    </div>
  )
}

export default Donations

"use client"

import { useState, useEffect } from "react"
import { sponsorsAPI, donationsAPI, ontologyAPI } from "../../utils/api"
import GraphViz from "./GraphViz"
import "./Sponsors.css"

const Sponsors = () => {
  const [sponsors, setSponsors] = useState([])
  const [donations, setDonations] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ name: "", industry: "" })
  const [expandedSponsor, setExpandedSponsor] = useState(null)
  const [showGraph, setShowGraph] = useState(false)
  const [graphData, setGraphData] = useState(null)
  const [loadingGraph, setLoadingGraph] = useState(false)

  useEffect(() => {
    fetchSponsors()
    fetchDonations()
  }, [])

  const fetchSponsors = async () => {
    try {
      const res = await sponsorsAPI.getAll()
      setSponsors(res.data)
    } catch (err) {
      console.error("Erreur chargement sponsors:", err)
    }
  }

  const fetchDonations = async () => {
    try {
      const res = await donationsAPI.getAll()
      setDonations(res.data)
    } catch (err) {
      console.error("Erreur chargement donations:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await sponsorsAPI.search(filters)
      setSponsors(res.data)
    } catch (err) {
      console.error("Erreur recherche sponsors:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }))
  }

  useEffect(() => {
    const loadGraph = async () => {
      if (!showGraph) return
      if (graphData) return
      setLoadingGraph(true)
      try {
        const res = await ontologyAPI.getGraph()
        setGraphData(res.data)
      } catch (err) {
        console.error("Erreur chargement graphe ontologie:", err)
      } finally {
        setLoadingGraph(false)
      }
    }
    loadGraph()
  }, [showGraph])

  if (loading) return <div className="loading">Chargement des sponsors...</div>

  return (
    <div className="sponsors-page">
      <div className="sponsors-header">
        <h2>Sponsors et Donations</h2>
        <p className="sponsors-subtitle">Découvrez nos partenaires et leurs contributions</p>
      </div>

      <form onSubmit={handleSearch} className="sponsors-search">
        <input
          type="text"
          placeholder="Nom de l'entreprise..."
          value={filters.name}
          onChange={(e) => handleChange("name", e.target.value)}
        />
        <input
          type="text"
          placeholder="Secteur..."
          value={filters.industry}
          onChange={(e) => handleChange("industry", e.target.value)}
        />
        <button type="submit" className="btn-search">
          Rechercher
        </button>
        <button type="button" className="btn-graph" onClick={() => setShowGraph((prev) => !prev)}>
          {showGraph ? "Masquer graphe" : "Visualiser graphe"}
        </button>
      </form>

      {showGraph && (
        <div className="graph-section">
          <h3>Graphe Sponsors ↔ Donations</h3>
          {loadingGraph ? (
            <div className="loading">Chargement du graphe...</div>
          ) : (
            <GraphViz sponsors={sponsors} donations={donations} graphData={graphData} width={1000} height={600} />
          )}
        </div>
      )}

      <div className="sponsors-list">
        <h3>Liste des sponsors</h3>
        {sponsors.length > 0 ? (
          <div className="events-grid">
            {sponsors.map((s, idx) => {
              const name = s.nomEntreprise || s.companyName || s.firstName || s.name || "Sponsor"
              const donationsFor = donations.filter((d) => {
                const donor = d.donateur || d.donorName || d.donor || ""
                return donor && donor === name
              })
              return (
                <div key={idx} className="event-card">
                  <div className="card-header">
                    <h4>{name}</h4>
                    <span className="donation-badge">{donationsFor.length}</span>
                  </div>
                  <div className="event-details">
                    {(s.secteur || s.industry) && (
                      <p>
                        <strong>Secteur:</strong> {s.secteur || s.industry}
                      </p>
                    )}
                    {(s.niveauDeSponsoring || s.levelName) && (
                      <p>
                        <strong>Niveau:</strong> {s.niveauDeSponsoring || s.levelName}
                      </p>
                    )}
                    {(s.courriel || s.contactEmail || s.email) && (
                      <p>
                        <strong>Email:</strong> {s.courriel || s.contactEmail || s.email}
                      </p>
                    )}
                    {(s.telephone || s.phoneNumber || s.phone) && (
                      <p>
                        <strong>Téléphone:</strong> {s.telephone || s.phoneNumber || s.phone}
                      </p>
                    )}
                    {(s.siteWeb || s.website) && (
                      <p>
                        <strong>Site Web:</strong>{" "}
                        <a
                          href={
                            (s.siteWeb || s.website).startsWith("http")
                              ? s.siteWeb || s.website
                              : `https://${s.siteWeb || s.website}`
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          {s.siteWeb || s.website}
                        </a>
                      </p>
                    )}
                  </div>

                  <button
                    className="btn-expand"
                    onClick={() => setExpandedSponsor(expandedSponsor === idx ? null : idx)}
                  >
                    {expandedSponsor === idx ? "Masquer donations" : "Voir donations"}
                  </button>

                  {expandedSponsor === idx && (
                    <div className="sponsor-donations-list">
                      {donationsFor.length > 0 ? (
                        <ul>
                          {donationsFor.map((d, di) => (
                            <li key={di}>
                              {d.rdfs_label || d.donation || d.label || d.rdfsLabel || "Donation"} —{" "}
                              {d.montant || d.amount || ""} {d.devise || d.currency || ""}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div>Aucune donation trouvée pour ce sponsor</div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <p className="no-results">Aucun sponsor trouvé</p>
        )}
      </div>
    </div>
  )
}

export default Sponsors

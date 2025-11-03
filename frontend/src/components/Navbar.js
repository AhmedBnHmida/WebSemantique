"use client"

import { Link, useLocation } from "react-router-dom"
import "./Navbar.css"

const Navbar = () => {
  const location = useLocation()

  const menuItems = [
    { path: "/personnes", label: "Personnes", icon: "👥" },
    { path: "/specialites", label: "Spécialités", icon: "🎓" },
    { path: "/universites", label: "Universités", icon: "🏛️" },
    { path: "/cours", label: "Cours", icon: "📚" },
    { path: "/ressources-pedagogiques", label: "Ressources", icon: "📖" },
    { path: "/evaluations", label: "Évaluations", icon: "📝" },
    { path: "/competences", label: "Compétences", icon: "💡" },
    { path: "/projets-academiques", label: "Projets", icon: "🔬" },
    { path: "/technologies-educatives", label: "Technologies", icon: "💻" },
    { path: "/orientations-academiques", label: "Orientations", icon: "🧭" },
  ]

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          <div className="nav-logo-icon">
            <div className="book book-bottom"></div>
            <div className="book book-middle"></div>
            <div className="book book-top"></div>
          </div>
          <span className="nav-brand-text">Edu Smart</span>
        </Link>

        <ul className="nav-menu">
          {menuItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link 
                to={item.path} 
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            </li>
          ))}
          
          {/* Search Link */}
          <li className="nav-item">
            <Link to="/rechercher" className={`nav-link search-link ${isActive('/rechercher') ? 'active' : ''}`}>
              <span className="nav-icon">🔍</span>
              <span className="nav-label">Rechercher</span>
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navbar
"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import "./Navbar.css"

const Navbar = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen)
  }

  const closeDropdown = () => {
    setIsDropdownOpen(false)
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <a href="/" style={{ textDecoration: "none", color: "inherit" }}>
          <h1 className="nav-logo">🌿 Eco Platform</h1>
        </a>

        <ul className="nav-menu">
          {/* Classes Dropdown Menu */}
          <li className="nav-item dropdown">
            <button className="nav-link dropdown-toggle" onClick={toggleDropdown}>
              Classes
              <span className="dropdown-icon">▼</span>
            </button>

            {isDropdownOpen && (
              <ul className="dropdown-menu">
                <li>
                  <Link to="/campaigns" className="dropdown-link" onClick={closeDropdown}>
                    Campagnes
                  </Link>
                </li>
                <li>
                  <Link to="/resources" className="dropdown-link" onClick={closeDropdown}>
                    Ressources
                  </Link>
                </li>
                <li>
                  <Link to="/events" className="dropdown-link" onClick={closeDropdown}>
                    Événements
                  </Link>
                </li>
                <li>
                  <Link to="/locations" className="dropdown-link" onClick={closeDropdown}>
                    Locations
                  </Link>
                </li>
                <li>
                  <Link to="/reservations" className="dropdown-link" onClick={closeDropdown}>
                    Réservations
                  </Link>
                </li>
                <li>
                  <Link to="/certifications" className="dropdown-link" onClick={closeDropdown}>
                    Certifications
                  </Link>
                </li>
                <li>
                  <Link to="/volunteers" className="dropdown-link" onClick={closeDropdown}>
                    Volontaires
                  </Link>
                </li>
                <li>
                  <Link to="/assignments" className="dropdown-link" onClick={closeDropdown}>
                    Assignements
                  </Link>
                </li>
                <li>
                  <Link to="/sponsors" className="dropdown-link" onClick={closeDropdown}>
                    Sponsors
                  </Link>
                </li>
                <li>
                  <Link to="/donations" className="dropdown-link" onClick={closeDropdown}>
                    Donations
                  </Link>
                </li>
                <li>
                  <Link to="/blogs" className="dropdown-link" onClick={closeDropdown}>
                    Blogs
                  </Link>
                </li>
                <li>
                  <Link to="/users" className="dropdown-link" onClick={closeDropdown}>
                    Utilisateurs
                  </Link>
                </li>
              </ul>
            )}
          </li>

          {/* Search Link */}
          <li className="nav-item">
            <Link to="/" className="nav-link">
              Rechercher
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navbar

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Campaigns from './pages/campaigns-resources/Campaigns';
import Resources from './pages/campaigns-resources/Resources';
import Users from './pages/Users';
import SemanticSearch from './pages/SemanticSearch';
import Events from './pages/events/Events';
import Locations from './pages/events-locations/Locations';
import Reservations from './pages/reservations/Reservations';
import Certifications from './pages/certifications/Certifications';
import Sponsors from './pages/sponsors/Sponsors';
import Donations from './pages/donations/Donations';
import Volunteers from './pages/volunteers/Volunteers';
import Assignments from './pages/assignments/Assignments';
import Blogs from './pages/blogs/Blogs';

// New educational components
import Personnes from './pages/education/Personnes/Personnes';
import Specialites from './pages/education/Specialites/Specialites';
import Universites from './pages/education/Universites/Universites';
import Cours from './pages/education/Cours/Cours';
import RessourcesPedagogiques from './pages/education/RessourcesPedagogiques/RessourcesPedagogiques';
import Evaluations from './pages/education/Evaluations/Evaluations';
import Competences from './pages/education/Competences/Competences';
import ProjetsAcademiques from './pages/education/ProjetsAcademiques/ProjetsAcademiques';
import TechnologiesEducatives from './pages/education/TechnologiesEducatives/TechnologiesEducatives';
import OrientationsAcademiques from './pages/education/OrientationsAcademiques/OrientationsAcademiques';

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            {/* Original Routes */}
            <Route path="/" element={<SemanticSearch />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/users" element={<Users />} />
            <Route path="/events" element={<Events />} />
            <Route path="/locations" element={<Locations />} />
            <Route path="/reservations" element={<Reservations />} />
            <Route path="/certifications" element={<Certifications />} />
            <Route path="/sponsors" element={<Sponsors />} />
            <Route path="/donations" element={<Donations />} />
            <Route path="/volunteers" element={<Volunteers />} />
            <Route path="/assignments" element={<Assignments />} />
            <Route path="/blogs" element={<Blogs />} />

            {/* New Educational Routes */}
            <Route path="/personnes" element={<Personnes />} />
            <Route path="/specialites" element={<Specialites />} />
            <Route path="/universites" element={<Universites />} />
            <Route path="/cours" element={<Cours />} />
            <Route path="/ressources-pedagogiques" element={<RessourcesPedagogiques />} />
            <Route path="/evaluations" element={<Evaluations />} />
            <Route path="/competences" element={<Competences />} />
            <Route path="/projets-academiques" element={<ProjetsAcademiques />} />
            <Route path="/technologies-educatives" element={<TechnologiesEducatives />} />
            <Route path="/orientations-academiques" element={<OrientationsAcademiques />} />
            <Route path="/rechercher" element={<SemanticSearch />} />

            <Route path="*" element={<h2>404 - Page Not Found</h2>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';

// Education domain components
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
import SemanticSearch from './pages/SemanticSearch';

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            {/* Education Domain Routes */}
            <Route path="/" element={<Personnes />} />
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
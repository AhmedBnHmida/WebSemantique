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



import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
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

            <Route path="*" element={<h2>404 - Page Not Found</h2>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
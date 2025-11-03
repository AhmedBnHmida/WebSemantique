# 📚 Project Index - Web Sémantique Platform

## 🎯 Project Overview

A semantic web platform for managing ecological events and educational resources using OWL ontologies, SPARQL queries, and AI-powered natural language processing.

**Core Technologies:**
- **Backend**: Flask (Python) with SPARQL/OWL support
- **Frontend**: React.js
- **Semantic Store**: Apache Jena Fuseki
- **AI Integration**: Google Gemini for SPARQL generation + TALN for entity extraction

---

## 📁 Directory Structure

```
web-semantique-main/
├── backend/                    # Flask API server
│   ├── modules/               # Blueprint modules
│   │   ├── assignments.py     # Assignment management
│   │   ├── blogs.py           # Blog posts
│   │   ├── campRes.py         # Campaigns & Resources
│   │   ├── certifications.py  # Certifications
│   │   ├── events.py          # Events management
│   │   ├── gemini_sparql_service.py  # Gemini AI SPARQL generator
│   │   ├── locations.py       # Location management
│   │   ├── personne.py        # Person entities
│   │   ├── reservations.py    # Reservations
│   │   ├── reviews.py         # Reviews
│   │   ├── search.py          # Semantic search pipeline (TALN→Gemini→SPARQL)
│   │   ├── specialite_bp.py  # Specializations
│   │   ├── sponsors.py        # Sponsors & donations
│   │   ├── taln_service.py    # TALN entity extraction
│   │   ├── universite_bp.py   # Universities
│   │   ├── users.py           # User management
│   │   └── volunteers.py      # Volunteers
│   ├── app.py                 # Main Flask application
│   ├── sparql_utils.py        # SPARQL utilities
│   ├── requirements.txt       # Python dependencies
│   ├── test_taln_integration.py    # TALN+Gemini tests
│   └── debug_taln_integration.py    # TALN debugging script
│
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── Navbar.js      # Navigation bar
│   │   │   └── OntologyStats.js  # Ontology statistics
│   │   ├── pages/             # Page components
│   │   │   ├── assignments/   # Assignments page
│   │   │   ├── blogs/         # Blogs page
│   │   │   ├── campaigns-resources/  # Campaigns & Resources
│   │   │   ├── certifications/       # Certifications
│   │   │   ├── donations/           # Donations
│   │   │   ├── education/           # Education domain
│   │   │   │   ├── Competences/     # Competencies
│   │   │   │   ├── Cours/           # Courses
│   │   │   │   ├── Evaluations/     # Evaluations
│   │   │   │   ├── OrientationsAcademiques/  # Academic orientations
│   │   │   │   ├── Personnes/       # People
│   │   │   │   ├── ProjetsAcademiques/       # Academic projects
│   │   │   │   ├── RessourcesPedagogiques/  # Pedagogical resources
│   │   │   │   ├── Specialites/     # Specializations
│   │   │   │   ├── TechnologiesEducatives/   # Educational technologies
│   │   │   │   └── Universites/     # Universities
│   │   │   ├── events/        # Events
│   │   │   ├── events-locations/    # Events & Locations
│   │   │   ├── reservations/       # Reservations
│   │   │   ├── SemanticSearch.js   # Semantic search (main feature)
│   │   │   ├── sponsors/      # Sponsors
│   │   │   ├── Users.js       # Users
│   │   │   └── volunteers/    # Volunteers
│   │   └── utils/
│   │       └── api.js         # API utility functions
│   └── package.json           # Node.js dependencies
│
├── fuseki/                    # Apache Jena Fuseki server
│   └── apache-jena-fuseki-5.6.0/
│       ├── fuseki-server.jar  # Fuseki server JAR
│       └── run/
│           └── configuration/ # Fuseki datasets config
│
├── data/                      # RDF data files
│   └── educationInfin.rdf    # Education ontology data
│
├── scripts/                   # Utility scripts
│   └── load_data.py          # Load RDF data to Fuseki
│
└── [root scripts]             # Various utility/debug scripts
    ├── add_statuses_one_by_one.py    # Add assignment statuses
    ├── check_property_exists.py      # Check ontology properties
    ├── cleanup_caches.py             # Clean Python caches
    ├── debug_assignments.py          # Debug assignments
    └── test_*.py                     # Various test scripts
```

---

## 🔧 Core Components

### 1. **Backend Flask Application** (`backend/app.py`)

**Main Entry Point:**
- Flask application with CORS enabled
- Blueprint-based modular architecture
- Health check endpoints
- Test connection endpoints

**Key Endpoints:**
- `GET /` - API status
- `GET /api/health` - Health check
- `GET /api/test` - Test Fuseki connection
- `GET /api/ontology-stats` - Ontology statistics
- `GET /api/ontology/graph` - Graph visualization data
- `GET /api/education-stats` - Education domain statistics

**Registered Blueprints:**
- `/api` - All API routes
  - `campRes` - Campaigns & Resources
  - `personne` - Person entities
  - `specialite_bp` - Specializations
  - `locations` - Locations
  - `universite_bp` - Universities
  - `users` - Users
  - `search` - Semantic search ⭐ **Main feature**
  - `reservations` - Reservations
  - `certifications` - Certifications
  - `sponsors` - Sponsors
  - `volunteers` - Volunteers
  - `assignments` - Assignments
  - `blogs` - Blog posts
  - `reviews` - Reviews

### 2. **SPARQL Utilities** (`backend/sparql_utils.py`)

**SPARQLUtils Class:**
- Manages connection to Fuseki endpoint
- `execute_query(query)` - Execute SELECT queries
- `execute_update(query)` - Execute INSERT/DELETE updates
- Auto-formats results for readability

**Configuration:**
- Endpoint: `http://localhost:3030/educationInfin` (default)
- Configurable via `FUSEKI_ENDPOINT` environment variable

### 3. **Semantic Search Pipeline** (`backend/modules/search.py`)

**Three Search Methods:**

1. **Main Pipeline** (`POST /api/search`)
   - TALN Analysis → Gemini SPARQL Generation → SPARQL Execution
   - Returns comprehensive analysis results

2. **AI Search** (`POST /api/search/ai`)
   - Direct Gemini transformation (bypasses TALN)
   - Faster but less accurate

3. **Hybrid Search** (`POST /api/search/hybrid`)
   - Tries TALN+Gemini first, falls back to direct Gemini

**Response Structure:**
```json
{
  "question": "string",
  "taln_analysis": {
    "entities": [...],
    "intent": {...},
    "confidence_scores": {...}
  },
  "sparql_query": "SPARQL query string",
  "results": [...],
  "pipeline_info": {
    "taln_confidence": 0.0-1.0,
    "entities_detected": 0,
    "intent_classified": "string",
    "query_length": 0,
    "results_count": 0
  }
}
```

### 4. **TALN Service** (`backend/modules/taln_service.py`)

**Purpose:** Extract entities, relationships, and intent from natural language questions

**Features:**
- Entity detection (Events, Locations, Users, Campaigns, Volunteers, Assignments, etc.)
- Intent classification (list, count, filter, search, details)
- Temporal expression extraction
- Location information extraction
- Keyword extraction
- Relationship extraction
- **Fallback mode:** Works without external TALN API using pattern matching

**Entity Mapping:**
- `eco:Event`, `eco:EducationalEvent`, `eco:EntertainmentEvent`, etc.
- `webprotege:RCXXzqv27uFuX5nYU81XUvw` (Volunteers)
- `webprotege:Rj2A7xNWLfpNcbE4HJMKqN` (Assignments)
- `eco:Campaign`, `eco:Location`, `eco:Resource`, etc.

**Analysis Output:**
```python
{
  "original_question": "string",
  "entities": [
    {
      "text": "event",
      "type": "Event",
      "ontology_class": "eco:Event",
      "confidence": 0.9
    }
  ],
  "intent": {
    "primary_intent": "list",
    "query_type": "list"
  },
  "temporal_info": {
    "relative_time": "future",
    "time_expressions": ["à venir"]
  },
  "location_info": {
    "locations": ["paris"]
  },
  "confidence_scores": {
    "overall_confidence": 0.85
  }
}
```

### 5. **Gemini SPARQL Service** (`backend/modules/gemini_sparql_service.py`)

**Purpose:** Generate SPARQL queries from natural language or TALN analysis

**Key Methods:**
- `transform_question_to_sparql(question)` - Direct transformation
- `transform_taln_analysis_to_sparql(taln_analysis)` - From TALN analysis ⭐

**Gemini Models (Fallback Chain):**
1. `models/gemini-2.0-flash` (preferred)
2. `models/gemini-flash-latest`
3. `models/gemini-pro-latest`

**Query Generation Features:**
- Uses correct ontology prefixes (`eco:`, `webprotege:`)
- Handles UNION queries for event subtypes
- Makes optional properties OPTIONAL
- Adds appropriate LIMITs
- Defensive fixes for donation queries
- Validates and cleans generated queries

**Fallback Queries:**
- Predefined queries for volunteers, assignments, reservations, certifications, campaigns
- Handles specific question patterns

**Ontology Knowledge:**
- Event types and properties
- Location properties
- User properties
- Campaign types
- Resource types
- Volunteer properties (webprotege IDs)
- Assignment properties
- Certification properties
- Reservation properties
- Blog properties
- Sponsor/Donation properties

---

## 🌐 API Endpoints Reference

### **Semantic Search**
- `POST /api/search` - Main semantic search (TALN→Gemini→SPARQL)
- `POST /api/search/ai` - Direct Gemini search
- `POST /api/search/hybrid` - Hybrid search with fallback

### **Domain Entities**
- `GET /api/personnes` - List persons
- `GET /api/universites` - List universities
- `GET /api/specialites` - List specializations
- `GET /api/locations` - List locations
- `GET /api/users` - List users
- `GET /api/volunteers` - List volunteers
- `GET /api/assignments` - List assignments
- `GET /api/reservations` - List reservations
- `GET /api/certifications` - List certifications
- `GET /api/sponsors` - List sponsors
- `GET /api/blogs` - List blogs
- `GET /api/reviews` - List reviews

### **Campaigns & Resources**
- `GET /api/campaigns` - List campaigns
- `GET /api/resources` - List resources

### **Statistics & Info**
- `GET /api/ontology-stats` - Ontology statistics
- `GET /api/ontology/graph` - Graph visualization data
- `GET /api/education-stats` - Education statistics
- `GET /api/health` - Health check
- `GET /api/test` - Test Fuseki connection

---

## 🗄️ Ontology Structure

### **Main Namespaces:**
- `eco:` - `http://www.semanticweb.org/eco-ontology#` (Ecological domain)
- `webprotege:` - `http://webprotege.stanford.edu/` (Volunteers, Assignments)
- `edu:` - `http://www.education-intelligente.org/ontologie#` (Education domain)

### **Key Classes:**

**Ecological Domain (eco:):**
- `Event`, `EducationalEvent`, `EntertainmentEvent`, `CompetitiveEvent`, `SocializationEvent`
- `Location`, `Indoor`, `Outdoor`, `VirtualPlatform`
- `Campaign`, `AwarenessCampaign`, `CleanupCampaign`, `FundingCampaign`, `EventCampaign`
- `Resource`, `DigitalResource`, `EquipmentResource`, `FinancialResource`, `HumanResource`, `MaterialResource`
- `Reservation`
- `Certification`
- `Blog`
- `Sponsor`, `BronzeSponsor`, `SilverSponsor`, `GoldSponsor`, `PlatinumSponsor`
- `Donation`, `FinancialDonation`, `MaterialDonation`, `ServiceDonation`
- `User`

**WebProtege Classes:**
- `RCXXzqv27uFuX5nYU81XUvw` - Volunteer
- `Rj2A7xNWLfpNcbE4HJMKqN` - Assignment

**Education Domain (edu:):**
- `Personne`, `Etudiant`, `Enseignant`
- `Cours`, `Universite`, `Specialite`
- `Competence`, `ProjetAcademique`
- `RessourcePedagogique`, `TechnologieEducative`

### **Key Properties:**
- Event: `eventTitle`, `eventDate`, `eventDescription`, `maxParticipants`, `isLocatedAt`, `eventStatus`, `eventType`
- Location: `locationName`, `address`, `city`, `country`, `capacity`, `price`, `reserved`, `inRepair`
- Campaign: `campaignName`, `campaignStatus`, `startDate`, `endDate`, `goal`, `targetAmount`, `fundsRaised`
- Volunteer: `phone` (R8BxRbqkCT2nIQCr5UoVlXD), `experience` (R9tdW5crNU837y5TemwdNfR), `skills` (RBqpxvMVBnwM1Wb6OhzTpHf)
- Assignment: `startDate` (RD3Wor03BEPInfzUaMNVPC7), `status` (RDT3XEARggTy1BIBKDXXrmx), `rating` (RRatingAssignment)

---

## 🔐 Configuration & Environment Variables

### **Backend Environment Variables:**
```bash
# Fuseki Configuration
FUSEKI_ENDPOINT=http://localhost:3030/educationInfin

# AI Services
GEMINI_API_KEY=your_gemini_api_key
TALN_API_KEY=your_taln_api_key  # Optional (has fallback)
TALN_API_URL=https://api.taln.fr/v1  # Optional
```

### **Frontend Configuration:**
- API base URL configured in `frontend/src/utils/api.js`
- Default: `http://localhost:5000/api`

---

## 🚀 Setup & Installation

### **1. Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python app.py  # Runs on http://localhost:5000
```

### **2. Frontend Setup:**
```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

### **3. Fuseki Setup:**
```bash
cd fuseki/apache-jena-fuseki-5.6.0
java -jar fuseki-server.jar  # Runs on http://localhost:3030
```

### **4. Load Data:**
```bash
cd scripts
python load_data.py  # Loads RDF data into Fuseki
```

---

## 🧪 Testing & Debugging

### **Test Scripts:**
- `test_taln_integration.py` - Test TALN + Gemini integration
- `debug_taln_integration.py` - Debug TALN pipeline
- `debug_assignments.py` - Debug assignment queries
- `check_property_exists.py` - Check ontology properties

### **Running Tests:**
```bash
# Test TALN + Gemini pipeline
cd backend
python test_taln_integration.py

# Debug specific issues
python debug_taln_integration.py
```

### **Debug Features:**
- Comprehensive logging throughout the pipeline
- TALN analysis visualization in frontend
- SPARQL query display for debugging
- Pipeline statistics and confidence scores

---

## 🔄 Integration Architecture

### **Semantic Search Flow:**
```
User Question
    ↓
TALN Service (Entity Extraction)
    ↓
TALN Analysis (Entities, Intent, Temporal, Location)
    ↓
Gemini SPARQL Transformer
    ↓
SPARQL Query Generation
    ↓
SPARQLUtils (Execute Query)
    ↓
Results + Analysis Metadata
```

### **Key Integration Points:**

1. **TALN → Gemini**
   - TALN extracts structured information
   - Gemini receives structured context (not raw text)
   - Better query accuracy

2. **Gemini → SPARQL**
   - Gemini generates SPARQL using ontology knowledge
   - Validates and fixes common syntax errors
   - Adds defensive patterns for complex queries

3. **SPARQL → Fuseki**
   - Executes queries via SPARQLWrapper
   - Formats results for frontend consumption
   - Handles errors gracefully

---

## 📝 Key Files Reference

### **Backend Core:**
- `app.py` - Main Flask application (360 lines)
- `sparql_utils.py` - SPARQL utilities (58 lines)
- `requirements.txt` - Python dependencies

### **AI Integration:**
- `modules/taln_service.py` - TALN entity extraction (486 lines)
- `modules/gemini_sparql_service.py` - Gemini SPARQL generation (984 lines)
- `modules/search.py` - Search pipeline orchestration (188 lines)

### **Entity Modules:**
- `modules/assignments.py` - Assignment management
- `modules/volunteers.py` - Volunteer management
- `modules/reservations.py` - Reservation management
- `modules/certifications.py` - Certification management
- `modules/sponsors.py` - Sponsor/donation management

### **Frontend Core:**
- `src/App.js` - Main React app
- `src/pages/SemanticSearch.js` - Semantic search UI ⭐
- `src/utils/api.js` - API utilities
- `src/components/Navbar.js` - Navigation

### **Data & Scripts:**
- `data/educationInfin.rdf` - Education ontology RDF
- `scripts/load_data.py` - Data loader (203 lines)

---

## 🐛 Known Issues & Solutions

### **1. Assignment Status Encoding:**
- **Issue:** Status values (`approuvé`/`rejeté`) encoding issues in Fuseki
- **Solution:** Use English values (`approved`/`rejected`) or handle both in SPARQL filters
- **Script:** `add_statuses_one_by_one.py` for manual status addition

### **2. Volunteer Query Filters:**
- **Issue:** `FILTER(BOUND(?skills))` outside WHERE clause
- **Solution:** Use required properties instead of FILTER on OPTIONAL
- **Documentation:** `CORRECTIONS_VOLONTAIRES.md`

### **3. Donation Type Queries:**
- **Issue:** Missing `eco:donationType` on some donations
- **Solution:** Defensive fix makes `donationType` OPTIONAL
- **Location:** `gemini_sparql_service.py` lines 409-414

---

## 📚 Documentation Files

- `README.md` - Basic project overview
- `INTEGRATION_SUCCESS.md` - TALN+Gemini integration details
- `CORRECTIONS_VOLONTAIRES.md` - Volunteer query corrections
- `IMPORTANT_README_STATUS.md` - Assignment status issues
- `TALN_INTEGRATION.md` - TALN integration guide (if exists)
- `TALN_API_ALTERNATIVES.md` - TALN API alternatives (if exists)

---

## 🎯 Project Status

✅ **Working Features:**
- Semantic search with TALN + Gemini pipeline
- Entity extraction (Events, Volunteers, Assignments, Campaigns, etc.)
- SPARQL query generation
- Multiple search methods (main, AI, hybrid)
- Frontend semantic search UI
- All entity management endpoints
- Ontology statistics and visualization

🔧 **In Progress:**
- Assignment status handling (encoding issues)
- Donation query improvements
- Frontend visualization enhancements

---

## 🔍 Quick Reference

### **Common Questions:**
- **Where is the semantic search?** → `backend/modules/search.py` + `frontend/src/pages/SemanticSearch.js`
- **How to add new entity types?** → Update `taln_service.py` entity_keywords + `gemini_sparql_service.py` ontology context
- **Where are SPARQL queries executed?** → `sparql_utils.py` → Fuseki endpoint
- **How to test the pipeline?** → Run `test_taln_integration.py` or use `/api/search` endpoint
- **Where is the ontology?** → `data/educationInfin.rdf` or loaded in Fuseki

---

**Last Updated:** Based on current codebase structure  
**Project Type:** Semantic Web Platform with AI-Powered Natural Language Query  
**License:** (Check repository for license information)


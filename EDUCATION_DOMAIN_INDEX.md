# 🎓 Education Domain - Complete Index

## 📋 Overview

The Education Domain is a comprehensive semantic web platform for managing academic institutions, students, teachers, courses, specializations, and educational resources. This domain uses an OWL ontology (`education-intelligente.org`) stored in Fuseki with the dataset name `educationInfin`.

**Ontology Namespace:** `http://www.education-intelligente.org/ontologie#`  
**Prefixes Used:** `edu:`, `ont:`  
**Fuseki Dataset:** `educationInfin`  
**Backend Endpoint:** `http://localhost:3030/educationInfin`

---

## 📁 Domain Structure

### **Core Entities:**
1. **Personnes** (People) - Students, Teachers, Professors, Assistants
2. **Universites** (Universities) - Public/Private universities
3. **Specialites** (Specializations) - Academic specializations
4. **Cours** (Courses) - Individual courses
5. **Competences** (Competencies) - Skills and competencies
6. **ProjetsAcademiques** (Academic Projects) - Student/Research projects
7. **RessourcesPedagogiques** (Pedagogical Resources) - Educational materials
8. **TechnologiesEducatives** (Educational Technologies) - Tech tools used in education
9. **Evaluations** (Evaluations) - Assessments and exams
10. **OrientationsAcademiques** (Academic Orientations) - Academic paths

---

## 🗄️ Backend API Modules

### ✅ **Fully Implemented Modules**

#### **1. Personnes API** (`backend/modules/personne.py`)
**Status:** ✅ Fully Implemented (209 lines)

**Endpoints:**
- `GET /api/personnes` - Get all people (students, teachers, etc.)
- `GET /api/personnes/<personne_id>` - Get specific person details
- `POST /api/personnes/search` - Search people by criteria
- `GET /api/personnes/etudiants` - Get all students
- `GET /api/personnes/enseignants` - Get all teachers
- `GET /api/personnes/<personne_id>/cours` - Get courses for a person

**SPARQL Features:**
- Supports multiple person types: `Personne`, `Etudiant`, `Enseignant`, `Professeur`, `Assistant`, `Encadrant`, `EtudiantLicence`, `EtudiantMaster`, `EtudiantDoctorat`
- Retrieves: nom, prenom, email, telephone, dateNaissance, role, universite, specialite, cours
- Student-specific: numeroMatricule, niveauEtude, moyenneGenerale
- Teacher-specific: grade, anciennete

**Data Structure:**
```json
{
  "personne": "URI",
  "type": "edu:Etudiant",
  "nom": "string",
  "prenom": "string",
  "email": "string",
  "telephone": "string",
  "role": "string",
  "nomUniversite": "string",
  "niveauEtude": "string",  // Student only
  "moyenneGenerale": "float",  // Student only
  "grade": "string",  // Teacher only
  "anciennete": "int"  // Teacher only
}
```

---

#### **2. Universites API** (`backend/modules/universite_bp.py`)
**Status:** ✅ Fully Implemented (485 lines)

**Endpoints:**
- `GET /api/universites` - Get all universities
- `GET /api/universites/<universite_id>` - Get university details
- `POST /api/universites/search` - Search universities
- `GET /api/universites/<universite_id>/specialites` - Get university specializations
- `GET /api/universites/<universite_id>/enseignants` - Get university teachers
- `GET /api/universites/<universite_id>/etudiants` - Get university students
- `GET /api/universites/<universite_id>/technologies` - Get university technologies
- `GET /api/universites/<universite_id>/projets` - Get university projects
- `GET /api/universites/stats` - Get university statistics
- `GET /api/universites/ranking` - Get university rankings

**SPARQL Features:**
- Supports: `Universite`, `UniversitePublique`, `UniversitePrivee`
- Retrieves: nomUniversite, anneeFondation, ville, pays, nombreEtudiants, rangNational, siteWeb, typeUniversite
- Related entities: specialites, enseignants, etudiants, technologies, projets

**Data Structure:**
```json
{
  "info_generale": {
    "universite": "URI",
    "nomUniversite": "string",
    "anneeFondation": "int",
    "ville": "string",
    "pays": "string",
    "nombreEtudiants": "int",
    "rangNational": "int",
    "siteWeb": "string",
    "typeUniversite": "Publique|Privée|Générale"
  },
  "specialites": [...],
  "enseignants": [...],
  "etudiants": [...],
  "technologies": [...],
  "projets": [...]
}
```

---

#### **3. Specialites API** (`backend/modules/specialite_bp.py`)
**Status:** ✅ Fully Implemented (381 lines)

**Endpoints:**
- `GET /api/specialites` - Get all specializations
- `GET /api/specialites/<specialite_id>` - Get specialization details
- `POST /api/specialites/search` - Search specializations
- `GET /api/specialites/<specialite_id>/cours` - Get specialization courses
- `GET /api/specialites/<specialite_id>/etudiants` - Get specialization students
- `GET /api/specialites/<specialite_id>/competences` - Get specialization competencies
- `GET /api/specialites/stats` - Get specialization statistics
- `GET /api/specialites/par-universite` - Get specializations grouped by university

**SPARQL Features:**
- Supports multiple types: `Specialite`, `SpecialiteInformatique`, `SpecialiteDataScience`, `SpecialiteIngenierie`, `SpecialiteSciences`, `SpecialiteMedecine`, `SpecialiteEconomie`, `SpecialiteDroit`, `SpecialiteLettres`
- Retrieves: nomSpecialite, codeSpecialite, description, dureeFormation, niveauDiplome, nombreModules, universite
- Related entities: cours, competences, etudiants

**Data Structure:**
```json
{
  "info_generale": {
    "specialite": "URI",
    "nomSpecialite": "string",
    "codeSpecialite": "string",
    "description": "string",
    "dureeFormation": "int",
    "niveauDiplome": "string",
    "nombreModules": "int"
  },
  "universite": {...},
  "cours": [...],
  "competences": [...],
  "etudiants": [...]
}
```

---

### ❌ **Missing Backend Modules**

The following entities have frontend pages but **NO backend API implementation**:

1. **Cours** (Courses)
2. **Competences** (Competencies)
3. **ProjetsAcademiques** (Academic Projects)
4. **RessourcesPedagogiques** (Pedagogical Resources)
5. **TechnologiesEducatives** (Educational Technologies)
6. **Evaluations** (Evaluations)
7. **OrientationsAcademiques** (Academic Orientations)

**Impact:** Frontend pages for these entities cannot fetch real data and are currently using placeholder templates.

---

## 🎨 Frontend Pages

### ✅ **Fully Implemented Frontend Pages**

#### **1. Personnes Page** (`frontend/src/pages/education/Personnes/Personnes.js`)
**Status:** ✅ Fully Implemented (1227 lines)

**Features:**
- Complete React component with state management
- Statistics dashboard (Total, Students, Teachers, Others)
- Advanced filtering (Role, University, Study Level, Grade, Search)
- Person cards with detailed information
- Student-specific info display (niveauEtude, moyenneGenerale, numeroMatricule)
- Teacher-specific info display (grade, anciennete)
- Modal for detailed view
- Course association viewing
- Responsive design with styled-components

**API Integration:**
- Uses `personnesAPI.getAll()`
- Uses `personnesAPI.getById()`
- Uses `personnesAPI.getCoursByPersonne()`

**UI Components:**
- Statistics cards
- Filter section with dropdowns and search
- Person grid with cards
- Modal dialog for details
- Loading and error states

---

#### **2. Specialites Page** (`frontend/src/pages/education/Specialites/Specialites.js`)
**Status:** ✅ Fully Implemented (943 lines)

**Features:**
- Complete React component
- Statistics dashboard (Total, by Domain: Informatique, Ingénierie, Sciences)
- Advanced filtering (Domain, University, Level, Search)
- Specialization cards with domain badges
- Domain icons (💻 Informatique, ⚙️ Ingénierie, 🔬 Sciences, 🏥 Médecine, etc.)
- Description display
- Module count display
- Links to courses and details

**API Integration:**
- Uses `specialitesAPI.getAll()`

**UI Components:**
- Statistics cards by domain
- Domain-based filtering
- Specialization grid with cards
- Domain badges with color coding
- Responsive design

---

#### **3. Universites Page** (`frontend/src/pages/education/Universites/Universites.js`)
**Status:** ✅ Fully Implemented (1398 lines)

**Features:**
- Complete React component with advanced functionality
- Statistics dashboard (Total, Public, Private, Total Students)
- Advanced filtering (Type, City, Country, Search)
- University cards with detailed information
- Tabbed modal dialog (Info, Specializations, Teachers, Students)
- Quick stats display (Rank, Students, Foundation Year)
- Links to related entities (specializations, teachers, students)
- Responsive design with styled-components
- Multi-tab detail view with lazy loading of related data

**API Integration:**
- Uses `universitesAPI.getAll()`
- Uses `universitesAPI.getById()`
- Uses `universitesAPI.getSpecialitesByUniversite()`
- Uses `universitesAPI.getEnseignantsByUniversite()`
- Uses `universitesAPI.getEtudiantsByUniversite()`

**UI Components:**
- Statistics cards with icons
- Filter section with dynamic dropdowns
- University grid with cards
- Tabbed modal dialog
- Related entity lists (specializations, teachers, students)
- Loading and error states

---

### ❌ **Placeholder Frontend Pages**

The following pages exist but use the **Campaigns template** (wrong component) and need full implementation:

1. **Cours** (`frontend/src/pages/education/Cours/Cours.js`)
   - Currently shows campaigns template
   - Title says "Cours" but displays campaigns data
   - Needs: Course list, filtering by specialization, semester, credits, etc.

2. **Competences** (`frontend/src/pages/education/Competences/Competences.js`)
   - Currently shows campaigns template
   - Title says "Competences" but displays campaigns data
   - Needs: Competency list, filtering by type, specialization, etc.

3. **ProjetsAcademiques** (`frontend/src/pages/education/ProjetsAcademiques/ProjetsAcademiques.js`)
   - Currently shows campaigns template
   - Title says "Projets Académiques" but displays campaigns data
   - Needs: Project list, filtering by type, university, student, etc.

4. **RessourcesPedagogiques** (`frontend/src/pages/education/RessourcesPedagogiques/RessourcesPedagogiques.js`)
   - Currently shows campaigns template
   - Title says "Ressources Pédagogiques" but displays campaigns data
   - Needs: Resource list, filtering by type, course, etc.

5. **TechnologiesEducatives** (`frontend/src/pages/education/TechnologiesEducatives/TechnologiesEducatives.js`)
   - Currently shows campaigns template
   - Title says "Technologies Éducatives" but displays campaigns data
   - Needs: Technology list, filtering by type, university, etc.

6. **Evaluations** (`frontend/src/pages/education/Evaluations/Evaluations.js`)
   - Currently shows campaigns template
   - Title says "Evaluations" but displays campaigns data
   - Needs: Evaluation list, filtering by course, student, grade, etc.

7. **OrientationsAcademiques** (`frontend/src/pages/education/OrientationsAcademiques/OrientationsAcademiques.js`)
   - Currently shows campaigns template
   - Title says "Orientations Académiques" but displays campaigns data
   - Needs: Orientation paths, filtering by specialization, university, etc.

---

## 🔗 API Client Configuration

**File:** `frontend/src/utils/api.js`

**Available Education APIs:**
```javascript
// Personnes API
personnesAPI.getAll()
personnesAPI.getById(id)
personnesAPI.search(filters)
personnesAPI.getEtudiants()
personnesAPI.getEnseignants()
personnesAPI.getCoursByPersonne(id)
personnesAPI.advancedSearch(criteria)

// Specialites API
specialitesAPI.getAll()
specialitesAPI.getById(id)
specialitesAPI.search(filters)
specialitesAPI.getCoursBySpecialite(id)
specialitesAPI.getEtudiantsBySpecialite(id)
specialitesAPI.getCompetencesBySpecialite(id)
specialitesAPI.getStats()
specialitesAPI.getByUniversite()

// Universites API
universitesAPI.getAll()
universitesAPI.getById(id)
universitesAPI.search(filters)
universitesAPI.getSpecialitesByUniversite(id)
universitesAPI.getEnseignantsByUniversite(id)
universitesAPI.getEtudiantsByUniversite(id)
universitesAPI.getTechnologiesByUniversite(id)
universitesAPI.getProjetsByUniversite(id)
universitesAPI.getStats()
universitesAPI.getRanking()

// Education Statistics API
educationStatsAPI.getOntologyStats()
educationStatsAPI.getEducationStats()
educationStatsAPI.getTestStats()
```

**Missing APIs:**
- `coursAPI` - Not implemented
- `competencesAPI` - Not implemented
- `projetsAPI` - Not implemented
- `ressourcesAPI` - Not implemented
- `technologiesAPI` - Not implemented
- `evaluationsAPI` - Not implemented
- `orientationsAPI` - Not implemented

---

## 🗺️ Ontology Structure

### **Main Classes:**

**Core Entities:**
- `edu:Personne` - Base class for all people
  - Subclasses: `Etudiant`, `Enseignant`, `Professeur`, `Assistant`, `Encadrant`
  - Student subclasses: `EtudiantLicence`, `EtudiantMaster`, `EtudiantDoctorat`

- `edu:Universite` - Universities
  - Subclasses: `UniversitePublique`, `UniversitePrivee`

- `edu:Specialite` - Academic specializations
  - Subclasses: `SpecialiteInformatique`, `SpecialiteDataScience`, `SpecialiteIngenierie`, `SpecialiteSciences`, `SpecialiteMedecine`, `SpecialiteEconomie`, `SpecialiteDroit`, `SpecialiteLettres`

- `edu:Cours` - Courses

- `edu:Competence` - Competencies/Skills

- `edu:ProjetAcademique` - Academic projects

- `edu:RessourcePedagogique` - Pedagogical resources

- `edu:TechnologieEducative` - Educational technologies

- `edu:Evaluation` - Evaluations/Assessments

- `edu:OrientationsAcademiques` - Academic orientations

### **Key Properties:**

**Personne Properties:**
- `edu:nom`, `edu:prenom`, `edu:email`, `edu:telephone`, `edu:dateNaissance`, `edu:role`
- `edu:appartientA` (→ Universite)
- `edu:specialiseEn` (→ Specialite) - for students
- `edu:suitCours` (→ Cours) - for students
- `edu:enseigne` (→ Cours) - for teachers
- `edu:numeroMatricule`, `edu:niveauEtude`, `edu:moyenneGenerale` - student-specific
- `edu:grade`, `edu:anciennete` - teacher-specific

**Universite Properties:**
- `edu:nomUniversite`, `edu:anneeFondation`, `edu:ville`, `edu:pays`
- `edu:nombreEtudiants`, `edu:rangNational`, `edu:siteWeb`
- `edu:offre` (→ Specialite)
- `edu:emploie` (→ Enseignant)
- `edu:adopteTechnologie` (→ TechnologieEducative)

**Specialite Properties:**
- `edu:nomSpecialite`, `edu:codeSpecialite`, `edu:description`
- `edu:dureeFormation`, `edu:niveauDiplome`, `edu:nombreModules`
- `edu:estOffertePar` (→ Universite)
- `edu:faitPartieDe` (→ Cours) [reverse relationship]
- `edu:formePour` (→ Competence)

**Cours Properties:**
- `edu:intitule`, `edu:codeCours`, `edu:creditsECTS`
- `edu:semestre`, `edu:volumeHoraire`, `edu:langueCours`
- `edu:faitPartieDe` (→ Specialite)
- `edu:enseignePar` (→ Enseignant)

---

## 🔄 Data Flow

### **Current Working Flow:**

```
Frontend Page → API Client (api.js) → Backend Blueprint → SPARQL Utils → Fuseki → Results
```

**Example - Personnes:**
```
Personnes.js → personnesAPI.getAll() → /api/personnes → personne_bp.get_all_personnes() 
→ sparql_utils.execute_query() → Fuseki (educationInfin) → JSON Response → Frontend Display
```

---

## 📊 Statistics & Queries

### **Available Statistics Endpoints:**

1. **Ontology Statistics** (`GET /api/ontology-stats`)
   - Total classes, properties, individuals
   - Instance counts by type
   - Ontology metadata

2. **Education Statistics** (`GET /api/education-stats`)
   - Students by level
   - Teachers by grade
   - Courses by specialization

3. **University Statistics** (`GET /api/universites/stats`)
   - Total universities, students, teachers
   - Specializations, technologies counts

4. **Specialization Statistics** (`GET /api/specialites/stats`)
   - Total specializations, students, courses, competencies

---

## ⚠️ Implementation Gaps

### **Critical Missing Components:**

1. **Backend APIs (7 missing):**
   - ❌ Cours API
   - ❌ Competences API
   - ❌ ProjetsAcademiques API
   - ❌ RessourcesPedagogiques API
   - ❌ TechnologiesEducatives API
   - ❌ Evaluations API
   - ❌ OrientationsAcademiques API

2. **Frontend Components (7 placeholders):**
   - ❌ Cours page (using campaigns template)
   - ❌ Competences page (using campaigns template)
   - ❌ ProjetsAcademiques page (using campaigns template)
   - ❌ RessourcesPedagogiques page (using campaigns template)
   - ❌ TechnologiesEducatives page (using campaigns template)
   - ❌ Evaluations page (using campaigns template)
   - ❌ OrientationsAcademiques page (using campaigns template)

3. **API Client Methods:**
   - Missing API client definitions for all 7 entities above

---

## 🚀 Next Steps for Full Implementation

### **Priority 1: Backend APIs**
For each missing entity, create a blueprint module similar to `personne.py`:

1. Create `backend/modules/cours_bp.py`
2. Create `backend/modules/competences_bp.py`
3. Create `backend/modules/projets_bp.py`
4. Create `backend/modules/ressources_bp.py`
5. Create `backend/modules/technologies_bp.py`
6. Create `backend/modules/evaluations_bp.py`
7. Create `backend/modules/orientations_bp.py`

Each should have:
- `GET /api/<entity>` - List all
- `GET /api/<entity>/<id>` - Get details
- `POST /api/<entity>/search` - Search
- Related entity endpoints (e.g., `/api/cours/<id>/etudiants`)

### **Priority 2: Frontend Pages**
Replace placeholder components with full implementations similar to `Personnes.js`:

1. Implement proper data fetching
2. Add statistics dashboard
3. Add filtering and search
4. Add card/grid display
5. Add detail modals

### **Priority 3: API Client**
Add API client methods to `frontend/src/utils/api.js`:

```javascript
export const coursAPI = {
  getAll: () => api.get('/cours'),
  getById: (id) => api.get(`/cours/${id}`),
  search: (filters) => api.post('/cours/search', filters),
  // ... more methods
};
```

### **Priority 4: Register Blueprints**
Update `backend/app.py` to register new blueprints:

```python
from modules.cours_bp import cours_bp
# ... other imports
app.register_blueprint(cours_bp, url_prefix='/api')
# ... other registrations
```

---

## 📝 File Locations Reference

### **Backend:**
- `backend/modules/personne.py` ✅
- `backend/modules/universite_bp.py` ✅
- `backend/modules/specialite_bp.py` ✅
- `backend/modules/cours_bp.py` ❌ (missing)
- `backend/modules/competences_bp.py` ❌ (missing)
- `backend/modules/projets_bp.py` ❌ (missing)
- `backend/modules/ressources_bp.py` ❌ (missing)
- `backend/modules/technologies_bp.py` ❌ (missing)
- `backend/modules/evaluations_bp.py` ❌ (missing)
- `backend/modules/orientations_bp.py` ❌ (missing)

### **Frontend:**
- `frontend/src/pages/education/Personnes/Personnes.js` ✅
- `frontend/src/pages/education/Specialites/Specialites.js` ✅
- `frontend/src/pages/education/Universites/Universites.js` ⚠️ (verify)
- `frontend/src/pages/education/Cours/Cours.js` ❌ (placeholder)
- `frontend/src/pages/education/Competences/Competences.js` ❌ (placeholder)
- `frontend/src/pages/education/ProjetsAcademiques/ProjetsAcademiques.js` ❌ (placeholder)
- `frontend/src/pages/education/RessourcesPedagogiques/RessourcesPedagogiques.js` ❌ (placeholder)
- `frontend/src/pages/education/TechnologiesEducatives/TechnologiesEducatives.js` ❌ (placeholder)
- `frontend/src/pages/education/Evaluations/Evaluations.js` ❌ (placeholder)
- `frontend/src/pages/education/OrientationsAcademiques/OrientationsAcademiques.js` ❌ (placeholder)

### **API Client:**
- `frontend/src/utils/api.js` - Contains `personnesAPI`, `specialitesAPI`, `universitesAPI` ✅

---

## 🔍 Testing & Verification

### **To Test Current Implementation:**

1. **Start Services:**
   ```bash
   # Fuseki (educationInfin dataset)
   java -jar fuseki-server.jar
   
   # Backend
   cd backend
   python app.py
   
   # Frontend
   cd frontend
   npm start
   ```

2. **Test Endpoints:**
   - `http://localhost:5000/api/personnes` ✅
   - `http://localhost:5000/api/universites` ✅
   - `http://localhost:5000/api/specialites` ✅
   - `http://localhost:5000/api/cours` ❌ (not implemented)
   - `http://localhost:5000/api/competences` ❌ (not implemented)

3. **Test Frontend Pages:**
   - `http://localhost:3000/personnes` ✅ (should work)
   - `http://localhost:3000/specialites` ✅ (should work)
   - `http://localhost:3000/cours` ❌ (shows campaigns template)

---

## 📚 Quick Reference

### **What Works:**
- ✅ **Personnes** (People) - Full stack implementation (Backend + Frontend)
- ✅ **Universites** (Universities) - Full stack implementation (Backend + Frontend)
- ✅ **Specialites** (Specializations) - Full stack implementation (Backend + Frontend)
- ✅ Statistics endpoints - Working
- ✅ API client integration - Complete for 3 entities

### **What's Missing:**
- ❌ 7 backend API modules (Cours, Competences, ProjetsAcademiques, RessourcesPedagogiques, TechnologiesEducatives, Evaluations, OrientationsAcademiques)
- ❌ 7 frontend page implementations (using wrong Campaigns template instead of proper components)
- ❌ 7 API client definitions in `api.js`

### **Architecture Pattern:**
```
Frontend Component (React)
  ↓
API Client Method (api.js)
  ↓
Backend Blueprint Route (Flask)
  ↓
SPARQL Query Builder
  ↓
SPARQL Utils (execute_query)
  ↓
Fuseki (educationInfin dataset)
  ↓
RDF/OWL Data
```

---

**Last Updated:** Based on current codebase analysis  
**Status:** Partially Implemented (3/10 entities fully working)  
**Completion:** ~30% of education domain implemented

### **Implementation Summary:**
- ✅ **3 Entities Fully Implemented:** Personnes, Universites, Specialites
- ❌ **7 Entities Missing Backend:** Cours, Competences, ProjetsAcademiques, RessourcesPedagogiques, TechnologiesEducatives, Evaluations, OrientationsAcademiques
- ❌ **7 Frontend Pages Using Wrong Template:** Need proper React components instead of Campaigns template
- 📊 **Backend:** 3/10 modules implemented (30%)
- 🎨 **Frontend:** 3/10 pages fully implemented (30%)
- 🔗 **API Client:** 3/10 API definitions implemented (30%)


# CRUD Implementation Guide for Education Entities

This guide shows how to add CRUD (Create, Read, Update, Delete) functionality to all education entities.

## ✅ Completed

- ✅ Backend CRUD modules created for all 10 entities
- ✅ Validation functions in `backend/modules/validators.py`
- ✅ API client updated with all CRUD endpoints
- ✅ Reusable CRUDModal component created
- ✅ Personnes - CRUD implemented
- ✅ Specialites - CRUD implemented

## 📋 Remaining Entities to Implement

1. **Universites** 
2. **Cours**
3. **Competences**
4. **ProjetsAcademiques**
5. **RessourcesPedagogiques**
6. **TechnologiesEducatives**
7. **Evaluations**
8. **OrientationsAcademiques**

## 🔧 Implementation Pattern

For each entity, add the following to the React component:

### 1. Import CRUDModal and API
```javascript
import CRUDModal from '../../../components/CRUDModal';
import { [entity]API } from '../../../utils/api'; // e.g., coursAPI, competencesAPI
```

### 2. Add State for Modals
```javascript
const [modalState, setModalState] = useState({
  isOpen: false,
  mode: null, // 'add', 'edit', 'delete'
  data: {}
});
const [submitLoading, setSubmitLoading] = useState(false);
```

### 3. Add CRUD Handlers
```javascript
const handleCreate = async (data) => {
  setSubmitLoading(true);
  try {
    await [entity]API.create(data);
    await fetch[Entity](); // Refresh data
  } finally {
    setSubmitLoading(false);
  }
};

const handleUpdate = async (data) => {
  setSubmitLoading(true);
  try {
    await [entity]API.update(data.[entity], data); // data.[entity] is the ID field
    await fetch[Entity]();
  } finally {
    setSubmitLoading(false);
  }
};

const handleDelete = async (data) => {
  setSubmitLoading(true);
  try {
    await [entity]API.delete(data.[entity]);
    await fetch[Entity]();
  } finally {
    setSubmitLoading(false);
  }
};

const handleModalSubmit = async (formData) => {
  if (modalState.mode === 'add') {
    await handleCreate(formData);
  } else if (modalState.mode === 'edit') {
    await handleUpdate(formData);
  } else if (modalState.mode === 'delete') {
    await handleDelete(formData);
  }
};
```

### 4. Define Form Fields
```javascript
const [entity]Fields = [
  { name: 'fieldName', label: 'Field Label', type: 'text', required: true },
  { name: 'fieldName2', label: 'Field Label 2', type: 'select', options: [
    { value: 'val1', label: 'Label 1' },
    { value: 'val2', label: 'Label 2' }
  ] },
  // ... more fields
];
```

### 5. Add "Add" Button in Header
```javascript
<div style={{ display: 'flex', gap: '8px' }}>
  <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
    ➕ Ajouter
  </button>
  <button className="btn-refresh" onClick={fetch[Entity]} title="Actualiser">
    🔄
  </button>
</div>
```

### 6. Add Edit/Delete Buttons in Card Actions
```javascript
<div className="card-actions">
  {/* Existing buttons */}
  <button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: item })}>
    ✏️
  </button>
  <button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: item })}>
    🗑️
  </button>
</div>
```

### 7. Add Modal Components Before Closing `</div>`
```javascript
{/* CRUD Modals */}
<CRUDModal
  isOpen={modalState.isOpen && modalState.mode !== 'delete'}
  onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
  mode={modalState.mode}
  title={modalState.mode === 'add' ? `Ajouter un(e) [entity]` : `Modifier un(e) [entity]`}
  data={modalState.data}
  onSubmit={handleModalSubmit}
  fields={[entity]Fields}
  loading={submitLoading}
/>

<CRUDModal
  isOpen={modalState.isOpen && modalState.mode === 'delete'}
  onClose={() => setModalState({ isOpen: false, mode: null, data: {} })}
  mode="delete"
  title={`Supprimer un(e) [entity]`}
  data={modalState.data}
  onSubmit={handleModalSubmit}
  loading={submitLoading}
/>
```

### 8. Add CSS Styles
```javascript
.btn-add {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-edit, .btn-delete {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  background: #fbbf24;
  color: white;
}

.btn-edit:hover {
  background: #f59e0b;
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
}

.card-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
```

## 📝 Entity-Specific Field Definitions

### Universites Fields
```javascript
const universiteFields = [
  { name: 'nomUniversite', label: 'Nom de l\'université', type: 'text', required: true },
  { name: 'type', label: 'Type', type: 'select', options: [
    { value: 'Publique', label: 'Publique' },
    { value: 'Privée', label: 'Privée' }
  ] },
  { name: 'anneeFondation', label: 'Année de fondation', type: 'number', min: '1800', max: '2024' },
  { name: 'ville', label: 'Ville', type: 'text' },
  { name: 'pays', label: 'Pays', type: 'text' },
  { name: 'nombreEtudiants', label: 'Nombre d\'étudiants', type: 'number', min: '0' },
  { name: 'rangNational', label: 'Rang national', type: 'number', min: '1' },
  { name: 'siteWeb', label: 'Site web', type: 'url', placeholder: 'https://...' }
];
```

### Cours Fields
```javascript
const coursFields = [
  { name: 'intitule', label: 'Intitulé', type: 'text', required: true },
  { name: 'codeCours', label: 'Code cours', type: 'text', required: true, placeholder: 'Ex: INF101' },
  { name: 'creditsECTS', label: 'Credits ECTS', type: 'number', min: '0', max: '30' },
  { name: 'semestre', label: 'Semestre', type: 'text', placeholder: 'S1, S2, etc.' },
  { name: 'volumeHoraire', label: 'Volume horaire', type: 'number', min: '0' },
  { name: 'langueCours', label: 'Langue', type: 'text', placeholder: 'Français, Anglais, etc.' }
];
```

### Competences Fields
```javascript
const competenceFields = [
  { name: 'nomCompetence', label: 'Nom de la compétence', type: 'text', required: true },
  { name: 'typeCompetence', label: 'Type', type: 'select', options: [
    { value: 'Technique', label: 'Technique' },
    { value: 'Transversale', label: 'Transversale' },
    { value: 'Recherche', label: 'Recherche' }
  ] },
  { name: 'niveauCompetence', label: 'Niveau', type: 'text', placeholder: 'Débutant, Intermédiaire, Avancé' },
  { name: 'descriptionCompetence', label: 'Description', type: 'textarea', rows: 4 },
  { name: 'motsCles', label: 'Mots-clés', type: 'text', placeholder: 'Séparés par des virgules' }
];
```

### ProjetsAcademiques Fields
```javascript
const projetFields = [
  { name: 'titreProjet', label: 'Titre du projet', type: 'text', required: true },
  { name: 'domaineProjet', label: 'Domaine', type: 'text' },
  { name: 'typeProjet', label: 'Type', type: 'text', placeholder: 'Recherche, Stage, etc.' },
  { name: 'noteProjet', label: 'Note', type: 'number', step: '0.1', min: '0', max: '20' }
];
```

### RessourcesPedagogiques Fields
```javascript
const ressourceFields = [
  { name: 'titreRessource', label: 'Titre de la ressource', type: 'text', required: true },
  { name: 'typeRessource', label: 'Type', type: 'select', options: [
    { value: 'Article scientifique', label: 'Article scientifique' },
    { value: 'Livre', label: 'Livre' },
    { value: 'Vidéo', label: 'Vidéo' },
    { value: 'Documentation', label: 'Documentation' }
  ] }
];
```

### TechnologiesEducatives Fields
```javascript
const technologieFields = [
  { name: 'nomTechnologie', label: 'Nom de la technologie', type: 'text', required: true },
  { name: 'typeTechnologie', label: 'Type', type: 'select', options: [
    { value: 'Application Mobile', label: 'Application Mobile' },
    { value: 'Plateforme en ligne', label: 'Plateforme en ligne' },
    { value: 'Outil de gestion', label: 'Outil de gestion' }
  ] }
];
```

### Evaluations Fields
```javascript
const evaluationFields = [
  { name: 'typeEvaluation', label: 'Type d\'évaluation', type: 'text', required: true, placeholder: 'Contrôle continu, Examen, etc.' },
  { name: 'dateEvaluation', label: 'Date', type: 'date' }
];
```

### OrientationsAcademiques Fields
```javascript
const orientationFields = [
  { name: 'objectifOrientation', label: 'Objectif', type: 'textarea', rows: 4, required: true },
  { name: 'typeOrientation', label: 'Type', type: 'text', placeholder: 'Stage, Carrière, etc.' },
  { name: 'dateOrientation', label: 'Date', type: 'date' }
];
```

## 🎯 ID Field Names for Update/Delete

Each entity uses a different field name for the ID:
- **Personnes**: `data.personne`
- **Specialites**: `data.specialite`
- **Universites**: `data.universite`
- **Cours**: `data.cours`
- **Competences**: `data.competence`
- **Projets**: `data.projet`
- **Ressources**: `data.ressource`
- **Technologies**: `data.technologie`
- **Evaluations**: `data.evaluation`
- **Orientations**: `data.orientation`

## ✅ Validation

All backend endpoints return validation errors in this format:
```json
{
  "errors": {
    "fieldName": "Error message",
    "fieldName2": "Error message 2"
  }
}
```

The CRUDModal component automatically displays these errors inline below each field.

## 📦 Backend Status

All backend CRUD endpoints are implemented and registered in `app.py`:
- ✅ `cours_bp` - `/api/cours`
- ✅ `competences_bp` - `/api/competences`
- ✅ `projets_bp` - `/api/projets-academiques`
- ✅ `ressources_bp` - `/api/ressources-pedagogiques`
- ✅ `technologies_bp` - `/api/technologies-educatives`
- ✅ `evaluations_bp` - `/api/evaluations`
- ✅ `orientations_bp` - `/api/orientations-academiques`
- ✅ `personne_bp` - `/api/personnes` (with CRUD)
- ✅ `specialite_bp` - `/api/specialites` (with CRUD)
- ✅ `universite_bp` - `/api/universites` (with CRUD)


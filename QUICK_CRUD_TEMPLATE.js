/**
 * QUICK TEMPLATE FOR ADDING CRUD TO REMAINING ENTITIES
 * 
 * Copy this template and customize for: Competences, ProjetsAcademiques, 
 * RessourcesPedagogiques, TechnologiesEducatives, Evaluations, OrientationsAcademiques
 * 
 * ===== STEP 1: ADD IMPORTS =====
 */
import CRUDModal from '../../../components/CRUDModal';
import { [ENTITY]API } from '../../../utils/api'; // e.g., competencesAPI, projetsAPI

/**
 * ===== STEP 2: ADD STATE =====
 * Add after existing useState declarations
 */
const [modalState, setModalState] = useState({
  isOpen: false,
  mode: null, // 'add', 'edit', 'delete'
  data: {}
});
const [submitLoading, setSubmitLoading] = useState(false);

/**
 * ===== STEP 3: ADD CRUD HANDLERS =====
 * Add after clearFilters or similar function
 */
// CRUD Handlers
const handleCreate = async (data) => {
  setSubmitLoading(true);
  try {
    await [ENTITY]API.create(data);
    await fetch[ENTITY](); // Refresh data
  } finally {
    setSubmitLoading(false);
  }
};

const handleUpdate = async (data) => {
  setSubmitLoading(true);
  try {
    await [ENTITY]API.update(data.[entity], data); // entity = competence, projet, etc.
    await fetch[ENTITY]();
  } finally {
    setSubmitLoading(false);
  }
};

const handleDelete = async (data) => {
  setSubmitLoading(true);
  try {
    await [ENTITY]API.delete(data.[entity]);
    await fetch[ENTITY]();
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

/**
 * ===== STEP 4: DEFINE FIELDS =====
 * Define form fields for the entity (see CRUD_IMPLEMENTATION_GUIDE.md for examples)
 */
const [entity]Fields = [
  // Define fields based on entity properties
  // See CRUD_IMPLEMENTATION_GUIDE.md for complete field definitions
];

/**
 * ===== STEP 5: ADD BUTTON IN HEADER =====
 * Replace the refresh button section with:
 */
<div style={{ display: 'flex', gap: '8px' }}>
  <button className="btn-add" onClick={() => setModalState({ isOpen: true, mode: 'add', data: {} })}>
    ➕ Ajouter
  </button>
  <button className="btn-refresh" onClick={fetch[ENTITY]} title="Actualiser">
    🔄
  </button>
</div>

/**
 * ===== STEP 6: ADD EDIT/DELETE BUTTONS =====
 * In card-actions section, add:
 */
<button className="btn-edit" onClick={() => setModalState({ isOpen: true, mode: 'edit', data: item })}>
  ✏️
</button>
<button className="btn-delete" onClick={() => setModalState({ isOpen: true, mode: 'delete', data: item })}>
  🗑️
</button>

/**
 * ===== STEP 7: ADD MODAL COMPONENTS =====
 * Before closing </div> tag, add:
 */
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

/**
 * ===== STEP 8: ADD CSS STYLES =====
 * Add to existing <style> block before closing:
 */
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

/**
 * ===== ENTITY-SPECIFIC NOTES =====
 * 
 * Competences: ID field = data.competence
 * ProjetsAcademiques: ID field = data.projet
 * RessourcesPedagogiques: ID field = data.ressource
 * TechnologiesEducatives: ID field = data.technologie
 * Evaluations: ID field = data.evaluation
 * OrientationsAcademiques: ID field = data.orientation
 */


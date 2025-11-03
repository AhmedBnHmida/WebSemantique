import React, { useState, useEffect } from 'react';
import './CRUDModal.css';

const CRUDModal = ({ 
  isOpen, 
  onClose, 
  mode, // 'add', 'edit', 'delete'
  title,
  data = {},
  onSubmit,
  fields = [],
  children,
  loading = false
}) => {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (mode === 'edit' || mode === 'delete') {
      setFormData(data);
    } else {
      setFormData({});
    }
    setErrors({});
  }, [isOpen, mode, data]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors);
      } else {
        setErrors({ submit: error.message || 'Une erreur est survenue' });
      }
    }
  };

  const handleDelete = async () => {
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors);
      } else {
        setErrors({ submit: error.message || 'Une erreur est survenue' });
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="crud-modal-overlay" onClick={onClose}>
      <div className="crud-modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="crud-modal-header">
          <h2 className="crud-modal-title">{title}</h2>
          <button className="crud-modal-close" onClick={onClose}>×</button>
        </div>

        <div className="crud-modal-body">
          {mode === 'delete' ? (
            <div className="crud-modal-delete">
              <p>Êtes-vous sûr de vouloir supprimer cet élément ?</p>
              <p className="crud-modal-delete-warning">Cette action est irréversible.</p>
              {errors.submit && (
                <div className="crud-error-message">{errors.submit}</div>
              )}
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {children ? children(formData, handleChange, errors) : (
                fields.map((field) => (
                  <div key={field.name} className="crud-form-group">
                    <label className="crud-form-label">
                      {field.label}
                      {field.required && <span className="crud-required">*</span>}
                    </label>
                    {field.type === 'textarea' ? (
                      <textarea
                        className={`crud-form-input ${errors[field.name] ? 'crud-error' : ''}`}
                        value={formData[field.name] || ''}
                        onChange={(e) => handleChange(field.name, e.target.value)}
                        placeholder={field.placeholder}
                        required={field.required}
                        rows={field.rows || 3}
                      />
                    ) : field.type === 'select' ? (
                      <select
                        className={`crud-form-input ${errors[field.name] ? 'crud-error' : ''}`}
                        value={formData[field.name] || ''}
                        onChange={(e) => handleChange(field.name, e.target.value)}
                        required={field.required}
                      >
                        <option value="">Sélectionner...</option>
                        {field.options?.map(opt => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={field.type || 'text'}
                        className={`crud-form-input ${errors[field.name] ? 'crud-error' : ''}`}
                        value={formData[field.name] || ''}
                        onChange={(e) => handleChange(field.name, e.target.value)}
                        placeholder={field.placeholder}
                        required={field.required}
                        min={field.min}
                        max={field.max}
                        step={field.step}
                      />
                    )}
                    {errors[field.name] && (
                      <div className="crud-error-message">{errors[field.name]}</div>
                    )}
                  </div>
                ))
              )}
              {errors.submit && (
                <div className="crud-error-message">{errors.submit}</div>
              )}
            </form>
          )}
        </div>

        <div className="crud-modal-footer">
          <button 
            type="button" 
            className="crud-button crud-button-cancel" 
            onClick={onClose}
            disabled={loading}
          >
            Annuler
          </button>
          {mode === 'delete' ? (
            <button 
              type="button" 
              className="crud-button crud-button-delete" 
              onClick={handleDelete}
              disabled={loading}
            >
              {loading ? 'Suppression...' : 'Supprimer'}
            </button>
          ) : (
            <button 
              type="submit" 
              className="crud-button crud-button-submit" 
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Enregistrement...' : mode === 'add' ? 'Créer' : 'Mettre à jour'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CRUDModal;


import React from 'react';
import './DetailsModal.css';

const DetailsModal = ({ isOpen, onClose, title, data, fields = [] }) => {
  if (!isOpen || !data) return null;

  return (
    <div className="details-modal-overlay" onClick={onClose}>
      <div className="details-modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="details-modal-header">
          <h2 className="details-modal-title">{title}</h2>
          <button className="details-modal-close" onClick={onClose}>×</button>
        </div>

        <div className="details-modal-body">
          {fields.length > 0 ? (
            <div className="details-grid">
              {fields.map((field) => {
                const value = data[field.name];
                if (field.hideIfEmpty && !value) return null;
                
                const displayValue = field.format ? field.format(value) : (value || 'Non spécifié');

                return (
                  <div key={field.name} className="detail-item">
                    <label className="detail-label">{field.label}:</label>
                    <span className="detail-value">{displayValue}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="details-grid">
              {Object.entries(data).map(([key, value]) => {
                if (key === 'id' || key === 'uri' || key.includes('URI') || typeof value === 'object' || Array.isArray(value)) return null;
                return (
                  <div key={key} className="detail-item">
                    <label className="detail-label">{key}:</label>
                    <span className="detail-value">{value || 'Non spécifié'}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="details-modal-footer">
          <button className="details-modal-button" onClick={onClose}>
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};

export default DetailsModal;


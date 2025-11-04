import React, { useState } from 'react';
import { searchAPI } from '../utils/api';
import './SemanticSearch.css';

const SemanticSearch = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [sparqlQuery, setSparqlQuery] = useState(null);
  const [talnAnalysis, setTalnAnalysis] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setSparqlQuery(null);
    setTalnAnalysis(null);

    try {
      const response = await searchAPI.semanticSearch(question);
      const data = response.data;

      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.results || []);
        setSparqlQuery(data.sparql_query);
        setTalnAnalysis(data.taln_analysis);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.error || 'An error occurred during search');
    } finally {
      setLoading(false);
    }
  };

  const exampleQuestions = [
    "Quels sont tous les étudiants?",
    "Montre-moi les universités à Tunis",
    "Combien d'enseignants y a-t-il?",
    "Quels cours sont enseignés par l'enseignant X?",
    "Trouve les spécialités en informatique",
    "Quels projets académiques sont actifs?",
    "Montre-moi toutes les ressources pédagogiques",
  ];

  const handleExampleClick = (example) => {
    setQuestion(example);
  };

  // Format SPARQL query with better indentation
  const formatSparqlQuery = (query) => {
    if (!query) return '';
    
    // Basic formatting: add line breaks after keywords
    let formatted = query
      .replace(/\s+PREFIX\s+/gi, '\nPREFIX ')
      .replace(/\s+SELECT\s+/gi, '\nSELECT ')
      .replace(/\s+WHERE\s+/gi, '\nWHERE ')
      .replace(/\s+OPTIONAL\s+/gi, '\n  OPTIONAL ')
      .replace(/\s+UNION\s+/gi, '\n  UNION ')
      .replace(/\s+FILTER\s+/gi, '\n  FILTER ')
      .replace(/\s+ORDER BY\s+/gi, '\nORDER BY ')
      .replace(/\s+LIMIT\s+/gi, '\nLIMIT ')
      .replace(/\s+GROUP BY\s+/gi, '\nGROUP BY ')
      .replace(/\{\s+/g, '{\n    ')
      .replace(/\s+\}/g, '\n  }')
      .trim();
    
    return formatted;
  };

  // Format field names for display
  const formatFieldName = (name) => {
    // Remove common prefixes and format
    return name
      .replace(/^[?]/, '')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .replace(/^\w/, c => c.toUpperCase());
  };

  // Format cell values for display
  const formatCellValue = (value) => {
    if (value === null || value === undefined) return <span className="null-value">N/A</span>;
    if (typeof value === 'object') {
      return <pre className="cell-json">{JSON.stringify(value, null, 2)}</pre>;
    }
    const str = String(value);
    // If it's a URI, make it shorter
    if (str.startsWith('http://') || str.startsWith('https://')) {
      const short = str.split('/').pop() || str.split('#').pop() || str;
      return <span className="uri-value" title={str}>{short}</span>;
    }
    // If it's very long, truncate it
    if (str.length > 100) {
      return <span title={str}>{str.substring(0, 100)}...</span>;
    }
    return str;
  };

  // Copy to clipboard function
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Requête SPARQL copiée dans le presse-papiers!');
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Requête SPARQL copiée!');
    }
  };

  return (
    <div className="semantic-search-container">
      <div className="search-header">
        <h1>🔍 Recherche Sémantique</h1>
        <p className="subtitle">
          Posez une question en langage naturel et obtenez des résultats de votre base de données éducative.
          <br />
          La recherche utilise AI pour générer des requêtes SPARQL automatiquement.
        </p>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Exemple: Quels sont tous les étudiants en informatique?"
            className="search-input"
            disabled={loading}
          />
          <button type="submit" className="search-button" disabled={loading}>
            {loading ? '⏳ Recherche...' : '🔍 Rechercher'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          <strong>Erreur:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="loading-message">
          <div className="spinner"></div>
          <p>Génération et exécution de la requête SPARQL...</p>
        </div>
      )}

      {results && (
        <div className="results-container">
          <div className="results-header">
            <h2>📊 Résultats ({results.length})</h2>
            
            {/* TALN Analysis - Prettier Display */}
            {talnAnalysis && (
              <details className="taln-details" open>
                <summary>🧠 Analyse TALN (entités détectées)</summary>
                <div className="taln-analysis-container">
                  {talnAnalysis.entities && talnAnalysis.entities.length > 0 && (
                    <div className="taln-section">
                      <h3 className="taln-section-title">📌 Entités ({talnAnalysis.entities.length})</h3>
                      <div className="entities-grid">
                        {talnAnalysis.entities.map((entity, idx) => (
                          <div key={idx} className="entity-card">
                            <div className="entity-header">
                              <span className="entity-text">{entity.text || entity.entity || 'N/A'}</span>
                              <span className="entity-confidence">{Math.round((entity.confidence || 0) * 100)}%</span>
                            </div>
                            <div className="entity-details">
                              <div className="entity-detail-item">
                                <strong>Type:</strong> {entity.type || 'N/A'}
                              </div>
                              {entity.ontology_class && (
                                <div className="entity-detail-item">
                                  <strong>Classe Ontologie:</strong> 
                                  <code className="ontology-code">{entity.ontology_class}</code>
                                </div>
                              )}
                              {entity.category && (
                                <div className="entity-detail-item">
                                  <strong>Catégorie:</strong> {entity.category}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {talnAnalysis.intent && (
                    <div className="taln-section">
                      <h3 className="taln-section-title">🎯 Intention</h3>
                      <div className="intent-card">
                        <div className="intent-item">
                          <strong>Intention principale:</strong> 
                          <span className="intent-value">{talnAnalysis.intent.primary_intent || 'N/A'}</span>
                        </div>
                        {talnAnalysis.intent.query_type && (
                          <div className="intent-item">
                            <strong>Type de requête:</strong> 
                            <span className="intent-value">{talnAnalysis.intent.query_type}</span>
                          </div>
                        )}
                        {talnAnalysis.intent.confidence && (
                          <div className="intent-item">
                            <strong>Confiance:</strong> 
                            <span className="intent-value">{Math.round(talnAnalysis.intent.confidence * 100)}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {talnAnalysis.temporal_info && Object.keys(talnAnalysis.temporal_info).length > 0 && (
                    <div className="taln-section">
                      <h3 className="taln-section-title">⏰ Information Temporelle</h3>
                      <div className="temporal-card">
                        {talnAnalysis.temporal_info.relative_time && (
                          <div className="temporal-item">
                            <strong>Temps relatif:</strong> {talnAnalysis.temporal_info.relative_time}
                          </div>
                        )}
                        {talnAnalysis.temporal_info.time_expressions && talnAnalysis.temporal_info.time_expressions.length > 0 && (
                          <div className="temporal-item">
                            <strong>Expressions temporelles:</strong> 
                            {talnAnalysis.temporal_info.time_expressions.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {talnAnalysis.location_info && talnAnalysis.location_info.locations && talnAnalysis.location_info.locations.length > 0 && (
                    <div className="taln-section">
                      <h3 className="taln-section-title">📍 Localisations</h3>
                      <div className="location-card">
                        <strong>Lieux détectés:</strong> 
                        <div className="locations-list">
                          {talnAnalysis.location_info.locations.map((loc, idx) => (
                            <span key={idx} className="location-tag">{loc}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {talnAnalysis.keywords && talnAnalysis.keywords.length > 0 && (
                    <div className="taln-section">
                      <h3 className="taln-section-title">🔑 Mots-clés ({talnAnalysis.keywords.length})</h3>
                      <div className="keywords-list">
                        {talnAnalysis.keywords.map((kw, idx) => (
                          <span key={idx} className="keyword-tag">
                            {kw.text || kw}
                            {kw.importance && <span className="keyword-importance"> ({Math.round(kw.importance * 100)}%)</span>}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </details>
            )}

            {/* SPARQL Query - Prettier Display */}
            {sparqlQuery && (
              <details className="sparql-details" open>
                <summary>📝 Requête SPARQL générée</summary>
                <div className="sparql-container">
                  <pre className="sparql-query">{formatSparqlQuery(sparqlQuery)}</pre>
                  <button 
                    className="copy-button" 
                    onClick={() => copyToClipboard(sparqlQuery)}
                    title="Copier la requête"
                  >
                    📋 Copier
                  </button>
                </div>
              </details>
            )}
          </div>

          {results.length === 0 ? (
            <div className="no-results">
              <p>Aucun résultat trouvé pour cette question.</p>
            </div>
          ) : (
            <div className="results-table-wrapper">
              <div className="results-table">
                <table>
                  <thead>
                    <tr>
                      {results[0] && Object.keys(results[0]).map((key) => (
                        <th key={key} title={key}>{formatFieldName(key)}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, index) => (
                      <tr key={index}>
                        {Object.entries(row).map(([key, value], colIndex) => (
                          <td key={colIndex} className="table-cell" title={String(value)}>
                            {formatCellValue(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="examples-section">
        <h3>💡 Exemples de questions</h3>
        <div className="examples-grid">
          {exampleQuestions.map((example, index) => (
            <button
              key={index}
              className="example-button"
              onClick={() => handleExampleClick(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SemanticSearch;


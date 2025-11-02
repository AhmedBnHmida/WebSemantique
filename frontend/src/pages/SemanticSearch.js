import React, { useState } from 'react';
import { searchAPI } from '../utils/api';
import './SemanticSearch.css';

const SemanticSearch = () => {
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const categorizedSuggestions = {
    "Campagnes": [
      "Quelles sont les campagnes actives ?",
      "Montre-moi les campagnes de nettoyage",
      "Quelles campagnes de sensibilisation existent ?",
      "Quelles campagnes de financement sont disponibles ?",
      "Combien y a-t-il de campagnes par type ?",
      "Quel est le nombre total de campagnes ?",
      "Trier les campagnes par date de début"
    ],
    "Ressources": [
      "Quelles ressources humaines sont disponibles ?",
      "Montre-moi les ressources matérielles",
      "Quels équipements sont disponibles ?",
      "Quelles ressources financières avons-nous ?",
      "Quelles ressources numériques existent ?",
      "Combien y a-t-il de ressources par catégorie ?",
      "Quel est le nombre total de ressources ?",
      "Trier les ressources par coût"
    ],
    "Événements": [
      "Tous les événements",
      "Événements à venir",
      "Événements passés",
      "Événements éducatifs",
      "Événements compétitifs",
      "Événements de divertissement",
      "Événements de socialisation",
      "Qui organise les événements ?",
      "Montre-moi les organisateurs d'événements",
    ],
    "Locations": [
      "Où se déroulent les événements ?",
      "Quels événements ont lieu à Paris ?",
      "Événements ont lieu à New York ",
      "Locations disponibles",
      "Locations à Boston",
    ],
    "Volontaires": [
    "Quels sont les volontaires ?",
    "Quelles sont les compétences des volontaires ?",
    "Quels volontaires ont de l'expérience ?",
    "Quels sont les contacts des volontaires ?"
    ],
    "assignements":
    [
        "Quels sont les assignements ?",
    "Quels assignements sont approuvés ?",
    "Quels assignements sont rejetés ?",
    "Quelles sont les notes des assignements ?",
    "Statistiques des assignements"
    ],
    "Certificats": [
      "Quelles certifications ont été émises ?",
      "Qui a reçu des certifications ?",
      "Quels types de certifications existent ?",
      "Montre-moi les certifications par points",
      "Qui émet les certifications ?"
    ],
    "Réservations": [
      "Quelles réservations sont confirmées ?",
      "Qui a fait des réservations ?",
      "Quelles réservations sont en attente ?",
      "Montre-moi les réservations par événement",
    ],
    "Sponsors": [
      "Qui sont les sponsors ?",
      "Quels sponsors ont fait des donations ?",
      "Quels sponsors de l'industrie Environmental Services ?",
      "Quels sponsors de niveau Gold ?",
      "Contact des sponsors",
      "Liste des sponsors avec niveau"
    ],
    "Donations": [
      "Quelles sont les donations ?",
      "Quelles sont les donations les plus récentes ?",
      "Quelles donations de type FinancialDonation ?",
      "Quelles donations de type MaterialDonation ?",
      "Quelles donations ont financé un événement ?",
      "Quelles sont les dernières donations ?",
      "Qui a fait des donations ?"
    ]
  };
  
  

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await searchAPI.semanticSearch(question);
      setResults(response.data);
      
      // Log TALN analysis for debugging
      if (response.data.taln_analysis) {
        console.log('🔍 TALN Analysis:', response.data.taln_analysis);
        console.log('📊 Pipeline Info:', response.data.pipeline_info);
      }
      
      // DEBUG: Voir la structure complète de la réponse
      console.log('🔍 FULL RESPONSE STRUCTURE:', response.data);
      console.log('📊 Results key:', response.data.results);
      console.log('🔎 Results type:', typeof response.data.results);
      
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      setResults({ error: 'Erreur lors de la recherche sémantique' });
    }
    setLoading(false);
  };

  const handleSuggestionClick = (suggestion) => {
    // Set the suggestion and run the search immediately
    setQuestion(suggestion);
    (async () => {
      setLoading(true);
      try {
        const response = await searchAPI.semanticSearch(suggestion);
        setResults(response.data);
      } catch (error) {
        console.error('Erreur lors de la recherche:', error);
        setResults({ error: 'Erreur lors de la recherche sémantique' });
      }
      setLoading(false);
    })();
  };

  // Fonction pour afficher les résultats de comptage
  const renderCountResults = (resultsData) => {
    // Vérifier que resultsData est un tableau
    if (!Array.isArray(resultsData) || resultsData.length === 0) {
      return null;
    }

    console.log('🔢 COUNT RESULTS DATA:', resultsData[0]);

    // Résultat de comptage total campagnes (format string direct)
    if (resultsData.length === 1 && resultsData[0].hasOwnProperty('totalCampaigns')) {
      const count = resultsData[0].totalCampaigns;
      return (
        <div className="count-result">
          <h4>🎯 Nombre total de campagnes: <span className="count-number">{count}</span></h4>
        </div>
      );
    }
    
    // Résultat de comptage total ressources (format string direct)
    if (resultsData.length === 1 && resultsData[0].hasOwnProperty('totalResources')) {
      const count = resultsData[0].totalResources;
      return (
        <div className="count-result">
          <h4>🎯 Nombre total de ressources: <span className="count-number">{count}</span></h4>
        </div>
      );
    }
    
    // Résultat de comptage par type/catégorie (format string direct)
    if (resultsData.some(row => row.hasOwnProperty('count'))) {
      return (
        <div className="count-results">
          <h4>📊 Répartition:</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Catégorie/Type</th>
                <th>Nombre</th>
              </tr>
            </thead>
            <tbody>
              {resultsData.map((row, index) => {
                const type = row.type || row.category || 'Non catégorisé';
                const count = row.count;
                
                return (
                  <tr key={index}>
                    <td>{type}</td>
                    <td className="count-number">{count}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      );
    }
    
    return null;
  };

  const renderResults = () => {
    if (!results) return null;
    
    if (results.error) {
      return <div className="error">Erreur: {results.error}</div>;
    }

    // DEBUG: Afficher la structure complète
    console.log('🔍 RENDERING RESULTS:', results);

    // Extraire les données des résultats selon différents formats possibles
    let resultsData = [];
    
    // Format 1: Standard SPARQL (results.bindings)
    if (results.results && results.results.results && results.results.results.bindings) {
      resultsData = results.results.results.bindings;
      console.log('📊 Using format 1: results.results.results.bindings');
    }
    // Format 2: Tableau direct dans results
    else if (Array.isArray(results.results)) {
      resultsData = results.results;
      console.log('📊 Using format 2: Array results.results');
    }
    // Format 3: Données directes
    else if (Array.isArray(results)) {
      resultsData = results;
      console.log('📊 Using format 3: Array results');
    }
    // Format 4: Autre structure
    else if (results.results && Array.isArray(results.results.bindings)) {
      resultsData = results.results.bindings;
      console.log('📊 Using format 4: results.results.bindings');
    }
    // Format 5: Structure simple
    else if (results.bindings && Array.isArray(results.bindings)) {
      resultsData = results.bindings;
      console.log('📊 Using format 5: results.bindings');
    }
    // Format 6: Résultats directs sans nesting
    else if (results.results && Array.isArray(results.results)) {
      resultsData = results.results;
      console.log('📊 Using format 6: results.results (direct array)');
    }
    else {
      console.log('❌ Unknown results format:', results);
      // Afficher les données brutes pour debug
      return (
        <div className="results">
          <h3>Résultats (Format Debug):</h3>
          <div className="debug-info">
            <p><strong>Structure des données reçues:</strong></p>
            <pre>{JSON.stringify(results, null, 2)}</pre>
          </div>
        </div>
      );
    }

    console.log('📈 Results data to display:', resultsData);

    const questionText = results.question || results.original_question || question;
    const sparqlQuery = results.sparql_query || results.generated_sparql;

    // Vérifier d'abord si c'est un résultat de comptage
    const countResults = renderCountResults(resultsData);
    if (countResults) {
      return (
        <div className="results">
          <h3>Résultats pour: "{questionText}"</h3>
          {sparqlQuery && (
            <div className="sparql-query">
              <strong>Requête SPARQL générée:</strong>
              <pre>{sparqlQuery}</pre>
            </div>
          )}
          {countResults}
        </div>
      );
    }

    // Affichage normal des résultats
    return (
      <div className="results">
        <h3>Résultats pour: "{questionText}"</h3>
        
        {/* TALN Analysis Information */}
        {results.taln_analysis && (
          <div className="taln-analysis">
            <h4>🔍 Analyse TALN</h4>
            <div className="analysis-details">
              <div className="analysis-section">
                <strong>Entités détectées:</strong>
                <ul>
                  {results.taln_analysis.entities.map((entity, index) => (
                    <li key={index}>
                      {entity.text} ({entity.ontology_class}) - Confiance: {Math.round(entity.confidence * 100)}%
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="analysis-section">
                <strong>Intention:</strong> {results.taln_analysis.intent.primary_intent} ({results.taln_analysis.intent.query_type})
              </div>
              
              {results.taln_analysis.temporal_info.relative_time && (
                <div className="analysis-section">
                  <strong>Temps:</strong> {results.taln_analysis.temporal_info.relative_time}
                </div>
              )}
              
              {results.taln_analysis.location_info.locations.length > 0 && (
                <div className="analysis-section">
                  <strong>Lieux:</strong> {results.taln_analysis.location_info.locations.join(', ')}
                </div>
              )}
              
              <div className="analysis-section">
                <strong>Confiance globale:</strong> {Math.round(results.taln_analysis.confidence_scores.overall_confidence * 100)}%
              </div>
            </div>
          </div>
        )}
        
        {/* Pipeline Information */}
        {results.pipeline_info && (
          <div className="pipeline-info">
            <h4>📊 Informations du Pipeline</h4>
            <div className="pipeline-stats">
              <span>Entités: {results.pipeline_info.entities_detected}</span>
              <span>Intention: {results.pipeline_info.intent_classified}</span>
              <span>Confiance TALN: {Math.round(results.pipeline_info.taln_confidence * 100)}%</span>
              <span>Résultats: {results.pipeline_info.results_count}</span>
            </div>
          </div>
        )}
        
        {sparqlQuery && (
          <div className="sparql-query">
            <strong>Requête SPARQL générée:</strong>
            <pre>{sparqlQuery}</pre>
          </div>
        )}
        
        {resultsData.length > 0 ? (
          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  {/* Build a stable header order: collect all keys across rows then use that as column order */}
                  {(() => {
                    const headerSet = new Set();
                    resultsData.forEach(row => Object.keys(row).forEach(k => headerSet.add(k)));
                    const headers = Array.from(headerSet);
                    return headers.map(key => (<th key={key}>{key}</th>));
                  })()}
                </tr>
              </thead>
              <tbody>
                {resultsData.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((cell, cellIndex) => {
                      // Gérer les différents formats de cellules
                      const value = cell && cell.value ? cell.value : cell;
                      const displayValue = value || 'N/A';
                      
                      return (
                        <td key={cellIndex}>
                          {String(displayValue).length > 50 
                            ? String(displayValue).substring(0, 50) + '...' 
                            : String(displayValue)
                          }
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="results-count">📊 {resultsData.length} résultat(s) trouvé(s)</p>
          </div>
        ) : (
          <div className="no-results">
            <p>❌ Aucun résultat trouvé pour cette requête</p>
            <div className="debug-info">
              <details>
                <summary>Informations de débogage</summary>
                <pre>{JSON.stringify(results, null, 2)}</pre>
              </details>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="semantic-search">
      <h1>Recherche Sémantique</h1>
      <p>Posez votre question en langage naturel sur les campagnes, ressources, événements, locations, utilisateurs, réservations et certifications</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Posez votre question en français... Ex: Quelles sont les campagnes actives ?"
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-button">
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>

      {/* Suggested Questions Section - Organisée par catégories */}
      <div className="suggestions">
        <h4>Questions suggérées par catégorie:</h4>
        
        {/* Campagnes */}
        <div className="suggestion-category">
          <h5>🏆 Campagnes</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Campagnes.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Ressources */}
        <div className="suggestion-category">
          <h5>🛠️ Ressources</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Ressources.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Événements */}
        <div className="suggestion-category">
          <h5>📅 Événements</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Événements.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Locations */}
        <div className="suggestion-category">
          <h5>🏢 Locations</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Locations.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Volontaires */}
        <div className="suggestion-category">
          <h5>👥 Volontaires</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Volontaires.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Assignements */}
        <div className="suggestion-category">
          <h5>📋 Assignements</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.assignements.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Certificats */}
        <div className="suggestion-category">
          <h5>📜 Certificats</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Certificats.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Réservations */}
        <div className="suggestion-category">
          <h5>📋 Réservations</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Réservations.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
        {/* Réservations */}
        <div className="suggestion-category">
          <h5>📋 Sponsors</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Sponsors.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Donations */}
        <div className="suggestion-category">
          <h5>💰 Donations</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Donations.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

      </div>

      {renderResults()}
    </div>
  );
};

export default SemanticSearch;
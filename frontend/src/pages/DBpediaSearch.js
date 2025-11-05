import React, { useState } from 'react';
import { searchAPI } from '../utils/api';
import './DBpediaSearch.css';

const DBpediaSearch = () => {
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchText.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await searchAPI.dbpediaSearch(searchText);
      
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setResults(response.data);
      }
    } catch (err) {
      console.error('Error searching DBpedia:', err);
      setError('Erreur lors de la recherche DBpedia');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dbpedia-search-container">
      <div className="dbpedia-search-header">
        <h1>DBpedia Search</h1>
        <p>Search for entities in DBpedia knowledge base</p>
      </div>

      <form onSubmit={handleSearch} className="dbpedia-search-form">
        <div className="search-input-group">
          <label htmlFor="search-input">Search:</label>
          <input
            id="search-input"
            type="text"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="Enter search term (e.g., master, computer science, Paris)"
            className="search-input"
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={loading || !searchText.trim()}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {loading && (
        <div className="loading-message">Searching DBpedia...</div>
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && results.results && results.results.length > 0 && (
        <div className="search-results">
          <h2>Top {results.count} Results:</h2>
          <ol className="results-list">
            {results.results.map((result, index) => (
              <li key={index} className="result-item">
                <div className="result-content">
                  <strong className="result-title">{result.title}</strong>
                  <a 
                    href={result.uri} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="result-uri"
                  >
                    {result.uri}
                  </a>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {results && results.results && results.results.length === 0 && (
        <div className="no-results">
          <p>No results found for "{results.search_text}". Try a different search term.</p>
        </div>
      )}
    </div>
  );
};

export default DBpediaSearch;




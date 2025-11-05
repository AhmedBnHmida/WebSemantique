from SPARQLWrapper import SPARQLWrapper, JSON, POST

from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv

load_dotenv()

class SPARQLUtils:
    def __init__(self):
        self.endpoint = os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/educationInfin')
        self.sparql = SPARQLWrapper(self.endpoint + "/query")
        self.sparql.setReturnFormat(JSON)
    
    def execute_query(self, query):
        """Exécute une requête SPARQL et retourne les résultats"""
        try:
            # Normalize line endings but keep intended formatting (SPARQL comments rely on newlines)
            query = query.replace('\r', '').strip()

            # Use POST for all queries to avoid URL length limits
            # Create a fresh wrapper instance to ensure method is set correctly
            query_wrapper = SPARQLWrapper(self.endpoint + "/query")
            query_wrapper.setReturnFormat(JSON)
            query_wrapper.setMethod(POST)
            query_wrapper.setQuery(query)
            
            # Debug: log query details and verify it's complete
            if len(query) > 900:
                print(f"DEBUG: Executing long query ({len(query)} chars) via POST")
                print(f"DEBUG: Query starts: {query[:100]}...")
                print(f"DEBUG: Query ends: ...{query[-50:]}")
                # Verify query is complete (ends with DESC or appropriate closing)
                if not (query.endswith('DESC') or query.endswith('ASC') or query.endswith('}')):
                    print(f"WARNING: Query may be incomplete! Ends with: {query[-20:]}")
            
            results = query_wrapper.query().convert()
            
            # Formater les résultats
            formatted_results = []
            for result in results["results"]["bindings"]:
                formatted_result = {}
                for key, value in result.items():
                    # Nettoyer les URLs pour un affichage plus lisible
                    if 'value' in value:
                        clean_value = value['value']
                        if '#' in clean_value:
                            clean_value = clean_value.split('#')[-1]
                        elif '/' in clean_value:
                            clean_value = clean_value.split('/')[-1]
                        formatted_result[key] = clean_value
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Erreur SPARQL: {str(e)}")
            print(f"Requête: {query}")
            return {"error": f"Erreur SPARQL: {str(e)}"}

    def execute_update(self, update_query):
        """Exécute une requête SPARQL Update (INSERT/DELETE)."""
        try:
            update_endpoint = self.endpoint + "/update"
            sparql_upd = SPARQLWrapper(update_endpoint)
            sparql_upd.setMethod(POST)
            sparql_upd.setQuery(update_query)
            response = sparql_upd.query()
            
            # Check if response indicates success (200, 204, or None for some implementations)
            # SPARQLWrapper doesn't always expose status codes, so we check for exceptions
            # If we get here without exception, the update was likely successful
            return {"status": "success"}
        except Exception as e:
            error_msg = str(e)
            print(f"Erreur SPARQL Update: {error_msg}")
            print(f"Update: {update_query}")
            return {"error": f"Erreur SPARQL Update: {error_msg}"}

# Instance globale
sparql_utils = SPARQLUtils()
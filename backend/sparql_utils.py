from SPARQLWrapper import SPARQLWrapper, JSON, POST

from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv

load_dotenv()

class SPARQLUtils:
    def __init__(self):
        self.endpoint = os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/eco-ontology')
        self.sparql = SPARQLWrapper(self.endpoint + "/query")
        self.sparql.setReturnFormat(JSON)
    
    def execute_query(self, query):
        """Exécute une requête SPARQL et retourne les résultats"""
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
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
            sparql_upd.query()
            return {"status": "success"}
        except Exception as e:
            print(f"Erreur SPARQL Update: {str(e)}")
            print(f"Update: {update_query}")
            return {"error": f"Erreur SPARQL Update: {str(e)}"}

# Instance globale
sparql_utils = SPARQLUtils()
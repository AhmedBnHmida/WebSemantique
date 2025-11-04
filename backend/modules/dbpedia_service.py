"""
DBpedia Linked Data Integration Service
Enables federated SPARQL queries to enrich local data with DBpedia information
"""
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import requests
import xml.etree.ElementTree as ET
import os

class DBpediaService:
    """Service for querying DBpedia and enriching local ontology data"""
    
    def __init__(self):
        self.dbpedia_endpoint = "https://dbpedia.org/sparql"
        self.dbpedia_lookup_api = "http://lookup.dbpedia.org/api/search/KeywordSearch"
        
    def search_entities(self, search_text):
        """
        Simple search method that uses DBpedia Lookup API (much faster than SPARQL)
        Takes the whole text and returns a list of DBpedia references
        
        Args:
            search_text: The full text to search for in DBpedia
        
        Returns:
            Dictionary with 'results' list containing 'title' and 'uri' keys, or error message
        """
        if not search_text or not search_text.strip():
            return {"error": "Search text is required"}
        
        # Clean the search text (trim whitespace)
        search_text = search_text.strip()
        
        try:
            print(f"DEBUG: Searching DBpedia Lookup API for: {search_text}")
            
            # Use DBpedia Lookup API (much faster than SPARQL queries)
            params = {
                'QueryString': search_text,
                'MaxHits': 10
            }
            
            headers = {
                'Accept': 'application/json'
            }
            
            response = requests.get(
                self.dbpedia_lookup_api,
                params=params,
                headers=headers,
                timeout=10
            )
            
            print(f"DEBUG: Lookup API response status: {response.status_code}")
            print(f"DEBUG: Response content type: {response.headers.get('Content-Type', 'unknown')}")
            print(f"DEBUG: Response content preview: {response.text[:200]}")
            
            response.raise_for_status()
            
            # Parse the Lookup API response (returns XML by default)
            references = []
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'xml' in content_type or 'text' in content_type:
                # Parse XML response
                try:
                    root = ET.fromstring(response.content)
                    print(f"DEBUG: Parsing XML response, root tag: {root.tag}")
                    
                    # Look for results in XML (common structure: ArrayOfResult -> Result -> Label/URI)
                    for result in root.findall('.//Result'):
                        label_elem = result.find('Label')
                        uri_elem = result.find('URI')
                        
                        if label_elem is not None and uri_elem is not None:
                            label = label_elem.text
                            uri = uri_elem.text
                            
                            if label and uri:
                                references.append({
                                    "title": label,
                                    "uri": uri
                                })
                    
                    # Alternative XML structure
                    if not references:
                        for result in root.findall('.//result'):
                            label = result.findtext('label') or result.findtext('Label')
                            uri = result.findtext('uri') or result.findtext('URI') or result.findtext('resource')
                            
                            if label and uri:
                                references.append({
                                    "title": label,
                                    "uri": uri
                                })
                    
                    print(f"DEBUG: Parsed {len(references)} results from XML")
                    
                except ET.ParseError as e:
                    print(f"DEBUG: XML parsing error: {str(e)}")
                    return {
                        "search_text": search_text,
                        "error": f"Failed to parse XML response: {str(e)}"
                    }
            else:
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"DEBUG: Parsed JSON keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                    
                    # The Lookup API returns results in different formats depending on version
                    results = []
                    if isinstance(data, dict):
                        results = data.get('results', []) or data.get('docs', []) or data.get('data', [])
                    elif isinstance(data, list):
                        results = data
                    
                    print(f"DEBUG: Found {len(results)} raw results")
                    
                    for result in results:
                        if isinstance(result, dict):
                            label = result.get('label') or result.get('Label') or result.get('name') or result.get('Name')
                            uri = result.get('uri') or result.get('URI') or result.get('resource') or result.get('@URI')
                            
                            if not uri:
                                resource = result.get('resource') or result.get('Resource')
                                if resource:
                                    if isinstance(resource, str):
                                        uri = resource
                                    elif isinstance(resource, dict):
                                        uri = resource.get('uri') or resource.get('URI')
                            
                            if uri and label:
                                references.append({
                                    "title": label,
                                    "uri": uri
                                })
                        elif isinstance(result, str):
                            references.append({
                                "title": result.split('/')[-1].replace('_', ' '),
                                "uri": result
                            })
                except ValueError as e:
                    print(f"DEBUG: JSON parsing error: {str(e)}")
                    return {
                        "search_text": search_text,
                        "error": f"Failed to parse response (not XML or JSON): {str(e)}"
                    }
            
            print(f"DEBUG: Found {len(references)} parsed results")
            
            if references:
                return {
                    "search_text": search_text,
                    "results": references[:10],  # Limit to top 10
                    "count": len(references[:10])
                }
            else:
                # Return the raw response for debugging
                return {
                    "search_text": search_text,
                    "error": f"No results found for '{search_text}'. API response: {str(data)[:200]}"
                }
                
        except requests.exceptions.Timeout:
            print(f"DEBUG: Lookup API request timed out for: {search_text}")
            return {
                "search_text": search_text,
                "error": f"DBpedia lookup request timed out. Try a shorter search term."
            }
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Lookup API request failed: {str(e)}")
            return {
                "search_text": search_text,
                "error": f"DBpedia lookup failed: {str(e)}"
            }
        except Exception as e:
            print(f"Error querying DBpedia Lookup API: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "search_text": search_text,
                "error": f"DBpedia lookup failed: {str(e)}"
            }
    
    def enrich_entity(self, search_term, entity_type=None):
        """
        Generic method to enrich any entity from DBpedia (backward compatibility)
        Uses the new search_entities method and returns first result
        """
        if not search_term:
            return {"error": "Search term is required"}
        
        # Use the new search method
        search_results = self.search_entities(search_term)
        
        if "error" in search_results:
            return search_results
        
        # Return first result for backward compatibility
        if search_results.get("results"):
            first_result = search_results["results"][0]
            return {
                "term": search_term,
                "title": first_result["title"],
                "uri": first_result["uri"]
            }
        
        return {
            "term": search_term,
            "error": f"No data found in DBpedia for '{search_term}'"
        }
    
    def enrich_city_info(self, city_name):
        """
        Enrich city information from DBpedia (backward compatibility)
        Uses the generic enrich_entity method with Settlement type filter
        """
        return self.enrich_entity(city_name, entity_type="Settlement")
    
    def federated_query_universities(self, university_name, city_name=None):
        """
        Federated SPARQL query combining local ontology with DBpedia
        Returns enriched university information
        """
        # This would typically be executed against Fuseki with SERVICE clause
        # For now, return a structure that can be used in CONSTRUCT queries
        federated_query_template = f"""
        PREFIX ont: <http://www.education-intelligente.org/ontologie#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?univ ?nomUniv ?ville ?pays ?rangNational 
               ?dbpediaCity ?population ?country ?abstract
        WHERE {{
            ?univ a ont:Universite .
            ?univ ont:nomUniversite ?nomUniv .
            OPTIONAL {{ ?univ ont:ville ?ville . }}
            OPTIONAL {{ ?univ ont:pays ?pays . }}
            OPTIONAL {{ ?univ ont:rangNational ?rangNational . }}
            
            # Federated query to DBpedia
            SERVICE <https://dbpedia.org/sparql> {{
                ?dbpediaCity rdfs:label ?villeLabel .
                FILTER(LANG(?villeLabel) = "en")
                OPTIONAL {{ ?dbpediaCity dbo:populationTotal ?population . }}
                OPTIONAL {{ 
                    ?dbpediaCity dbo:country ?countryRes .
                    ?countryRes rdfs:label ?country .
                    FILTER(LANG(?country) = "en")
                }}
                OPTIONAL {{
                    ?dbpediaCity dbo:abstract ?abstract .
                    FILTER(LANG(?abstract) = "en")
                }}
            }}
            FILTER(?villeLabel = ?ville)
        }}
        LIMIT 10
        """
        
        return federated_query_template

# Global instance
dbpedia_service = DBpediaService()

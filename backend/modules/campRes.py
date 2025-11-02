from flask import Blueprint, jsonify, request
from SPARQLWrapper import SPARQLWrapper, JSON
import json

api_routes = Blueprint('api', __name__)

# Configuration Fuseki - CORRIGÉ pour utiliser le même endpoint que sparql_utils.py
FUSEKI_ENDPOINT = "http://localhost:3030/eco-ontology"
sparql = SPARQLWrapper(FUSEKI_ENDPOINT + "/query")
sparql.setReturnFormat(JSON)

@api_routes.route('/campaigns', methods=['GET'])
def get_campaigns():
    """Récupérer toutes les campagnes (y compris sous-classes)"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?campaign ?name ?description ?status ?startDate ?endDate ?goal ?type ?resource ?resourceName
    WHERE {
        {
            ?campaign a eco:Campaign .
        }
        UNION
        {
            ?subClass rdfs:subClassOf* eco:Campaign .
            ?campaign a ?subClass .
        }
        ?campaign eco:campaignName ?name .
        OPTIONAL { ?campaign eco:campaignDescription ?description }
        OPTIONAL { ?campaign eco:campaignStatus ?status }
        OPTIONAL { ?campaign eco:startDate ?startDate }
        OPTIONAL { ?campaign eco:endDate ?endDate }
        OPTIONAL { ?campaign eco:goal ?goal }
        OPTIONAL { 
            ?campaign a ?type .
            FILTER(?type != eco:Campaign)
        }
        OPTIONAL { 
            ?campaign eco:requiresResource ?resource .
            ?resource eco:resourceName ?resourceName 
        }
    }
    ORDER BY ?name
    """
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/campaigns/<campaign_name>', methods=['GET'])
def get_campaign_details(campaign_name):
    """Récupérer les détails d'une campagne spécifique"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?campaign ?name ?description ?status ?startDate ?endDate ?goal ?resource ?resourceName ?resourceDescription ?type
    WHERE {
        {
            ?campaign a eco:Campaign .
        }
        UNION
        {
            ?subClass rdfs:subClassOf* eco:Campaign .
            ?campaign a ?subClass .
        }
        ?campaign eco:campaignName ?name .
        FILTER(STR(?name) = "%s")
        OPTIONAL { ?campaign eco:campaignDescription ?description }
        OPTIONAL { ?campaign eco:campaignStatus ?status }
        OPTIONAL { ?campaign eco:startDate ?startDate }
        OPTIONAL { ?campaign eco:endDate ?endDate }
        OPTIONAL { ?campaign eco:goal ?goal }
        OPTIONAL { 
            ?campaign eco:requiresResource ?resource .
            ?resource eco:resourceName ?resourceName .
            OPTIONAL { ?resource eco:resourceDescription ?resourceDescription }
        }
        OPTIONAL { 
            ?campaign a ?type .
            FILTER(?type != eco:Campaign)
        }
    }
    """ % campaign_name
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/campaigns/active', methods=['GET'])
def get_active_campaigns():
    """Récupérer les campagnes actives"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?campaign ?name ?description ?status ?startDate ?endDate ?goal ?type
    WHERE {
        {
            ?campaign a eco:Campaign .
        }
        UNION
        {
            ?subClass rdfs:subClassOf* eco:Campaign .
            ?campaign a ?subClass .
        }
        ?campaign eco:campaignName ?name .
        ?campaign eco:campaignStatus ?status .
        FILTER(LCASE(STR(?status)) = "active" || LCASE(STR(?status)) = "actif" || LCASE(STR(?status)) = "en cours")
        OPTIONAL { ?campaign eco:campaignDescription ?description }
        OPTIONAL { ?campaign eco:startDate ?startDate }
        OPTIONAL { ?campaign eco:endDate ?endDate }
        OPTIONAL { ?campaign eco:goal ?goal }
        OPTIONAL { 
            ?campaign a ?type .
            FILTER(?type != eco:Campaign)
        }
    }
    ORDER BY ?name
    """
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/campaigns/type/<campaign_type>', methods=['GET'])
def get_campaigns_by_type(campaign_type):
    """Récupérer les campagnes par type"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?campaign ?name ?description ?status ?startDate ?endDate ?goal
    WHERE {
        ?campaign a eco:%s .
        ?campaign eco:campaignName ?name .
        OPTIONAL { ?campaign eco:campaignDescription ?description }
        OPTIONAL { ?campaign eco:campaignStatus ?status }
        OPTIONAL { ?campaign eco:startDate ?startDate }
        OPTIONAL { ?campaign eco:endDate ?endDate }
        OPTIONAL { ?campaign eco:goal ?goal }
    }
    ORDER BY ?name
    """ % campaign_type
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/resources', methods=['GET'])
def get_resources():
    """Récupérer toutes les ressources (y compris sous-classes)"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?resource ?name ?description ?category ?quantity ?unitCost ?type ?campaign ?campaignName
    WHERE {
        {
            ?resource a eco:Resource .
        }
        UNION
        {
            ?subClass rdfs:subClassOf* eco:Resource .
            ?resource a ?subClass .
        }
        ?resource eco:resourceName ?name .
        OPTIONAL { ?resource eco:resourceDescription ?description }
        OPTIONAL { ?resource eco:resourceCategory ?category }
        OPTIONAL { ?resource eco:quantityAvailable ?quantity }
        OPTIONAL { ?resource eco:unitCost ?unitCost }
        OPTIONAL { 
            ?resource a ?type .
            FILTER(?type != eco:Resource)
        }
        OPTIONAL { 
            ?campaign eco:requiresResource ?resource .
            ?campaign eco:campaignName ?campaignName 
        }
    }
    ORDER BY ?name
    """
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/resources/<resource_name>', methods=['GET'])
def get_resource_details(resource_name):
    """Récupérer les détails d'une ressource spécifique"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?resource ?name ?description ?category ?quantity ?unitCost ?type ?campaign ?campaignName ?campaignDescription
    WHERE {
        {
            ?resource a eco:Resource .
        }
        UNION
        {
            ?subClass rdfs:subClassOf* eco:Resource .
            ?resource a ?subClass .
        }
        ?resource eco:resourceName ?name .
        FILTER(STR(?name) = "%s")
        OPTIONAL { ?resource eco:resourceDescription ?description }
        OPTIONAL { ?resource eco:resourceCategory ?category }
        OPTIONAL { ?resource eco:quantityAvailable ?quantity }
        OPTIONAL { ?resource eco:unitCost ?unitCost }
        OPTIONAL { 
            ?resource a ?type .
            FILTER(?type != eco:Resource)
        }
        OPTIONAL { 
            ?campaign eco:requiresResource ?resource .
            ?campaign eco:campaignName ?campaignName .
            OPTIONAL { ?campaign eco:campaignDescription ?campaignDescription }
        }
    }
    """ % resource_name
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/resources/type/<resource_type>', methods=['GET'])
def get_resources_by_type(resource_type):
    """Récupérer les ressources par type"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?resource ?name ?description ?category ?quantity ?unitCost
    WHERE {
        ?resource a eco:%s .
        ?resource eco:resourceName ?name .
        OPTIONAL { ?resource eco:resourceDescription ?description }
        OPTIONAL { ?resource eco:resourceCategory ?category }
        OPTIONAL { ?resource eco:quantityAvailable ?quantity }
        OPTIONAL { ?resource eco:unitCost ?unitCost }
    }
    ORDER BY ?name
    """ % resource_type
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/campaigns/<campaign_name>/resources', methods=['GET'])
def get_campaign_resources(campaign_name):
    """Récupérer les ressources nécessaires pour une campagne spécifique"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?resource ?resourceName ?resourceDescription ?category ?quantity ?unitCost ?resourceType
    WHERE {
        {
            ?campaign a eco:Campaign .
        }
        UNION
        {
            ?subClass rdfs:subClassOf* eco:Campaign .
            ?campaign a ?subClass .
        }
        ?campaign eco:campaignName ?campaignName .
        FILTER(STR(?campaignName) = "%s")
        ?campaign eco:requiresResource ?resource .
        ?resource eco:resourceName ?resourceName .
        OPTIONAL { ?resource eco:resourceDescription ?resourceDescription }
        OPTIONAL { ?resource eco:resourceCategory ?category }
        OPTIONAL { ?resource eco:quantityAvailable ?quantity }
        OPTIONAL { ?resource eco:unitCost ?unitCost }
        OPTIONAL { 
            ?resource a ?resourceType .
            FILTER(?resourceType != eco:Resource)
        }
    }
    ORDER BY ?resourceName
    """ % campaign_name
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return jsonify(results)
    except Exception as e:
        print(f"Erreur SPARQL: {str(e)}")
        return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500

@api_routes.route('/search/semantic', methods=['POST'])
def semantic_search():
    """Recherche sémantique avec transformation question -> SPARQL"""
    data = request.json
    question = data.get('question', '')
    
    # Appel à la fonction de transformation
    sparql_query = transform_question_to_sparql(question)
    
    if sparql_query:
        try:
            sparql.setQuery(sparql_query)
            results = sparql.query().convert()
            return jsonify({
                "original_question": question,
                "generated_sparql": sparql_query,
                "results": results
            })
        except Exception as e:
            return jsonify({"error": f"Erreur SPARQL: {str(e)}"}), 500
    else:
        return jsonify({"error": "Impossible de traiter la question"}), 400

def transform_question_to_sparql(question):
    """Transforme une question en langage naturel en requête SPARQL"""
    question_lower = question.lower()
    
    # QUESTIONS SUR LES CAMPAGNES
    if any(word in question_lower for word in ["campagne", "campaign"]):
        # REQUÊTES DE COMPTAGE POUR CAMPAGNES
        if "nombre" in question_lower or "combien" in question_lower or "count" in question_lower:
            if "type" in question_lower or "catégorie" in question_lower:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?type (COUNT(DISTINCT ?campaign) as ?count)
                WHERE {
                    {
                        ?campaign a eco:Campaign .
                        BIND("Campagne Générale" as ?type)
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Campaign .
                        ?campaign a ?subClass .
                        ?campaign a ?type .
                        FILTER(?type != eco:Campaign)
                    }
                }
                GROUP BY ?type
                ORDER BY DESC(?count)
                """
            else:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT (COUNT(DISTINCT ?campaign) as ?totalCampaigns)
                WHERE {
                    {
                        ?campaign a eco:Campaign .
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Campaign .
                        ?campaign a ?subClass .
                    }
                }
                """
        
        # REQUÊTES DE TRI POUR CAMPAGNES
        elif "trier" in question_lower or "sort" in question_lower or "ordre" in question_lower:
            if "date" in question_lower and "début" in question_lower:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?name ?description ?status ?startDate ?endDate ?goal ?type
                WHERE {
                    {
                        ?campaign a eco:Campaign .
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Campaign .
                        ?campaign a ?subClass .
                    }
                    ?campaign eco:campaignName ?name .
                    OPTIONAL { ?campaign eco:campaignDescription ?description }
                    OPTIONAL { ?campaign eco:campaignStatus ?status }
                    OPTIONAL { ?campaign eco:startDate ?startDate }
                    OPTIONAL { ?campaign eco:endDate ?endDate }
                    OPTIONAL { ?campaign eco:goal ?goal }
                    OPTIONAL { 
                        ?campaign a ?type .
                        FILTER(?type != eco:Campaign)
                    }
                    FILTER(BOUND(?startDate))
                }
                ORDER BY DESC(?startDate)
                LIMIT 10
                """
            else:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?name ?description ?status ?startDate ?endDate ?goal ?type
                WHERE {
                    {
                        ?campaign a eco:Campaign .
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Campaign .
                        ?campaign a ?subClass .
                    }
                    ?campaign eco:campaignName ?name .
                    OPTIONAL { ?campaign eco:campaignDescription ?description }
                    OPTIONAL { ?campaign eco:campaignStatus ?status }
                    OPTIONAL { ?campaign eco:startDate ?startDate }
                    OPTIONAL { ?campaign eco:endDate ?endDate }
                    OPTIONAL { ?campaign eco:goal ?goal }
                    OPTIONAL { 
                        ?campaign a ?type .
                        FILTER(?type != eco:Campaign)
                    }
                }
                ORDER BY DESC(?name)
                LIMIT 10
                """
        
        elif any(word in question_lower for word in ["actif", "active", "en cours", "current"]):
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?type
            WHERE {
                {
                    ?campaign a eco:Campaign .
                }
                UNION
                {
                    ?subClass rdfs:subClassOf* eco:Campaign .
                    ?campaign a ?subClass .
                }
                ?campaign eco:campaignName ?name .
                ?campaign eco:campaignStatus ?status .
                FILTER(LCASE(STR(?status)) = "active" || LCASE(STR(?status)) = "actif" || LCASE(STR(?status)) = "en cours")
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { 
                    ?campaign a ?type .
                    FILTER(?type != eco:Campaign)
                }
            }
            ORDER BY ?name
            """
        
        elif "nettoyage" in question_lower or "cleanup" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal
            WHERE {
                ?campaign a eco:CleanupCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
            }
            ORDER BY ?name
            """
        
        elif "sensibilisation" in question_lower or "awareness" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal
            WHERE {
                ?campaign a eco:AwarenessCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
            }
            ORDER BY ?name
            """
        
        elif "financement" in question_lower or "funding" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?targetAmount ?fundsRaised
            WHERE {
                ?campaign a eco:FundingCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { ?campaign eco:targetAmount ?targetAmount }
                OPTIONAL { ?campaign eco:fundsRaised ?fundsRaised }
            }
            ORDER BY ?name
            """
        
        elif "événement" in question_lower or "event" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?targetParticipants
            WHERE {
                ?campaign a eco:EventCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { ?campaign eco:targetParticipants ?targetParticipants }
            }
            ORDER BY ?name
            """
        
        else:
            # Requête générale pour les campagnes
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?type
            WHERE {
                {
                    ?campaign a eco:Campaign .
                }
                UNION
                {
                    ?subClass rdfs:subClassOf* eco:Campaign .
                    ?campaign a ?subClass .
                }
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { 
                    ?campaign a ?type .
                    FILTER(?type != eco:Campaign)
                }
            }
            ORDER BY ?name
            LIMIT 20
            """
    
    # QUESTIONS SUR LES RESSOURCES
    elif any(word in question_lower for word in ["ressource", "resource"]):
        # REQUÊTES DE COMPTAGE POUR RESSOURCES
        if "nombre" in question_lower or "combien" in question_lower or "count" in question_lower:
            if "catégorie" in question_lower or "category" in question_lower:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?category (COUNT(DISTINCT ?resource) as ?count)
                WHERE {
                    {
                        ?resource a eco:Resource .
                        OPTIONAL { ?resource eco:resourceCategory ?category }
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Resource .
                        ?resource a ?subClass .
                        OPTIONAL { ?resource eco:resourceCategory ?category }
                    }
                    FILTER(BOUND(?category))
                }
                GROUP BY ?category
                ORDER BY DESC(?count)
                """
            else:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT (COUNT(DISTINCT ?resource) as ?totalResources)
                WHERE {
                    {
                        ?resource a eco:Resource .
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Resource .
                        ?resource a ?subClass .
                    }
                }
                """
        
        # REQUÊTES DE TRI POUR RESSOURCES
        elif "trier" in question_lower or "sort" in question_lower or "ordre" in question_lower:
            if "coût" in question_lower or "cost" in question_lower:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?name ?description ?category ?quantity ?unitCost ?type
                WHERE {
                    {
                        ?resource a eco:Resource .
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Resource .
                        ?resource a ?subClass .
                    }
                    ?resource eco:resourceName ?name .
                    OPTIONAL { ?resource eco:resourceDescription ?description }
                    OPTIONAL { ?resource eco:resourceCategory ?category }
                    OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                    OPTIONAL { ?resource eco:unitCost ?unitCost }
                    OPTIONAL { 
                        ?resource a ?type .
                        FILTER(?type != eco:Resource)
                    }
                    FILTER(BOUND(?unitCost))
                }
                ORDER BY DESC(xsd:decimal(?unitCost))
                LIMIT 10
                """
            else:
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?name ?description ?category ?quantity ?unitCost ?type
                WHERE {
                    {
                        ?resource a eco:Resource .
                    }
                    UNION
                    {
                        ?subClass rdfs:subClassOf* eco:Resource .
                        ?resource a ?subClass .
                    }
                    ?resource eco:resourceName ?name .
                    OPTIONAL { ?resource eco:resourceDescription ?description }
                    OPTIONAL { ?resource eco:resourceCategory ?category }
                    OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                    OPTIONAL { ?resource eco:unitCost ?unitCost }
                    OPTIONAL { 
                        ?resource a ?type .
                        FILTER(?type != eco:Resource)
                    }
                }
                ORDER BY DESC(?name)
                LIMIT 10
                """
        
        elif "humaine" in question_lower or "human" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?skillLevel
            WHERE {
                ?resource a eco:HumanResource .
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { ?resource eco:skillLevel ?skillLevel }
            }
            ORDER BY ?name
            """
        
        elif "matérielle" in question_lower or "material" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?condition
            WHERE {
                ?resource a eco:MaterialResource .
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { ?resource eco:condition ?condition }
            }
            ORDER BY ?name
            """
        
        elif "équipement" in question_lower or "equipment" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?specifications
            WHERE {
                ?resource a eco:Equipment .
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { ?resource eco:specifications ?specifications }
            }
            ORDER BY ?name
            """
        
        elif "financière" in question_lower or "financial" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?currency
            WHERE {
                ?resource a eco:FinancialResource .
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { ?resource eco:currency ?currency }
            }
            ORDER BY ?name
            """
        
        elif "numérique" in question_lower or "digital" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?format
            WHERE {
                ?resource a eco:DigitalResource .
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { ?resource eco:format ?format }
            }
            ORDER BY ?name
            """
        
        else:
            # Requête générale pour les ressources
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?type
            WHERE {
                {
                    ?resource a eco:Resource .
                }
                UNION
                {
                    ?subClass rdfs:subClassOf* eco:Resource .
                    ?resource a ?subClass .
                }
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { 
                    ?resource a ?type .
                    FILTER(?type != eco:Resource)
                }
            }
            ORDER BY ?name
            LIMIT 20
            """
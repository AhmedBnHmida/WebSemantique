from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.gemini_sparql_service import GeminiSPARQLTransformer

reservations_bp = Blueprint('reservations', __name__)

try:
    transformer = GeminiSPARQLTransformer()
except Exception as e:
    print(f"⚠️ Warning: Gemini not available: {e}")
    transformer = None

@reservations_bp.route('/reservations', methods=['GET'])
def get_reservations():
    """Récupère toutes les réservations"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail ?confirmedByName ?confirmedByEmail
        WHERE {
            ?reservation a eco:Reservation .
            OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }
            OPTIONAL { ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }
            OPTIONAL { 
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
            OPTIONAL { 
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL { ?user eco:lastName ?userLastName . }
                OPTIONAL { ?user eco:email ?userEmail . }
            }
            OPTIONAL { 
                ?reservation eco:confirmedBy ?admin .
                ?admin eco:firstName ?confirmedByName .
                OPTIONAL { ?admin eco:email ?confirmedByEmail . }
            }
        }
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/status/<status>', methods=['GET'])
def get_reservations_by_status(status):
    """Récupère les réservations par statut (pending, confirmed, cancelled)"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail
        WHERE {{
            ?reservation a eco:Reservation .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
            FILTER(LCASE(STR(?status)) = "{status.lower()}")
            OPTIONAL {{ ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }}
            OPTIONAL {{ 
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }}
            OPTIONAL {{ 
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL {{ ?user eco:lastName ?userLastName . }}
                OPTIONAL {{ ?user eco:email ?userEmail . }}
            }}
        }}
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/event/<event_name>', methods=['GET'])
def get_reservations_by_event(event_name):
    """Récupère les réservations pour un événement spécifique"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail
        WHERE {{
            ?reservation a eco:Reservation .
            ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
            ?event eco:eventTitle ?eventTitle .
            FILTER(CONTAINS(LCASE(STR(?eventTitle)), "{event_name.lower()}"))
            OPTIONAL {{ ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }}
            OPTIONAL {{ ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }}
            OPTIONAL {{ 
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL {{ ?user eco:lastName ?userLastName . }}
                OPTIONAL {{ ?user eco:email ?userEmail . }}
            }}
        }}
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/user/<user_name>', methods=['GET'])
def get_reservations_by_user(user_name):
    """Récupère les réservations d'un utilisateur spécifique"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userLastName ?userEmail
        WHERE {{
            ?reservation a eco:Reservation .
            ?reservation eco:belongsToUser ?user .
            ?user eco:firstName ?userName .
            FILTER(CONTAINS(LCASE(STR(?userName)), "{user_name.lower()}"))
            OPTIONAL {{ ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }}
            OPTIONAL {{ ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }}
            OPTIONAL {{ 
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }}
            OPTIONAL {{ ?user eco:email ?userEmail . }}
        }}
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/stats', methods=['GET'])
def get_reservations_stats():
    """Récupère les statistiques des réservations"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?status (COUNT(?reservation) as ?count)
        WHERE {
            ?reservation a eco:Reservation .
            OPTIONAL { ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }
        }
        GROUP BY ?status
        ORDER BY ?status
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/search/semantic', methods=['POST'])
def semantic_search_reservations():
    """Recherche sémantique de réservations avec Gemini"""
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    if not transformer:
        return jsonify({"error": "Gemini service not available"}), 500
    
    try:
        # Générer la requête SPARQL avec Gemini
        sparql_query = transformer.transform_question_to_sparql(question)
        
        # Exécuter la requête
        results = sparql_utils.execute_query(sparql_query)
        
        return jsonify({
            "original_question": question,
            "generated_sparql": sparql_query,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

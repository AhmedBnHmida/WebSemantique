from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.gemini_sparql_service import GeminiSPARQLTransformer

certifications_bp = Blueprint('certifications', __name__)

try:
    transformer = GeminiSPARQLTransformer()
except Exception as e:
    print(f"⚠️ Warning: Gemini not available: {e}")
    transformer = None

@certifications_bp.route('/certifications', methods=['GET'])
def get_certifications():
    """Récupère toutes les certifications"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail ?awardedToName ?awardedToEmail ?reservationCode ?eventTitle ?reservationStatus ?confirmedByName
        WHERE {
            ?certification a eco:Certification .
            ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode .
            ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned .
            ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
            ?certification eco:issuedBy ?issuer .
            ?issuer eco:firstName ?issuerName .
            OPTIONAL { ?issuer eco:email ?issuerEmail . }
            ?certification eco:awardedTo ?recipient .
            ?recipient eco:firstName ?awardedToName .
            OPTIONAL { ?recipient eco:email ?awardedToEmail . }
            
            # Jointure obligatoire avec réservation confirmée
            ?reservation a eco:Reservation .
            ?reservation eco:belongsToUser ?recipient .
            ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?reservationCode .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr "confirmed" .
            ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
            ?event eco:eventTitle ?eventTitle .
            ?reservation eco:confirmedBy ?admin .
            ?admin eco:firstName ?confirmedByName .
            
            BIND("confirmed" as ?reservationStatus)
        }
        ORDER BY ?certification
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certifications_bp.route('/certifications/type/<cert_type>', methods=['GET'])
def get_certifications_by_type(cert_type):
    """Récupère les certifications par type (participation, achievement, eco-points, etc.)"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
        WHERE {{
            ?certification a eco:Certification .
            ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
            FILTER(CONTAINS(LCASE(STR(?type)), "{cert_type.lower()}"))
            OPTIONAL {{ ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }}
            OPTIONAL {{ ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }}
            OPTIONAL {{ 
                ?certification eco:issuedBy ?issuer .
                ?issuer eco:firstName ?issuerName .
                OPTIONAL {{ ?issuer eco:email ?issuerEmail . }}
            }}
        }}
        ORDER BY ?certification
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certifications_bp.route('/certifications/issuer/<issuer_name>', methods=['GET'])
def get_certifications_by_issuer(issuer_name):
    """Récupère les certifications émises par un utilisateur spécifique"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
        WHERE {{
            ?certification a eco:Certification .
            ?certification eco:issuedBy ?issuer .
            ?issuer eco:firstName ?issuerName .
            FILTER(CONTAINS(LCASE(STR(?issuerName)), "{issuer_name.lower()}"))
            OPTIONAL {{ ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }}
            OPTIONAL {{ ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }}
            OPTIONAL {{ ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type . }}
            OPTIONAL {{ ?issuer eco:email ?issuerEmail . }}
        }}
        ORDER BY ?certification
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certifications_bp.route('/certifications/points/<int:min_points>', methods=['GET'])
def get_certifications_by_points(min_points):
    """Récupère les certifications avec un minimum de points"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
        WHERE {{
            ?certification a eco:Certification .
            ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned .
            FILTER(?pointsEarned >= {min_points})
            OPTIONAL {{ ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }}
            OPTIONAL {{ ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type . }}
            OPTIONAL {{ 
                ?certification eco:issuedBy ?issuer .
                ?issuer eco:firstName ?issuerName .
                OPTIONAL {{ ?issuer eco:email ?issuerEmail . }}
            }}
        }}
        ORDER BY DESC(?pointsEarned)
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certifications_bp.route('/certifications/stats', methods=['GET'])
def get_certifications_stats():
    """Récupère les statistiques des certifications"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?type (COUNT(?certification) as ?count) (AVG(?pointsEarned) as ?avgPoints) (SUM(?pointsEarned) as ?totalPoints)
        WHERE {
            ?certification a eco:Certification .
            ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
            ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned .
            ?certification eco:awardedTo ?recipient .
            
            # Jointure obligatoire avec réservation confirmée
            ?reservation a eco:Reservation .
            ?reservation eco:belongsToUser ?recipient .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr "confirmed" .
            ?reservation eco:confirmedBy ?admin .
        }
        GROUP BY ?type
        ORDER BY ?type
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certifications_bp.route('/certifications/leaderboard', methods=['GET'])
def get_certifications_leaderboard():
    """Récupère le classement des utilisateurs par points de certification"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?awardedToName ?awardedToEmail (COUNT(?certification) as ?certCount) (AVG(?pointsEarned) as ?avgPoints)
        WHERE {
            ?certification a eco:Certification .
            ?certification eco:awardedTo ?recipient .
            ?recipient eco:firstName ?awardedToName .
            OPTIONAL { ?recipient eco:email ?awardedToEmail . }
            ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned .
            
            # Jointure obligatoire avec réservation confirmée
            ?reservation a eco:Reservation .
            ?reservation eco:belongsToUser ?recipient .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr "confirmed" .
            ?reservation eco:confirmedBy ?admin .
            
            # Exclure l'admin du classement
            FILTER(?recipient != <http://www.semanticweb.org/eco-ontology#AdminUser>)
        }
        GROUP BY ?awardedToName ?awardedToEmail
        ORDER BY DESC(?avgPoints) DESC(?certCount)
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certifications_bp.route('/certifications/search/semantic', methods=['POST'])
def semantic_search_certifications():
    """Recherche sémantique de certifications avec Gemini"""
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

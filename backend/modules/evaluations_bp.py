"""CRUD endpoints for Evaluations"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_evaluation
from modules.dbpedia_service import dbpedia_service
import uuid

evaluations_bp = Blueprint('evaluations', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_evaluation_uri(type_eval: str, date_eval: str = None) -> str:
    """Generate a unique URI for an evaluation"""
    safe_type = type_eval.upper().replace(' ', '_')[:30]
    date_part = date_eval.replace('-', '') if date_eval else ''
    return f"{PREFIX}Evaluation_{safe_type}_{date_part}_{uuid.uuid4().hex[:8]}"

@evaluations_bp.route('/evaluations', methods=['GET'])
def get_all_evaluations():
    """Get all evaluations"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?evaluation ?typeEvaluation ?dateEvaluation
           ?cours ?intitule ?competence ?nomCompetence
           ?technologie ?nomTechnologie
    WHERE {{
        ?evaluation a ?type .
        ?type rdfs:subClassOf* ont:Evaluation .
        OPTIONAL {{ ?evaluation ont:typeEvaluation ?typeEvaluation . }}
        OPTIONAL {{ ?evaluation ont:dateEvaluation ?dateEvaluation . }}
        OPTIONAL {{
            ?evaluation ont:porteSur ?cours .
            ?cours ont:intitule ?intitule .
        }}
        OPTIONAL {{
            ?evaluation ont:mesureCompetence ?competence .
            ?competence ont:nomCompetence ?nomCompetence .
        }}
        OPTIONAL {{
            ?evaluation ont:faciliteePar ?technologie .
            ?technologie ont:nomTechnologie ?nomTechnologie .
        }}
    }}
    ORDER BY DESC(?dateEvaluation)
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations/<evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    """Get a specific evaluation"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?evaluation ?typeEvaluation ?dateEvaluation
           ?cours ?intitule ?projet ?titreProjet
           ?competence ?nomCompetence
           ?technologie ?nomTechnologie
    WHERE {{
        <{evaluation_id}> a ?type .
        ?type rdfs:subClassOf* ont:Evaluation .
        OPTIONAL {{ <{evaluation_id}> ont:typeEvaluation ?typeEvaluation . }}
        OPTIONAL {{ <{evaluation_id}> ont:dateEvaluation ?dateEvaluation . }}
        OPTIONAL {{
            <{evaluation_id}> ont:porteSur ?cours .
            ?cours ont:intitule ?intitule .
        }}
        OPTIONAL {{
            <{evaluation_id}> ont:porteSur ?projet .
            ?projet ont:titreProjet ?titreProjet .
        }}
        OPTIONAL {{
            <{evaluation_id}> ont:mesureCompetence ?competence .
            ?competence ont:nomCompetence ?nomCompetence .
        }}
        OPTIONAL {{
            <{evaluation_id}> ont:faciliteePar ?technologie .
            ?technologie ont:nomTechnologie ?nomTechnologie .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations', methods=['POST'])
def create_evaluation():
    """Create a new evaluation"""
    data = request.json
    
    errors = validate_evaluation(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    evaluation_uri = generate_evaluation_uri(
        data.get('typeEvaluation', ''),
        data.get('dateEvaluation', '')
    )
    
    insert_parts = [
        f"<{evaluation_uri}> a ont:Evaluation",
        f"; ont:typeEvaluation \"{data.get('typeEvaluation')}\""
    ]
    
    if data.get('dateEvaluation'):
        insert_parts.append(f"; ont:dateEvaluation \"{data.get('dateEvaluation')}\"^^xsd:date")
    if data.get('cours'):
        insert_parts.append(f"; ont:porteSur <{data.get('cours')}>")
    if data.get('projet'):
        insert_parts.append(f"; ont:porteSur <{data.get('projet')}>")
    if data.get('competence'):
        insert_parts.append(f"; ont:mesureCompetence <{data.get('competence')}>")
    if data.get('technologie'):
        insert_parts.append(f"; ont:faciliteePar <{data.get('technologie')}>")
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Évaluation créée avec succès", "uri": evaluation_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations/<evaluation_id>', methods=['PUT'])
def update_evaluation(evaluation_id):
    """Update an evaluation"""
    data = request.json
    
    errors = validate_evaluation(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{evaluation_id}> ?p ?o .
    }}
    WHERE {{
        <{evaluation_id}> ?p ?o .
    }}
    """
    
    insert_parts = [f"<{evaluation_id}> a ont:Evaluation"]
    
    if data.get('typeEvaluation'):
        insert_parts.append(f"; ont:typeEvaluation \"{data.get('typeEvaluation')}\"")
    if data.get('dateEvaluation'):
        insert_parts.append(f"; ont:dateEvaluation \"{data.get('dateEvaluation')}\"^^xsd:date")
    if data.get('cours'):
        insert_parts.append(f"; ont:porteSur <{data.get('cours')}>")
    if data.get('projet'):
        insert_parts.append(f"; ont:porteSur <{data.get('projet')}>")
    if data.get('competence'):
        insert_parts.append(f"; ont:mesureCompetence <{data.get('competence')}>")
    if data.get('technologie'):
        insert_parts.append(f"; ont:faciliteePar <{data.get('technologie')}>")
    
    insert_query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        sparql_utils.execute_update(delete_query)
        result = sparql_utils.execute_update(insert_query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Évaluation mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations/<evaluation_id>', methods=['DELETE'])
def delete_evaluation(evaluation_id):
    """Delete an evaluation"""
    # Construct full URI if not already a full URI
    if evaluation_id.startswith('http://') or evaluation_id.startswith('https://'):
        evaluation_uri = evaluation_id
    else:
        if evaluation_id.startswith(PREFIX):
            evaluation_uri = evaluation_id
        else:
            evaluation_uri = f"{PREFIX}{evaluation_id}"
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{evaluation_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(delete_query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Évaluation supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations/search', methods=['POST'])
def search_evaluations():
    """Search evaluations"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?evaluation ?typeEvaluation ?dateEvaluation
    WHERE {{
        ?evaluation a ?type .
        ?type rdfs:subClassOf* ont:Evaluation .
        OPTIONAL {{ ?evaluation ont:typeEvaluation ?typeEvaluation . }}
        OPTIONAL {{ ?evaluation ont:dateEvaluation ?dateEvaluation . }}
    """
    
    if data and data.get('typeEvaluation'):
        filters.append(f'REGEX(?typeEvaluation, "{data.get("typeEvaluation")}", "i")')
    if data and data.get('dateEvaluation'):
        filters.append(f'?dateEvaluation = "{data.get("dateEvaluation")}"^^xsd:date')
    
    if filters:
        query += "\n        FILTER(" + " && ".join(filters) + ")"
    
    query += "\n    } ORDER BY DESC(?dateEvaluation)"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations/facets', methods=['GET'])
def get_evaluations_facets():
    """Récupère les facettes pour la navigation filtrée"""
    query_type = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?typeEvaluation (COUNT(DISTINCT ?evaluation) as ?count)
    WHERE {{
        ?evaluation a ?type .
        ?type rdfs:subClassOf* ont:Evaluation .
        ?evaluation ont:typeEvaluation ?typeEvaluation .
    }}
    GROUP BY ?typeEvaluation
    ORDER BY DESC(?count)
    """
    query_cours = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?cours ?intitule (COUNT(DISTINCT ?evaluation) as ?count)
    WHERE {{
        ?evaluation a ?type .
        ?type rdfs:subClassOf* ont:Evaluation .
        ?evaluation ont:porteSur ?cours .
        ?cours ont:intitule ?intitule .
    }}
    GROUP BY ?cours ?intitule
    ORDER BY DESC(?count)
    LIMIT 20
    """
    query_competence = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?competence ?nomCompetence (COUNT(DISTINCT ?evaluation) as ?count)
    WHERE {{
        ?evaluation a ?type .
        ?type rdfs:subClassOf* ont:Evaluation .
        ?evaluation ont:mesureCompetence ?competence .
        ?competence ont:nomCompetence ?nomCompetence .
    }}
    GROUP BY ?competence ?nomCompetence
    ORDER BY DESC(?count)
    LIMIT 20
    """
    try:
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_cours": sparql_utils.execute_query(query_cours),
            "by_competence": sparql_utils.execute_query(query_competence)
        }
        return jsonify(facets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluations_bp.route('/evaluations/<path:evaluation_id>/dbpedia-enrich', methods=['GET'])
def enrich_evaluation_with_dbpedia(evaluation_id):
    """Enrich evaluation data with DBpedia information"""
    try:
        query = f"""
        PREFIX ont: <{PREFIX}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?typeEvaluation ?intituleCours
        WHERE {{
            <{evaluation_id}> a ?type .
            ?type rdfs:subClassOf* ont:Evaluation .
            OPTIONAL {{ <{evaluation_id}> ont:typeEvaluation ?typeEvaluation . }}
            OPTIONAL {{
                <{evaluation_id}> ont:evalue ?cours .
                ?cours ont:intitule ?intituleCours .
            }}
        }}
        LIMIT 1
        """
        results = sparql_utils.execute_query(query)
        if not results:
            return jsonify({"error": "Évaluation non trouvée"}), 404
        evaluation_data = results[0]
        search_term = request.args.get('term') or evaluation_data.get("typeEvaluation") or evaluation_data.get("intituleCours", "")
        enriched_data = {"evaluation": evaluation_data, "search_term": search_term, "dbpedia_enrichment": None}
        if search_term:
            dbpedia_results = dbpedia_service.search_entities(search_term)
            if dbpedia_results.get("results") and len(dbpedia_results["results"]) > 0:
                first_result = dbpedia_results["results"][0]
                enriched_data["dbpedia_enrichment"] = {"title": first_result["title"], "uri": first_result["uri"], "all_results": dbpedia_results["results"][:5]}
            else:
                enriched_data["dbpedia_enrichment"] = dbpedia_results
        return jsonify(enriched_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


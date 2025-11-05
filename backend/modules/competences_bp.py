"""CRUD endpoints for Competences"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_competence
from modules.dbpedia_service import dbpedia_service
import uuid

competences_bp = Blueprint('competences', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_competence_uri(nom: str) -> str:
    """Generate a unique URI for a competence"""
    safe_nom = nom.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}Competence_{safe_nom}_{uuid.uuid4().hex[:8]}"

@competences_bp.route('/competences', methods=['GET'])
def get_all_competences():
    """Get all competences"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?competence ?nomCompetence ?typeCompetence ?niveauCompetence ?descriptionCompetence ?motsCles
           ?specialite ?nomSpecialite
    WHERE {{
        ?competence a ?type .
        ?type rdfs:subClassOf* ont:Competence .
        OPTIONAL {{ ?competence ont:nomCompetence ?nomCompetence . }}
        OPTIONAL {{ ?competence ont:typeCompetence ?typeCompetence . }}
        OPTIONAL {{ ?competence ont:niveauCompetence ?niveauCompetence . }}
        OPTIONAL {{ ?competence ont:descriptionCompetence ?descriptionCompetence . }}
        OPTIONAL {{ ?competence ont:motsCles ?motsCles . }}
        OPTIONAL {{
            ?specialite ont:formePour ?competence .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
    }}
    ORDER BY ?nomCompetence
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences/<competence_id>', methods=['GET'])
def get_competence(competence_id):
    """Get a specific competence"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?competence ?nomCompetence ?typeCompetence ?niveauCompetence ?descriptionCompetence ?motsCles
           ?specialite ?nomSpecialite ?projet ?titreProjet
    WHERE {{
        <{competence_id}> a ?type .
        ?type rdfs:subClassOf* ont:Competence .
        OPTIONAL {{ <{competence_id}> ont:nomCompetence ?nomCompetence . }}
        OPTIONAL {{ <{competence_id}> ont:typeCompetence ?typeCompetence . }}
        OPTIONAL {{ <{competence_id}> ont:niveauCompetence ?niveauCompetence . }}
        OPTIONAL {{ <{competence_id}> ont:descriptionCompetence ?descriptionCompetence . }}
        OPTIONAL {{ <{competence_id}> ont:motsCles ?motsCles . }}
        OPTIONAL {{
            ?specialite ont:formePour <{competence_id}> .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
        OPTIONAL {{
            ?projet ont:requiertCompetence <{competence_id}> .
            ?projet ont:titreProjet ?titreProjet .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences', methods=['POST'])
def create_competence():
    """Create a new competence"""
    data = request.json
    
    errors = validate_competence(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    competence_uri = generate_competence_uri(data.get('nomCompetence'))
    
    insert_parts = [
        f"<{competence_uri}> a ont:Competence",
        f"; ont:nomCompetence \"{data.get('nomCompetence')}\""
    ]
    
    if data.get('typeCompetence'):
        insert_parts.append(f"; ont:typeCompetence \"{data.get('typeCompetence')}\"")
    if data.get('niveauCompetence'):
        insert_parts.append(f"; ont:niveauCompetence \"{data.get('niveauCompetence')}\"")
    if data.get('descriptionCompetence'):
        insert_parts.append(f"; ont:descriptionCompetence \"{data.get('descriptionCompetence')}\"")
    if data.get('motsCles'):
        insert_parts.append(f"; ont:motsCles \"{data.get('motsCles')}\"")
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Compétence créée avec succès", "uri": competence_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences/<competence_id>', methods=['PUT'])
def update_competence(competence_id):
    """Update a competence"""
    data = request.json
    
    errors = validate_competence(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{competence_id}> ?p ?o .
    }}
    WHERE {{
        <{competence_id}> ?p ?o .
        FILTER(?p != ont:formePour && ?p != ont:requiertCompetence)
    }}
    """
    
    insert_parts = [f"<{competence_id}> a ont:Competence"]
    
    if data.get('nomCompetence'):
        insert_parts.append(f"; ont:nomCompetence \"{data.get('nomCompetence')}\"")
    if data.get('typeCompetence'):
        insert_parts.append(f"; ont:typeCompetence \"{data.get('typeCompetence')}\"")
    if data.get('niveauCompetence'):
        insert_parts.append(f"; ont:niveauCompetence \"{data.get('niveauCompetence')}\"")
    if data.get('descriptionCompetence'):
        insert_parts.append(f"; ont:descriptionCompetence \"{data.get('descriptionCompetence')}\"")
    if data.get('motsCles'):
        insert_parts.append(f"; ont:motsCles \"{data.get('motsCles')}\"")
    
    insert_query = f"""
    PREFIX ont: <{PREFIX}>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        sparql_utils.execute_update(delete_query)
        result = sparql_utils.execute_update(insert_query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Compétence mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences/<competence_id>', methods=['DELETE'])
def delete_competence(competence_id):
    """Delete a competence"""
    # Construct full URI if not already a full URI
    if competence_id.startswith('http://') or competence_id.startswith('https://'):
        competence_uri = competence_id
    else:
        if competence_id.startswith(PREFIX):
            competence_uri = competence_id
        else:
            competence_uri = f"{PREFIX}{competence_id}"
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{competence_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Compétence supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences/search', methods=['POST'])
def search_competences():
    """Search competences"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?competence ?nomCompetence ?typeCompetence ?niveauCompetence ?descriptionCompetence
    WHERE {{
        ?competence a ?type .
        ?type rdfs:subClassOf* ont:Competence .
        OPTIONAL {{ ?competence ont:nomCompetence ?nomCompetence . }}
        OPTIONAL {{ ?competence ont:typeCompetence ?typeCompetence . }}
        OPTIONAL {{ ?competence ont:niveauCompetence ?niveauCompetence . }}
        OPTIONAL {{ ?competence ont:descriptionCompetence ?descriptionCompetence . }}
    """
    
    if data.get('nomCompetence'):
        filters.append(f'REGEX(?nomCompetence, "{data.get("nomCompetence")}", "i")')
    if data.get('typeCompetence'):
        filters.append(f'REGEX(?typeCompetence, "{data.get("typeCompetence")}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?nomCompetence"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences/facets', methods=['GET'])
def get_competences_facets():
    """Récupère les facettes pour la navigation filtrée"""
    query_type = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?typeCompetence (COUNT(DISTINCT ?competence) as ?count)
    WHERE {{
        ?competence a ?type .
        ?type rdfs:subClassOf* ont:Competence .
        ?competence ont:typeCompetence ?typeCompetence .
    }}
    GROUP BY ?typeCompetence
    ORDER BY DESC(?count)
    """
    query_niveau = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?niveauCompetence (COUNT(DISTINCT ?competence) as ?count)
    WHERE {{
        ?competence a ?type .
        ?type rdfs:subClassOf* ont:Competence .
        ?competence ont:niveauCompetence ?niveauCompetence .
    }}
    GROUP BY ?niveauCompetence
    ORDER BY DESC(?count)
    """
    query_specialite = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?specialite ?nomSpecialite (COUNT(DISTINCT ?competence) as ?count)
    WHERE {{
        ?specialite ont:formePour ?competence .
        ?specialite ont:nomSpecialite ?nomSpecialite .
    }}
    GROUP BY ?specialite ?nomSpecialite
    ORDER BY DESC(?count)
    LIMIT 20
    """
    try:
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_niveau": sparql_utils.execute_query(query_niveau),
            "by_specialite": sparql_utils.execute_query(query_specialite)
        }
        return jsonify(facets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competences_bp.route('/competences/<path:competence_id>/dbpedia-enrich', methods=['GET'])
def enrich_competence_with_dbpedia(competence_id):
    """Enrich competence data with DBpedia information"""
    try:
        query = f"""
        PREFIX ont: <{PREFIX}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?nomCompetence ?typeCompetence
        WHERE {{
            <{competence_id}> a ?type .
            ?type rdfs:subClassOf* ont:Competence .
            OPTIONAL {{ <{competence_id}> ont:nomCompetence ?nomCompetence . }}
            OPTIONAL {{ <{competence_id}> ont:typeCompetence ?typeCompetence . }}
        }}
        LIMIT 1
        """
        results = sparql_utils.execute_query(query)
        if not results:
            return jsonify({"error": "Compétence non trouvée"}), 404
        competence_data = results[0]
        search_term = request.args.get('term') or competence_data.get("nomCompetence") or competence_data.get("typeCompetence", "")
        enriched_data = {"competence": competence_data, "search_term": search_term, "dbpedia_enrichment": None}
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


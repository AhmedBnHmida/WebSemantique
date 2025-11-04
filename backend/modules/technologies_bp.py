"""CRUD endpoints for TechnologiesEducatives"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_technologie
from modules.dbpedia_service import dbpedia_service
import uuid

technologies_bp = Blueprint('technologies', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_technologie_uri(nom: str) -> str:
    """Generate a unique URI for a technologie"""
    safe_nom = nom.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}TechnologieEducative_{safe_nom}_{uuid.uuid4().hex[:8]}"

@technologies_bp.route('/technologies-educatives', methods=['GET'])
def get_all_technologies():
    """Get all educational technologies"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?technologie ?nomTechnologie ?typeTechnologie ?universite ?nomUniversite
           ?ressource ?titreRessource
    WHERE {{
        ?technologie a ont:TechnologieEducative .
        OPTIONAL {{ ?technologie ont:nomTechnologie ?nomTechnologie . }}
        OPTIONAL {{ ?technologie ont:typeTechnologie ?typeTechnologie . }}
        OPTIONAL {{
            ?universite ont:adopteTechnologie ?technologie .
            ?universite ont:nomUniversite ?nomUniversite .
        }}
        OPTIONAL {{
            ?technologie ont:hebergeRessource ?ressource .
            ?ressource ont:titreRessource ?titreRessource .
        }}
    }}
    ORDER BY ?nomTechnologie
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives/<technologie_id>', methods=['GET'])
def get_technologie(technologie_id):
    """Get a specific technology"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?technologie ?nomTechnologie ?typeTechnologie
           ?universite ?nomUniversite
           ?ressource ?titreRessource
           ?cours ?intitule
    WHERE {{
        <{technologie_id}> a ont:TechnologieEducative .
        OPTIONAL {{ <{technologie_id}> ont:nomTechnologie ?nomTechnologie . }}
        OPTIONAL {{ <{technologie_id}> ont:typeTechnologie ?typeTechnologie . }}
        OPTIONAL {{
            ?universite ont:adopteTechnologie <{technologie_id}> .
            ?universite ont:nomUniversite ?nomUniversite .
        }}
        OPTIONAL {{
            <{technologie_id}> ont:hebergeRessource ?ressource .
            ?ressource ont:titreRessource ?titreRessource .
        }}
        OPTIONAL {{
            ?cours ont:integreTechnologie <{technologie_id}> .
            ?cours ont:intitule ?intitule .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives', methods=['POST'])
def create_technologie():
    """Create a new technology"""
    data = request.json
    
    errors = validate_technologie(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    technologie_uri = generate_technologie_uri(data.get('nomTechnologie'))
    
    insert_parts = [
        f"<{technologie_uri}> a ont:TechnologieEducative",
        f"; ont:nomTechnologie \"{data.get('nomTechnologie')}\""
    ]
    
    if data.get('typeTechnologie'):
        insert_parts.append(f"; ont:typeTechnologie \"{data.get('typeTechnologie')}\"")
    if data.get('universite'):
        insert_parts.append(f"<{data.get('universite')}> ont:adopteTechnologie <{technologie_uri}> .")
    
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
        return jsonify({"message": "Technologie créée avec succès", "uri": technologie_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives/<technologie_id>', methods=['PUT'])
def update_technologie(technologie_id):
    """Update a technology"""
    data = request.json
    
    errors = validate_technologie(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{technologie_id}> ?p ?o .
        ?univ ont:adopteTechnologie <{technologie_id}> .
    }}
    WHERE {{
        <{technologie_id}> ?p ?o .
        OPTIONAL {{ ?univ ont:adopteTechnologie <{technologie_id}> . }}
    }}
    """
    
    insert_parts = [f"<{technologie_id}> a ont:TechnologieEducative"]
    
    if data.get('nomTechnologie'):
        insert_parts.append(f"; ont:nomTechnologie \"{data.get('nomTechnologie')}\"")
    if data.get('typeTechnologie'):
        insert_parts.append(f"; ont:typeTechnologie \"{data.get('typeTechnologie')}\"")
    
    query_parts = [f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ {' '.join(insert_parts)} . }}"]
    
    if data.get('universite'):
        query_parts.append(f"INSERT DATA {{ <{data.get('universite')}> ont:adopteTechnologie <{technologie_id}> . }}")
    
    try:
        sparql_utils.execute_update(delete_query)
        for insert_q in query_parts:
            sparql_utils.execute_update(insert_q)
        return jsonify({"message": "Technologie mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives/<technologie_id>', methods=['DELETE'])
def delete_technologie(technologie_id):
    """Delete a technology"""
    # Construct full URI if not already a full URI
    if technologie_id.startswith('http://') or technologie_id.startswith('https://'):
        technologie_uri = technologie_id
    else:
        if technologie_id.startswith(PREFIX):
            technologie_uri = technologie_id
        else:
            technologie_uri = f"{PREFIX}{technologie_id}"
    
    # Delete triples where technologie is subject
    query1 = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{technologie_uri}> ?p ?o .
    }}
    """
    
    # Delete triples where technologie appears in reverse relationships
    query2 = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        ?univ ont:adopteTechnologie <{technologie_uri}> .
    }}
    """
    
    query3 = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        ?cours ont:integreTechnologie <{technologie_uri}> .
    }}
    """
    
    try:
        result1 = sparql_utils.execute_update(query1)
        if "error" in result1:
            return jsonify(result1), 500
        
        result2 = sparql_utils.execute_update(query2)
        if "error" in result2:
            return jsonify(result2), 500
        
        result3 = sparql_utils.execute_update(query3)
        if "error" in result3:
            return jsonify(result3), 500
        
        return jsonify({"message": "Technologie supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives/search', methods=['POST'])
def search_technologies():
    """Search technologies"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?technologie ?nomTechnologie ?typeTechnologie
    WHERE {{
        ?technologie a ont:TechnologieEducative .
        OPTIONAL {{ ?technologie ont:nomTechnologie ?nomTechnologie . }}
        OPTIONAL {{ ?technologie ont:typeTechnologie ?typeTechnologie . }}
    """
    
    if data.get('nomTechnologie'):
        filters.append(f'REGEX(?nomTechnologie, "{data.get("nomTechnologie")}", "i")')
    if data.get('typeTechnologie'):
        filters.append(f'REGEX(?typeTechnologie, "{data.get("typeTechnologie")}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?nomTechnologie"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives/facets', methods=['GET'])
def get_technologies_facets():
    """Récupère les facettes pour la navigation filtrée"""
    query_type = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?typeTechnologie (COUNT(DISTINCT ?technologie) as ?count)
    WHERE {{
        ?technologie a ont:TechnologieEducative .
        ?technologie ont:typeTechnologie ?typeTechnologie .
    }}
    GROUP BY ?typeTechnologie
    ORDER BY DESC(?count)
    """
    query_universite = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?universite ?nomUniversite (COUNT(DISTINCT ?technologie) as ?count)
    WHERE {{
        ?universite ont:adopteTechnologie ?technologie .
        ?universite ont:nomUniversite ?nomUniversite .
    }}
    GROUP BY ?universite ?nomUniversite
    ORDER BY DESC(?count)
    LIMIT 20
    """
    try:
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_universite": sparql_utils.execute_query(query_universite)
        }
        return jsonify(facets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technologies_bp.route('/technologies-educatives/<path:technologie_id>/dbpedia-enrich', methods=['GET'])
def enrich_technologie_with_dbpedia(technologie_id):
    """Enrich technologie data with DBpedia information"""
    try:
        query = f"""
        PREFIX ont: <{PREFIX}>
        SELECT ?nomTechnologie ?typeTechnologie
        WHERE {{
            <{technologie_id}> a ont:TechnologieEducative .
            OPTIONAL {{ <{technologie_id}> ont:nomTechnologie ?nomTechnologie . }}
            OPTIONAL {{ <{technologie_id}> ont:typeTechnologie ?typeTechnologie . }}
        }}
        LIMIT 1
        """
        results = sparql_utils.execute_query(query)
        if not results:
            return jsonify({"error": "Technologie non trouvée"}), 404
        technologie_data = results[0]
        search_term = request.args.get('term') or technologie_data.get("nomTechnologie") or technologie_data.get("typeTechnologie", "")
        enriched_data = {"technologie": technologie_data, "search_term": search_term, "dbpedia_enrichment": None}
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


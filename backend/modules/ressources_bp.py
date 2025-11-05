"""CRUD endpoints for RessourcesPedagogiques"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_ressource
from modules.dbpedia_service import dbpedia_service
import uuid

ressources_bp = Blueprint('ressources', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_ressource_uri(titre: str) -> str:
    """Generate a unique URI for a ressource"""
    safe_titre = titre.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}RessourcePedagogique_{safe_titre}_{uuid.uuid4().hex[:8]}"

@ressources_bp.route('/ressources-pedagogiques', methods=['GET'])
def get_all_ressources():
    """Get all pedagogical resources"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?ressource ?titreRessource ?typeRessource ?formatRessource ?urlRessource
           ?technologie ?nomTechnologie
    WHERE {{
        ?ressource a ?type .
        ?type rdfs:subClassOf* ont:RessourcePedagogique .
        OPTIONAL {{ ?ressource ont:titreRessource ?titreRessource . }}
        OPTIONAL {{ ?ressource ont:typeRessource ?typeRessource . }}
        OPTIONAL {{ ?ressource ont:formatRessource ?formatRessource . }}
        OPTIONAL {{ ?ressource ont:urlRessource ?urlRessource . }}
        OPTIONAL {{
            ?ressource ont:estHebergePar ?technologie .
            ?technologie ont:nomTechnologie ?nomTechnologie .
        }}
    }}
    ORDER BY ?titreRessource
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/<ressource_id>', methods=['GET'])
def get_ressource(ressource_id):
    """Get a specific pedagogical resource"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?ressource ?titreRessource ?typeRessource ?formatRessource ?urlRessource
           ?technologie ?nomTechnologie
    WHERE {{
        <{ressource_id}> a ?type .
        ?type rdfs:subClassOf* ont:RessourcePedagogique .
        OPTIONAL {{ <{ressource_id}> ont:titreRessource ?titreRessource . }}
        OPTIONAL {{ <{ressource_id}> ont:typeRessource ?typeRessource . }}
        OPTIONAL {{ <{ressource_id}> ont:formatRessource ?formatRessource . }}
        OPTIONAL {{ <{ressource_id}> ont:urlRessource ?urlRessource . }}
        OPTIONAL {{
            <{ressource_id}> ont:estHebergePar ?technologie .
            ?technologie ont:nomTechnologie ?nomTechnologie .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques', methods=['POST'])
def create_ressource():
    """Create a new pedagogical resource"""
    data = request.json
    errors = validate_ressource(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    ressource_uri = generate_ressource_uri(data.get('titreRessource'))
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    INSERT DATA {{
        <{ressource_uri}> a ont:RessourcePedagogique .
        <{ressource_uri}> ont:titreRessource "{data.get('titreRessource')}" .
    """
    
    if data.get('typeRessource'):
        query += f'        <{ressource_uri}> ont:typeRessource "{data.get("typeRessource")}" .\n'
    if data.get('formatRessource'):
        query += f'        <{ressource_uri}> ont:formatRessource "{data.get("formatRessource")}" .\n'
    if data.get('urlRessource'):
        query += f'        <{ressource_uri}> ont:urlRessource <{data.get("urlRessource")}> .\n'
    if data.get('technologie'):
        query += f'        <{ressource_uri}> ont:estHebergePar <{data.get("technologie")}> .\n'
    
    query += "    }"
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Ressource créée avec succès", "uri": ressource_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/<ressource_id>', methods=['PUT'])
def update_ressource(ressource_id):
    """Update a pedagogical resource"""
    data = request.json
    errors = validate_ressource(data, is_update=True)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Delete existing properties
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{ressource_id}> ?p ?o .
    }}
    WHERE {{
        <{ressource_id}> ?p ?o .
    }}
    """
    
    # Insert new properties
    insert_query = f"""
    PREFIX ont: <{PREFIX}>
    INSERT DATA {{
        <{ressource_id}> a ont:RessourcePedagogique .
        <{ressource_id}> ont:titreRessource "{data.get('titreRessource')}" .
    """
    
    if data.get('typeRessource'):
        insert_query += f'        <{ressource_id}> ont:typeRessource "{data.get("typeRessource")}" .\n'
    if data.get('formatRessource'):
        insert_query += f'        <{ressource_id}> ont:formatRessource "{data.get("formatRessource")}" .\n'
    if data.get('urlRessource'):
        insert_query += f'        <{ressource_id}> ont:urlRessource <{data.get("urlRessource")}> .\n'
    if data.get('technologie'):
        insert_query += f'        <{ressource_id}> ont:estHebergePar <{data.get("technologie")}> .\n'
    
    insert_query += "    }"
    
    try:
        # Execute delete first
        delete_result = sparql_utils.execute_update(delete_query)
        if "error" in delete_result:
            return jsonify(delete_result), 500
        
        # Then insert new data
        insert_result = sparql_utils.execute_update(insert_query)
        if "error" in insert_result:
            return jsonify(insert_result), 500
        
        return jsonify({"message": "Ressource mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/<ressource_id>', methods=['DELETE'])
def delete_ressource(ressource_id):
    """Delete a pedagogical resource"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{ressource_id}> ?p ?o .
    }}
    WHERE {{
        <{ressource_id}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Ressource supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/search', methods=['POST'])
def search_ressources():
    """Search resources by criteria"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?ressource ?titreRessource ?typeRessource ?formatRessource ?urlRessource
    WHERE {{
        ?ressource a ?type .
        ?type rdfs:subClassOf* ont:RessourcePedagogique .
    """
    
    if data.get('titreRessource'):
        filters.append(f'FILTER(CONTAINS(LCASE(?titreRessource), LCASE("{data.get("titreRessource")}")))')
    
    if data.get('typeRessource'):
        filters.append(f'?ressource ont:typeRessource "{data.get("typeRessource")}" .')
    
    if filters:
        query += "        " + " .\n        ".join(filters) + " .\n"
    
    query += """
        OPTIONAL { ?ressource ont:titreRessource ?titreRessource . }
        OPTIONAL { ?ressource ont:typeRessource ?typeRessource . }
        OPTIONAL { ?ressource ont:formatRessource ?formatRessource . }
        OPTIONAL { ?ressource ont:urlRessource ?urlRessource . }
    }
    ORDER BY ?titreRessource
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/facets', methods=['GET'])
def get_ressources_facets():
    """Récupère les facettes pour la navigation filtrée"""
    query_type = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?typeRessource (COUNT(DISTINCT ?ressource) as ?count)
    WHERE {{
        ?ressource a ?type .
        ?type rdfs:subClassOf* ont:RessourcePedagogique .
        ?ressource ont:typeRessource ?typeRessource .
    }}
    GROUP BY ?typeRessource
    ORDER BY DESC(?count)
    """
    query_technologie = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?technologie ?nomTechnologie (COUNT(DISTINCT ?ressource) as ?count)
    WHERE {{
        ?technologie ont:hebergeRessource ?ressource .
        ?technologie ont:nomTechnologie ?nomTechnologie .
    }}
    GROUP BY ?technologie ?nomTechnologie
    ORDER BY DESC(?count)
    LIMIT 20
    """
    try:
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_technologie": sparql_utils.execute_query(query_technologie)
        }
        return jsonify(facets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/<path:ressource_id>/dbpedia-enrich', methods=['GET'])
def enrich_ressource_with_dbpedia(ressource_id):
    """Enrich ressource data with DBpedia information"""
    try:
        query = f"""
        PREFIX ont: <{PREFIX}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?titreRessource ?typeRessource
        WHERE {{
            <{ressource_id}> a ?type .
            ?type rdfs:subClassOf* ont:RessourcePedagogique .
            OPTIONAL {{ <{ressource_id}> ont:titreRessource ?titreRessource . }}
            OPTIONAL {{ <{ressource_id}> ont:typeRessource ?typeRessource . }}
        }}
        LIMIT 1
        """
        results = sparql_utils.execute_query(query)
        if not results:
            return jsonify({"error": "Ressource non trouvée"}), 404
        ressource_data = results[0]
        search_term = request.args.get('term') or ressource_data.get("titreRessource") or ressource_data.get("typeRessource", "")
        enriched_data = {"ressource": ressource_data, "search_term": search_term, "dbpedia_enrichment": None}
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

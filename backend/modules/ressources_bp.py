"""CRUD endpoints for RessourcesPedagogiques"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_ressource
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
    SELECT ?ressource ?titreRessource ?typeRessource ?technologie ?nomTechnologie
    WHERE {{
        ?ressource a ont:RessourcePedagogique .
        OPTIONAL {{ ?ressource ont:titreRessource ?titreRessource . }}
        OPTIONAL {{ ?ressource ont:typeRessource ?typeRessource . }}
        OPTIONAL {{
            ?technologie ont:hebergeRessource ?ressource .
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
    """Get a specific resource"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?ressource ?titreRessource ?typeRessource ?technologie ?nomTechnologie
    WHERE {{
        <{ressource_id}> a ont:RessourcePedagogique .
        OPTIONAL {{ <{ressource_id}> ont:titreRessource ?titreRessource . }}
        OPTIONAL {{ <{ressource_id}> ont:typeRessource ?typeRessource . }}
        OPTIONAL {{
            ?technologie ont:hebergeRessource <{ressource_id}> .
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
    """Create a new resource"""
    data = request.json
    
    errors = validate_ressource(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    ressource_uri = generate_ressource_uri(data.get('titreRessource'))
    
    insert_parts = [
        f"<{ressource_uri}> a ont:RessourcePedagogique",
        f"; ont:titreRessource \"{data.get('titreRessource')}\""
    ]
    
    if data.get('typeRessource'):
        insert_parts.append(f"; ont:typeRessource \"{data.get('typeRessource')}\"")
    if data.get('technologie'):
        insert_parts.append(f"<{data.get('technologie')}> ont:hebergeRessource <{ressource_uri}> .")
    
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
        return jsonify({"message": "Ressource créée avec succès", "uri": ressource_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/<ressource_id>', methods=['PUT'])
def update_ressource(ressource_id):
    """Update a resource"""
    data = request.json
    
    errors = validate_ressource(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{ressource_id}> ?p ?o .
        ?tech ont:hebergeRessource <{ressource_id}> .
    }}
    WHERE {{
        <{ressource_id}> ?p ?o .
        OPTIONAL {{ ?tech ont:hebergeRessource <{ressource_id}> . }}
    }}
    """
    
    insert_parts = [f"<{ressource_id}> a ont:RessourcePedagogique"]
    
    if data.get('titreRessource'):
        insert_parts.append(f"; ont:titreRessource \"{data.get('titreRessource')}\"")
    if data.get('typeRessource'):
        insert_parts.append(f"; ont:typeRessource \"{data.get('typeRessource')}\"")
    
    query_parts = [f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ {' '.join(insert_parts)} . }}"]
    
    if data.get('technologie'):
        query_parts.append(f"INSERT DATA {{ <{data.get('technologie')}> ont:hebergeRessource <{ressource_id}> . }}")
    
    try:
        sparql_utils.execute_update(delete_query)
        for insert_q in query_parts:
            sparql_utils.execute_update(insert_q)
        return jsonify({"message": "Ressource mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/<ressource_id>', methods=['DELETE'])
def delete_ressource(ressource_id):
    """Delete a resource"""
    # Construct full URI if not already a full URI
    if ressource_id.startswith('http://') or ressource_id.startswith('https://'):
        ressource_uri = ressource_id
    else:
        if ressource_id.startswith(PREFIX):
            ressource_uri = ressource_id
        else:
            ressource_uri = f"{PREFIX}{ressource_id}"
    
    # Delete triples where ressource is subject
    query1 = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{ressource_uri}> ?p ?o .
    }}
    """
    
    # Delete triples with reverse relationships
    query2 = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        ?tech ont:hebergeRessource <{ressource_uri}> .
    }}
    """
    
    try:
        result1 = sparql_utils.execute_update(query1)
        if "error" in result1:
            return jsonify(result1), 500
        
        result2 = sparql_utils.execute_update(query2)
        if "error" in result2:
            return jsonify(result2), 500
        
        return jsonify({"message": "Ressource supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ressources_bp.route('/ressources-pedagogiques/search', methods=['POST'])
def search_ressources():
    """Search resources"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?ressource ?titreRessource ?typeRessource
    WHERE {{
        ?ressource a ont:RessourcePedagogique .
        OPTIONAL {{ ?ressource ont:titreRessource ?titreRessource . }}
        OPTIONAL {{ ?ressource ont:typeRessource ?typeRessource . }}
    """
    
    if data.get('titreRessource'):
        filters.append(f'REGEX(?titreRessource, "{data.get("titreRessource")}", "i")')
    if data.get('typeRessource'):
        filters.append(f'REGEX(?typeRessource, "{data.get("typeRessource")}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?titreRessource"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


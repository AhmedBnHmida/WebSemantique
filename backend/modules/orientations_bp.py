"""CRUD endpoints for OrientationsAcademiques"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_orientation
import uuid

orientations_bp = Blueprint('orientations', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_orientation_uri(objectif: str) -> str:
    """Generate a unique URI for an orientation"""
    safe_objectif = objectif.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}OrientationAcademique_{safe_objectif}_{uuid.uuid4().hex[:8]}"

@orientations_bp.route('/orientations-academiques', methods=['GET'])
def get_all_orientations():
    """Get all academic orientations"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?orientation ?objectifOrientation ?typeOrientation ?dateOrientation
           ?personne ?nomPersonne ?prenomPersonne
           ?specialite ?nomSpecialite
           ?cours ?intitule
           ?projet ?titreProjet
    WHERE {{
        ?orientation a ont:OrientationAcademique .
        OPTIONAL {{ ?orientation ont:objectifOrientation ?objectifOrientation . }}
        OPTIONAL {{ ?orientation ont:typeOrientation ?typeOrientation . }}
        OPTIONAL {{ ?orientation ont:dateOrientation ?dateOrientation . }}
        OPTIONAL {{
            ?personne ont:participeA ?orientation .
            ?personne ont:nom ?nomPersonne .
            ?personne ont:prenom ?prenomPersonne .
        }}
        OPTIONAL {{
            ?orientation ont:recommandeSpecialite ?specialite .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
        OPTIONAL {{
            ?orientation ont:recommandeCours ?cours .
            ?cours ont:intitule ?intitule .
        }}
        OPTIONAL {{
            ?orientation ont:proposeStage ?projet .
            ?projet ont:titreProjet ?titreProjet .
        }}
    }}
    ORDER BY ?dateOrientation DESC
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/<orientation_id>', methods=['GET'])
def get_orientation(orientation_id):
    """Get a specific orientation"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?orientation ?objectifOrientation ?typeOrientation ?dateOrientation
           ?personne ?nomPersonne ?prenomPersonne
           ?specialite ?nomSpecialite
           ?cours ?intitule
           ?projet ?titreProjet
    WHERE {{
        <{orientation_id}> a ont:OrientationAcademique .
        OPTIONAL {{ <{orientation_id}> ont:objectifOrientation ?objectifOrientation . }}
        OPTIONAL {{ <{orientation_id}> ont:typeOrientation ?typeOrientation . }}
        OPTIONAL {{ <{orientation_id}> ont:dateOrientation ?dateOrientation . }}
        OPTIONAL {{
            ?personne ont:participeA <{orientation_id}> .
            ?personne ont:nom ?nomPersonne .
            ?personne ont:prenom ?prenomPersonne .
        }}
        OPTIONAL {{
            <{orientation_id}> ont:recommandeSpecialite ?specialite .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
        OPTIONAL {{
            <{orientation_id}> ont:recommandeCours ?cours .
            ?cours ont:intitule ?intitule .
        }}
        OPTIONAL {{
            <{orientation_id}> ont:proposeStage ?projet .
            ?projet ont:titreProjet ?titreProjet .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques', methods=['POST'])
def create_orientation():
    """Create a new orientation"""
    data = request.json
    
    errors = validate_orientation(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    orientation_uri = generate_orientation_uri(data.get('objectifOrientation'))
    
    insert_parts = [
        f"<{orientation_uri}> a ont:OrientationAcademique",
        f"; ont:objectifOrientation \"{data.get('objectifOrientation')}\""
    ]
    
    if data.get('typeOrientation'):
        insert_parts.append(f"; ont:typeOrientation \"{data.get('typeOrientation')}\"")
    if data.get('dateOrientation'):
        insert_parts.append(f"; ont:dateOrientation \"{data.get('dateOrientation')}\"^^xsd:date")
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    # Handle relationships separately
    relationship_queries = []
    if data.get('personne'):
        relationship_queries.append(f"INSERT DATA {{ <{data.get('personne')}> ont:participeA <{orientation_uri}> . }}")
    if data.get('specialite'):
        relationship_queries.append(f"INSERT DATA {{ <{orientation_uri}> ont:recommandeSpecialite <{data.get('specialite')}> . }}")
    if data.get('cours'):
        relationship_queries.append(f"INSERT DATA {{ <{orientation_uri}> ont:recommandeCours <{data.get('cours')}> . }}")
    if data.get('projet'):
        relationship_queries.append(f"INSERT DATA {{ <{orientation_uri}> ont:proposeStage <{data.get('projet')}> . }}")
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        
        for rel_query in relationship_queries:
            sparql_utils.execute_update(rel_query)
        
        return jsonify({"message": "Orientation créée avec succès", "uri": orientation_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/<orientation_id>', methods=['PUT'])
def update_orientation(orientation_id):
    """Update an orientation"""
    data = request.json
    
    errors = validate_orientation(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Delete all relationships and properties
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{orientation_id}> ?p ?o .
        ?personne ont:participeA <{orientation_id}> .
        ?specialite ont:recommandeSpecialite <{orientation_id}> .
        ?cours ont:recommandeCours <{orientation_id}> .
        ?projet ont:proposeStage <{orientation_id}> .
    }}
    WHERE {{
        <{orientation_id}> ?p ?o .
        OPTIONAL {{ ?personne ont:participeA <{orientation_id}> . }}
        OPTIONAL {{ ?specialite ont:recommandeSpecialite <{orientation_id}> . }}
        OPTIONAL {{ ?cours ont:recommandeCours <{orientation_id}> . }}
        OPTIONAL {{ ?projet ont:proposeStage <{orientation_id}> . }}
    }}
    """
    
    insert_parts = [f"<{orientation_id}> a ont:OrientationAcademique"]
    
    if data.get('objectifOrientation'):
        insert_parts.append(f"; ont:objectifOrientation \"{data.get('objectifOrientation')}\"")
    if data.get('typeOrientation'):
        insert_parts.append(f"; ont:typeOrientation \"{data.get('typeOrientation')}\"")
    if data.get('dateOrientation'):
        insert_parts.append(f"; ont:dateOrientation \"{data.get('dateOrientation')}\"^^xsd:date")
    
    insert_query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    relationship_queries = []
    if data.get('personne'):
        relationship_queries.append(f"INSERT DATA {{ <{data.get('personne')}> ont:participeA <{orientation_id}> . }}")
    if data.get('specialite'):
        relationship_queries.append(f"INSERT DATA {{ <{orientation_id}> ont:recommandeSpecialite <{data.get('specialite')}> . }}")
    if data.get('cours'):
        relationship_queries.append(f"INSERT DATA {{ <{orientation_id}> ont:recommandeCours <{data.get('cours')}> . }}")
    if data.get('projet'):
        relationship_queries.append(f"INSERT DATA {{ <{orientation_id}> ont:proposeStage <{data.get('projet')}> . }}")
    
    try:
        sparql_utils.execute_update(delete_query)
        sparql_utils.execute_update(insert_query)
        for rel_query in relationship_queries:
            sparql_utils.execute_update(rel_query)
        return jsonify({"message": "Orientation mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/<orientation_id>', methods=['DELETE'])
def delete_orientation(orientation_id):
    """Delete an orientation"""
    # Construct full URI if not already a full URI
    if orientation_id.startswith('http://') or orientation_id.startswith('https://'):
        orientation_uri = orientation_id
    else:
        if orientation_id.startswith(PREFIX):
            orientation_uri = orientation_id
        else:
            orientation_uri = f"{PREFIX}{orientation_id}"
    
    # Delete triples where orientation is subject
    query1 = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{orientation_uri}> ?p ?o .
    }}
    """
    
    # Delete triples with reverse relationships
    queries = [
        f"""PREFIX ont: <{PREFIX}>
    DELETE WHERE {{ ?personne ont:participeA <{orientation_uri}> . }}""",
        f"""PREFIX ont: <{PREFIX}>
    DELETE WHERE {{ ?specialite ont:recommandeSpecialite <{orientation_uri}> . }}""",
        f"""PREFIX ont: <{PREFIX}>
    DELETE WHERE {{ ?cours ont:recommandeCours <{orientation_uri}> . }}""",
        f"""PREFIX ont: <{PREFIX}>
    DELETE WHERE {{ ?projet ont:proposeStage <{orientation_uri}> . }}"""
    ]
    
    try:
        result1 = sparql_utils.execute_update(query1)
        if "error" in result1:
            return jsonify(result1), 500
        
        for query in queries:
            result = sparql_utils.execute_update(query)
            if "error" in result:
                return jsonify(result), 500
        
        return jsonify({"message": "Orientation supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/search', methods=['POST'])
def search_orientations():
    """Search orientations"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?orientation ?objectifOrientation ?typeOrientation ?dateOrientation
    WHERE {{
        ?orientation a ont:OrientationAcademique .
        OPTIONAL {{ ?orientation ont:objectifOrientation ?objectifOrientation . }}
        OPTIONAL {{ ?orientation ont:typeOrientation ?typeOrientation . }}
        OPTIONAL {{ ?orientation ont:dateOrientation ?dateOrientation . }}
    """
    
    if data.get('objectifOrientation'):
        filters.append(f'REGEX(?objectifOrientation, "{data.get("objectifOrientation")}", "i")')
    if data.get('typeOrientation'):
        filters.append(f'REGEX(?typeOrientation, "{data.get("typeOrientation")}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?dateOrientation DESC"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""CRUD endpoints for OrientationsAcademiques"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_orientation
from modules.dbpedia_service import dbpedia_service
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
    # Build query as a single continuous line - ensure no newlines or extra whitespace
    query = f"PREFIX ont: <{PREFIX}> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?orientation ?objectifOrientation ?typeOrientation ?dateOrientation ?personne ?nomPersonne ?prenomPersonne ?specialite ?nomSpecialite ?cours ?intitule ?projet ?titreProjet WHERE {{ ?orientation a ?type . ?type rdfs:subClassOf* ont:OrientationAcademique . OPTIONAL {{ ?orientation ont:objectifOrientation ?objectifOrientation . }} OPTIONAL {{ ?orientation ont:typeOrientation ?typeOrientation . }} OPTIONAL {{ ?orientation ont:dateOrientation ?dateOrientation . }} OPTIONAL {{ ?personne ont:participeA ?orientation . ?personne ont:nom ?nomPersonne . ?personne ont:prenom ?prenomPersonne . }} OPTIONAL {{ ?orientation ont:recommandeSpecialite ?specialite . ?specialite ont:nomSpecialite ?nomSpecialite . }} OPTIONAL {{ ?orientation ont:recommandeCours ?cours . ?cours ont:intitule ?intitule . }} OPTIONAL {{ ?orientation ont:proposeStage ?projet . ?projet ont:titreProjet ?titreProjet . }} }} ORDER BY DESC(?dateOrientation)"
    # Remove any potential newlines and normalize whitespace
    query = query.replace('\n', ' ').replace('\r', ' ').strip()
    # Replace multiple spaces with single space
    while '  ' in query:
        query = query.replace('  ', ' ')
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/<orientation_id>', methods=['GET'])
def get_orientation(orientation_id):
    """Get a specific orientation"""
    # Build query as a single continuous line - ensure no newlines or extra whitespace
    query = f"PREFIX ont: <{PREFIX}> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?orientation ?objectifOrientation ?typeOrientation ?dateOrientation ?personne ?nomPersonne ?prenomPersonne ?specialite ?nomSpecialite ?cours ?intitule ?projet ?titreProjet WHERE {{ <{orientation_id}> a ?type . ?type rdfs:subClassOf* ont:OrientationAcademique . OPTIONAL {{ <{orientation_id}> ont:objectifOrientation ?objectifOrientation . }} OPTIONAL {{ <{orientation_id}> ont:typeOrientation ?typeOrientation . }} OPTIONAL {{ <{orientation_id}> ont:dateOrientation ?dateOrientation . }} OPTIONAL {{ ?personne ont:participeA <{orientation_id}> . ?personne ont:nom ?nomPersonne . ?personne ont:prenom ?prenomPersonne . }} OPTIONAL {{ <{orientation_id}> ont:recommandeSpecialite ?specialite . ?specialite ont:nomSpecialite ?nomSpecialite . }} OPTIONAL {{ <{orientation_id}> ont:recommandeCours ?cours . ?cours ont:intitule ?intitule . }} OPTIONAL {{ <{orientation_id}> ont:proposeStage ?projet . ?projet ont:titreProjet ?titreProjet . }} }}"
    # Remove any potential newlines and normalize whitespace
    query = query.replace('\n', ' ').replace('\r', ' ').strip()
    # Replace multiple spaces with single space
    while '  ' in query:
        query = query.replace('  ', ' ')
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
    
    # Escape quotes in string values
    def escape_sparql_string(value):
        if value is None:
            return None
        return str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    
    objectif = escape_sparql_string(data.get('objectifOrientation'))
    type_orient = escape_sparql_string(data.get('typeOrientation')) if data.get('typeOrientation') else None
    date_orient = data.get('dateOrientation')
    
    insert_parts = [
        f"<{orientation_uri}> a ont:OrientationAcademique",
        f"; ont:objectifOrientation \"{objectif}\""
    ]
    
    if type_orient:
        insert_parts.append(f"; ont:typeOrientation \"{type_orient}\"")
    if date_orient:
        insert_parts.append(f"; ont:dateOrientation \"{date_orient}\"^^xsd:date")
    
    # Build the query - ensure it's a single line for INSERT DATA
    data_line = ' '.join(insert_parts) + ' .'
    
    query = f"""PREFIX ont: <{PREFIX}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
INSERT DATA {{
    {data_line}
}}"""
    
    # Handle relationships separately
    relationship_queries = []
    if data.get('personne'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{data.get('personne')}> ont:participeA <{orientation_uri}> . }}")
    if data.get('specialite'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{orientation_uri}> ont:recommandeSpecialite <{data.get('specialite')}> . }}")
    if data.get('cours'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{orientation_uri}> ont:recommandeCours <{data.get('cours')}> . }}")
    if data.get('projet'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{orientation_uri}> ont:proposeStage <{data.get('projet')}> . }}")
    
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
    
    # Delete all properties of the orientation (using DELETE WHERE)
    delete_properties_query = f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_id}> ?p ?o . }}"
    
    # Delete reverse relationships separately
    delete_relationships_queries = [
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ ?personne ont:participeA <{orientation_id}> . }}",
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_id}> ont:recommandeSpecialite ?specialite . }}",
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_id}> ont:recommandeCours ?cours . }}",
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_id}> ont:proposeStage ?projet . }}"
    ]
    
    # Escape quotes in string values
    def escape_sparql_string(value):
        if value is None:
            return None
        return str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    
    objectif = escape_sparql_string(data.get('objectifOrientation')) if data.get('objectifOrientation') else None
    type_orient = escape_sparql_string(data.get('typeOrientation')) if data.get('typeOrientation') else None
    date_orient = data.get('dateOrientation')
    
    insert_parts = [f"<{orientation_id}> a ont:OrientationAcademique"]
    
    if objectif:
        insert_parts.append(f"; ont:objectifOrientation \"{objectif}\"")
    if type_orient:
        insert_parts.append(f"; ont:typeOrientation \"{type_orient}\"")
    if date_orient:
        insert_parts.append(f"; ont:dateOrientation \"{date_orient}\"^^xsd:date")
    
    # Build the query - ensure it's a single line for INSERT DATA
    data_line = ' '.join(insert_parts) + ' .'
    
    insert_query = f"""PREFIX ont: <{PREFIX}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
INSERT DATA {{
    {data_line}
}}"""
    
    relationship_queries = []
    if data.get('personne'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{data.get('personne')}> ont:participeA <{orientation_id}> . }}")
    if data.get('specialite'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{orientation_id}> ont:recommandeSpecialite <{data.get('specialite')}> . }}")
    if data.get('cours'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{orientation_id}> ont:recommandeCours <{data.get('cours')}> . }}")
    if data.get('projet'):
        relationship_queries.append(f"PREFIX ont: <{PREFIX}>\nINSERT DATA {{ <{orientation_id}> ont:proposeStage <{data.get('projet')}> . }}")
    
    try:
        # Delete existing properties and relationships
        result = sparql_utils.execute_update(delete_properties_query)
        if "error" in result:
            return jsonify(result), 500
        
        # Delete all relationships
        for del_query in delete_relationships_queries:
            result = sparql_utils.execute_update(del_query)
            if "error" in result:
                return jsonify(result), 500
        
        # Insert updated properties
        result = sparql_utils.execute_update(insert_query)
        if "error" in result:
            return jsonify(result), 500
        
        # Insert new relationships
        for rel_query in relationship_queries:
            result = sparql_utils.execute_update(rel_query)
            if "error" in result:
                return jsonify(result), 500
        
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
    query1 = f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_uri}> ?p ?o . }}"
    
    # Delete triples with reverse relationships (personne participates in orientation)
    # and forward relationships (orientation recommends specialite/cours/projet)
    queries = [
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ ?personne ont:participeA <{orientation_uri}> . }}",
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_uri}> ont:recommandeSpecialite ?specialite . }}",
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_uri}> ont:recommandeCours ?cours . }}",
        f"PREFIX ont: <{PREFIX}>\nDELETE WHERE {{ <{orientation_uri}> ont:proposeStage ?projet . }}"
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
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?orientation ?objectifOrientation ?typeOrientation ?dateOrientation
    WHERE {{
        ?orientation a ?type .
        ?type rdfs:subClassOf* ont:OrientationAcademique .
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
    
    query += "} ORDER BY DESC(?dateOrientation)"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/facets', methods=['GET'])
def get_orientations_facets():
    """Récupère les facettes pour la navigation filtrée"""
    query_type = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?typeOrientation (COUNT(DISTINCT ?orientation) as ?count)
    WHERE {{
        ?orientation a ?type .
        ?type rdfs:subClassOf* ont:OrientationAcademique .
        ?orientation ont:typeOrientation ?typeOrientation .
    }}
    GROUP BY ?typeOrientation
    ORDER BY DESC(?count)
    """
    query_specialite = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?specialite ?nomSpecialite (COUNT(DISTINCT ?orientation) as ?count)
    WHERE {{
        ?orientation a ?type .
        ?type rdfs:subClassOf* ont:OrientationAcademique .
        ?orientation ont:recommandeSpecialite ?specialite .
        ?specialite ont:nomSpecialite ?nomSpecialite .
    }}
    GROUP BY ?specialite ?nomSpecialite
    ORDER BY DESC(?count)
    LIMIT 20
    """
    try:
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_specialite": sparql_utils.execute_query(query_specialite)
        }
        return jsonify(facets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orientations_bp.route('/orientations-academiques/<path:orientation_id>/dbpedia-enrich', methods=['GET'])
def enrich_orientation_with_dbpedia(orientation_id):
    """Enrich orientation data with DBpedia information"""
    try:
        query = f"""
        PREFIX ont: <{PREFIX}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?objectifOrientation ?typeOrientation
        WHERE {{
            <{orientation_id}> a ?type .
            ?type rdfs:subClassOf* ont:OrientationAcademique .
            OPTIONAL {{ <{orientation_id}> ont:objectifOrientation ?objectifOrientation . }}
            OPTIONAL {{ <{orientation_id}> ont:typeOrientation ?typeOrientation . }}
        }}
        LIMIT 1
        """
        results = sparql_utils.execute_query(query)
        if not results:
            return jsonify({"error": "Orientation non trouvée"}), 404
        orientation_data = results[0]
        search_term = request.args.get('term') or orientation_data.get("objectifOrientation") or orientation_data.get("typeOrientation", "")
        enriched_data = {"orientation": orientation_data, "search_term": search_term, "dbpedia_enrichment": None}
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


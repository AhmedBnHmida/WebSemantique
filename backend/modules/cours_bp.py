"""CRUD endpoints for Cours (Courses)"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_cours
import uuid

cours_bp = Blueprint('cours', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_cours_uri(code_cours: str) -> str:
    """Generate a unique URI for a cours"""
    safe_code = code_cours.upper().replace(' ', '_')
    return f"{PREFIX}Cours_{safe_code}_{uuid.uuid4().hex[:8]}"

@cours_bp.route('/cours', methods=['GET'])
def get_all_cours():
    """Get all courses"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre ?volumeHoraire ?langueCours
           ?specialite ?nomSpecialite
    WHERE {{
        ?cours a ont:Cours .
        OPTIONAL {{ ?cours ont:intitule ?intitule . }}
        OPTIONAL {{ ?cours ont:codeCours ?codeCours . }}
        OPTIONAL {{ ?cours ont:creditsECTS ?creditsECTS . }}
        OPTIONAL {{ ?cours ont:semestre ?semestre . }}
        OPTIONAL {{ ?cours ont:volumeHoraire ?volumeHoraire . }}
        OPTIONAL {{ ?cours ont:langueCours ?langueCours . }}
        OPTIONAL {{
            ?cours ont:faitPartieDe ?specialite .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
    }}
    ORDER BY ?codeCours
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cours_bp.route('/cours/<cours_id>', methods=['GET'])
def get_cours(cours_id):
    """Get a specific course"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre ?volumeHoraire ?langueCours
           ?specialite ?nomSpecialite ?enseignant ?nomEnseignant ?prenomEnseignant
    WHERE {{
        <{cours_id}> a ont:Cours .
        OPTIONAL {{ <{cours_id}> ont:intitule ?intitule . }}
        OPTIONAL {{ <{cours_id}> ont:codeCours ?codeCours . }}
        OPTIONAL {{ <{cours_id}> ont:creditsECTS ?creditsECTS . }}
        OPTIONAL {{ <{cours_id}> ont:semestre ?semestre . }}
        OPTIONAL {{ <{cours_id}> ont:volumeHoraire ?volumeHoraire . }}
        OPTIONAL {{ <{cours_id}> ont:langueCours ?langueCours . }}
        OPTIONAL {{
            <{cours_id}> ont:faitPartieDe ?specialite .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
        OPTIONAL {{
            <{cours_id}> ont:enseignePar ?enseignant .
            ?enseignant ont:nom ?nomEnseignant .
            ?enseignant ont:prenom ?prenomEnseignant .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cours_bp.route('/cours', methods=['POST'])
def create_cours():
    """Create a new course"""
    data = request.json
    
    # Validation
    errors = validate_cours(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Generate URI
    cours_uri = generate_cours_uri(data.get('codeCours'))
    
    # Build INSERT query
    insert_parts = [
        f"<{cours_uri}> a ont:Cours",
        f"; ont:intitule \"{data.get('intitule')}\"",
        f"; ont:codeCours \"{data.get('codeCours')}\""
    ]
    
    if data.get('creditsECTS'):
        insert_parts.append(f"; ont:creditsECTS {int(data.get('creditsECTS'))}")
    
    if data.get('semestre'):
        insert_parts.append(f"; ont:semestre \"{data.get('semestre')}\"")
    
    if data.get('volumeHoraire'):
        insert_parts.append(f"; ont:volumeHoraire {int(data.get('volumeHoraire'))}")
    
    if data.get('langueCours'):
        insert_parts.append(f"; ont:langueCours \"{data.get('langueCours')}\"")
    
    if data.get('specialite'):
        insert_parts.append(f"; ont:faitPartieDe <{data.get('specialite')}>")
    
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
        return jsonify({"message": "Cours créé avec succès", "uri": cours_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cours_bp.route('/cours/<cours_id>', methods=['PUT'])
def update_cours(cours_id):
    """Update a course"""
    data = request.json
    
    # Validation
    errors = validate_cours(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Build DELETE and INSERT for update
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{cours_id}> ?p ?o .
    }}
    WHERE {{
        <{cours_id}> ?p ?o .
    }}
    """
    
    insert_parts = [f"<{cours_id}> a ont:Cours"]
    
    if data.get('intitule'):
        insert_parts.append(f"; ont:intitule \"{data.get('intitule')}\"")
    if data.get('codeCours'):
        insert_parts.append(f"; ont:codeCours \"{data.get('codeCours')}\"")
    if data.get('creditsECTS'):
        insert_parts.append(f"; ont:creditsECTS {int(data.get('creditsECTS'))}")
    if data.get('semestre'):
        insert_parts.append(f"; ont:semestre \"{data.get('semestre')}\"")
    if data.get('volumeHoraire'):
        insert_parts.append(f"; ont:volumeHoraire {int(data.get('volumeHoraire'))}")
    if data.get('langueCours'):
        insert_parts.append(f"; ont:langueCours \"{data.get('langueCours')}\"")
    if data.get('specialite'):
        insert_parts.append(f"; ont:faitPartieDe <{data.get('specialite')}>")
    
    insert_query = f"""
    PREFIX ont: <{PREFIX}>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        # Execute delete
        sparql_utils.execute_update(delete_query)
        # Execute insert
        result = sparql_utils.execute_update(insert_query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Cours mis à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cours_bp.route('/cours/<cours_id>', methods=['DELETE'])
def delete_cours(cours_id):
    """Delete a course"""
    # Construct full URI if not already a full URI
    if cours_id.startswith('http://') or cours_id.startswith('https://'):
        cours_uri = cours_id
    else:
        if cours_id.startswith(PREFIX):
            cours_uri = cours_id
        else:
            cours_uri = f"{PREFIX}{cours_id}"
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{cours_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Cours supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cours_bp.route('/cours/search', methods=['POST'])
def search_cours():
    """Search courses by criteria"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre ?volumeHoraire ?langueCours
    WHERE {{
        ?cours a ont:Cours .
        OPTIONAL {{ ?cours ont:intitule ?intitule . }}
        OPTIONAL {{ ?cours ont:codeCours ?codeCours . }}
        OPTIONAL {{ ?cours ont:creditsECTS ?creditsECTS . }}
        OPTIONAL {{ ?cours ont:semestre ?semestre . }}
        OPTIONAL {{ ?cours ont:volumeHoraire ?volumeHoraire . }}
        OPTIONAL {{ ?cours ont:langueCours ?langueCours . }}
    """
    
    if data.get('intitule'):
        filters.append(f'REGEX(?intitule, "{data.get("intitule")}", "i")')
    if data.get('codeCours'):
        filters.append(f'REGEX(?codeCours, "{data.get("codeCours")}", "i")')
    if data.get('semestre'):
        filters.append(f'REGEX(?semestre, "{data.get("semestre")}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?codeCours"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


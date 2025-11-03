"""CRUD endpoints for ProjetsAcademiques"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_projet
import uuid

projets_bp = Blueprint('projets', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

def generate_projet_uri(titre: str) -> str:
    """Generate a unique URI for a projet"""
    safe_titre = titre.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}ProjetAcademique_{safe_titre}_{uuid.uuid4().hex[:8]}"

@projets_bp.route('/projets-academiques', methods=['GET'])
def get_all_projets():
    """Get all academic projects"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?projet ?titreProjet ?domaineProjet ?typeProjet ?noteProjet ?etudiant ?nomEtudiant ?prenomEtudiant
           ?universite ?nomUniversite
    WHERE {{
        ?projet a ont:ProjetAcademique .
        OPTIONAL {{ ?projet ont:titreProjet ?titreProjet . }}
        OPTIONAL {{ ?projet ont:domaineProjet ?domaineProjet . }}
        OPTIONAL {{ ?projet ont:typeProjet ?typeProjet . }}
        OPTIONAL {{ ?projet ont:noteProjet ?noteProjet . }}
        OPTIONAL {{
            ?projet ont:realisePar ?etudiant .
            ?etudiant ont:nom ?nomEtudiant .
            ?etudiant ont:prenom ?prenomEtudiant .
        }}
        OPTIONAL {{
            ?etudiant ont:appartientA ?universite .
            ?universite ont:nomUniversite ?nomUniversite .
        }}
    }}
    ORDER BY ?titreProjet
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projets_bp.route('/projets-academiques/<projet_id>', methods=['GET'])
def get_projet(projet_id):
    """Get a specific project"""
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?projet ?titreProjet ?domaineProjet ?typeProjet ?noteProjet
           ?etudiant ?nomEtudiant ?prenomEtudiant
           ?competence ?nomCompetence
           ?orientation ?objectifOrientation
    WHERE {{
        <{projet_id}> a ont:ProjetAcademique .
        OPTIONAL {{ <{projet_id}> ont:titreProjet ?titreProjet . }}
        OPTIONAL {{ <{projet_id}> ont:domaineProjet ?domaineProjet . }}
        OPTIONAL {{ <{projet_id}> ont:typeProjet ?typeProjet . }}
        OPTIONAL {{ <{projet_id}> ont:noteProjet ?noteProjet . }}
        OPTIONAL {{
            <{projet_id}> ont:realisePar ?etudiant .
            ?etudiant ont:nom ?nomEtudiant .
            ?etudiant ont:prenom ?prenomEtudiant .
        }}
        OPTIONAL {{
            <{projet_id}> ont:requiertCompetence ?competence .
            ?competence ont:nomCompetence ?nomCompetence .
        }}
        OPTIONAL {{
            ?orientation ont:proposeStage <{projet_id}> .
            ?orientation ont:objectifOrientation ?objectifOrientation .
        }}
    }}
    """
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {}), 404 if not results else 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projets_bp.route('/projets-academiques', methods=['POST'])
def create_projet():
    """Create a new project"""
    data = request.json
    
    errors = validate_projet(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    projet_uri = generate_projet_uri(data.get('titreProjet'))
    
    insert_parts = [
        f"<{projet_uri}> a ont:ProjetAcademique",
        f"; ont:titreProjet \"{data.get('titreProjet')}\""
    ]
    
    if data.get('domaineProjet'):
        insert_parts.append(f"; ont:domaineProjet \"{data.get('domaineProjet')}\"")
    if data.get('typeProjet'):
        insert_parts.append(f"; ont:typeProjet \"{data.get('typeProjet')}\"")
    if data.get('noteProjet'):
        insert_parts.append(f"; ont:noteProjet {float(data.get('noteProjet'))}")
    if data.get('etudiant'):
        insert_parts.append(f"; ont:realisePar <{data.get('etudiant')}>")
    if data.get('competence'):
        insert_parts.append(f"; ont:requiertCompetence <{data.get('competence')}>")
    
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
        return jsonify({"message": "Projet créé avec succès", "uri": projet_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projets_bp.route('/projets-academiques/<projet_id>', methods=['PUT'])
def update_projet(projet_id):
    """Update a project"""
    data = request.json
    
    errors = validate_projet(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{projet_id}> ?p ?o .
    }}
    WHERE {{
        <{projet_id}> ?p ?o .
        FILTER(?p != ont:realisePar && ?p != ont:requiertCompetence)
    }}
    """
    
    insert_parts = [f"<{projet_id}> a ont:ProjetAcademique"]
    
    if data.get('titreProjet'):
        insert_parts.append(f"; ont:titreProjet \"{data.get('titreProjet')}\"")
    if data.get('domaineProjet'):
        insert_parts.append(f"; ont:domaineProjet \"{data.get('domaineProjet')}\"")
    if data.get('typeProjet'):
        insert_parts.append(f"; ont:typeProjet \"{data.get('typeProjet')}\"")
    if data.get('noteProjet'):
        insert_parts.append(f"; ont:noteProjet {float(data.get('noteProjet'))}")
    if data.get('etudiant'):
        insert_parts.append(f"; ont:realisePar <{data.get('etudiant')}>")
    if data.get('competence'):
        insert_parts.append(f"; ont:requiertCompetence <{data.get('competence')}>")
    
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
        return jsonify({"message": "Projet mis à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projets_bp.route('/projets-academiques/<projet_id>', methods=['DELETE'])
def delete_projet(projet_id):
    """Delete a project"""
    # Construct full URI if not already a full URI
    if projet_id.startswith('http://') or projet_id.startswith('https://'):
        projet_uri = projet_id
    else:
        if projet_id.startswith(PREFIX):
            projet_uri = projet_id
        else:
            projet_uri = f"{PREFIX}{projet_id}"
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{projet_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Projet supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projets_bp.route('/projets-academiques/search', methods=['POST'])
def search_projets():
    """Search projects"""
    data = request.json
    filters = []
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?projet ?titreProjet ?domaineProjet ?typeProjet ?noteProjet
    WHERE {{
        ?projet a ont:ProjetAcademique .
        OPTIONAL {{ ?projet ont:titreProjet ?titreProjet . }}
        OPTIONAL {{ ?projet ont:domaineProjet ?domaineProjet . }}
        OPTIONAL {{ ?projet ont:typeProjet ?typeProjet . }}
        OPTIONAL {{ ?projet ont:noteProjet ?noteProjet . }}
    """
    
    if data.get('titreProjet'):
        filters.append(f'REGEX(?titreProjet, "{data.get("titreProjet")}", "i")')
    if data.get('domaineProjet'):
        filters.append(f'REGEX(?domaineProjet, "{data.get("domaineProjet")}", "i")')
    if data.get('typeProjet'):
        filters.append(f'REGEX(?typeProjet, "{data.get("typeProjet")}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?titreProjet"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


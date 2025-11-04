"""CRUD endpoints for ProjetsAcademiques"""

from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_projet
from modules.dbpedia_service import dbpedia_service
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

def normalize_projet_id(projet_id):
    """Normalize projet ID to full URI format"""
    from urllib.parse import unquote
    projet_id = unquote(projet_id)
    
    if not projet_id.startswith('http://') and not projet_id.startswith('https://'):
        if not projet_id.startswith(PREFIX):
            projet_id = f"{PREFIX}{projet_id}"
    
    return projet_id

@projets_bp.route('/projets-academiques/<path:projet_id>', methods=['GET'])
def get_projet(projet_id):
    """Get a specific project"""
    projet_id = normalize_projet_id(projet_id)
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

@projets_bp.route('/projets-academiques/<path:projet_id>', methods=['PUT'])
def update_projet(projet_id):
    """Update a project"""
    projet_id = normalize_projet_id(projet_id)
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

@projets_bp.route('/projets-academiques/<path:projet_id>', methods=['DELETE'])
def delete_projet(projet_id):
    """Delete a project"""
    projet_id = normalize_projet_id(projet_id)
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

@projets_bp.route('/projets-academiques/facets', methods=['GET'])
def get_projets_facets():
    """Récupère les facettes pour la navigation filtrée"""
    query_type = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?typeProjet (COUNT(DISTINCT ?projet) as ?count)
    WHERE {{
        ?projet a ont:ProjetAcademique .
        ?projet ont:typeProjet ?typeProjet .
    }}
    GROUP BY ?typeProjet
    ORDER BY DESC(?count)
    """
    query_domaine = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?domaineProjet (COUNT(DISTINCT ?projet) as ?count)
    WHERE {{
        ?projet a ont:ProjetAcademique .
        ?projet ont:domaineProjet ?domaineProjet .
    }}
    GROUP BY ?domaineProjet
    ORDER BY DESC(?count)
    """
    query_universite = f"""
    PREFIX ont: <{PREFIX}>
    SELECT ?universite ?nomUniversite (COUNT(DISTINCT ?projet) as ?count)
    WHERE {{
        ?projet a ont:ProjetAcademique .
        ?projet ont:estOrganisePar ?universite .
        ?universite ont:nomUniversite ?nomUniversite .
    }}
    GROUP BY ?universite ?nomUniversite
    ORDER BY DESC(?count)
    LIMIT 20
    """
    try:
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_domaine": sparql_utils.execute_query(query_domaine),
            "by_universite": sparql_utils.execute_query(query_universite)
        }
        return jsonify(facets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projets_bp.route('/projets-academiques/<path:projet_id>/dbpedia-enrich', methods=['GET'])
def enrich_projet_with_dbpedia(projet_id):
    """Enrich projet data with DBpedia information via university city (Linked Data integration)"""
    try:
        projet_id = normalize_projet_id(projet_id)
        
        # First get the projet and its university's city
        query = f"""
        PREFIX ont: <{PREFIX}>
        SELECT ?titreProjet ?ville ?pays ?nomUniversite
        WHERE {{
            <{projet_id}> a ont:ProjetAcademique .
            OPTIONAL {{ <{projet_id}> ont:titreProjet ?titreProjet . }}
            OPTIONAL {{
                <{projet_id}> ont:estOrganisePar ?universite .
                ?universite ont:nomUniversite ?nomUniversite .
                OPTIONAL {{ ?universite ont:ville ?ville . }}
                OPTIONAL {{ ?universite ont:pays ?pays . }}
            }}
        }}
        LIMIT 1
        """
        
        results = sparql_utils.execute_query(query)
        
        if not results:
            return jsonify({"error": "Projet non trouvé"}), 404
        
        projet_data = results[0]
        city_name = projet_data.get("ville")
        titre_projet = projet_data.get("titreProjet")
        
        # Get search term from query parameter or use projet title/city
        search_term = request.args.get('term')
        if not search_term:
            # Prefer titreProjet over ville for better DBpedia matching
            search_term = titre_projet or city_name
        
        enriched_data = {
            "projet": projet_data,
            "search_term": search_term,
            "dbpedia_enrichment": None
        }
        
        # Enrich with DBpedia using the search term (use search_entities for better results)
        if search_term:
            # Use search_entities to get a list of references
            dbpedia_results = dbpedia_service.search_entities(search_term)
            
            # If we got results, return the first one for backward compatibility
            if dbpedia_results.get("results") and len(dbpedia_results["results"]) > 0:
                first_result = dbpedia_results["results"][0]
                enriched_data["dbpedia_enrichment"] = {
                    "title": first_result["title"],
                    "uri": first_result["uri"],
                    "all_results": dbpedia_results["results"][:5]  # Include top 5 for reference
                }
            else:
                # Return error if no results
                enriched_data["dbpedia_enrichment"] = dbpedia_results
        
        return jsonify(enriched_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_specialite
import uuid

specialite_bp = Blueprint('specialite', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

@specialite_bp.route('/specialites', methods=['GET'])
def get_all_specialites():
    """Récupère toutes les spécialités"""
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?specialite ?type ?nomSpecialite ?codeSpecialite ?description 
           ?dureeFormation ?niveauDiplome ?nombreModules ?universite ?nomUniversite
    WHERE {
      ?specialite rdf:type ?type .
      FILTER(?type IN (ont:Specialite, ont:SpecialiteInformatique, ont:SpecialiteDataScience, 
                       ont:SpecialiteIngenierie, ont:SpecialiteSciences, ont:SpecialiteMedecine,
                       ont:SpecialiteEconomie, ont:SpecialiteDroit, ont:SpecialiteLettres))
      
      OPTIONAL { ?specialite ont:nomSpecialite ?nomSpecialite }
      OPTIONAL { ?specialite ont:codeSpecialite ?codeSpecialite }
      OPTIONAL { ?specialite ont:description ?description }
      OPTIONAL { ?specialite ont:dureeFormation ?dureeFormation }
      OPTIONAL { ?specialite ont:niveauDiplome ?niveauDiplome }
      OPTIONAL { ?specialite ont:nombreModules ?nombreModules }
      
      # Informations sur l'université qui offre cette spécialité
      OPTIONAL { 
        ?specialite ont:estOffertePar ?universite .
        ?universite ont:nomUniversite ?nomUniversite 
      }
    }
    ORDER BY ?nomSpecialite
    """
    
    try:
        results = sparql_utils.execute_query(query)
        
        # Debug détaillé
        print("DEBUG - Raw SPARQL results for specialites:")
        for i, specialite in enumerate(results):
            print(f"Spécialité {i}: {specialite}")
        
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching specialites: {str(e)}")
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/<specialite_id>', methods=['GET'])
def get_specialite(specialite_id):
    """Récupère une spécialité spécifique avec tous ses détails"""
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?specialite ?nomSpecialite ?codeSpecialite ?description ?dureeFormation 
           ?niveauDiplome ?nombreModules ?universite ?nomUniversite ?ville ?pays
           ?cours ?intituleCours ?codeCours ?creditsECTS
           ?competence ?nomCompetence ?typeCompetence
           ?etudiant ?nomEtudiant ?prenomEtudiant
    WHERE {{
        <{specialite_id}> a ont:Specialite ;
               ont:nomSpecialite ?nomSpecialite ;
               ont:codeSpecialite ?codeSpecialite .
        
        OPTIONAL {{ <{specialite_id}> ont:description ?description . }}
        OPTIONAL {{ <{specialite_id}> ont:dureeFormation ?dureeFormation . }}
        OPTIONAL {{ <{specialite_id}> ont:niveauDiplome ?niveauDiplome . }}
        OPTIONAL {{ <{specialite_id}> ont:nombreModules ?nombreModules . }}
        
        # Informations sur l'université
        OPTIONAL {{ 
            <{specialite_id}> ont:estOffertePar ?universite .
            ?universite ont:nomUniversite ?nomUniversite .
            OPTIONAL {{ ?universite ont:ville ?ville . }}
            OPTIONAL {{ ?universite ont:pays ?pays . }}
        }}
        
        # Cours associés à cette spécialité
        OPTIONAL {{
            ?cours ont:faitPartieDe <{specialite_id}> .
            ?cours ont:intitule ?intituleCours .
            OPTIONAL {{ ?cours ont:codeCours ?codeCours . }}
            OPTIONAL {{ ?cours ont:creditsECTS ?creditsECTS . }}
        }}
        
        # Compétences développées dans cette spécialité
        OPTIONAL {{
            <{specialite_id}> ont:formePour ?competence .
            ?competence ont:nomCompetence ?nomCompetence .
            OPTIONAL {{ ?competence ont:typeCompetence ?typeCompetence . }}
        }}
        
        # Étudiants inscrits dans cette spécialité
        OPTIONAL {{
            ?etudiant ont:specialiseEn <{specialite_id}> .
            ?etudiant ont:nom ?nomEtudiant .
            ?etudiant ont:prenom ?prenomEtudiant .
        }}
    }}
    """
    
    try:
        results = sparql_utils.execute_query(query)
        
        if not results:
            return jsonify({"error": "Spécialité non trouvée"}), 404
            
        # Structurer les données pour une meilleure organisation
        specialite_data = {
            "info_generale": {},
            "universite": {},
            "cours": [],
            "competences": [],
            "etudiants": []
        }
        
        for result in results:
            # Informations générales
            if not specialite_data["info_generale"]:
                specialite_data["info_generale"] = {
                    "specialite": result.get("specialite"),
                    "nomSpecialite": result.get("nomSpecialite"),
                    "codeSpecialite": result.get("codeSpecialite"),
                    "description": result.get("description"),
                    "dureeFormation": result.get("dureeFormation"),
                    "niveauDiplome": result.get("niveauDiplome"),
                    "nombreModules": result.get("nombreModules")
                }
            
            # Université
            if result.get("universite") and not specialite_data["universite"]:
                specialite_data["universite"] = {
                    "universite": result.get("universite"),
                    "nomUniversite": result.get("nomUniversite"),
                    "ville": result.get("ville"),
                    "pays": result.get("pays")
                }
            
            # Cours
            if result.get("cours") and result.get("cours") not in [c["cours"] for c in specialite_data["cours"]]:
                specialite_data["cours"].append({
                    "cours": result.get("cours"),
                    "intituleCours": result.get("intituleCours"),
                    "codeCours": result.get("codeCours"),
                    "creditsECTS": result.get("creditsECTS")
                })
            
            # Compétences
            if result.get("competence") and result.get("competence") not in [c["competence"] for c in specialite_data["competences"]]:
                specialite_data["competences"].append({
                    "competence": result.get("competence"),
                    "nomCompetence": result.get("nomCompetence"),
                    "typeCompetence": result.get("typeCompetence")
                })
            
            # Étudiants
            if result.get("etudiant") and result.get("etudiant") not in [e["etudiant"] for e in specialite_data["etudiants"]]:
                specialite_data["etudiants"].append({
                    "etudiant": result.get("etudiant"),
                    "nomEtudiant": result.get("nomEtudiant"),
                    "prenomEtudiant": result.get("prenomEtudiant")
                })
        
        return jsonify(specialite_data)
        
    except Exception as e:
        print(f"Error fetching specialite: {str(e)}")
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/search', methods=['POST'])
def search_specialites():
    """Recherche de spécialités par critères"""
    data = request.json
    nom = data.get('nom', '')
    domaine = data.get('domaine', '')
    universite = data.get('universite', '')
    niveau = data.get('niveau', '')
    
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?specialite ?nomSpecialite ?codeSpecialite ?description ?dureeFormation 
           ?niveauDiplome ?universite ?nomUniversite
    WHERE {
        ?specialite a ont:Specialite ;
               ont:nomSpecialite ?nomSpecialite .
        
        OPTIONAL { ?specialite ont:codeSpecialite ?codeSpecialite . }
        OPTIONAL { ?specialite ont:description ?description . }
        OPTIONAL { ?specialite ont:dureeFormation ?dureeFormation . }
        OPTIONAL { ?specialite ont:niveauDiplome ?niveauDiplome . }
        OPTIONAL { 
            ?specialite ont:estOffertePar ?universite .
            ?universite ont:nomUniversite ?nomUniversite .
        }
    """
    
    filters = []
    if nom:
        filters.append(f'REGEX(?nomSpecialite, "{nom}", "i")')
    if domaine:
        # Recherche dans la description pour le domaine
        filters.append(f'REGEX(?description, "{domaine}", "i")')
    if universite:
        filters.append(f'REGEX(?nomUniversite, "{universite}", "i")')
    if niveau:
        filters.append(f'REGEX(?niveauDiplome, "{niveau}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?nomSpecialite"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/<specialite_id>/cours', methods=['GET'])
def get_specialite_cours(specialite_id):
    """Récupère tous les cours d'une spécialité"""
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre ?volumeHoraire 
           ?langueCours ?enseignant ?nomEnseignant ?prenomEnseignant
    WHERE {{
        ?cours ont:faitPartieDe <{specialite_id}> ;
               ont:intitule ?intitule .
        
        OPTIONAL {{ ?cours ont:codeCours ?codeCours . }}
        OPTIONAL {{ ?cours ont:creditsECTS ?creditsECTS . }}
        OPTIONAL {{ ?cours ont:semestre ?semestre . }}
        OPTIONAL {{ ?cours ont:volumeHoraire ?volumeHoraire . }}
        OPTIONAL {{ ?cours ont:langueCours ?langueCours . }}
        
        # Enseignants du cours
        OPTIONAL {{
            ?cours ont:enseignePar ?enseignant .
            ?enseignant ont:nom ?nomEnseignant .
            ?enseignant ont:prenom ?prenomEnseignant .
        }}
    }}
    ORDER BY ?semestre ?codeCours
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/<specialite_id>/etudiants', methods=['GET'])
def get_specialite_etudiants(specialite_id):
    """Récupère tous les étudiants d'une spécialité"""
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?etudiant ?nom ?prenom ?email ?telephone ?dateNaissance 
           ?numeroMatricule ?niveauEtude ?moyenneGenerale ?universite ?nomUniversite
    WHERE {{
        ?etudiant ont:specialiseEn <{specialite_id}> ;
               ont:nom ?nom ;
               ont:prenom ?prenom .
        
        OPTIONAL {{ ?etudiant ont:email ?email . }}
        OPTIONAL {{ ?etudiant ont:telephone ?telephone . }}
        OPTIONAL {{ ?etudiant ont:dateNaissance ?dateNaissance . }}
        OPTIONAL {{ ?etudiant ont:numeroMatricule ?numeroMatricule . }}
        OPTIONAL {{ ?etudiant ont:niveauEtude ?niveauEtude . }}
        OPTIONAL {{ ?etudiant ont:moyenneGenerale ?moyenneGenerale . }}
        OPTIONAL {{ 
            ?etudiant ont:appartientA ?universite .
            ?universite ont:nomUniversite ?nomUniversite .
        }}
    }}
    ORDER BY ?nom ?prenom
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/<specialite_id>/competences', methods=['GET'])
def get_specialite_competences(specialite_id):
    """Récupère toutes les compétences développées dans une spécialité"""
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?competence ?nomCompetence ?typeCompetence ?niveauCompetence 
           ?descriptionCompetence ?motsCles
    WHERE {{
        <{specialite_id}> ont:formePour ?competence .
        ?competence ont:nomCompetence ?nomCompetence .
        
        OPTIONAL {{ ?competence ont:typeCompetence ?typeCompetence . }}
        OPTIONAL {{ ?competence ont:niveauCompetence ?niveauCompetence . }}
        OPTIONAL {{ ?competence ont:descriptionCompetence ?descriptionCompetence . }}
        OPTIONAL {{ ?competence ont:motsCles ?motsCles . }}
    }}
    ORDER BY ?typeCompetence ?nomCompetence
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/stats', methods=['GET'])
def get_specialites_stats():
    """Récupère les statistiques des spécialités"""
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    
    SELECT 
        (COUNT(DISTINCT ?specialite) as ?total_specialites)
        (COUNT(DISTINCT ?etudiant) as ?total_etudiants)
        (COUNT(DISTINCT ?cours) as ?total_cours)
        (COUNT(DISTINCT ?competence) as ?total_competences)
    WHERE {
        ?specialite a ont:Specialite .
        OPTIONAL { ?etudiant ont:specialiseEn ?specialite . }
        OPTIONAL { ?cours ont:faitPartieDe ?specialite . }
        OPTIONAL { ?specialite ont:formePour ?competence . }
    }
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results[0] if results else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/par-universite', methods=['GET'])
def get_specialites_par_universite():
    """Récupère les spécialités groupées par université"""
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?universite ?nomUniversite ?specialite ?nomSpecialite ?codeSpecialite 
           ?niveauDiplome ?dureeFormation
    WHERE {
        ?specialite a ont:Specialite ;
                   ont:nomSpecialite ?nomSpecialite ;
                   ont:estOffertePar ?universite .
        ?universite ont:nomUniversite ?nomUniversite .
        
        OPTIONAL { ?specialite ont:codeSpecialite ?codeSpecialite . }
        OPTIONAL { ?specialite ont:niveauDiplome ?niveauDiplome . }
        OPTIONAL { ?specialite ont:dureeFormation ?dureeFormation . }
    }
    ORDER BY ?nomUniversite ?nomSpecialite
    """
    
    try:
        results = sparql_utils.execute_query(query)
        
        # Grouper par université
        grouped_data = {}
        for result in results:
            universite = result.get("nomUniversite")
            if universite not in grouped_data:
                grouped_data[universite] = {
                    "universite": result.get("universite"),
                    "nomUniversite": universite,
                    "specialites": []
                }
            
            grouped_data[universite]["specialites"].append({
                "specialite": result.get("specialite"),
                "nomSpecialite": result.get("nomSpecialite"),
                "codeSpecialite": result.get("codeSpecialite"),
                "niveauDiplome": result.get("niveauDiplome"),
                "dureeFormation": result.get("dureeFormation")
            })
        
        return jsonify(list(grouped_data.values()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_specialite_uri(nom: str) -> str:
    """Generate a unique URI for a specialite"""
    safe_nom = nom.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}Specialite_{safe_nom}_{uuid.uuid4().hex[:8]}"

@specialite_bp.route('/specialites', methods=['POST'])
def create_specialite():
    """Create a new specialite"""
    data = request.json
    
    errors = validate_specialite(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    specialite_uri = generate_specialite_uri(data.get('nomSpecialite'))
    
    insert_parts = [
        f"<{specialite_uri}> a ont:Specialite",
        f"; ont:nomSpecialite \"{data.get('nomSpecialite')}\""
    ]
    
    if data.get('codeSpecialite'):
        insert_parts.append(f"; ont:codeSpecialite \"{data.get('codeSpecialite')}\"")
    if data.get('description'):
        insert_parts.append(f"; ont:description \"{data.get('description')}\"")
    if data.get('dureeFormation'):
        insert_parts.append(f"; ont:dureeFormation \"{data.get('dureeFormation')}\"")
    if data.get('niveauDiplome'):
        insert_parts.append(f"; ont:niveauDiplome \"{data.get('niveauDiplome')}\"")
    if data.get('nombreModules'):
        insert_parts.append(f"; ont:nombreModules {int(data.get('nombreModules'))}")
    if data.get('universite'):
        insert_parts.append(f"; ont:estOffertePar <{data.get('universite')}>")
    
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
        return jsonify({"message": "Spécialité créée avec succès", "uri": specialite_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/<specialite_id>', methods=['PUT'])
def update_specialite(specialite_id):
    """Update a specialite"""
    data = request.json
    
    errors = validate_specialite(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{specialite_id}> ?p ?o .
    }}
    WHERE {{
        <{specialite_id}> ?p ?o .
        FILTER(?p != ont:formePour && ?p != ont:faitPartieDe)
    }}
    """
    
    insert_parts = [f"<{specialite_id}> a ont:Specialite"]
    
    if data.get('nomSpecialite'):
        insert_parts.append(f"; ont:nomSpecialite \"{data.get('nomSpecialite')}\"")
    if data.get('codeSpecialite'):
        insert_parts.append(f"; ont:codeSpecialite \"{data.get('codeSpecialite')}\"")
    if data.get('description'):
        insert_parts.append(f"; ont:description \"{data.get('description')}\"")
    if data.get('dureeFormation'):
        insert_parts.append(f"; ont:dureeFormation \"{data.get('dureeFormation')}\"")
    if data.get('niveauDiplome'):
        insert_parts.append(f"; ont:niveauDiplome \"{data.get('niveauDiplome')}\"")
    if data.get('nombreModules'):
        insert_parts.append(f"; ont:nombreModules {int(data.get('nombreModules'))}")
    if data.get('universite'):
        insert_parts.append(f"; ont:estOffertePar <{data.get('universite')}>")
    
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
        return jsonify({"message": "Spécialité mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@specialite_bp.route('/specialites/<specialite_id>', methods=['DELETE'])
def delete_specialite(specialite_id):
    """Delete a specialite"""
    # Construct full URI if not already a full URI
    if specialite_id.startswith('http://') or specialite_id.startswith('https://'):
        specialite_uri = specialite_id
    else:
        # If it doesn't start with PREFIX, add it
        if specialite_id.startswith(PREFIX):
            specialite_uri = specialite_id
        else:
            specialite_uri = f"{PREFIX}{specialite_id}"
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{specialite_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Spécialité supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
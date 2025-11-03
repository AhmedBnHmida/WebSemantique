from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_personne
import uuid

personne_bp = Blueprint('personne', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

@personne_bp.route('/personnes', methods=['GET'])
def get_all_personnes():
    """Récupère toutes les personnes"""
    query = """
    

PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?personne ?type ?nom ?prenom ?email ?telephone ?role
    WHERE {
      ?personne rdf:type ?type .
      FILTER(?type IN (ont:Personne, ont:Etudiant, ont:Enseignant, ont:Professeur, 
                       ont:Assistant, ont:Encadrant, ont:EtudiantLicence, 
                       ont:EtudiantMaster, ont:EtudiantDoctorat))
      OPTIONAL { ?personne ont:nom ?nom }
      OPTIONAL { ?personne ont:prenom ?prenom }
      OPTIONAL { ?personne ont:email ?email }
      OPTIONAL { ?personne ont:telephone ?telephone }
      OPTIONAL { ?personne ont:role ?role }
    }
    ORDER BY ?type ?nom



    """
    results = sparql_utils.execute_query(query)
    
    # Debug détaillé
    print("DEBUG - Raw SPARQL results:")
    for i, personne in enumerate(results):
        print(f"Personne {i}: {personne}")
    
    # Renvoyer directement les résultats
    return jsonify(results)





@personne_bp.route('/personnes/<personne_id>', methods=['GET'])
def get_personne(personne_id):
    """Récupère une personne spécifique avec tous ses détails"""
    query = f"""
    PREFIX edu: <http://www.education-intelligente.org/ontologie#>
    SELECT ?personne ?nom ?prenom ?email ?telephone ?dateNaissance ?role ?universite ?nomUniversite
           ?specialite ?nomSpecialite ?cours ?intituleCours
    WHERE {{
        <{personne_id}> a edu:Personne ;
               edu:nom ?nom ;
               edu:prenom ?prenom .
        
        OPTIONAL {{ <{personne_id}> edu:email ?email . }}
        OPTIONAL {{ <{personne_id}> edu:telephone ?telephone . }}
        OPTIONAL {{ <{personne_id}> edu:dateNaissance ?dateNaissance . }}
        OPTIONAL {{ <{personne_id}> edu:role ?role . }}
        
        # Informations sur l'université
        OPTIONAL {{ 
            <{personne_id}> edu:appartientA ?universite .
            ?universite edu:nomUniversite ?nomUniversite .
        }}
        
        # Informations sur la spécialité (pour les étudiants)
        OPTIONAL {{
            <{personne_id}> edu:specialiseEn ?specialite .
            ?specialite edu:nomSpecialite ?nomSpecialite .
        }}
        
        # Informations sur les cours suivis/enseignés
        OPTIONAL {{
            <{personne_id}> edu:suitCours ?cours .
            ?cours edu:intitule ?intituleCours .
        }}
        OPTIONAL {{
            <{personne_id}> edu:enseigne ?cours .
            ?cours edu:intitule ?intituleCours .
        }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@personne_bp.route('/personnes/search', methods=['POST'])
def search_personnes():
    """Recherche de personnes par critères"""
    data = request.json
    nom = data.get('nom', '')
    prenom = data.get('prenom', '')
    role = data.get('role', '')
    universite = data.get('universite', '')
    
    query = """
    PREFIX edu: <http://www.education-intelligente.org/ontologie#>
    SELECT ?personne ?nom ?prenom ?email ?telephone ?dateNaissance ?role ?universite ?nomUniversite
    WHERE {
        ?personne a edu:Personne ;
               edu:nom ?nom ;
               edu:prenom ?prenom .
        
        OPTIONAL { ?personne edu:email ?email . }
        OPTIONAL { ?personne edu:telephone ?telephone . }
        OPTIONAL { ?personne edu:dateNaissance ?dateNaissance . }
        OPTIONAL { ?personne edu:role ?role . }
        OPTIONAL { 
            ?personne edu:appartientA ?universite .
            ?universite edu:nomUniversite ?nomUniversite .
        }
    """
    
    filters = []
    if nom:
        filters.append(f'REGEX(?nom, "{nom}", "i")')
    if prenom:
        filters.append(f'REGEX(?prenom, "{prenom}", "i")')
    if role:
        filters.append(f'REGEX(?role, "{role}", "i")')
    if universite:
        filters.append(f'REGEX(?nomUniversite, "{universite}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?nom ?prenom"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@personne_bp.route('/personnes/etudiants', methods=['GET'])
def get_etudiants():
    """Récupère tous les étudiants"""
    query = """
    PREFIX edu: <http://www.education-intelligente.org/ontologie#>
    SELECT ?etudiant ?nom ?prenom ?email ?telephone ?dateNaissance ?numeroMatricule ?niveauEtude ?moyenneGenerale ?universite ?nomUniversite
    WHERE {
        ?etudiant a edu:Etudiant ;
               edu:nom ?nom ;
               edu:prenom ?prenom .
        
        OPTIONAL { ?etudiant edu:email ?email . }
        OPTIONAL { ?etudiant edu:telephone ?telephone . }
        OPTIONAL { ?etudiant edu:dateNaissance ?dateNaissance . }
        OPTIONAL { ?etudiant edu:numeroMatricule ?numeroMatricule . }
        OPTIONAL { ?etudiant edu:niveauEtude ?niveauEtude . }
        OPTIONAL { ?etudiant edu:moyenneGenerale ?moyenneGenerale . }
        OPTIONAL { 
            ?etudiant edu:appartientA ?universite .
            ?universite edu:nomUniversite ?nomUniversite .
        }
    }
    ORDER BY ?nom ?prenom
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@personne_bp.route('/personnes/enseignants', methods=['GET'])
def get_enseignants():
    """Récupère tous les enseignants"""
    query = """
    PREFIX edu: <http://www.education-intelligente.org/ontologie#>
    SELECT ?enseignant ?nom ?prenom ?email ?telephone ?dateNaissance ?grade ?anciennete ?universite ?nomUniversite
    WHERE {
        ?enseignant a edu:Enseignant ;
               edu:nom ?nom ;
               edu:prenom ?prenom .
        
        OPTIONAL { ?enseignant edu:email ?email . }
        OPTIONAL { ?enseignant edu:telephone ?telephone . }
        OPTIONAL { ?enseignant edu:dateNaissance ?dateNaissance . }
        OPTIONAL { ?enseignant edu:grade ?grade . }
        OPTIONAL { ?enseignant edu:anciennete ?anciennete . }
        OPTIONAL { 
            ?enseignant edu:appartientA ?universite .
            ?universite edu:nomUniversite ?nomUniversite .
        }
    }
    ORDER BY ?nom ?prenom
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@personne_bp.route('/personnes/<personne_id>/cours', methods=['GET'])
def get_personne_cours(personne_id):
    """Récupère les cours associés à une personne (suivis ou enseignés)"""
    query = f"""
    PREFIX edu: <http://www.education-intelligente.org/ontologie#>
    SELECT ?cours ?intitule ?codeCours ?creditsECTS ?semestre ?volumeHoraire
    WHERE {{
        {{
            <{personne_id}> edu:suitCours ?cours .
        }} UNION {{
            <{personne_id}> edu:enseigne ?cours .
        }}
        
        ?cours edu:intitule ?intitule .
        OPTIONAL {{ ?cours edu:codeCours ?codeCours . }}
        OPTIONAL {{ ?cours edu:creditsECTS ?creditsECTS . }}
        OPTIONAL {{ ?cours edu:semestre ?semestre . }}
        OPTIONAL {{ ?cours edu:volumeHoraire ?volumeHoraire . }}
    }}
    ORDER BY ?semestre
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

def generate_personne_uri(nom: str, prenom: str) -> str:
    """Generate a unique URI for a personne"""
    safe_nom = nom.upper().replace(' ', '_')[:30]
    safe_prenom = prenom.upper().replace(' ', '_')[:30]
    return f"{PREFIX}Personne_{safe_nom}_{safe_prenom}_{uuid.uuid4().hex[:8]}"

@personne_bp.route('/personnes', methods=['POST'])
def create_personne():
    """Create a new person"""
    data = request.json
    
    errors = validate_personne(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    personne_uri = generate_personne_uri(data.get('nom'), data.get('prenom'))
    role = data.get('role', 'Personne')
    
    # Determine the type based on role
    type_mapping = {
        'Etudiant': 'ont:Etudiant',
        'Enseignant': 'ont:Enseignant',
        'Professeur': 'ont:Professeur',
        'Assistant': 'ont:Assistant',
        'Encadrant': 'ont:Encadrant'
    }
    person_type = type_mapping.get(role, 'ont:Personne')
    
    insert_parts = [
        f"<{personne_uri}> a {person_type}",
        f"; ont:nom \"{data.get('nom')}\"",
        f"; ont:prenom \"{data.get('prenom')}\""
    ]
    
    if data.get('email'):
        insert_parts.append(f"; ont:email \"{data.get('email')}\"")
    if data.get('telephone'):
        insert_parts.append(f"; ont:telephone \"{data.get('telephone')}\"")
    if data.get('dateNaissance'):
        insert_parts.append(f"; ont:dateNaissance \"{data.get('dateNaissance')}\"^^xsd:date")
    if data.get('role'):
        insert_parts.append(f"; ont:role \"{data.get('role')}\"")
    if data.get('universite'):
        insert_parts.append(f"; ont:appartientA <{data.get('universite')}>")
    if data.get('specialite'):
        insert_parts.append(f"; ont:specialiseEn <{data.get('specialite')}>")
    if data.get('numeroMatricule'):
        insert_parts.append(f"; ont:numeroMatricule \"{data.get('numeroMatricule')}\"")
    if data.get('niveauEtude'):
        insert_parts.append(f"; ont:niveauEtude \"{data.get('niveauEtude')}\"")
    if data.get('moyenneGenerale'):
        insert_parts.append(f"; ont:moyenneGenerale {float(data.get('moyenneGenerale'))}")
    if data.get('grade'):
        insert_parts.append(f"; ont:grade \"{data.get('grade')}\"")
    if data.get('anciennete'):
        insert_parts.append(f"; ont:anciennete \"{data.get('anciennete')}\"")
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Personne créée avec succès", "uri": personne_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@personne_bp.route('/personnes/<personne_id>', methods=['PUT'])
def update_personne(personne_id):
    """Update a person"""
    data = request.json
    
    errors = validate_personne(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{personne_id}> ?p ?o .
    }}
    WHERE {{
        <{personne_id}> ?p ?o .
        FILTER(?p != ont:suitCours && ?p != ont:enseigne)
    }}
    """
    
    insert_parts = [f"<{personne_id}> a ont:Personne"]
    
    if data.get('nom'):
        insert_parts.append(f"; ont:nom \"{data.get('nom')}\"")
    if data.get('prenom'):
        insert_parts.append(f"; ont:prenom \"{data.get('prenom')}\"")
    if data.get('email'):
        insert_parts.append(f"; ont:email \"{data.get('email')}\"")
    if data.get('telephone'):
        insert_parts.append(f"; ont:telephone \"{data.get('telephone')}\"")
    if data.get('dateNaissance'):
        insert_parts.append(f"; ont:dateNaissance \"{data.get('dateNaissance')}\"^^xsd:date")
    if data.get('role'):
        insert_parts.append(f"; ont:role \"{data.get('role')}\"")
    if data.get('universite'):
        insert_parts.append(f"; ont:appartientA <{data.get('universite')}>")
    if data.get('specialite'):
        insert_parts.append(f"; ont:specialiseEn <{data.get('specialite')}>")
    if data.get('numeroMatricule'):
        insert_parts.append(f"; ont:numeroMatricule \"{data.get('numeroMatricule')}\"")
    if data.get('niveauEtude'):
        insert_parts.append(f"; ont:niveauEtude \"{data.get('niveauEtude')}\"")
    if data.get('moyenneGenerale'):
        insert_parts.append(f"; ont:moyenneGenerale {float(data.get('moyenneGenerale'))}")
    if data.get('grade'):
        insert_parts.append(f"; ont:grade \"{data.get('grade')}\"")
    if data.get('anciennete'):
        insert_parts.append(f"; ont:anciennete \"{data.get('anciennete')}\"")
    
    insert_query = f"""
    PREFIX ont: <{PREFIX}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {' '.join(insert_parts)} .
    }}
    """
    
    try:
        sparql_utils.execute_update(delete_query)
        result = sparql_utils.execute_update(insert_query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Personne mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@personne_bp.route('/personnes/<personne_id>', methods=['DELETE'])
def delete_personne(personne_id):
    """Delete a person"""
    # Construct full URI if not already a full URI
    if personne_id.startswith('http://') or personne_id.startswith('https://'):
        personne_uri = personne_id
    else:
        if personne_id.startswith(PREFIX):
            personne_uri = personne_id
        else:
            personne_uri = f"{PREFIX}{personne_id}"
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{personne_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Personne supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.validators import validate_universite
from modules.dbpedia_service import dbpedia_service
import uuid

universite_bp = Blueprint('universite', __name__)
PREFIX = "http://www.education-intelligente.org/ontologie#"

@universite_bp.route('/universites', methods=['GET'])
def get_all_universites():
    """Récupère toutes les universités"""
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?universite ?type ?nomUniversite ?anneeFondation ?ville ?pays 
           ?nombreEtudiants ?rangNational ?siteWeb ?typeUniversite
    WHERE {
      ?universite rdf:type ?type .
      FILTER(?type IN (ont:Universite, ont:UniversitePublique, ont:UniversitePrivee))
      
      OPTIONAL { ?universite ont:nomUniversite ?nomUniversite }
      OPTIONAL { ?universite ont:anneeFondation ?anneeFondation }
      OPTIONAL { ?universite ont:ville ?ville }
      OPTIONAL { ?universite ont:pays ?pays }
      OPTIONAL { ?universite ont:nombreEtudiants ?nombreEtudiants }
      OPTIONAL { ?universite ont:rangNational ?rangNational }
      OPTIONAL { ?universite ont:siteWeb ?siteWeb }
      
      # Déterminer le type d'université
      BIND(
        IF(?type = ont:UniversitePublique, "Publique",
          IF(?type = ont:UniversitePrivee, "Privée", "Générale")
        ) AS ?typeUniversite
      )
    }
    ORDER BY ?nomUniversite
    """
    
    try:
        results = sparql_utils.execute_query(query)
        
        # Debug détaillé
        print("DEBUG - Raw SPARQL results for universites:")
        for i, universite in enumerate(results):
            print(f"Université {i}: {universite}")
        
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching universites: {str(e)}")
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>', methods=['GET'])
def get_universite(universite_id):
    """Récupère une université spécifique avec tous ses détails"""
    universite_id = normalize_universite_id(universite_id)
    
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?universite ?nomUniversite ?anneeFondation ?ville ?pays 
           ?nombreEtudiants ?rangNational ?siteWeb ?typeUniversite
           ?specialite ?nomSpecialite ?codeSpecialite ?niveauDiplome
           ?enseignant ?nomEnseignant ?prenomEnseignant ?grade ?email
           ?etudiant ?nomEtudiant ?prenomEtudiant ?niveauEtude ?moyenneGenerale
           ?technologie ?nomTechnologie ?typeTechnologie
           ?projet ?titreProjet ?typeProjet
    WHERE {{
        <{universite_id}> rdf:type ?type .
        FILTER(?type IN (ont:Universite, ont:UniversitePublique, ont:UniversitePrivee))
        <{universite_id}> ont:nomUniversite ?nomUniversite .
        
        OPTIONAL {{ <{universite_id}> ont:anneeFondation ?anneeFondation . }}
        OPTIONAL {{ <{universite_id}> ont:ville ?ville . }}
        OPTIONAL {{ <{universite_id}> ont:pays ?pays . }}
        OPTIONAL {{ <{universite_id}> ont:nombreEtudiants ?nombreEtudiants . }}
        OPTIONAL {{ <{universite_id}> ont:rangNational ?rangNational . }}
        OPTIONAL {{ <{universite_id}> ont:siteWeb ?siteWeb . }}
        
        # Déterminer le type d'université
        OPTIONAL {{
            <{universite_id}> a ?type .
            FILTER(?type IN (ont:UniversitePublique, ont:UniversitePrivee))
            BIND(
              IF(?type = ont:UniversitePublique, "Publique",
                IF(?type = ont:UniversitePrivee, "Privée", "Générale")
              ) AS ?typeUniversite
            )
        }}
        
        # Spécialités offertes par cette université
        OPTIONAL {{
            <{universite_id}> ont:offre ?specialite .
            ?specialite ont:nomSpecialite ?nomSpecialite .
            OPTIONAL {{ ?specialite ont:codeSpecialite ?codeSpecialite . }}
            OPTIONAL {{ ?specialite ont:niveauDiplome ?niveauDiplome . }}
        }}
        
        # Enseignants employés par cette université
        OPTIONAL {{
            <{universite_id}> ont:emploie ?enseignant .
            ?enseignant ont:nom ?nomEnseignant .
            ?enseignant ont:prenom ?prenomEnseignant .
            OPTIONAL {{ ?enseignant ont:grade ?grade . }}
            OPTIONAL {{ ?enseignant ont:email ?email . }}
        }}
        
        # Étudiants inscrits dans cette université
        OPTIONAL {{
            ?etudiant ont:appartientA <{universite_id}> .
            ?etudiant ont:nom ?nomEtudiant .
            ?etudiant ont:prenom ?prenomEtudiant .
            OPTIONAL {{ ?etudiant ont:niveauEtude ?niveauEtude . }}
            OPTIONAL {{ ?etudiant ont:moyenneGenerale ?moyenneGenerale . }}
        }}
        
        # Technologies adoptées par cette université
        OPTIONAL {{
            <{universite_id}> ont:adopteTechnologie ?technologie .
            ?technologie ont:nomTechnologie ?nomTechnologie .
            OPTIONAL {{ ?technologie ont:typeTechnologie ?typeTechnologie . }}
        }}
        
        # Projets organisés par cette université
        OPTIONAL {{
            ?projet ont:estOrganisePar <{universite_id}> .
            ?projet ont:titreProjet ?titreProjet .
            OPTIONAL {{ ?projet ont:typeProjet ?typeProjet . }}
        }}
    }}
    """
    
    try:
        results = sparql_utils.execute_query(query)
        
        if not results:
            return jsonify({"error": "Université non trouvée"}), 404
            
        # Structurer les données pour une meilleure organisation
        universite_data = {
            "info_generale": {},
            "specialites": [],
            "enseignants": [],
            "etudiants": [],
            "technologies": [],
            "projets": []
        }
        
        for result in results:
            # Informations générales
            if not universite_data["info_generale"]:
                universite_data["info_generale"] = {
                    "universite": result.get("universite"),
                    "nomUniversite": result.get("nomUniversite"),
                    "anneeFondation": result.get("anneeFondation"),
                    "ville": result.get("ville"),
                    "pays": result.get("pays"),
                    "nombreEtudiants": result.get("nombreEtudiants"),
                    "rangNational": result.get("rangNational"),
                    "siteWeb": result.get("siteWeb"),
                    "typeUniversite": result.get("typeUniversite")
                }
            
            # Spécialités
            if result.get("specialite") and result.get("specialite") not in [s["specialite"] for s in universite_data["specialites"]]:
                universite_data["specialites"].append({
                    "specialite": result.get("specialite"),
                    "nomSpecialite": result.get("nomSpecialite"),
                    "codeSpecialite": result.get("codeSpecialite"),
                    "niveauDiplome": result.get("niveauDiplome")
                })
            
            # Enseignants
            if result.get("enseignant") and result.get("enseignant") not in [e["enseignant"] for e in universite_data["enseignants"]]:
                universite_data["enseignants"].append({
                    "enseignant": result.get("enseignant"),
                    "nomEnseignant": result.get("nomEnseignant"),
                    "prenomEnseignant": result.get("prenomEnseignant"),
                    "grade": result.get("grade"),
                    "email": result.get("email")
                })
            
            # Étudiants
            if result.get("etudiant") and result.get("etudiant") not in [e["etudiant"] for e in universite_data["etudiants"]]:
                universite_data["etudiants"].append({
                    "etudiant": result.get("etudiant"),
                    "nomEtudiant": result.get("nomEtudiant"),
                    "prenomEtudiant": result.get("prenomEtudiant"),
                    "niveauEtude": result.get("niveauEtude"),
                    "moyenneGenerale": result.get("moyenneGenerale")
                })
            
            # Technologies
            if result.get("technologie") and result.get("technologie") not in [t["technologie"] for t in universite_data["technologies"]]:
                universite_data["technologies"].append({
                    "technologie": result.get("technologie"),
                    "nomTechnologie": result.get("nomTechnologie"),
                    "typeTechnologie": result.get("typeTechnologie")
                })
            
            # Projets
            if result.get("projet") and result.get("projet") not in [p["projet"] for p in universite_data["projets"]]:
                universite_data["projets"].append({
                    "projet": result.get("projet"),
                    "titreProjet": result.get("titreProjet"),
                    "typeProjet": result.get("typeProjet")
                })
        
        return jsonify(universite_data)
        
    except Exception as e:
        print(f"Error fetching universite: {str(e)}")
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/search', methods=['POST'])
def search_universites():
    """Recherche d'universités par critères"""
    data = request.json
    nom = data.get('nom', '')
    ville = data.get('ville', '')
    pays = data.get('pays', '')
    type_universite = data.get('type', '')
    
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?universite ?nomUniversite ?ville ?pays ?typeUniversite 
           ?nombreEtudiants ?rangNational ?anneeFondation
    WHERE {
        ?universite a ont:Universite ;
               ont:nomUniversite ?nomUniversite .
        
        OPTIONAL { ?universite ont:ville ?ville . }
        OPTIONAL { ?universite ont:pays ?pays . }
        OPTIONAL { ?universite ont:nombreEtudiants ?nombreEtudiants . }
        OPTIONAL { ?universite ont:rangNational ?rangNational . }
        OPTIONAL { ?universite ont:anneeFondation ?anneeFondation . }
        
        # Déterminer le type d'université
        OPTIONAL {
            ?universite a ?type .
            FILTER(?type IN (ont:UniversitePublique, ont:UniversitePrivee))
            BIND(
              IF(?type = ont:UniversitePublique, "Publique",
                IF(?type = ont:UniversitePrivee, "Privée", "Générale")
              ) AS ?typeUniversite
            )
        }
    """
    
    filters = []
    if nom:
        filters.append(f'REGEX(?nomUniversite, "{nom}", "i")')
    if ville:
        filters.append(f'REGEX(?ville, "{ville}", "i")')
    if pays:
        filters.append(f'REGEX(?pays, "{pays}", "i")')
    if type_universite:
        filters.append(f'REGEX(?typeUniversite, "{type_universite}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?nomUniversite"
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def normalize_universite_id(universite_id):
    """Normalize university ID to full URI format"""
    from urllib.parse import unquote
    universite_id = unquote(universite_id)
    
    # If it's not a full URI, try to construct it
    if not universite_id.startswith('http://') and not universite_id.startswith('https://'):
        # It might be just the fragment (e.g., "Universite_Marakech")
        # Try with the full prefix
        if not universite_id.startswith(PREFIX):
            universite_id = f"{PREFIX}{universite_id}"
    
    # Debug logging
    print(f"DEBUG: Normalized universite_id: {universite_id}")
    
    return universite_id

@universite_bp.route('/universites/<path:universite_id>/specialites', methods=['GET'])
def get_universite_specialites(universite_id):
    """Récupère toutes les spécialités d'une université"""
    universite_id = normalize_universite_id(universite_id)
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?specialite ?nomSpecialite ?codeSpecialite ?description 
           ?dureeFormation ?niveauDiplome ?nombreModules
    WHERE {{
        <{universite_id}> ont:offre ?specialite .
        ?specialite ont:nomSpecialite ?nomSpecialite .
        
        OPTIONAL {{ ?specialite ont:codeSpecialite ?codeSpecialite . }}
        OPTIONAL {{ ?specialite ont:description ?description . }}
        OPTIONAL {{ ?specialite ont:dureeFormation ?dureeFormation . }}
        OPTIONAL {{ ?specialite ont:niveauDiplome ?niveauDiplome . }}
        OPTIONAL {{ ?specialite ont:nombreModules ?nombreModules . }}
    }}
    ORDER BY ?nomSpecialite
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>/enseignants', methods=['GET'])
def get_universite_enseignants(universite_id):
    """Récupère tous les enseignants d'une université"""
    universite_id = normalize_universite_id(universite_id)
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?enseignant ?nom ?prenom ?email ?telephone ?dateNaissance 
           ?grade ?anciennete ?cours ?intituleCours
    WHERE {{
        <{universite_id}> ont:emploie ?enseignant .
        ?enseignant ont:nom ?nom ;
                   ont:prenom ?prenom .
        
        OPTIONAL {{ ?enseignant ont:email ?email . }}
        OPTIONAL {{ ?enseignant ont:telephone ?telephone . }}
        OPTIONAL {{ ?enseignant ont:dateNaissance ?dateNaissance . }}
        OPTIONAL {{ ?enseignant ont:grade ?grade . }}
        OPTIONAL {{ ?enseignant ont:anciennete ?anciennete . }}
        
        # Cours enseignés
        OPTIONAL {{
            ?enseignant ont:enseigne ?cours .
            ?cours ont:intitule ?intituleCours .
        }}
    }}
    ORDER BY ?nom ?prenom
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>/etudiants', methods=['GET'])
def get_universite_etudiants(universite_id):
    """Récupère tous les étudiants d'une université"""
    universite_id = normalize_universite_id(universite_id)
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?etudiant ?nom ?prenom ?email ?telephone ?dateNaissance 
           ?numeroMatricule ?niveauEtude ?moyenneGenerale ?specialite ?nomSpecialite
    WHERE {{
        ?etudiant ont:appartientA <{universite_id}> ;
               ont:nom ?nom ;
               ont:prenom ?prenom .
        
        OPTIONAL {{ ?etudiant ont:email ?email . }}
        OPTIONAL {{ ?etudiant ont:telephone ?telephone . }}
        OPTIONAL {{ ?etudiant ont:dateNaissance ?dateNaissance . }}
        OPTIONAL {{ ?etudiant ont:numeroMatricule ?numeroMatricule . }}
        OPTIONAL {{ ?etudiant ont:niveauEtude ?niveauEtude . }}
        OPTIONAL {{ ?etudiant ont:moyenneGenerale ?moyenneGenerale . }}
        
        # Spécialité de l'étudiant
        OPTIONAL {{
            ?etudiant ont:specialiseEn ?specialite .
            ?specialite ont:nomSpecialite ?nomSpecialite .
        }}
    }}
    ORDER BY ?nom ?prenom
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>/technologies', methods=['GET'])
def get_universite_technologies(universite_id):
    """Récupère toutes les technologies adoptées par une université"""
    universite_id = normalize_universite_id(universite_id)
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?technologie ?nomTechnologie ?typeTechnologie ?version 
           ?editeur ?anneeImpl ?nbUtilisateurs
    WHERE {{
        <{universite_id}> ont:adopteTechnologie ?technologie .
        ?technologie ont:nomTechnologie ?nomTechnologie .
        
        OPTIONAL {{ ?technologie ont:typeTechnologie ?typeTechnologie . }}
        OPTIONAL {{ ?technologie ont:version ?version . }}
        OPTIONAL {{ ?technologie ont:editeur ?editeur . }}
        OPTIONAL {{ ?technologie ont:anneeImpl ?anneeImpl . }}
        OPTIONAL {{ ?technologie ont:nbUtilisateurs ?nbUtilisateurs . }}
    }}
    ORDER BY ?nomTechnologie
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>/projets', methods=['GET'])
def get_universite_projets(universite_id):
    """Récupère tous les projets organisés par une université"""
    universite_id = normalize_universite_id(universite_id)
    query = f"""
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?projet ?titreProjet ?typeProjet ?domaineProjet ?anneeRealisation 
           ?noteProjet ?etudiant ?nomEtudiant ?encadrant ?nomEncadrant
    WHERE {{
        ?projet ont:estOrganisePar <{universite_id}> ;
               ont:titreProjet ?titreProjet .
        
        OPTIONAL {{ ?projet ont:typeProjet ?typeProjet . }}
        OPTIONAL {{ ?projet ont:domaineProjet ?domaineProjet . }}
        OPTIONAL {{ ?projet ont:anneeRealisation ?anneeRealisation . }}
        OPTIONAL {{ ?projet ont:noteProjet ?noteProjet . }}
        
        # Étudiants réalisateurs
        OPTIONAL {{
            ?projet ont:realisePar ?etudiant .
            ?etudiant ont:nom ?nomEtudiant .
        }}
        
        # Enseignants encadrants
        OPTIONAL {{
            ?projet ont:encadrePar ?encadrant .
            ?encadrant ont:nom ?nomEncadrant .
        }}
    }}
    ORDER BY ?anneeRealisation DESC
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/stats', methods=['GET'])
def get_universites_stats():
    """Récupère les statistiques des universités avec facettes"""
    # Stats générales
    query_stats = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    
    SELECT 
        (COUNT(DISTINCT ?universite) as ?total_universites)
        (SUM(?nbEtudiants) as ?total_etudiants)
        (COUNT(DISTINCT ?enseignant) as ?total_enseignants)
        (COUNT(DISTINCT ?specialite) as ?total_specialites)
        (COUNT(DISTINCT ?technologie) as ?total_technologies)
    WHERE {
        ?universite a ont:Universite .
        OPTIONAL { ?universite ont:nombreEtudiants ?nbEtudiants . }
        OPTIONAL { ?universite ont:emploie ?enseignant . }
        OPTIONAL { ?universite ont:offre ?specialite . }
        OPTIONAL { ?universite ont:adopteTechnologie ?technologie . }
    }
    """
    
    # Facettes par type
    query_type = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?typeUniversite (COUNT(DISTINCT ?universite) as ?count)
    WHERE {
        ?universite rdf:type ?type .
        FILTER(?type IN (ont:Universite, ont:UniversitePublique, ont:UniversitePrivee))
        BIND(
          IF(?type = ont:UniversitePublique, "Publique",
            IF(?type = ont:UniversitePrivee, "Privée", "Générale")
          ) AS ?typeUniversite
        )
    }
    GROUP BY ?typeUniversite
    ORDER BY DESC(?count)
    """
    
    # Facettes par pays
    query_pays = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    
    SELECT ?pays (COUNT(DISTINCT ?universite) as ?count)
    WHERE {
        ?universite a ont:Universite .
        ?universite ont:pays ?pays .
    }
    GROUP BY ?pays
    ORDER BY DESC(?count)
    LIMIT 20
    """
    
    # Facettes par ville
    query_ville = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    
    SELECT ?ville (COUNT(DISTINCT ?universite) as ?count)
    WHERE {
        ?universite a ont:Universite .
        ?universite ont:ville ?ville .
    }
    GROUP BY ?ville
    ORDER BY DESC(?count)
    LIMIT 20
    """
    
    # Top-rated universities (rang <= 5) - Inference layer
    query_top_rated = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    
    SELECT ?universite ?nomUniversite ?ville ?pays ?rangNational ?nombreEtudiants
    WHERE {
        ?universite a ont:Universite .
        ?universite ont:nomUniversite ?nomUniversite .
        ?universite ont:rangNational ?rangNational .
        FILTER(xsd:integer(?rangNational) <= 5)
        OPTIONAL { ?universite ont:ville ?ville . }
        OPTIONAL { ?universite ont:pays ?pays . }
        OPTIONAL { ?universite ont:nombreEtudiants ?nombreEtudiants . }
    }
    ORDER BY xsd:integer(?rangNational)
    """
    
    try:
        stats = sparql_utils.execute_query(query_stats)
        facets = {
            "by_type": sparql_utils.execute_query(query_type),
            "by_pays": sparql_utils.execute_query(query_pays),
            "by_ville": sparql_utils.execute_query(query_ville),
            "top_rated": sparql_utils.execute_query(query_top_rated)
        }
        
        return jsonify({
            "stats": stats[0] if stats else {},
            "facets": facets
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/ranking', methods=['GET'])
def get_universites_ranking():
    """Récupère le classement des universités"""
    query = """
    PREFIX ont: <http://www.education-intelligente.org/ontologie#>
    SELECT ?universite ?nomUniversite ?ville ?pays ?rangNational 
           ?nombreEtudiants ?anneeFondation ?typeUniversite
    WHERE {
        ?universite a ont:Universite ;
                   ont:nomUniversite ?nomUniversite ;
                   ont:rangNational ?rangNational .
        
        OPTIONAL { ?universite ont:ville ?ville . }
        OPTIONAL { ?universite ont:pays ?pays . }
        OPTIONAL { ?universite ont:nombreEtudiants ?nombreEtudiants . }
        OPTIONAL { ?universite ont:anneeFondation ?anneeFondation . }
        
        # Déterminer le type d'université
        OPTIONAL {
            ?universite a ?type .
            FILTER(?type IN (ont:UniversitePublique, ont:UniversitePrivee))
            BIND(
              IF(?type = ont:UniversitePublique, "Publique",
                IF(?type = ont:UniversitePrivee, "Privée", "Générale")
              ) AS ?typeUniversite
            )
        }
    }
    ORDER BY xsd:integer(?rangNational)
    """
    
    try:
        results = sparql_utils.execute_query(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_universite_uri(nom: str) -> str:
    """Generate a unique URI for a universite"""
    safe_nom = nom.upper().replace(' ', '_').replace("'", "")[:50]
    return f"{PREFIX}Universite_{safe_nom}_{uuid.uuid4().hex[:8]}"

@universite_bp.route('/universites', methods=['POST'])
def create_universite():
    """Create a new universite"""
    data = request.json
    
    errors = validate_universite(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    universite_uri = generate_universite_uri(data.get('nomUniversite'))
    type_univ = data.get('type', 'Universite')
    
    type_mapping = {
        'Publique': 'ont:UniversitePublique',
        'Privée': 'ont:UniversitePrivee'
    }
    univ_type = type_mapping.get(type_univ, 'ont:Universite')
    
    insert_parts = [
        f"<{universite_uri}> a {univ_type}",
        f"; ont:nomUniversite \"{data.get('nomUniversite')}\""
    ]
    
    if data.get('anneeFondation'):
        insert_parts.append(f"; ont:anneeFondation {int(data.get('anneeFondation'))}")
    if data.get('ville'):
        insert_parts.append(f"; ont:ville \"{data.get('ville')}\"")
    if data.get('pays'):
        insert_parts.append(f"; ont:pays \"{data.get('pays')}\"")
    if data.get('nombreEtudiants'):
        insert_parts.append(f"; ont:nombreEtudiants {int(data.get('nombreEtudiants'))}")
    if data.get('rangNational'):
        insert_parts.append(f"; ont:rangNational {int(data.get('rangNational'))}")
    if data.get('siteWeb'):
        insert_parts.append(f"; ont:siteWeb \"{data.get('siteWeb')}\"")
    
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
        return jsonify({"message": "Université créée avec succès", "uri": universite_uri}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>', methods=['PUT'])
def update_universite(universite_id):
    """Update a universite"""
    universite_id = normalize_universite_id(universite_id)
    data = request.json
    
    errors = validate_universite(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    delete_query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE {{
        <{universite_id}> ?p ?o .
    }}
    WHERE {{
        <{universite_id}> ?p ?o .
        FILTER(?p != ont:offre && ?p != ont:emploie && ?p != ont:adopteTechnologie)
    }}
    """
    
    insert_parts = [f"<{universite_id}> a ont:Universite"]
    
    if data.get('nomUniversite'):
        insert_parts.append(f"; ont:nomUniversite \"{data.get('nomUniversite')}\"")
    if data.get('anneeFondation'):
        insert_parts.append(f"; ont:anneeFondation {int(data.get('anneeFondation'))}")
    if data.get('ville'):
        insert_parts.append(f"; ont:ville \"{data.get('ville')}\"")
    if data.get('pays'):
        insert_parts.append(f"; ont:pays \"{data.get('pays')}\"")
    if data.get('nombreEtudiants'):
        insert_parts.append(f"; ont:nombreEtudiants {int(data.get('nombreEtudiants'))}")
    if data.get('rangNational'):
        insert_parts.append(f"; ont:rangNational {int(data.get('rangNational'))}")
    if data.get('siteWeb'):
        insert_parts.append(f"; ont:siteWeb \"{data.get('siteWeb')}\"")
    
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
        return jsonify({"message": "Université mise à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>', methods=['DELETE'])
def delete_universite(universite_id):
    """Delete a universite"""
    universite_id = normalize_universite_id(universite_id)
    # Construct full URI if not already a full URI
    if universite_id.startswith('http://') or universite_id.startswith('https://'):
        universite_uri = universite_id
    else:
        if universite_id.startswith(PREFIX):
            universite_uri = universite_id
        else:
            universite_uri = f"{PREFIX}{universite_id}"
    
    query = f"""
    PREFIX ont: <{PREFIX}>
    DELETE WHERE {{
        <{universite_uri}> ?p ?o .
    }}
    """
    
    try:
        result = sparql_utils.execute_update(query)
        if "error" in result:
            return jsonify(result), 500
        return jsonify({"message": "Université supprimée avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@universite_bp.route('/universites/<path:universite_id>/dbpedia-enrich', methods=['GET'])
def enrich_universite_with_dbpedia(universite_id):
    """Enrich university data with DBpedia information (Linked Data integration)"""
    try:
        universite_id = normalize_universite_id(universite_id)
        
        # First get the university data
        # Use rdf:type to match both Universite and its subclasses (UniversitePublique, UniversitePrivee)
        query = f"""
        PREFIX ont: <{PREFIX}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?nomUniversite ?ville ?pays
        WHERE {{
            <{universite_id}> rdf:type ?type .
            FILTER(?type IN (ont:Universite, ont:UniversitePublique, ont:UniversitePrivee))
            OPTIONAL {{ <{universite_id}> ont:nomUniversite ?nomUniversite . }}
            OPTIONAL {{ <{universite_id}> ont:ville ?ville . }}
            OPTIONAL {{ <{universite_id}> ont:pays ?pays . }}
        }}
        """
        
        print(f"DEBUG: DBpedia enrich query: {query}")
        results = sparql_utils.execute_query(query)
        print(f"DEBUG: Query results: {results}")
        
        if not results:
            return jsonify({"error": "Université non trouvée", "debug_uri": universite_id}), 404
        
        univ_data = results[0]
        city_name = univ_data.get("ville")
        
        # Get search term from query parameter or use university name/city
        search_term = request.args.get('term')
        if not search_term:
            # Prefer nomUniversite over ville for better DBpedia matching
            search_term = univ_data.get("nomUniversite") or city_name
        
        enriched_data = {
            "universite": univ_data,
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
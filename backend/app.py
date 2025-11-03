from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from modules.campRes import api_routes
import os
from modules.personne import personne_bp  # Updated import
from modules.locations import locations_bp
from modules.specialite_bp import specialite_bp  # New import
from modules.universite_bp import universite_bp  # New import
from modules.users import users_bp
from modules.search import search_bp
from modules.blogs import blogs_bp
from modules.reservations import reservations_bp
from modules.certifications import certifications_bp
from modules.sponsors import sponsors_bp
from modules.volunteers import volunteers_bp
from modules.assignments import assignments_bp
from sparql_utils import sparql_utils
from modules.reviews import reviews_bp
from modules.cours_bp import cours_bp
from modules.competences_bp import competences_bp
from modules.projets_bp import projets_bp
from modules.ressources_bp import ressources_bp
from modules.technologies_bp import technologies_bp
from modules.evaluations_bp import evaluations_bp
from modules.orientations_bp import orientations_bp

app = Flask(__name__)
CORS(app)

# Basic logger setup to avoid NameError in exception handlers
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enregistrement des routes
app.register_blueprint(api_routes, url_prefix='/api')
app.register_blueprint(personne_bp, url_prefix='/api')  # Updated blueprint registration
app.register_blueprint(specialite_bp, url_prefix='/api')  # New blueprint registration
app.register_blueprint(locations_bp, url_prefix='/api')
app.register_blueprint(universite_bp, url_prefix='/api')  # New blueprint registration
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(reservations_bp, url_prefix='/api')
app.register_blueprint(certifications_bp, url_prefix='/api')
app.register_blueprint(sponsors_bp, url_prefix='/api')
app.register_blueprint(volunteers_bp, url_prefix='/api')
app.register_blueprint(assignments_bp, url_prefix='/api')
app.register_blueprint(blogs_bp, url_prefix='/api')
app.register_blueprint(reviews_bp, url_prefix='/api')
# Education domain blueprints
app.register_blueprint(cours_bp, url_prefix='/api')
app.register_blueprint(competences_bp, url_prefix='/api')
app.register_blueprint(projets_bp, url_prefix='/api')
app.register_blueprint(ressources_bp, url_prefix='/api')
app.register_blueprint(technologies_bp, url_prefix='/api')
app.register_blueprint(evaluations_bp, url_prefix='/api')
app.register_blueprint(orientations_bp, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({"message": "Education Intelligente Platform API is running!"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de santé de l'API"""
    return jsonify({"status": "OK", "message": "API fonctionnelle"})

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Test de connexion à Fuseki et aux données"""
    try:
        if not sparql_utils:
            return jsonify({
                "status": "error",
                "message": "SPARQL utils non initialisé"
            }), 500
            
        # Test simple de comptage
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        results = sparql_utils.execute_query(query)
        
        # Test des personnes
        personnes_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT (COUNT(*) as ?personne_count) WHERE {
            ?personne a edu:Personne .
        }
        """
        personnes_results = sparql_utils.execute_query(personnes_query)
        
        # Test des étudiants
        etudiants_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT (COUNT(*) as ?etudiant_count) WHERE {
            ?etudiant a edu:Etudiant .
        }
        """
        etudiants_results = sparql_utils.execute_query(etudiants_query)
        
        # Test des enseignants
        enseignants_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT (COUNT(*) as ?enseignant_count) WHERE {
            ?enseignant a edu:Enseignant .
        }
        """
        enseignants_results = sparql_utils.execute_query(enseignants_query)
        
        # Test des cours
        cours_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT (COUNT(*) as ?cours_count) WHERE {
            ?cours a edu:Cours .
        }
        """
        cours_results = sparql_utils.execute_query(cours_query)
        
        return jsonify({
            "status": "success",
            "message": "Connexion Fuseki OK",
            "data_summary": {
                "total_triplets": results[0].get('count', 0) if results else 0,
                "total_personnes": personnes_results[0].get('personne_count', 0) if personnes_results else 0,
                "total_etudiants": etudiants_results[0].get('etudiant_count', 0) if etudiants_results else 0,
                "total_enseignants": enseignants_results[0].get('enseignant_count', 0) if enseignants_results else 0,
                "total_cours": cours_results[0].get('cours_count', 0) if cours_results else 0
            }
        })
        
    except Exception as e:
        app.logger.error(f"Erreur test Fuseki: {str(e)}")
        logger.error(f"Erreur test Fuseki: {str(e)}")

        return jsonify({
            "status": "error",
            "message": f"Erreur Fuseki: {str(e)}"
        }), 500

@app.route('/api/ontology-stats', methods=['GET'])
def get_ontology_stats():
    """Récupère les statistiques de l'ontologie pour affichage dans la navbar"""
    try:
        if not sparql_utils:
            return jsonify({
                "status": "error",
                "message": "SPARQL utils non initialisé"
            }), 500
        
        # Requête pour compter toutes les classes principales
        stats_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT 
            (COUNT(DISTINCT ?class) as ?total_classes)
            (COUNT(DISTINCT ?property) as ?total_properties)
            (COUNT(DISTINCT ?individual) as ?total_individuals)
        WHERE {
            {
                ?class a owl:Class .
                FILTER(STRSTARTS(STR(?class), "http://www.education-intelligente.org/ontologie#"))
            } UNION {
                ?property a owl:ObjectProperty .
                FILTER(STRSTARTS(STR(?property), "http://www.education-intelligente.org/ontologie#"))
            } UNION {
                ?property a owl:DatatypeProperty .
                FILTER(STRSTARTS(STR(?property), "http://www.education-intelligente.org/ontologie#"))
            } UNION {
                ?individual a ?class .
                FILTER(STRSTARTS(STR(?class), "http://www.education-intelligente.org/ontologie#"))
            }
        }
        """
        
        results = sparql_utils.execute_query(stats_query)
        
        # Requête pour compter les instances par type
        instances_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        
        SELECT 
            (COUNT(DISTINCT ?personne) as ?personnes)
            (COUNT(DISTINCT ?etudiant) as ?etudiants)
            (COUNT(DISTINCT ?enseignant) as ?enseignants)
            (COUNT(DISTINCT ?cours) as ?cours)
            (COUNT(DISTINCT ?universite) as ?universites)
            (COUNT(DISTINCT ?specialite) as ?specialites)
            (COUNT(DISTINCT ?competence) as ?competences)
            (COUNT(DISTINCT ?projet) as ?projets)
            (COUNT(DISTINCT ?ressource) as ?ressources)
            (COUNT(DISTINCT ?technologie) as ?technologies)
        WHERE {
            OPTIONAL { ?personne a edu:Personne }
            OPTIONAL { ?etudiant a edu:Etudiant }
            OPTIONAL { ?enseignant a edu:Enseignant }
            OPTIONAL { ?cours a edu:Cours }
            OPTIONAL { ?universite a edu:Universite }
            OPTIONAL { ?specialite a edu:Specialite }
            OPTIONAL { ?competence a edu:Competence }
            OPTIONAL { ?projet a edu:ProjetAcademique }
            OPTIONAL { ?ressource a edu:RessourcePedagogique }
            OPTIONAL { ?technologie a edu:TechnologieEducative }
        }
        """
        
        instances_results = sparql_utils.execute_query(instances_query)
        
        # Requête pour obtenir les informations de l'ontologie
        ontology_info_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        PREFIX terms: <http://purl.org/dc/terms/>
        
        SELECT ?title ?description ?version ?creator ?created
        WHERE {
            ?ontology a owl:Ontology .
            OPTIONAL { ?ontology terms:title ?title }
            OPTIONAL { ?ontology terms:description ?description }
            OPTIONAL { ?ontology owl:versionInfo ?version }
            OPTIONAL { ?ontology terms:creator ?creator }
            OPTIONAL { ?ontology terms:created ?created }
        }
        """
        
        ontology_info = sparql_utils.execute_query(ontology_info_query)
        
        return jsonify({
            "status": "success",
            "ontology_info": ontology_info[0] if ontology_info else {},
            "statistics": results[0] if results else {},
            "instances": instances_results[0] if instances_results else {}
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de la récupération des statistiques: {str(e)}"
        }), 500

@app.route('/api/ontology/graph', methods=['GET'])
def get_ontology_graph():
    """Return nodes and edges for a graph visualization focused on education domain."""
    try:
        # Build a SPARQL query that returns individuals of the main classes and their outgoing properties
        query = '''
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?s ?sLabel ?type ?p ?pLabel ?o ?oLabel WHERE {
            ?s a ?type .
            # include types that are the class itself or subclasses
            ?type rdfs:subClassOf* ?superType .
            VALUES ?superType { edu:Personne edu:Etudiant edu:Enseignant edu:Cours edu:Universite edu:Specialite edu:Competence }
            OPTIONAL { ?s rdfs:label ?sLabel }
            OPTIONAL {
                ?s ?p ?o .
                OPTIONAL { ?p rdfs:label ?pLabel }
                OPTIONAL { ?o rdfs:label ?oLabel }
            }
        }
        LIMIT 2000
        '''

        sparql_utils.sparql.setQuery(query)
        results = sparql_utils.sparql.query().convert()

        nodes = {}
        edges = []

        for b in results.get('results', {}).get('bindings', []):
            s = b.get('s', {}).get('value')
            t = b.get('type', {}).get('value')
            if not s:
                continue
            sLabel = b.get('sLabel', {}).get('value')

            if s not in nodes:
                nodes[s] = { 'id': s, 'label': sLabel or s.split('#')[-1].split('/')[-1], 'types': [], 'properties': {} }
            if t and t not in nodes[s]['types']:
                nodes[s]['types'].append(t)

            # handle p/o
            if 'p' in b and 'o' in b:
                pval = b['p']['value']
                pLabel = b.get('pLabel', {}).get('value')
                o = b['o']
                otype = o.get('type')
                oval = o.get('value')
                oLabel = b.get('oLabel', {}).get('value')
                if otype == 'uri':
                    # ensure target node exists
                    if oval not in nodes:
                        nodes[oval] = { 'id': oval, 'label': oLabel or oval.split('#')[-1].split('/')[-1], 'types': [], 'properties': {} }
                    # skip rdf:type triples as edges
                    if pval != 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                        edges.append({ 'source': s, 'target': oval, 'predicate': pval, 'predicateLabel': pLabel or (pval.split('#')[-1].split('/')[-1]) })
                else:
                    # literal -> store as property on subject
                    nodes[s]['properties'].setdefault(pval, []).append(oval)

        # Convert nodes dict to list
        nodes_list = []
        for n in nodes.values():
            nodes_list.append(n)

        return jsonify({ 'nodes': nodes_list, 'edges': edges })

    except Exception as e:
        app.logger.error(f"Erreur building ontology graph: {str(e)}")
        return jsonify({ 'error': str(e) }), 500

@app.route('/api/education-stats', methods=['GET'])
def get_education_stats():
    """Récupère les statistiques spécifiques au domaine éducatif"""
    try:
        if not sparql_utils:
            return jsonify({
                "status": "error",
                "message": "SPARQL utils non initialisé"
            }), 500
        
        # Statistiques des étudiants par niveau
        etudiants_niveau_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?niveau (COUNT(?etudiant) as ?count)
        WHERE {
            ?etudiant a edu:Etudiant .
            OPTIONAL { ?etudiant edu:niveauEtude ?niveau . }
        }
        GROUP BY ?niveau
        """
        
        # Statistiques des enseignants par grade
        enseignants_grade_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?grade (COUNT(?enseignant) as ?count)
        WHERE {
            ?enseignant a edu:Enseignant .
            OPTIONAL { ?enseignant edu:grade ?grade . }
        }
        GROUP BY ?grade
        """
        
        # Statistiques des cours par spécialité
        cours_specialite_query = """
        PREFIX edu: <http://www.education-intelligente.org/ontologie#>
        SELECT ?specialite (COUNT(?cours) as ?count)
        WHERE {
            ?cours a edu:Cours .
            ?cours edu:faitPartieDe ?specialite .
            ?specialite edu:nomSpecialite ?nomSpecialite .
        }
        GROUP BY ?specialite ?nomSpecialite
        """
        
        etudiants_niveau = sparql_utils.execute_query(etudiants_niveau_query)
        enseignants_grade = sparql_utils.execute_query(enseignants_grade_query)
        cours_specialite = sparql_utils.execute_query(cours_specialite_query)
        
        return jsonify({
            "status": "success",
            "etudiants_par_niveau": etudiants_niveau,
            "enseignants_par_grade": enseignants_grade,
            "cours_par_specialite": cours_specialite
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de la récupération des statistiques éducatives: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from modules.campRes import api_routes
import os
from modules.events import events_bp
from modules.locations import locations_bp
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


app = Flask(__name__)
CORS(app)

# Basic logger setup to avoid NameError in exception handlers
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enregistrement des routes
app.register_blueprint(api_routes, url_prefix='/api')
app.register_blueprint(events_bp, url_prefix='/api')
app.register_blueprint(locations_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(reservations_bp, url_prefix='/api')
app.register_blueprint(certifications_bp, url_prefix='/api')
app.register_blueprint(sponsors_bp, url_prefix='/api')

app.register_blueprint(volunteers_bp, url_prefix='/api')
app.register_blueprint(assignments_bp, url_prefix='/api')

app.register_blueprint(blogs_bp, url_prefix='/api')
app.register_blueprint(reviews_bp, url_prefix='/api')



@app.route('/')
def home():
    return jsonify({"message": "Eco Platform API is running!"})



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
        
        # Test des événements
        events_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT (COUNT(*) as ?event_count) WHERE {
            ?event a eco:Event .
        }
        """
        events_results = sparql_utils.execute_query(events_query)
        
        # Test des locations
        locations_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT (COUNT(*) as ?location_count) WHERE {
            ?location a eco:Location .
        }
        """
        locations_results = sparql_utils.execute_query(locations_query)
        
        # Test des utilisateurs
        users_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT (COUNT(*) as ?user_count) WHERE {
            ?user a eco:User .
        }
        """
        users_results = sparql_utils.execute_query(users_query)
        
        return jsonify({
            "status": "success",
            "message": "Connexion Fuseki OK",
            "data_summary": {
                "total_triplets": results[0].get('count', 0) if results else 0,
                "total_events": events_results[0].get('event_count', 0) if events_results else 0,
                "total_locations": locations_results[0].get('location_count', 0) if locations_results else 0,
                "total_users": users_results[0].get('user_count', 0) if users_results else 0
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
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT 
            (COUNT(DISTINCT ?class) as ?total_classes)
            (COUNT(DISTINCT ?property) as ?total_properties)
            (COUNT(DISTINCT ?individual) as ?total_individuals)
        WHERE {
            {
                ?class a owl:Class .
                FILTER(STRSTARTS(STR(?class), "http://www.semanticweb.org/eco-ontology#"))
            } UNION {
                ?property a owl:ObjectProperty .
                FILTER(STRSTARTS(STR(?property), "http://www.semanticweb.org/eco-ontology#"))
            } UNION {
                ?property a owl:DatatypeProperty .
                FILTER(STRSTARTS(STR(?property), "http://www.semanticweb.org/eco-ontology#"))
            } UNION {
                ?individual a ?class .
                FILTER(STRSTARTS(STR(?class), "http://www.semanticweb.org/eco-ontology#"))
            }
        }
        """
        
        results = sparql_utils.execute_query(stats_query)
        
        # Requête pour compter les instances par type
        instances_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        
        SELECT 
            (COUNT(DISTINCT ?event) as ?events)
            (COUNT(DISTINCT ?location) as ?locations)
            (COUNT(DISTINCT ?user) as ?users)
            (COUNT(DISTINCT ?campaign) as ?campaigns)
            (COUNT(DISTINCT ?resource) as ?resources)
            (COUNT(DISTINCT ?sponsor) as ?sponsors)
            (COUNT(DISTINCT ?donation) as ?donations)
            (COUNT(DISTINCT ?blog) as ?blogs)
        WHERE {
            OPTIONAL { ?event a eco:Event }
            OPTIONAL { ?location a eco:Location }
            OPTIONAL { ?user a eco:User }
            OPTIONAL { ?campaign a eco:Campaign }
            OPTIONAL { ?resource a eco:Resource }
            OPTIONAL { ?sponsor a eco:Sponsor }
            OPTIONAL { ?donation a eco:Donation }
            OPTIONAL { ?blog a eco:Blog }
        }
        """
        
        instances_results = sparql_utils.execute_query(instances_query)
        
        # Requête pour obtenir les informations de l'ontologie
        ontology_info_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
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
    """Return nodes and edges for a graph visualization focused on Sponsor/Donation/SponsorshipLevel/Event."""
    try:
        # Build a SPARQL query that returns individuals of the main classes and their outgoing properties
        query = '''
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                        SELECT DISTINCT ?s ?sLabel ?type ?p ?pLabel ?o ?oLabel WHERE {
                            ?s a ?type .
                            # include types that are the class itself or subclasses (captures FinancialDonation, etc.)
                            ?type rdfs:subClassOf* ?superType .
                            VALUES ?superType { eco:Sponsor eco:Donation eco:Event }
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
    


if __name__ == '__main__':
    app.run(debug=True, port=5000)
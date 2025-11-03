from flask import Blueprint, jsonify
from sparql_utils import sparql_utils

events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['GET'])
def get_all_events():
    """Récupère tous les événements"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?event ?title ?description ?date ?location ?locationName ?maxParticipants ?status ?duration ?images
    WHERE {
        ?event a eco:Event ;
               eco:eventTitle ?title ;
               eco:eventDate ?date ;
               eco:isLocatedAt ?location ;
               eco:maxParticipants ?maxParticipants .
        
        OPTIONAL { ?event eco:eventDescription ?description . }
        OPTIONAL { ?event eco:eventStatus ?status . }
        OPTIONAL { ?event eco:duration ?duration . }
        OPTIONAL { ?location eco:locationName ?locationName . }
        OPTIONAL { ?event eco:eventImages ?images . }
    }
    ORDER BY ?date
    """
    results = sparql_utils.execute_query(query)
    
    # Debug: Print what we're getting from SPARQL
    print("DEBUG - Raw images data from SPARQL:")
    for event in results:
        print(f"Event: {event.get('title')}, Images: {event.get('images')}")
    
    return jsonify(results)

@events_bp.route('/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Récupère un événement spécifique"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?event ?title ?description ?date ?location ?locationName ?address ?maxParticipants ?status ?duration
    WHERE {{
        <{event_id}> a eco:Event ;
               eco:eventTitle ?title ;
               eco:eventDate ?date ;
               eco:isLocatedAt ?location ;
               eco:maxParticipants ?maxParticipants .
        
        ?location eco:locationName ?locationName ;
                 eco:address ?address .
        
        OPTIONAL {{ <{event_id}> eco:eventDescription ?description . }}
        OPTIONAL {{ <{event_id}> eco:eventStatus ?status . }}
        OPTIONAL {{ <{event_id}> eco:duration ?duration . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@events_bp.route('/events/search', methods=['POST'])
def search_events():
    """Recherche d'événements par critères"""
    from flask import request
    
    data = request.json
    location = data.get('location', '')
    date = data.get('date', '')
    title = data.get('title', '')
    
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?event ?title ?description ?date ?location ?locationName ?maxParticipants
    WHERE {
        ?event a eco:Event ;
               eco:eventTitle ?title ;
               eco:eventDate ?date ;
               eco:isLocatedAt ?location ;
               eco:maxParticipants ?maxParticipants .
        
        ?location eco:locationName ?locationName .
        
        OPTIONAL { ?event eco:eventDescription ?description . }
    """
    
    filters = []
    if location:
        filters.append(f'REGEX(?locationName, "{location}", "i")')
    if date:
        filters.append(f'REGEX(?date, "{date}", "i")')
    if title:
        filters.append(f'REGEX(?title, "{title}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?date"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)
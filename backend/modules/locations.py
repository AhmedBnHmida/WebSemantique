from flask import Blueprint, jsonify
from sparql_utils import sparql_utils

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/locations', methods=['GET'])
def get_all_locations():
    """Récupère toutes les locations"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?location ?name ?address ?city ?country ?capacity ?price ?reserved ?inRepair ?description
    WHERE {
        ?location a eco:Location .
        
        OPTIONAL { ?location eco:locationName ?name . }
        OPTIONAL { ?location eco:address ?address . }
        OPTIONAL { ?location eco:city ?city . }
        OPTIONAL { ?location eco:country ?country . }
        OPTIONAL { ?location eco:capacity ?capacity . }
        OPTIONAL { ?location eco:price ?price . }
        OPTIONAL { ?location eco:reserved ?reserved . }
        OPTIONAL { ?location eco:inRepair ?inRepair . }
        OPTIONAL { ?location eco:locationDescription ?description . }
    }
    ORDER BY ?name
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@locations_bp.route('/locations/<location_id>', methods=['GET'])
def get_location(location_id):
    """Récupère une location spécifique"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?location ?name ?address ?city ?country ?capacity ?price ?reserved ?inRepair ?description ?latitude ?longitude ?images
    WHERE {{
        <{location_id}> a eco:Location ;
                 eco:locationName ?name ;
                 eco:address ?address ;
                 eco:capacity ?capacity .
        
        OPTIONAL {{ <{location_id}> eco:city ?city . }}
        OPTIONAL {{ <{location_id}> eco:country ?country . }}
        OPTIONAL {{ <{location_id}> eco:price ?price . }}
        OPTIONAL {{ <{location_id}> eco:reserved ?reserved . }}
        OPTIONAL {{ <{location_id}> eco:inRepair ?inRepair . }}
        OPTIONAL {{ <{location_id}> eco:locationDescription ?description . }}
        OPTIONAL {{ <{location_id}> eco:latitude ?latitude . }}
        OPTIONAL {{ <{location_id}> eco:longitude ?longitude . }}
        OPTIONAL {{ <{location_id}> eco:locationImages ?images . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@locations_bp.route('/locations/available', methods=['GET'])
def get_available_locations():
    """Récupère les locations disponibles (non réservées et non en réparation)"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?location ?name ?address ?city ?capacity ?price
    WHERE {
        ?location a eco:Location .
        
        OPTIONAL { ?location eco:locationName ?name . }
        OPTIONAL { ?location eco:address ?address . }
        OPTIONAL { ?location eco:city ?city . }
        OPTIONAL { ?location eco:capacity ?capacity . }
        OPTIONAL { ?location eco:price ?price . }
        OPTIONAL { ?location eco:reserved ?reserved . }
        OPTIONAL { ?location eco:inRepair ?inRepair . }
        
        # Filter for available locations
        FILTER (!BOUND(?reserved) || ?reserved = false)
        FILTER (!BOUND(?inRepair) || ?inRepair = false)
    }
    ORDER BY ?name
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@locations_bp.route('/locations/search', methods=['POST'])
def search_locations():
    """Recherche de locations par critères"""
    from flask import request
    
    data = request.json
    city = data.get('city', '')
    min_capacity = data.get('min_capacity', '')
    max_price = data.get('max_price', '')
    
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?location ?name ?address ?city ?capacity ?price
    WHERE {
        ?location a eco:Location ;
                 eco:locationName ?name ;
                 eco:address ?address ;
                 eco:capacity ?capacity ;
                 eco:price ?price .
        
        OPTIONAL { ?location eco:city ?city . }
    """
    
    filters = []
    if city:
        filters.append(f'REGEX(?city, "{city}", "i")')
    if min_capacity:
        filters.append(f'?capacity >= {min_capacity}')
    if max_price:
        filters.append(f'?price <= {max_price}')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?price"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)




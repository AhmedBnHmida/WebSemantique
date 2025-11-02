from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils

volunteers_bp = Blueprint('volunteers', __name__)

@volunteers_bp.route('/volunteers', methods=['GET'])
def get_all_volunteers():
    """Récupère tous les volontaires"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
    }
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/<volunteer_id>', methods=['GET'])
def get_volunteer(volunteer_id):
    """Récupère un volontaire spécifique"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {{
        <{volunteer_id}> a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL {{ <{volunteer_id}> rdfs:label ?label . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@volunteers_bp.route('/volunteers/search', methods=['POST'])
def search_volunteers():
    """Recherche de volontaires par critères"""
    from flask import request
    
    data = request.json
    skills = data.get('skills', '')
    activity_level = data.get('activity_level', '')
    medical_conditions = data.get('medical_conditions', '')
    
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
    """
    
    filters = []
    if skills:
        filters.append(f'REGEX(?skills, "{skills}", "i")')
    if activity_level:
        filters.append(f'REGEX(?activityLevel, "{activity_level}", "i")')
    if medical_conditions:
        filters.append(f'REGEX(?medicalConditions, "{medical_conditions}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?label"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/by-activity-level/<level>', methods=['GET'])
def get_volunteers_by_activity_level(level):
    """Récupère les volontaires par niveau d'activité"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?skills ?activityLevel
    WHERE {{
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> ;
                  <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
        
        OPTIONAL {{ ?volunteer rdfs:label ?label . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }}
        
        FILTER(REGEX(?activityLevel, "{level}", "i"))
    }}
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/by-skills/<skill>', methods=['GET'])
def get_volunteers_by_skills(skill):
    """Récupère les volontaires par compétence"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?skills ?activityLevel ?experience
    WHERE {{
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> ;
                  <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills .
        
        OPTIONAL {{ ?volunteer rdfs:label ?label . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }}
        
        FILTER(REGEX(?skills, "{skill}", "i"))
    }}
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/active', methods=['GET'])
def get_active_volunteers():
    """Récupère les volontaires actifs"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?skills ?activityLevel ?motivation ?experience
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> ;
                  <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        
        FILTER(REGEX(?activityLevel, "actif", "i"))
    }
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/experienced', methods=['GET'])
def get_experienced_volunteers():
    """Récupère les volontaires avec de l'expérience"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?skills ?activityLevel ?experience ?motivation
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> ;
                  <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
    }
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/statistics', methods=['GET'])
def get_volunteer_statistics():
    """Récupère les statistiques des volontaires"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    SELECT 
        (COUNT(?volunteer) as ?total)
        (COUNT(?active) as ?active_count)
        (COUNT(?experienced) as ?experienced_count)
        (COUNT(?with_skills) as ?with_skills_count)
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL { 
            ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
            FILTER(REGEX(?activityLevel, "actif", "i"))
            BIND(?volunteer as ?active)
        }
        OPTIONAL { 
            ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience .
            BIND(?volunteer as ?experienced)
        }
        OPTIONAL { 
            ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills .
            BIND(?volunteer as ?with_skills)
        }
    }
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@volunteers_bp.route('/volunteers/advanced-search', methods=['POST'])
def advanced_search_volunteers():
    """Recherche avancée de volontaires avec plusieurs critères"""
    data = request.get_json(force=True)
    
    skills = data.get('skills', '')
    activity_level = data.get('activity_level', '')
    has_experience = data.get('has_experience', False)
    has_medical_conditions = data.get('has_medical_conditions', None)
    motivation_keyword = data.get('motivation_keyword', '')
    
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
    """
    
    filters = []
    if skills:
        filters.append(f'REGEX(?skills, "{skills}", "i")')
    if activity_level:
        filters.append(f'REGEX(?activityLevel, "{activity_level}", "i")')
    if has_experience:
        filters.append('BOUND(?experience)')
    if has_medical_conditions is not None:
        if has_medical_conditions:
            filters.append('BOUND(?medicalConditions)')
        else:
            filters.append('!BOUND(?medicalConditions)')
    if motivation_keyword:
        filters.append(f'(REGEX(?motivation, "{motivation_keyword}", "i") || REGEX(?generalMotivation, "{motivation_keyword}", "i"))')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?label"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)

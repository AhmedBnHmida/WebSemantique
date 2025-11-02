from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils

assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('/assignments', methods=['GET'])
def get_all_assignments():
    """Récupère tous les assignements"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
    }
    ORDER BY ?assignment
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/<assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Récupère un assignement spécifique"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {{
        <{assignment_id}> a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
        
        OPTIONAL {{ <{assignment_id}> rdfs:label ?label . }}
        OPTIONAL {{ <{assignment_id}> <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }}
        OPTIONAL {{ <{assignment_id}> <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }}
        OPTIONAL {{ <{assignment_id}> <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }}
        OPTIONAL {{ <{assignment_id}> <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }}
        OPTIONAL {{ <{assignment_id}> <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@assignments_bp.route('/assignments/by-status/<status>', methods=['GET'])
def get_assignments_by_status(status):
    """Récupère les assignements par statut"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {{
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
        
        OPTIONAL {{ ?assignment rdfs:label ?label . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }}
        
        FILTER(REGEX(?status, "{status}", "i"))
    }}
    ORDER BY ?startDate DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/by-rating/<int:min_rating>', methods=['GET'])
def get_assignments_by_rating(min_rating):
    """Récupère les assignements avec une note minimale"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {{
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
        
        OPTIONAL {{ ?assignment rdfs:label ?label . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }}
        
        FILTER(?rating >= {min_rating})
    }}
    ORDER BY ?rating DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/search', methods=['POST'])
def search_assignments():
    """Recherche d'assignements par critères"""
    from flask import request
    
    data = request.json
    status = data.get('status', '')
    min_rating = data.get('min_rating', '')
    date_from = data.get('date_from', '')
    date_to = data.get('date_to', '')
    
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
    """
    
    filters = []
    if status:
        filters.append(f'REGEX(?status, "{status}", "i")')
    if min_rating:
        filters.append(f'?rating >= {min_rating}')
    if date_from:
        filters.append(f'?startDate >= "{date_from}"^^xsd:date')
    if date_to:
        filters.append(f'?startDate <= "{date_to}"^^xsd:date')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?startDate DESC"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/statistics', methods=['GET'])
def get_assignment_statistics():
    """Récupère les statistiques des assignements"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    SELECT 
        (COUNT(?assignment) as ?total)
        (COUNT(?approved) as ?approved_count)
        (COUNT(?rejected) as ?rejected_count)
        (AVG(?rating) as ?average_rating)
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
        
        OPTIONAL { 
            ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
            FILTER(REGEX(?status, "approuvé", "i"))
            BIND(?assignment as ?approved)
        }
        OPTIONAL { 
            ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
            FILTER(REGEX(?status, "non approuvé", "i"))
            BIND(?assignment as ?rejected)
        }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
    }
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@assignments_bp.route('/assignments/approved', methods=['GET'])
def get_approved_assignments():
    """Récupère les assignements approuvés"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        
        FILTER(REGEX(?status, "approuvé", "i"))
    }
    ORDER BY ?startDate DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/rejected', methods=['GET'])
def get_rejected_assignments():
    """Récupère les assignements rejetés"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        
        FILTER(REGEX(?status, "non approuvé", "i"))
    }
    ORDER BY ?startDate DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/by-volunteer/<volunteer_id>', methods=['GET'])
def get_assignments_by_volunteer(volunteer_id):
    """Récupère les assignements d'un volontaire spécifique"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {{
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> <{volunteer_id}> .
        
        OPTIONAL {{ ?assignment rdfs:label ?label . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }}
    }}
    ORDER BY ?startDate DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/by-event/<event_id>', methods=['GET'])
def get_assignments_by_event(event_id):
    """Récupère les assignements pour un événement spécifique"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {{
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> <{event_id}> .
        
        OPTIONAL {{ ?assignment rdfs:label ?label . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }}
        OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }}
    }}
    ORDER BY ?startDate DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/high-rated', methods=['GET'])
def get_high_rated_assignments():
    """Récupère les assignements avec une note élevée (>= 4)"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> ;
                   <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
        
        FILTER(?rating >= 4)
    }
    ORDER BY ?rating DESC
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@assignments_bp.route('/assignments/advanced-search', methods=['POST'])
def advanced_search_assignments():
    """Recherche avancée d'assignements avec plusieurs critères"""
    data = request.get_json(force=True)
    
    status = data.get('status', '')
    min_rating = data.get('min_rating', '')
    max_rating = data.get('max_rating', '')
    date_from = data.get('date_from', '')
    date_to = data.get('date_to', '')
    volunteer_id = data.get('volunteer_id', '')
    event_id = data.get('event_id', '')
    
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
    """
    
    filters = []
    if status:
        filters.append(f'REGEX(?status, "{status}", "i")')
    if min_rating:
        filters.append(f'?rating >= {min_rating}')
    if max_rating:
        filters.append(f'?rating <= {max_rating}')
    if date_from:
        filters.append(f'?startDate >= "{date_from}"^^xsd:date')
    if date_to:
        filters.append(f'?startDate <= "{date_to}"^^xsd:date')
    if volunteer_id:
        filters.append(f'?volunteer = <{volunteer_id}>')
    if event_id:
        filters.append(f'?event = <{event_id}>')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?startDate DESC"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)

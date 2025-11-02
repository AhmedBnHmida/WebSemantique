from flask import Blueprint, jsonify
from sparql_utils import sparql_utils

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    """Récupère tous les utilisateurs"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?user ?firstName ?lastName ?email ?phone ?role ?registrationDate
    WHERE {
        ?user a eco:User ;
              eco:firstName ?firstName ;
              eco:lastName ?lastName ;
              eco:email ?email ;
              eco:role ?role .
        
        OPTIONAL { ?user eco:phone ?phone . }
        OPTIONAL { ?user eco:registrationDate ?registrationDate . }
    }
    ORDER BY ?lastName ?firstName
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@users_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Récupère un utilisateur spécifique"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?user ?firstName ?lastName ?email ?phone ?role ?registrationDate
    WHERE {{
        <{user_id}> a eco:User ;
              eco:firstName ?firstName ;
              eco:lastName ?lastName ;
              eco:email ?email ;
              eco:role ?role .
        
        OPTIONAL {{ <{user_id}> eco:phone ?phone . }}
        OPTIONAL {{ <{user_id}> eco:registrationDate ?registrationDate . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@users_bp.route('/users/organizers', methods=['GET'])
def get_organizers():
    """Récupère les organisateurs d'événements"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT DISTINCT ?user ?firstName ?lastName ?email ?phone
    WHERE {
        ?event a eco:Event ;
               eco:isOrganizedBy ?user .
        
        ?user eco:firstName ?firstName ;
              eco:lastName ?lastName ;
              eco:email ?email .
        
        OPTIONAL { ?user eco:phone ?phone . }
    }
    ORDER BY ?lastName ?firstName
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@users_bp.route('/users/role/<role>', methods=['GET'])
def get_users_by_role(role):
    """Récupère les utilisateurs par rôle"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?user ?firstName ?lastName ?email ?phone ?registrationDate
    WHERE {{
        ?user a eco:User ;
              eco:firstName ?firstName ;
              eco:lastName ?lastName ;
              eco:email ?email ;
              eco:role ?userRole .
        
        OPTIONAL {{ ?user eco:phone ?phone . }}
        OPTIONAL {{ ?user eco:registrationDate ?registrationDate . }}
        
        FILTER(REGEX(?userRole, "{role}", "i"))
    }}
    ORDER BY ?lastName ?firstName
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)
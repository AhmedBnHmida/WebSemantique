from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils

sponsors_bp = Blueprint('sponsors', __name__)


@sponsors_bp.route('/sponsors', methods=['GET'])
def get_all_sponsors():
    """Récupère tous les sponsors"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring)
    WHERE {
        ?sponsor a eco:Sponsor .
        OPTIONAL { ?sponsor eco:companyName ?companyName }
        OPTIONAL { ?sponsor eco:industry ?industry }
        OPTIONAL { ?sponsor eco:contactEmail ?contactEmail }
        OPTIONAL { ?sponsor eco:phoneNumber ?phoneNumber }
        OPTIONAL { ?sponsor eco:website ?website }
        OPTIONAL { ?sponsor eco:hasSponsorshipLevel ?level . OPTIONAL { ?level eco:levelName ?levelName } }
    }
    ORDER BY ?companyName
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)


@sponsors_bp.route('/sponsors/<sponsor_id>', methods=['GET'])
def get_sponsor(sponsor_id):
    """Récupère un sponsor spécifique"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring) ?donation
    WHERE {{
        <{sponsor_id}> a eco:Sponsor .
        OPTIONAL {{ <{sponsor_id}> eco:companyName ?companyName }}
        OPTIONAL {{ <{sponsor_id}> eco:industry ?industry }}
        OPTIONAL {{ <{sponsor_id}> eco:contactEmail ?contactEmail }}
        OPTIONAL {{ <{sponsor_id}> eco:phoneNumber ?phoneNumber }}
        OPTIONAL {{ <{sponsor_id}> eco:website ?website }}
        OPTIONAL {{ <{sponsor_id}> eco:hasSponsorshipLevel ?level . OPTIONAL {{ ?level eco:levelName ?levelName }} }}
        OPTIONAL {{ <{sponsor_id}> eco:makesDonation ?donation }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})


@sponsors_bp.route('/sponsors/search', methods=['POST'])
def search_sponsors():
    """Recherche de sponsors par critères"""
    data = request.json
    name = data.get('name', '')
    industry = data.get('industry', '')

    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring)
    WHERE {
        ?sponsor a eco:Sponsor .
        OPTIONAL { ?sponsor eco:companyName ?companyName }
        OPTIONAL { ?sponsor eco:industry ?industry }
        OPTIONAL { ?sponsor eco:contactEmail ?contactEmail }
        OPTIONAL { ?sponsor eco:phoneNumber ?phoneNumber }
        OPTIONAL { ?sponsor eco:website ?website }
        OPTIONAL { ?sponsor eco:hasSponsorshipLevel ?level . OPTIONAL { ?level eco:levelName ?levelName } }
    """

    filters = []
    if name:
        filters.append(f'REGEX(?companyName, "{name}", "i")')
    if industry:
        filters.append(f'REGEX(?industry, "{industry}", "i")')

    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"

    query += "} ORDER BY ?companyName"

    results = sparql_utils.execute_query(query)
    return jsonify(results)


@sponsors_bp.route('/donations', methods=['GET'])
def get_all_donations():
    """Récupère toutes les donations"""
    # Query params: type (Donation|FinancialDonation|MaterialDonation|ServiceDonation), sort (newest|oldest), limit (int)
    q_type = request.args.get('type')  # expected short name, e.g. FinancialDonation
    q_sort = request.args.get('sort', 'newest')
    q_limit = request.args.get('limit')

    prefix = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    """

    where_clauses = [
        "?donation a ?type .",
        "OPTIONAL { ?donation eco:amount ?amount }",
        "OPTIONAL { ?donation eco:currency ?currency }",
        "OPTIONAL { ?donation eco:dateDonated ?date }",
        "OPTIONAL { ?donation eco:itemDescription ?itemDescription }",
        "OPTIONAL { ?donation eco:estimatedValue ?estimatedValue }",
        "OPTIONAL { ?donation eco:hoursDonated ?hoursDonated }",
        "OPTIONAL { ?donation eco:fundsEvent ?event . ?event eco:eventTitle ?eventTitle . }",
        "OPTIONAL { ?donation ^eco:makesDonation ?donor . OPTIONAL { ?donor eco:companyName ?donorName } }",
    ]

    # Build type filter
    type_filter = "(?type = eco:Donation || ?type = eco:FinancialDonation || ?type = eco:MaterialDonation || ?type = eco:ServiceDonation)"
    if q_type:
        # allow passing either full URI or short name
        if q_type.startswith('http'):
            type_filter = f"?type = <{q_type}>"
        else:
            # sanitize short name
            safe_type = ''.join(ch for ch in q_type if ch.isalnum() or ch == '_')
            type_filter = f"?type = eco:{safe_type}"

    where = "\n        ".join(where_clauses)

    order_clause = "ORDER BY DESC(?date)"
    if q_sort and q_sort.lower() in ('oldest', 'asc'):
        order_clause = "ORDER BY ASC(?date)"

    limit_clause = "LIMIT 200"
    if q_limit:
        try:
            li = int(q_limit)
            limit_clause = f"LIMIT {max(1, min(li, 1000))}"
        except Exception:
            pass

    query = f"""
    {prefix}
    SELECT ?donation ?type (?amount AS ?montant) (?currency AS ?devise) (?donorName AS ?donateur) ?date (?itemDescription AS ?description) (?estimatedValue AS ?valeurEstimee) (?hoursDonated AS ?heuresDonnees) (?eventTitle AS ?evenement)
    WHERE {{
        {where}
        FILTER({type_filter})
    }}
    {order_clause}
    {limit_clause}
    """

    results = sparql_utils.execute_query(query)
    return jsonify(results)


@sponsors_bp.route('/donations/<donation_id>', methods=['GET'])
def get_donation(donation_id):
    """Récupère une donation spécifique"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?donation ?type (?amount AS ?montant) (?currency AS ?devise) ?date (?donorName AS ?donateur) (?eventTitle AS ?evenement) (?itemDescription AS ?description) (?estimatedValue AS ?valeurEstimee) (?hoursDonated AS ?heuresDonnees)
    WHERE {{
        <{donation_id}> a ?type .
        OPTIONAL {{ <{donation_id}> eco:amount ?amount }}
        OPTIONAL {{ <{donation_id}> eco:currency ?currency }}
        OPTIONAL {{ <{donation_id}> eco:dateDonated ?date }}
        OPTIONAL {{ <{donation_id}> eco:itemDescription ?itemDescription }}
        OPTIONAL {{ <{donation_id}> eco:estimatedValue ?estimatedValue }}
        OPTIONAL {{ <{donation_id}> eco:hoursDonated ?hoursDonated }}
        OPTIONAL {{ <{donation_id}> ^eco:makesDonation ?donor . OPTIONAL {{ ?donor eco:companyName ?donorName }} }}
        OPTIONAL {{ <{donation_id}> eco:fundsEvent ?event . OPTIONAL {{ ?event eco:eventTitle ?eventTitle }} }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

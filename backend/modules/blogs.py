from flask import Blueprint, jsonify, request, current_app as app
from sparql_utils import sparql_utils
import uuid

BASE_BLOG_URI = "http://example.org/blog/"

blogs_bp = Blueprint('blogs', __name__)

@blogs_bp.route('/blogs', methods=['GET'])
def get_all_blogs():
    """Récupère tous les blogs"""
    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?blog ?title ?content ?category ?publicationDate
    WHERE {
        ?blog a eco:Blog .
        OPTIONAL { ?blog eco:blogTitle ?title . }
        OPTIONAL { ?blog eco:blogContent ?content . }
        OPTIONAL { ?blog eco:category ?category . }
        OPTIONAL { ?blog eco:publicationDate ?publicationDate . }
    }
    ORDER BY DESC(?publicationDate)
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)


@blogs_bp.route('/blogs/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    """Récupère un blog spécifique par son URI/id"""
    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?blog ?title ?content ?category ?publicationDate
    WHERE {{
        <{blog_id}> a eco:Blog .
        OPTIONAL {{ <{blog_id}> eco:blogTitle ?title . }}
        OPTIONAL {{ <{blog_id}> eco:blogContent ?content . }}
        OPTIONAL {{ <{blog_id}> eco:category ?category . }}
        OPTIONAL {{ <{blog_id}> eco:publicationDate ?publicationDate . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})


@blogs_bp.route('/blogs/search', methods=['POST'])
def search_blogs():
    """Recherche de blogs par critères: title, category, keyword, date range"""
    data = request.get_json(force=True) if request.data else {}
    title = data.get('title', '').strip()
    category = data.get('category', '').strip()
    keyword = data.get('keyword', '').strip()
    date_from = data.get('date_from', '').strip()
    date_to = data.get('date_to', '').strip()

    query = """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?blog ?blogTitle ?blogContent ?category ?publicationDate
    WHERE {
        ?blog a eco:Blog .
        ?blog eco:blogTitle ?blogTitle .
        ?blog eco:blogContent ?blogContent .
        OPTIONAL { ?blog eco:category ?category . }
        OPTIONAL { ?blog eco:publicationDate ?publicationDate . }
    """

    filters = []
    if title:
        # case-insensitive partial match for title
        filters.append(f'REGEX(?blogTitle, "{title}", "i")')
    if keyword:
        # search in both content and title
        filters.append(f'(REGEX(?blogContent, "{keyword}", "i") || REGEX(?blogTitle, "{keyword}", "i"))')
    if category:
        filters.append(f'REGEX(?category, "{category}", "i")')
    if date_from:
        # assume date in ISO format YYYY-MM-DD or full datetime; simple string comparison
        filters.append(f'(?publicationDate >= "{date_from}"^^xsd:dateTime || ?publicationDate >= "{date_from}"^^xsd:date)')
    if date_to:
        filters.append(f'(?publicationDate <= "{date_to}"^^xsd:dateTime || ?publicationDate <= "{date_to}"^^xsd:date)')

    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"

    # Debug: log the constructed SPARQL query for troubleshooting
    try:
        app.logger.debug("Blogs search SPARQL query:\n%s", query)
    except Exception:
        # Fallback to print if logger not available (shouldn't happen in Flask)
        print("Blogs search SPARQL query:\n", query)

    query += "} ORDER BY DESC(?publicationDate)"

    # Add xsd prefix if date filters used
    if date_from or date_to:
        query = 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n' + query

    results = sparql_utils.execute_query(query)
    return jsonify(results)


@blogs_bp.route('/blogs', methods=['POST'])
def create_blog():
    """Créer un nouveau blog. Attends JSON: title, content, category, publicationDate (optionnel)."""
    data = request.get_json(force=True) if request.data else {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', '').strip()
    publicationDate = data.get('publicationDate', '').strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    blog_id = str(uuid.uuid4())
    blog_uri = BASE_BLOG_URI + blog_id

    # Escape quotes in literals
    def esc(s):
        return s.replace('"', '\\"') if s else ''

    insert_parts = [f"<{blog_uri}> a eco:Blog ;",
                    f'eco:blogTitle "{esc(title)}" ;',
                    f'eco:blogContent "{esc(content)}" ;']
    if category:
        insert_parts.append(f'eco:category "{esc(category)}" ;')
    if publicationDate:
        insert_parts.append(f'eco:publicationDate "{esc(publicationDate)}" ;')

    # remove trailing semicolon on last triple
    insert_parts[-1] = insert_parts[-1].rstrip(' ;') + ' .'

    insert_query = "PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\n"
    insert_query += "INSERT DATA {\n" + "\n".join(insert_parts) + "\n}"

    res = sparql_utils.execute_update(insert_query)
    if isinstance(res, dict) and res.get('error'):
        return jsonify(res), 500

    return jsonify({"status": "created", "blog_uri": blog_uri}), 201


@blogs_bp.route('/blogs/<path:blog_id>', methods=['PUT'])
def update_blog(blog_id):
    """Mettre à jour un blog. Le paramètre blog_id peut être soit un URI complet soit l'UUID généré."""
    data = request.get_json(force=True) if request.data else {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', '').strip()
    publicationDate = data.get('publicationDate', '').strip()

    # normalize to full URI
    if blog_id.startswith('http://') or blog_id.startswith('https://'):
        blog_uri = blog_id
    else:
        blog_uri = BASE_BLOG_URI + blog_id

    def esc(s):
        return s.replace('"', '\\"') if s else ''

    # Delete existing triples for this blog and insert new ones
    delete_query = f"PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\nDELETE WHERE {{ <{blog_uri}> ?p ?o . }}"

    insert_parts = [f"<{blog_uri}> a eco:Blog ;"]
    if title:
        insert_parts.append(f'eco:blogTitle "{esc(title)}" ;')
    if content:
        insert_parts.append(f'eco:blogContent "{esc(content)}" ;')
    if category:
        insert_parts.append(f'eco:category "{esc(category)}" ;')
    if publicationDate:
        insert_parts.append(f'eco:publicationDate "{esc(publicationDate)}" ;')

    if len(insert_parts) == 1:
        # nothing to insert
        return jsonify({"status": "no_changes"}), 200

    insert_parts[-1] = insert_parts[-1].rstrip(' ;') + ' .'
    insert_query = "PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\nINSERT DATA {\n" + "\n".join(insert_parts) + "\n}"

    # execute delete then insert
    dres = sparql_utils.execute_update(delete_query)
    if isinstance(dres, dict) and dres.get('error'):
        return jsonify(dres), 500

    ires = sparql_utils.execute_update(insert_query)
    if isinstance(ires, dict) and ires.get('error'):
        return jsonify(ires), 500

    return jsonify({"status": "updated", "blog_uri": blog_uri}), 200


@blogs_bp.route('/blogs/<path:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    """Supprimer un blog et ses triplets associés."""
    if blog_id.startswith('http://') or blog_id.startswith('https://'):
        blog_uri = blog_id
    else:
        blog_uri = BASE_BLOG_URI + blog_id

    delete_query = f"PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\nDELETE WHERE {{ <{blog_uri}> ?p ?o . }}"
    res = sparql_utils.execute_update(delete_query)
    if isinstance(res, dict) and res.get('error'):
        return jsonify(res), 500
    return jsonify({"status": "deleted", "blog_uri": blog_uri}), 200

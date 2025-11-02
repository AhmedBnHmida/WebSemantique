from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
import uuid

reviews_bp = Blueprint('reviews', __name__)

BASE_REVIEW_URI = "http://example.org/review/"

@reviews_bp.route('/reviews', methods=['POST'])
def create_review():
    """Créer un review pour un blog.
    JSON attendu: blog (URI), reviewerName, rating (int), comment, date (optionnel)
    """
    data = request.get_json(force=True) if request.data else {}
    blog = data.get('blog', '').strip()
    reviewer = data.get('reviewerName', '').strip()
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    date = data.get('date', '').strip()

    if not blog or not reviewer or rating is None:
        return jsonify({"error": "blog, reviewerName and rating are required"}), 400

    review_id = str(uuid.uuid4())
    review_uri = BASE_REVIEW_URI + review_id

    def esc(s):
        return s.replace('"', '\\"') if s else ''

    insert_parts = [f"<{review_uri}> a eco:Review ;",
                    f'eco:reviewerName "{esc(reviewer)}" ;',
                    f'eco:rating "{esc(str(rating))}" ;',
                    f'eco:reviewOf <{blog}> ;']
    if comment:
        insert_parts.append(f'eco:reviewContent "{esc(comment)}" ;')
    if date:
        insert_parts.append(f'eco:reviewDate "{esc(date)}" ;')

    insert_parts[-1] = insert_parts[-1].rstrip(' ;') + ' .'

    insert_query = "PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\n"
    insert_query += "INSERT DATA {\n" + "\n".join(insert_parts) + "\n}"

    res = sparql_utils.execute_update(insert_query)
    if isinstance(res, dict) and res.get('error'):
        return jsonify(res), 500

    return jsonify({"status": "created", "review_uri": review_uri}), 201


@reviews_bp.route('/reviews', methods=['GET'])
def list_reviews():
    """Liste des reviews pour un blog: ?blog=URI"""
    blog = request.args.get('blog', '').strip()
    if not blog:
        return jsonify({"error": "blog query parameter required (full URI)"}), 400

    query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?review ?reviewerName ?rating ?reviewContent ?reviewDate
    WHERE {{
        ?review a eco:Review .
        ?review eco:reviewerName ?reviewerName .
        ?review eco:rating ?rating .
        OPTIONAL {{ ?review eco:reviewContent ?reviewContent }}
        OPTIONAL {{ ?review eco:reviewDate ?reviewDate }}
        FILTER(?review eco:reviewOf <{blog}>)
    }} ORDER BY DESC(?reviewDate)
    """

    # Note: SPARQL syntax in FILTER line above may need adjustment depending on ontology; if that fails,
    # use a simple pattern matching triple instead.

    # Fallback query if the FILTER approach above is invalid for the SPARQL engine:
    fallback_query = f"""
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    SELECT ?review ?reviewerName ?rating ?reviewContent ?reviewDate
    WHERE {{
        ?review a eco:Review .
        ?review eco:reviewerName ?reviewerName .
        ?review eco:rating ?rating .
        OPTIONAL {{ ?review eco:reviewContent ?reviewContent }}
        OPTIONAL {{ ?review eco:reviewDate ?reviewDate }}
        ?review eco:reviewOf <{blog}> .
    }} ORDER BY DESC(?reviewDate)
    """

    results = sparql_utils.execute_query(fallback_query)
    return jsonify(results)

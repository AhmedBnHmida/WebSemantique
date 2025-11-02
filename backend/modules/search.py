from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.taln_service import TALNService
from modules.gemini_sparql_service import GeminiSPARQLTransformer

search_bp = Blueprint('search', __name__)

# Initialize services
taln_service = TALNService()
gemini_transformer = GeminiSPARQLTransformer()

@search_bp.route('/search', methods=['POST'])
def semantic_search():
    """Recherche sémantique - TALN → Gemini → SPARQL pipeline"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🔍 Processing question: {question}")
        
        # Step 1: TALN Analysis - Extract entities, relationships, intent
        print("📝 Step 1: TALN Analysis...")
        taln_analysis = taln_service.analyze_question(question)
        print(f"✅ TALN Analysis completed. Entities: {len(taln_analysis.get('entities', []))}")
        
        # Step 2: Gemini SPARQL Generation - Generate query from TALN analysis
        print("🤖 Step 2: Gemini SPARQL Generation...")
        sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
        print(f"✅ SPARQL Query generated: {len(sparql_query)} characters")
        
        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 400

        # Heuristic override: if the user asks "who" (qui) about donations, prefer returning sponsors
        q_lower = question.lower()
        try:
            if 'qui' in q_lower and 'donat' in q_lower:
                print("DEBUG: Question asks who made donations - overriding to sponsor query")
                sparql_query = '''PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
SELECT DISTINCT ?sponsor ?companyName ?donation
WHERE {
  ?sponsor a eco:Sponsor .
  OPTIONAL { ?sponsor eco:companyName ?companyName . }
  OPTIONAL { ?sponsor eco:makesDonation ?donation . }
}
LIMIT 50'''
                print(f"DEBUG: Overridden SPARQL query (sponsor lookup): {sparql_query[:200]}...")
        except Exception:
            # If anything goes wrong with the heuristic, continue with original query
            pass
        
        # Step 3: Execute SPARQL Query
        print("⚡ Step 3: Executing SPARQL Query...")
        results = sparql_utils.execute_query(sparql_query)
        print(f"✅ Query executed. Results: {len(results) if results else 0} rows")
        
        # Return comprehensive response
        return jsonify({
            "question": question,
            "taln_analysis": taln_analysis,
            "sparql_query": sparql_query,
            "results": results,
            "pipeline_info": {
                "taln_confidence": taln_analysis.get('confidence_scores', {}).get('overall_confidence', 0.0),
                "entities_detected": len(taln_analysis.get('entities', [])),
                "intent_classified": taln_analysis.get('intent', {}).get('primary_intent', 'unknown'),
                "query_length": len(sparql_query),
                "results_count": len(results) if results else 0
            }
        })
        
    except Exception as e:
        print(f"❌ Error in semantic search pipeline: {str(e)}")
        return jsonify({"error": f"Erreur dans le pipeline de recherche: {str(e)}"}), 500

@search_bp.route('/search/ai', methods=['POST'])
def ai_search():
    """Recherche avec IA - Version alternative utilisant directement Gemini"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🤖 AI Search processing: {question}")
        
        # Direct Gemini transformation (fallback method)
        sparql_query = gemini_transformer.transform_question_to_sparql(question)
        
        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 400
        # Heuristic override for 'who made donations' questions
        q_lower = question.lower()
        try:
            if 'qui' in q_lower and 'donat' in q_lower:
                print("DEBUG: AI Search - question asks who made donations - overriding to sponsor query")
                sparql_query = '''PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
SELECT DISTINCT ?sponsor ?companyName ?donation
WHERE {
  ?sponsor a eco:Sponsor .
  OPTIONAL { ?sponsor eco:companyName ?companyName . }
  OPTIONAL { ?sponsor eco:makesDonation ?donation . }
}
LIMIT 50'''
        except Exception:
            pass
        
        # Execute query
        results = sparql_utils.execute_query(sparql_query)
        
        return jsonify({
            "question": question,
            "sparql_query": sparql_query,
            "results": results,
            "method": "direct_gemini"
        })
        
    except Exception as e:
        print(f"❌ Error in AI search: {str(e)}")
        return jsonify({"error": f"Erreur dans la recherche IA: {str(e)}"}), 500

@search_bp.route('/search/hybrid', methods=['POST'])
def hybrid_search():
    """Recherche hybride - Combine TALN + Gemini + fallback"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🔄 Hybrid Search processing: {question}")
        
        # Try TALN + Gemini first
        try:
            taln_analysis = taln_service.analyze_question(question)
            sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
            method_used = "taln_gemini"
        except Exception as e:
            print(f"TALN+Gemini failed, falling back to direct Gemini: {e}")
            sparql_query = gemini_transformer.transform_question_to_sparql(question)
            method_used = "direct_gemini"
            taln_analysis = None
        
        # Heuristic override: if the user asks "who" about donations, prefer returning sponsors
        q_lower = question.lower()
        try:
            if 'qui' in q_lower and 'donat' in q_lower:
                print("DEBUG: Hybrid Search - question asks who made donations - overriding to sponsor query")
                sparql_query = '''PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
SELECT DISTINCT ?sponsor ?companyName ?donation
WHERE {
  ?sponsor a eco:Sponsor .
  OPTIONAL { ?sponsor eco:companyName ?companyName . }
  OPTIONAL { ?sponsor eco:makesDonation ?donation . }
}
LIMIT 50'''
                method_used = "heuristic_sponsor_lookup"
        except Exception:
            pass

        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 400
        
        # Execute query
        results = sparql_utils.execute_query(sparql_query)

        response = {
            "question": question,
            "sparql_query": sparql_query,
            "results": results,
            "method": method_used,
            "heuristic": None
        }

        if taln_analysis:
            response["taln_analysis"] = taln_analysis

        return jsonify(response)

    except Exception as e:
        print(f"❌ Error in hybrid search: {str(e)}")
        return jsonify({"error": f"Erreur dans la recherche hybride: {str(e)}"}), 500
